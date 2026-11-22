#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
万能分镜适配器 (Universal Storyboard Adapter)
将任意外部 Skill（如 seedance-director、seedance-xiaomo、anything2explainer 或自定义大模型输出）
产出的分镜（Markdown 表格、段落文本、或者第三方 JSON）自动转换为本系统标准化的 storyboard.json。
"""

import os
import sys
import json
import re
import pathlib
import argparse
from typing import Dict, List, Any, Optional

def find_val_by_keywords(raw: Dict[str, Any], keywords: List[str], exclude_keywords: Optional[List[str]] = None) -> str:
    """根据关键词模糊匹配字典中的字段值"""
    # 优先精确匹配
    for kw in keywords:
        if kw in raw and raw[kw] is not None:
            return str(raw[kw]).strip()
    # 其次模糊包含匹配
    for k, v in raw.items():
        if v is None:
            continue
        k_lower = str(k).lower().strip()
        if exclude_keywords and any(ex in k_lower for ex in exclude_keywords):
            continue
        if any(kw in k_lower for kw in keywords):
            return str(v).strip()
    return ""

def normalize_shot_dict(raw: Dict[str, Any], default_idx: int) -> Dict[str, Any]:
    """标准化单个镜头字段（支持高度容错的模糊表头/字段识别）"""
    # 镜号
    idx_raw = find_val_by_keywords(raw, ["shotid", "number", "id", "镜号", "镜头", "序号", "no"])
    try:
        idx = int(re.search(r'\d+', idx_raw).group()) if idx_raw else default_idx
    except Exception:
        idx = default_idx

    # 标题 / 场景描述
    title = find_val_by_keywords(raw, ["title", "scene", "标题", "场景", "名称", "景别"])
    if not title:
        title = f"第{idx}镜"

    # 时长
    dur_raw = find_val_by_keywords(raw, ["duration", "seconds", "时长", "秒数", "时间"])
    try:
        duration = float(re.search(r'(\d+(?:\.\d+)?)', dur_raw).group(1)) if dur_raw else 5.0
    except Exception:
        duration = 5.0

    # 口播台词 / 旁白 (排除纯提示词)
    vo = find_val_by_keywords(raw, ["votext", "vo", "台词", "旁白", "口播", "文案", "解说", "dialogue", "narration"])
    vo = vo.strip(' "\'“”')

    # 尾帧生图词 (优先识别，避免被生图词截胡)
    end_img_p = find_val_by_keywords(raw, ["endimageprompt", "end_image_prompt", "尾帧", "落幅", "尾图", "end_frame"])

    # 运镜视频提示词
    v_p = find_val_by_keywords(raw, ["videoprompt", "video_prompt", "cameraprompt", "运镜", "动态演变", "运动", "摄像机", "camera", "motion"])

    # 生图提示词 (首帧)
    img_p = find_val_by_keywords(
        raw,
        ["imageprompt", "image_prompt", "firstframeprompt", "生图", "画面", "起幅", "首帧", "prompt", "visual", "视觉"],
        exclude_keywords=["运镜", "video", "camera", "motion", "尾帧", "end"]
    )

    # 如果只有画面描述但没有运镜词，给出合理的默认运镜
    if not v_p and img_p:
        v_p = f"第{idx}镜：摄影机缓慢平移推近，主体保持自然动态，高细节真实光影，5秒。"

    return {
        "shotId": idx,
        "title": title,
        "duration": duration,
        "voText": vo,
        "imagePrompt": img_p,
        "endImagePrompt": end_img_p,
        "videoPrompt": v_p
    }

def parse_markdown_table(md_text: str) -> List[Dict[str, Any]]:
    """解析 Markdown 格式的分镜表格（常见于各种分镜师 Skill 输出）"""
    lines = [l.strip() for l in md_text.splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    if len(table_lines) < 3:
        return []

    # 解析表头
    header = [c.strip() for c in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:  # 跳过表头和分割线
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) == len(header):
            rows.append(dict(zip(header, cols)))
        elif len(cols) > 0:
            row_dict = {}
            for i, col in enumerate(cols):
                k = header[i] if i < len(header) else f"col_{i}"
                row_dict[k] = col
            rows.append(row_dict)

    if not rows:
        return []

    shots = []
    for i, r in enumerate(rows, start=1):
        shots.append(normalize_shot_dict(r, i))
    return shots

def parse_markdown_sections(md_text: str) -> List[Dict[str, Any]]:
    """解析标准带标题分段的分镜（### 第X镜 / ### 场景X）"""
    shots = []
    # 匹配各类镜号标题
    pattern = r'(?:^|\n)###?\s*\[?(?:条目\s*0*(\d+)|ep\d+-0*(\d+)|第\s*0*(\d+)\s*镜|场景\s*0*(\d+)|Scene\s*0*(\d+))\]?([^\n]*)(.*?)(?=(?:\n###?|\Z))'
    matches = list(re.finditer(pattern, md_text, re.DOTALL | re.IGNORECASE))

    for i, m in enumerate(matches, start=1):
        idx_str = m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5)
        idx = int(idx_str) if idx_str else i
        title = m.group(6).strip(' ：:-[]') or f"第{idx}镜"
        body = m.group(7)

        # 提取时长
        dm = re.search(r'(?:推荐时长|建议时长|时长)\s*[*:：]*\s*(\d+(?:\.\d+)?)\s*秒?', body)
        duration = float(dm.group(1)) if dm else 5.0

        # 提取口播台词
        vom = re.search(r'(?:口播文案|对应文案|口播|台词|旁白|文案|VO)\s*[*:：]*\s*([^\n]+)', body)
        vo = vom.group(1).strip(' "\'“”') if vom else ""

        # 提取生图词
        ipm = re.search(r'(?:首帧提示词|首帧生图词|生图提示词|图片提示词|画面参考|画面描述|生图词)\s*[*:：]*\s*([^\n]+)', body)
        img_p = ipm.group(1).strip() if ipm else ""

        # 提取尾帧词
        epm = re.search(r'(?:尾帧提示词|尾帧生图词|尾图提示词|落幅)\s*[*:：]*\s*([^\n]+)', body)
        end_img_p = epm.group(1).strip() if epm else ""

        # 提取运镜词
        pm = re.search(r'```(?:text)?\s*(.*?)\s*```', body, re.DOTALL)
        if pm:
            v_p = pm.group(1).strip()
        else:
            pm2 = re.search(r'(?:运镜提示词|视频提示词|运镜指令|动态演变|运镜|运镜词)\s*[*:：]*\s*([^\n]+)', body)
            v_p = pm2.group(1).strip() if pm2 else ""

        shots.append({
            "shotId": idx,
            "title": title,
            "duration": duration,
            "voText": vo,
            "imagePrompt": img_p,
            "endImagePrompt": end_img_p,
            "videoPrompt": v_p
        })

    return shots

