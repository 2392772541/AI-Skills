#!/usr/bin/env python3
"""Convert a recovered weekly Markdown report to Feishu/Lark Docx XML.

Expected Markdown item shape:

1. Title text
确定链接：https://...
备选链接：https://...；https://...

The generated XML builds a heading-driven Feishu layout:

- `h2` section headings render the large category titles and drive Feishu's automatic left outline;
- `h3` item headings render numbered video/tool titles and become outline children;
- link rows, alternatives, bookmarks, and preview images stay under each item heading.

Detail item shape:

<h3><span text-color="blue">1.</span> Title text</h3>
<p><a href="https://...">https://...</a></p>
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ITEM_RE = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
URL_LINE_RE = re.compile(r"^https?://\S+$")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def parse_markdown(text: str):
    title = "视频复原周报"
    sections = []
    current_section = None
    current_item = None
    current_subsection = ""

    def flush_item():
        nonlocal current_item
        if current_section is not None and current_item is not None:
            current_section["items"].append(current_item)
        current_item = None

    def start_item(raw_title: str, level: int):
        nonlocal current_item
        flush_item()
        match = ITEM_RE.match(raw_title)
        current_item = {
            "number": match.group(1) if match else "",
            "numbered": bool(match),
            "title": match.group(2) if match else raw_title,
            "subsection": current_subsection,
            "level": level,
            "confirmed": "",
            "alternatives": [],
            "notes": [],
            "images": [],
            "local_images": [],
        }

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_item()
            current_section = {
                "title": line[3:].strip(),
                "items": [],
                "notes": [],
                "subsections": [],
                "subsection_notes": {},
            }
            sections.append(current_section)
            current_subsection = ""
            continue
        if line.startswith("### ") and current_section is not None:
            value = line[4:].strip()
            if ITEM_RE.match(value):
                start_item(value, 3)
            else:
                flush_item()
                current_subsection = value
                if value not in current_section["subsections"]:
                    current_section["subsections"].append(value)
                    current_section["subsection_notes"][value] = []
            continue
        if line.startswith("#### ") and current_section is not None:
            start_item(line[5:].strip(), 4)
            continue

        match = ITEM_RE.match(line)
        if match and current_section is not None:
            start_item(line, 3)
            continue

        if current_item is None:
            note = line[1:].strip() if line.startswith(">") else line
            if current_section is not None:
                if current_subsection:
                    current_section["subsection_notes"].setdefault(current_subsection, []).append(note)
                else:
                    current_section["notes"].append(note)
            continue
        if line.startswith("确定链接："):
            current_item["confirmed"] = line.split("：", 1)[1].strip()
        elif line.startswith(("备选链接：", "备选：")):
            raw_alts = line.split("：", 1)[1].strip()
            current_item["alternatives"].extend(
                part for part in re.split(r"[；;]\s*", raw_alts) if part
            )
        elif URL_LINE_RE.match(line):
            current_item["confirmed"] = line
        elif (image_match := IMAGE_RE.match(line)):
            href = image_match.group(2)
            if href.startswith(("http://", "https://")):
                current_item["images"].append(
                    {"href": href, "width": "700", "name": image_match.group(1) or "preview"}
                )
            else:
                current_item["local_images"].append(href)
        else:
            current_item["notes"].append(line[1:].strip() if line.startswith(">") else line)

    flush_item()
    return title, sections


def make_item(
    title,
    confirmed="",
    alternatives=None,
    notes=None,
    bookmarks=None,
    images=None,
    number="",
    subsection="",
    level=3,
    local_images=None,
    numbered=True,
):
    return {
        "title": title,
        "number": number,
        "numbered": numbered,
        "subsection": subsection,
        "level": level,
        "confirmed": confirmed,
        "alternatives": alternatives or [],
        "notes": notes or [],
        "bookmarks": bookmarks or [],
        "images": images or [],
        "local_images": local_images or [],
    }


def find_item(items, *needles):
    for needle in needles:
        needle_l = needle.lower()
        for item in items:
            if needle_l in item["title"].lower():
                return item
    return None


def apply_source_overrides(title, sections):
    """Correct known source-visible grouping for the 2026-07-07 weekly.

    The source video/screenshot shows "# 设计模块" and "# 工具与科技" as
    separate manual-directory sections. OCR regrouping can merge these.
    """
    if "2026-07-07" not in title:
        return sections

    out = []
    for section in sections:
        if section["title"] in {"AI视野", "AI改变"}:
            continue
        if section["title"] == "设计模块":
            source_items = section["items"]
            config = find_item(source_items, "Config")
            workflow = find_item(source_items, "AI设计工作流")
            lottie = find_item(source_items, "LottieFiles")
            figma_particle = find_item(source_items, "Figma 粒子")
            loader = find_item(source_items, "17个创意加载")
            vocab = find_item(source_items, "动画词汇")
            reicon = find_item(source_items, "Reicon")
            if reicon:
                reicon = dict(reicon)
                reicon["notes"] = [
                    "Reicon是一个隐藏的宝藏图标库，拥有2700+个专为现代 UI/UX项目打造的 SVG图标。它开源、免费、易于定制，完美适用于现代设计项目。",
                    "每个图标都提供两种字重--轮廓和填充--并且可以完全自定义大小、颜色和自定义属性/props。图标在与打包工具或框架一起使用时支持摇树优化，从而确保最小的包体积。",
                ]
                reicon["bookmarks"] = [
                    {
                        "name": "Reicon Figma 插件",
                        "href": "https://www.figma.com/community/plugin/1652983191908763066",
                    }
                ]
                reicon["images"] = [
                    {
                        "href": "https://reicon.dev/og-image.png?v=4",
                        "width": "700",
                        "name": "Reicon preview",
                    }
                ]
            icones = find_item(source_items, "Icones")
            mech = find_item(source_items, "Mech", "机械结构")
            play_fast = find_item(source_items, "Landing Page", "Play Fast")
            openpencil = find_item(source_items, "OpenPencil")

            out.append({
                "title": "设计模块",
                "items": [
                    make_item("「营销不是换皮肤做交互」", "https://www.woshipm.com/operate/6423000.html"),
                    make_item("山字货的微光生态：用户上当、商户泣诉、当灰色玩法的星际"),
                    config or make_item("2026 Figma Config 大会更新了哪些内容？（汇总版）"),
                    workflow or make_item("AI设计工作流全景拆解：Figma MCP/Claude Design/Codex/GoogleStitch"),
                    make_item("适配介入：以用户意图圈对全 AI 存在感"),
                    make_item("用OpenAI的Codex通过MCP插件来远程操控Blender建模"),
                ],
            })
            out.append({
                "title": "工具与科技",
                "items": [
                    make_item("灵感网站推荐：让AI也能拥有「设计感」"),
                    lottie or make_item("LottieFiles 插件支持导出 Figma Motion 的动画为json"),
                    figma_particle or make_item("Figma粒子特效插件"),
                    make_item("设计灵感采集站:Posts.design", "https://posts.design"),
                    make_item("着色器渐变生成器:Gradient Lab"),
                    loader or make_item("17个创意加载动画"),
                    vocab or make_item("动画词汇对照表"),
                    reicon or make_item("高质量SVG图标库:Reicon"),
                    icones or make_item("Icones 桌面客户端:Icones Desktop"),
                    mech or make_item("常见物品机械结构剖析:MechanicalPencil"),
                    play_fast or make_item("微动画 Landing Page 灵感:Play Fast"),
                    make_item("Reve 2.0 AI性图加载动画灵感设计"),
                    openpencil or make_item("OpenPencil—开源可编程的Figma替代品"),
                    make_item("Grill-me--让AI反问你澄清需求的Skill", "https://github.com/mattpocock/skills"),
                ],
            })
        elif section["title"] == "AI热点":
            out.append({
                "title": section["title"],
                "items": [item for item in section["items"] if "Grill" not in item["title"]],
            })
        else:
            out.append(section)
    out.append({"title": "星期快讯", "items": [make_item("且曼成都线下面会 😍")]})
    order = {"本周最TOP": 0, "AI热点": 1, "AI基础": 2, "设计模块": 3, "工具与科技": 4, "星期快讯": 5}
    return sorted(out, key=lambda section: order.get(section["title"], 99))


def link_label(url: str) -> str:
    if "figma.com" in url:
        return "Figma 插件"
    if "github.com" in url:
        return "Github"
    if "reicon.dev" in url or "mechanicalpencil.com" in url or "openpencil.dev" in url:
        return "网站"
    if "lottiefiles.com" in url:
        return "Figma 插件"
    return ""


def render_link_row(url: str) -> str:
    label = link_label(url)
    if label:
        return f'<p>{esc(label)}: <a href="{esc(url)}">{esc(url)}</a></p>'
    return f'<p><a href="{esc(url)}">{esc(url)}</a></p>'


def render_heading_item(item, seq: int, level: int = 3) -> str:
    number = item.get("number") or str(seq)
    tag = "h4" if level == 4 else "h3"
    if item.get("numbered", True):
        heading = f'<{tag}><span text-color="blue">{esc(number)}.</span> {esc(item["title"])}</{tag}>'
    else:
        heading = f'<{tag}>{esc(item["title"])}</{tag}>'
    lines = [heading]
    for note in item.get("notes", []):
        lines.append(f'<p><span text-color="gray">{esc(note)}</span></p>')
    confirmed = item.get("confirmed", "")
    if confirmed:
        lines.append(render_link_row(confirmed))

    alternatives = item.get("alternatives", [])
    if alternatives:
        for alt in alternatives:
            lines.append(render_link_row(alt))
    for bookmark in item.get("bookmarks", []):
        lines.append(
            f'<p><bookmark name="{esc(bookmark["name"])}" href="{esc(bookmark["href"])}"></bookmark></p>'
        )
    for image in item.get("images", []):
        width = esc(str(image.get("width", "700")))
        name = esc(image.get("name", "preview"))
        href = esc(image["href"])
        lines.append(f'<img href="{href}" width="{width}" name="{name}"/>')
    return "\n".join(lines)


def render_xml(title: str, sections) -> str:
    lines = [f"<title>{esc(title)}</title>"]
    for section in sections:
        lines.append(f'<h2><span text-color="red"># {esc(section["title"])}</span></h2>')
        for note in section.get("notes", []):
            lines.append(f'<p><span text-color="gray">{esc(note)}</span></p>')

        direct_items = [item for item in section["items"] if not item.get("subsection")]
        for seq, item in enumerate(direct_items, start=1):
            lines.append(render_heading_item(item, seq, 3))

        subsection_order = list(section.get("subsections", []))
        for item in section["items"]:
            subsection = item.get("subsection", "")
            if subsection and subsection not in subsection_order:
                subsection_order.append(subsection)
        for subsection in subsection_order:
            lines.append(f"<h3>{esc(subsection)}</h3>")
            for note in section.get("subsection_notes", {}).get(subsection, []):
                lines.append(f'<p><span text-color="gray">{esc(note)}</span></p>')
            subsection_items = [
                item for item in section["items"] if item.get("subsection") == subsection
            ]
            for seq, item in enumerate(subsection_items, start=1):
                lines.append(render_heading_item(item, seq, 4))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Recovered document.md")
    parser.add_argument("output", type=Path, help="Feishu Docx XML output path")
    parser.add_argument(
        "--media-manifest",
        type=Path,
        help="Optional JSON manifest for local images that must be inserted after document creation",
    )
    args = parser.parse_args()

    title, sections = parse_markdown(args.input.read_text(encoding="utf-8"))
    sections = apply_source_overrides(title, sections)
    if "2026-07-07" in title:
        title = "且曼内刊 - Vol.283 20260707"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_xml(title, sections), encoding="utf-8")

    local_media = [
        {
            "section": section["title"],
            "subsection": item.get("subsection", ""),
            "number": item.get("number", ""),
            "title": item["title"],
            "path": path,
        }
        for section in sections
        for item in section["items"]
        for path in item.get("local_images", [])
    ]
    if args.media_manifest:
        import json

        args.media_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.media_manifest.write_text(
            json.dumps(local_media, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    item_count = sum(len(section["items"]) for section in sections)
    linked_count = sum(
        1
        for section in sections
        for item in section["items"]
        if item.get("confirmed")
    )
    alt_count = sum(
        len(item.get("alternatives", []))
        for section in sections
        for item in section["items"]
    )
    print(
        f"sections={len(sections)} items={item_count} "
        f"linked={linked_count} alternatives={alt_count} "
        f"local_images={len(local_media)} output={args.output}"
    )


if __name__ == "__main__":
    main()
