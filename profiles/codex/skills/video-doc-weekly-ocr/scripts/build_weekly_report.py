import argparse
import json
import re
from collections import OrderedDict
from difflib import SequenceMatcher
from pathlib import Path


SECTION_ALIASES = [
    ("本周最TOP", "本周最TOP"),
    ("AI热点", "AI热点"),
    ("AI优秀文章", "AI优秀文章"),
    ("AI视野", "AI视野"),
    ("AI改变", "AI改变"),
    ("AI基础", "AI基础"),
    ("设计模块", "设计模块"),
]


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def clean_text(text: str) -> str:
    text = str(text or "").strip()
    text = text.replace("锛?", "：").replace("銆?", "。")
    text = text.replace(" Al", " AI").replace("A1", "AI")
    text = re.sub(r"\s+", " ", text)
    return text.strip("` ")


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text or ""))


def parse_section(text: str):
    raw = compact(clean_text(text)).replace("＃", "#")
    fuzzy = raw.lower().replace("al", "ai").replace("a1", "ai")
    for key, name in SECTION_ALIASES:
        if compact(key).lower() in fuzzy:
            return name
    return None


def parse_title(text: str):
    text = clean_text(text)
    m = re.match(r"^\s*(\d{1,3})\s*[\.\、\,，:：．。]\s*(.+)$", text)
    if not m:
        return None
    title = m.group(2).strip()
    if not title or cjk_count(title) < 2:
        return None
    return int(m.group(1)), title


def looks_like_url(text: str) -> bool:
    return bool(re.search(r"(https?|www\.|douyin|bilibili|xiaohongshu|\.com|/video)", text, re.I))


def normalize_url(raw: str):
    text = clean_text(raw)
    text = text.replace(" ", "")
    lower = text.lower()
    repl = {
        "hhtps": "https",
        "htps": "https",
        "httpa": "https",
        "https7": "https://",
        "http7": "http://",
        "：//": "://",
        "www。": "www.",
        "hmww": "www",
        "mww": "www",
        "wwc": "www",
        "c0m": "com",
        "corm": "com",
        "corn": "com",
        "douyir1": "douyin",
        "douyirl": "douyin",
        "douyif": "douyin",
        "douyi.com": "douyin.com",
        "douyn.com": "douyin.com",
        "couyin.com": "douyin.com",
        "douyin.corn": "douyin.com",
        "douyin.c0m": "douyin.com",
        "www.douyir": "www.douyin",
        "douyin.comjvideo": "douyin.com/video",
        "douyin.com/videoj": "douyin.com/video/",
        "douyin.com/vidco": "douyin.com/video",
        "douyin.com/vidcof": "douyin.com/video/",
        "douyin.com/wdeo": "douyin.com/video",
        "douyin.com/vdeal": "douyin.com/video",
        "douyin.com/video//": "douyin.com/video/",
    }
    for a, b in repl.items():
        lower = lower.replace(a, b)

    if "douyin" in lower:
        digits = "".join(re.findall(r"\d", lower[lower.find("douyin") :]))
        if len(digits) >= 12:
            return f"https://www.douyin.com/video/{digits[:19]}", "needs_check"
        return "https://www.douyin.com/video/待核对", "unparsed"

    m = re.search(r"https?://[^\s`<>，。]+", lower)
    if m:
        url = m.group(0).rstrip(".,;:，。")
        return url, "ok" if re.fullmatch(r"[\x00-\x7f]+", url) else "needs_check"
    if lower.startswith("www."):
        return f"https://{lower}", "needs_check"
    return "", "unparsed"