def adapt_to_storyboard(input_path_or_content: str, title: str = "短视频分镜工作流", aspect_ratio: str = "9:16") -> Dict[str, Any]:
    """主转换函数：自适应读取任意外部分镜并返回标准 storyboard 字典"""
    content = ""
    # 判断是文件还是直接传入的内容
    if os.path.exists(input_path_or_content):
        with open(input_path_or_content, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    else:
        content = input_path_or_content.strip()

    # 1. 尝试直接作为 JSON 解析
    try:
        data = json.loads(content)
        # 如果是已经符合标准的格式
        if isinstance(data, dict) and "shots" in data and isinstance(data["shots"], list):
            std_shots = [normalize_shot_dict(s, i) for i, s in enumerate(data["shots"], start=1)]
            return {
                "version": "1.0",
                "title": data.get("title", title),
                "aspectRatio": data.get("aspectRatio", aspect_ratio),
                "totalShots": len(std_shots),
                "shots": std_shots
            }
        # 如果是包含列表的第三方 JSON（如 seedance 导出的场景列表）
        elif isinstance(data, list):
            std_shots = [normalize_shot_dict(s, i) for i, s in enumerate(data, start=1)]
            return {
                "version": "1.0",
                "title": title,
                "aspectRatio": aspect_ratio,
                "totalShots": len(std_shots),
                "shots": std_shots
            }
        elif isinstance(data, dict):
            # 查找可能是镜头列表的键
            for key in ["scenes", "shots", "list", "items", "分镜", "镜头"]:
                if key in data and isinstance(data[key], list):
                    std_shots = [normalize_shot_dict(s, i) for i, s in enumerate(data[key], start=1)]
                    return {
                        "version": "1.0",
                        "title": data.get("title", title),
                        "aspectRatio": data.get("aspectRatio", aspect_ratio),
                        "totalShots": len(std_shots),
                        "shots": std_shots
                    }
    except Exception:
        pass

    # 2. 尝试解析 Markdown 表格
    shots = parse_markdown_table(content)
    if shots:
        return {
            "version": "1.0",
            "title": title,
            "aspectRatio": aspect_ratio,
            "totalShots": len(shots),
            "shots": shots
        }

    # 3. 尝试解析 Markdown 章节
    shots = parse_markdown_sections(content)
    if shots:
        return {
            "version": "1.0",
            "title": title,
            "aspectRatio": aspect_ratio,
            "totalShots": len(shots),
            "shots": shots
        }

    # 4. 极端情况兜底：按空行拆分成段
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if paragraphs:
        fallback_shots = []
        for i, p in enumerate(paragraphs, start=1):
            fallback_shots.append({
                "shotId": i,
                "title": f"第{i}镜",
                "duration": 5.0,
                "voText": p[:60],
                "imagePrompt": p,
                "endImagePrompt": "",
                "videoPrompt": f"第{i}镜平滑推近运镜，主体律动自然，5秒。"
            })
        return {
            "version": "1.0",
            "title": title,
            "aspectRatio": aspect_ratio,
            "totalShots": len(fallback_shots),
            "shots": fallback_shots
        }

    raise ValueError("无法识别输入的分镜格式，请提供标准 JSON、Markdown 分镜表或带有 ### 第X镜 的分镜头文本。")

def main():
    parser = argparse.ArgumentParser(description="万能分镜适配器：将任何 Skill 的分镜产物转为标准 storyboard.json")
    parser.add_argument("input_file", help="输入的分镜文件路径 (md, txt, json)")
    parser.add_argument("-o", "--output", default="storyboard.json", help="输出的标准 storyboard.json 路径")
    parser.add_argument("-t", "--title", default="AI视频分镜工作流", help="剧本标题")
    parser.add_argument("-a", "--aspect-ratio", default="9:16", help="画面比例 (9:16 或 16:9)")
    args = parser.parse_args()

    result = adapt_to_storyboard(args.input_file, title=args.title, aspect_ratio=args.aspect_ratio)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[✓] 成功转换分镜！共识别到 {result['totalShots']} 镜，已输出至: {args.output}")

if __name__ == "__main__":
    main()
