#!/usr/bin/env python3
"""
docx_to_md.py — Word 文档转 Markdown
用法: python docx_to_md.py input.docx [output.md]
"""

import sys
import os
import re
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    import docx.opc.constants
except ImportError:
    print("错误: 未安装 python-docx，请运行: pip install python-docx")
    sys.exit(1)


def get_cell_text(cell):
    """提取表格单元格的文本（含粗体/斜体）"""
    parts = []
    for para in cell.paragraphs:
        parts.append(get_para_text(para))
    return " ".join(parts).strip()


def get_para_text(para):
    """提取段落的 Markdown 文本（处理粗体、斜体、超链接）"""
    parts = []
    for run in para.runs:
        text = run.text
        if not text:
            continue
        # 处理超链接（run 所在的 hyperlink 元素）
        # 粗体 + 斜体
        if run.bold and run.italic:
            text = f"***{text}***"
        elif run.bold:
            text = f"**{text}**"
        elif run.italic:
            text = f"*{text}*"
        parts.append(text)
    return "".join(parts)


def extract_hyperlinks(para):
    """从段落 XML 中提取超链接，返回 {rId: url} 映射"""
    links = {}
    try:
        for rel in para.part.rels.values():
            if "hyperlink" in rel.reltype:
                links[rel.rId] = rel.target_ref
    except Exception:
        pass
    return links


def para_to_md(para, hyperlinks=None):
    """将段落转为 Markdown 字符串"""
    style_name = para.style.name if para.style else ""

    # 标题
    heading_map = {
        "Heading 1": "#",
        "Heading 2": "##",
        "Heading 3": "###",
        "Heading 4": "####",
        "Heading 5": "#####",
        "Heading 6": "######",
        "标题 1": "#",
        "标题 2": "##",
        "标题 3": "###",
        "标题 4": "####",
    }
    for style_key, prefix in heading_map.items():
        if style_name.startswith(style_key):
            text = para.text.strip()
            return f"{prefix} {text}" if text else ""

    # 列表项
    is_list = "List" in style_name or "列表" in style_name
    is_numbered = "Number" in style_name or "编号" in style_name or "List Number" in style_name

    # 超链接处理
    full_text = get_para_text(para)

    # 检查段落内是否有超链接 XML 节点
    try:
        for hyperlink in para._element.findall(f'.//{qn("w:hyperlink")}'):
            r_id = hyperlink.get(qn("r:id"))
            if r_id and hyperlinks and r_id in hyperlinks:
                url = hyperlinks[r_id]
                link_text = "".join(
                    r.text for r in hyperlink.findall(f'.//{qn("w:t")}')
                    if r.text
                )
                if link_text:
                    full_text = full_text.replace(link_text, f"[{link_text}]({url})")
    except Exception:
        pass

    if not full_text.strip():
        return ""

    if is_numbered:
        return f"1. {full_text}"
    if is_list:
        return f"- {full_text}"

    return full_text


def table_to_md(table):
    """将表格转为 Markdown 表格"""
    rows = table.rows
    if not rows:
        return ""

    lines = []
    for i, row in enumerate(rows):
        cells = [get_cell_text(cell) for cell in row.cells]
        # 合并相邻重复单元格（Word 合并单元格会重复）
        seen = []
        for j, c in enumerate(cells):
            if j > 0 and cells[j] == cells[j - 1]:
                seen.append("")
            else:
                seen.append(c)
        line = "| " + " | ".join(seen) + " |"
        lines.append(line)
        if i == 0:
            sep = "| " + " | ".join(["---"] * len(seen)) + " |"
            lines.append(sep)

    return "\n".join(lines)


def extract_images(doc, output_dir):
    """提取文档中的图片到 assets/ 目录，返回 {image_part: 文件名} 映射"""
    assets_dir = Path(output_dir) / "assets"
    image_map = {}

    try:
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_part = rel.target_part
                ext = Path(image_part.partname).suffix or ".png"
                fname = f"image_{len(image_map) + 1}{ext}"
                fpath = assets_dir / fname
                assets_dir.mkdir(parents=True, exist_ok=True)
                with open(fpath, "wb") as f:
                    f.write(image_part.blob)
                image_map[image_part] = f"assets/{fname}"
    except Exception as e:
        print(f"  警告: 图片提取部分失败: {e}")

    return image_map


def docx_to_markdown(input_path: str, output_path: str = None) -> str:
    """主转换函数，返回 Markdown 字符串"""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    doc = Document(str(input_path))

    # 确定输出目录（用于图片提取）
    out_dir = Path(output_path).parent if output_path else input_path.parent
    image_map = extract_images(doc, out_dir)

    lines = []
    # 用于追踪上一个元素，避免多余空行
    last_was_empty = False

    # 遍历文档 body 中的所有顶层元素
    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            # 段落
            from docx.text.paragraph import Paragraph
            para = Paragraph(element, doc)
            hyperlinks = extract_hyperlinks(para)

            # 检查是否是图片段落
            pics = element.findall(f'.//{qn("w:drawing")}') or \
                   element.findall('.//{urn:schemas-microsoft-com:vml}imagedata')
            if pics:
                lines.append("[图片]")
                last_was_empty = False
                continue

            md_line = para_to_md(para, hyperlinks)

            if md_line:
                lines.append(md_line)
                last_was_empty = False
            else:
                if not last_was_empty:
                    lines.append("")
                last_was_empty = True

        elif tag == "tbl":
            # 表格
            from docx.table import Table
            table = Table(element, doc)
            table_md = table_to_md(table)
            if table_md:
                if lines and lines[-1] != "":
                    lines.append("")
                lines.append(table_md)
                lines.append("")
            last_was_empty = True

    # 清理末尾多余空行
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python docx_to_md.py input.docx [output.md]")
        print("示例: python docx_to_md.py 报告.docx 报告.md")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".md"))

    print(f"转换中: {input_path} → {output_path}")

    try:
        md_content = docx_to_markdown(input_path, output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        lines = md_content.count("\n") + 1
        chars = len(md_content)
        print(f"完成！共 {lines} 行，{chars} 字符")
        print(f"输出: {output_path}")

        # 预览前5行
        preview = "\n".join(md_content.split("\n")[:5])
        print(f"\n--- 预览 ---\n{preview}\n...")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