def similar(a: str, b: str) -> float:
    a, b = compact(a), compact(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return min(len(a), len(b)) / max(len(a), len(b))
    return SequenceMatcher(None, a, b).ratio()


def better_title(old: str, new: str) -> str:
    old, new = clean_text(old), clean_text(new)
    if len(new) > len(old) + 3:
        return new
    if old.count("?") > new.count("?"):
        return new
    return old


def load_records(path: Path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    records.sort(key=lambda r: (r["part"], r.get("second") or 0, r["image"]))
    return records


def build_items(records):
    sections = OrderedDict()
    review = []
    links_seen = set()
    current_section = "未分组"
    last_item = None
    all_items = []

    for rec in records:
        lines = sorted(rec.get("lines", []), key=lambda x: (x["box"][1], x["box"][0]))
        frame_titles = []
        for line in lines:
            text = clean_text(line.get("text", ""))
            score = float(line.get("score") or 0)
            if len(text) <= 1:
                continue

            section = parse_section(text)
            if section:
                current_section = section
                sections.setdefault(current_section, OrderedDict())
                last_item = None
                continue

            parsed = parse_title(text)
            if parsed:
                num, title = parsed
                sections.setdefault(current_section, OrderedDict())
                key = None
                for old_key, old in sections[current_section].items():
                    if old["num"] == num and similar(old["title"], title) >= 0.55:
                        key = old_key
                        break
                if key is None:
                    key = f"{num}:{compact(title)[:32]}"
                    sections[current_section][key] = {
                        "section": current_section,
                        "num": num,
                        "title": title,
                        "score": score,
                        "sources": [],
                        "links": [],
                    }
                    all_items.append(sections[current_section][key])
                item = sections[current_section][key]
                item["title"] = better_title(item["title"], title)
                item["score"] = max(item["score"], score)
                item["sources"].append({"image": rec["image"], "second": rec.get("second"), "score": score, "raw": text})
                last_item = item
                frame_titles.append(item)
                if score < 0.82:
                    review.append(("标题低置信度", item, text, rec["image"]))
                continue

            if looks_like_url(text):
                url, status = normalize_url(text)
                target = frame_titles[-1] if frame_titles else None
                if target is None:
                    review.append(("未匹配标题的链接", None, text, rec["image"]))
                    continue
                link_key = (id(target), url or text)
                if link_key in links_seen:
                    continue
                links_seen.add(link_key)
                target["links"].append({"url": url, "status": status, "raw": text, "image": rec["image"], "second": rec.get("second")})
                if status != "ok":
                    review.append(("链接待核对", target, text, rec["image"]))

    for item in all_items:
        if not item["links"]:
            review.append(("缺少链接", item, item["title"], item["sources"][0]["image"] if item["sources"] else ""))

    return sections, review


def write_outputs(sections, review, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# 且曼周刊 2026-07-07 视频复原周报",
        "",
        "> 基于本周两段直播回放 1 秒抽帧、关键帧筛选与 OCR 复原。编号和章节以视频中可见文档为准；无法确认的标题或链接已放入排查清单。",
        "",
    ]
    paste = ["# 且曼周刊 2026-07-07 视频复原周报", ""]
    links_report = ["# 提取到的视频链接", ""]

    for section, items in sections.items():
        if not items:
            continue
        lines.extend([f"## {section}", ""])
        paste.extend([f"## {section}", ""])
        for item in sorted(items.values(), key=lambda x: x["num"]):
            title = f"{item['num']}. {item['title']}"
            lines.append(title)
            paste.append(title)
            if item["links"]:
                for link in item["links"]:
                    url = link["url"] or "待核对"
                    lines.append(f"链接：{url}")
                    paste.append(url)
                    links_report.extend([
                        f"## {title}",
                        f"- 链接：{url}",
                        f"- 状态：`{link['status']}`",
                        f"- 原始 OCR：`{link['raw']}`",
                        f"- 来源：`{link['image']}`",
                        "",
                    ])
                    if link["status"] != "ok":
                        lines.append(f"> 链接待核对：原始 OCR `{link['raw']}`；来源 `{link['image']}`")
            else:
                lines.append("> 链接待补充：未在相邻帧中识别到蓝色链接")
                paste.append("链接待补充")
            if item["score"] < 0.82:
                lines.append(f"> 标题待核对：OCR 置信度 `{item['score']:.3f}`")
            lines.append("")
            paste.append("")

    review_lines = ["# 待排查清单", ""]
    for reason, item, raw, image in review:
        if item:
            review_lines.append(f"## {item['section']} / {item['num']}. {item['title']}")
        else:
            review_lines.append("## 未匹配条目")
        review_lines.append(f"- 问题：{reason}")
        review_lines.append(f"- 原始 OCR：`{raw}`")
        review_lines.append(f"- 来源截图：`{image}`")
        review_lines.append("")

    stats = {
        "sections": len([s for s, items in sections.items() if items]),
        "items": sum(len(items) for items in sections.values()),
        "items_with_links": sum(1 for items in sections.values() for item in items.values() if item["links"]),
        "review_items": len(review),
    }
    stat_lines = ["# 统计", ""]
    for k, v in stats.items():
        stat_lines.append(f"- {k}: {v}")

    (out_dir / "document.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    (out_dir / "document_feishu_paste.md").write_text("\n".join(paste).strip() + "\n", encoding="utf-8")
    (out_dir / "links_extracted.md").write_text("\n".join(links_report).strip() + "\n", encoding="utf-8")
    (out_dir / "review_items.md").write_text("\n".join(review_lines).strip() + "\n", encoding="utf-8")
    (out_dir / "stats.md").write_text("\n".join(stat_lines).strip() + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = load_records(Path(args.raw))
    sections, review = build_items(records)
    write_outputs(sections, review, Path(args.output))


if __name__ == "__main__":
    main()

