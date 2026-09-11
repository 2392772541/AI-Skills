import argparse
import json
import os
import re
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

RAW_LABEL = "\u539f\u59cb OCR"
SOURCE_LABEL = "\u6765\u6e90"


def imread_unicode(path: Path):
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_unicode(path: Path, img):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise RuntimeError(f"Cannot write crop: {path}")
    buf.tofile(str(path))


def normalize_urlish(text: str) -> str:
    text = (text or "").strip().replace(" ", "")
    text = re.split(r"[A-Z]:\\", text)[0]
    lower = text.lower()
    replacements = {
        "hhtps": "https", "htps": "https", "httos": "https", "hltps": "https",
        "htt:ps": "https", "ntps": "https", "ittps": "https", "iltps": "https", "hlps": "https",
        "douyir1": "douyin", "douyirl": "douyin", "douyir.com": "douyin.com",
        "douyi.com": "douyin.com", "douyif": "douyin", "douyf.com": "douyin.com",
        "douyn.com": "douyin.com", "douyin1.com": "douyin.com", "dotyin.com": "douyin.com",
        "douym.com": "douyin.com", "douyil.com": "douyin.com", "douvir1.com": "douyin.com",
        "douvir.com": "douyin.com", "douyini.com": "douyin.com", "dot:yin.com": "douyin.com",
        "videoj": "video/", "videof": "video/", "video//": "video/", "vrdeo": "video",
        "cam": "com", "c0m": "com", "corn": "com",
        "mp.weixin.q.com": "mp.weixin.qq.com", "1fanrcom": "ifanr.com", "famtcom": "ifanr.com",
    }
    for src, dst in replacements.items():
        lower = lower.replace(src, dst)
    if "douyin.com" in lower:
        digits = "".join(re.findall(r"\d", lower[lower.find("douyin.com") :]))
        if len(digits) >= 4:
            return "https://www.douyin.com/video/" + (digits[:19] if len(digits) >= 19 else digits)
    match = re.search(r"https?://[^\s`<>，。；;]+", lower)
    return match.group(0).rstrip(".,;:，。") if match else ""


def is_full_link(url: str) -> bool:
    if re.fullmatch(r"https://www\.douyin\.com/video/\d{19}", url or ""):
        return True
    return (url or "").startswith(
        (
            "https://github.com/",
            "https://www.woshipm.com/",
            "https://mp.weixin.qq.com/",
            "https://zhuanlan.zhihu.com/",
            "https://x.com/",
            "https://reicon.dev",
            "https://www.ifanr.com/",
            "https://beu.dev/",
        )
    )


def load_raw_records(raw_jsonl: Path):
    records = {}
    for line in raw_jsonl.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            records[rec["image"]] = rec
    return records


def parse_review_notes(notes_md: Path):
    notes = notes_md.read_text(encoding="utf-8")
    items = []
    section = ""
    current = None
    for line in notes.splitlines():
        if line.startswith("## "):
            section = line[3:]
        elif re.match(r"^\d{1,3}\. ", line):
            current = {"section": section, "title": line, "notes": []}
            items.append(current)
        elif current and RAW_LABEL in line and SOURCE_LABEL in line:
            raw = re.search(RAW_LABEL + r" `([^`]+)`", line)
            source = re.search(SOURCE_LABEL + r" `([^`]+)`", line)
            if raw and source:
                current["notes"].append({"raw": raw.group(1), "source": source.group(1)})
    return items


def complete_links(notes_md: Path, raw_jsonl: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_records = load_raw_records(raw_jsonl)
    work = []
    for item in parse_review_notes(notes_md):
        for note in item["notes"]:
            partial = normalize_urlish(note["raw"])
            if partial and not is_full_link(partial):
                work.append((item, note, partial))

    ocr = RapidOCR()
    results = []
    for idx, (item, note, partial) in enumerate(work, 1):
        src = note["source"]
        img = imread_unicode(Path(src))
        candidates = []
        crops = []
        if img is not None:
            rec = raw_records.get(src)
            boxes = []
            raw_compact = re.sub(r"\s+", "", note["raw"]).lower()
            digit_runs = re.findall(r"\d{3,}", raw_compact)
            if rec:
                for line in rec.get("lines", []):
                    text = re.sub(r"\s+", "", line.get("text", "")).lower()
                    if (
                        text == raw_compact
                        or raw_compact in text
                        or text in raw_compact
                        or ("http" in text and any(d in text for d in digit_runs))
                        or ("douy" in text and any(d in text for d in digit_runs))
                    ):
                        boxes.append(line["box"])
            h, w = img.shape[:2]
            if not boxes:
                boxes = [[520, 80, 950, h - 40]]
            for box_index, box in enumerate(boxes[:2]):
                ymid = int((box[1] + box[3]) / 2)
                for variant, (x1, x2, dy) in enumerate([(430, 1250, 45), (350, 1500, 60), (500, 1100, 35)]):
                    y1, y2 = max(0, ymid - dy), min(h, ymid + dy)
                    crop = img[y1:y2, x1 : min(w, x2)]
                    if crop.size == 0:
                        continue
                    up = cv2.resize(crop, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
                    up = cv2.addWeighted(up, 1.55, cv2.GaussianBlur(up, (0, 0), 0.8), -0.55, 0)
                    crop_path = output_dir / f"{idx:03d}_{box_index}_{variant}.png"
                    imwrite_unicode(crop_path, up)
                    crops.append(str(crop_path))
                    recs, _ = ocr(str(crop_path))
                    for row in recs or []:
                        text = row[1]
                        if any(k in text.lower() for k in ["http", "douyin", "www", "video", "github", "woshipm", "ifanr", "zhihu", "weixin", "x.com"]):
                            candidates.append(text)

        normalized = []
        for text in candidates + [note["raw"], partial]:
            url = normalize_urlish(text)
            if url and url not in normalized:
                normalized.append(url)
        full = [url for url in normalized if is_full_link(url)]
        results.append(
            {
                "idx": idx,
                "section": item["section"],
                "title": item["title"],
                "raw": note["raw"],
                "partial": partial,
                "source": src,
                "crops": crops,
                "ocr_texts": candidates,
                "candidates": normalized,
                "full": full,
            }
        )
        if idx % 10 == 0:
            print(f"done {idx}/{len(work)} full={sum(1 for r in results if r['full'])}")
        (output_dir / "completion_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Link Completion Results", ""]
    for row in results:
        lines.append(f"## {row['idx']}. {row['section']} / {row['title']}")
        lines.append(f"- raw: `{row['raw']}`")
        lines.append(f"- partial: `{row['partial']}`")
        if row["full"]:
            lines.append("- full:")
            for url in row["full"]:
                lines.append(f"  - {url}")
        else:
            lines.append("- full: NOT FOUND")
            if row["candidates"]:
                lines.append("- candidates:")
                for url in row["candidates"][:5]:
                    lines.append(f"  - {url}")
        lines.append("")
    (output_dir / "completion_results.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"full_found={sum(1 for r in results if r['full'])} of {len(results)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--notes", required=True, help="document_with_review_notes.md")
    parser.add_argument("--raw", required=True, help="ocr_raw.jsonl")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    complete_links(Path(args.notes), Path(args.raw), Path(args.output))


if __name__ == "__main__":
    main()
