import argparse
import json
import os
import re
from pathlib import Path

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("PADDLE_DISABLE_MKLDNN", "1")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

import cv2
import numpy as np
from paddleocr import PaddleOCR


def imread_unicode(path: Path, flags=cv2.IMREAD_COLOR):
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, flags)


def imwrite_unicode(path: Path, img):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, data = cv2.imencode(path.suffix or ".png", img)
    if not ok:
        raise RuntimeError(f"Cannot encode image: {path}")
    data.tofile(str(path))


def frame_second(path: Path):
    m = re.search(r"_(\d+)\.jpg$", path.name)
    return int(m.group(1)) - 1 if m else None


def make_crop(path: Path, crop_path: Path):
    img = imread_unicode(path)
    if img is None:
        raise RuntimeError(f"Cannot read image: {path}")
    h, w = img.shape[:2]
    # Capture the Feishu outline and the main document body while dropping
    # browser chrome and most blank right-side space.
    crop = img[78 : max(78, h - 28), 120 : min(w, 1180)].copy()

    # Mask the video/player black overlay near the top center if present.
    ch, cw = crop.shape[:2]
    crop[0 : min(68, ch), int(cw * 0.43) : min(cw, int(cw * 0.95))] = 255

    crop = cv2.convertScaleAbs(crop, alpha=1.22, beta=6)
    crop = cv2.resize(crop, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    crop = cv2.addWeighted(crop, 1.28, cv2.GaussianBlur(crop, (0, 0), 0.8), -0.28, 0)
    imwrite_unicode(crop_path, crop)
    return 120, 78, 1.8


def normalize_box(box, offset_x: int, offset_y: int, scale: float):
    pts = np.asarray(box, dtype=float)
    if pts.ndim == 1 and len(pts) == 4:
        x1, y1, x2, y2 = pts
    else:
        x1, y1 = pts[:, 0].min(), pts[:, 1].min()
        x2, y2 = pts[:, 0].max(), pts[:, 1].max()
    return [
        round(x1 / scale + offset_x, 1),
        round(y1 / scale + offset_y, 1),
        round(x2 / scale + offset_x, 1),
        round(y2 / scale + offset_y, 1),
    ]


def predict_lines(ocr: PaddleOCR, crop_path: Path, offset_x: int, offset_y: int, scale: float):
    result = ocr.predict(str(crop_path))
    if not result:
        return []
    page = result[0]
    texts = list(page.get("rec_texts", []))
    scores = list(page.get("rec_scores", []))
    boxes = page.get("rec_boxes", None)
    polys = page.get("rec_polys", None)
    geom = boxes if boxes is not None else polys
    lines = []
    for idx, text in enumerate(texts):
        text = str(text).strip()
        if not text:
            continue
        score = float(scores[idx]) if idx < len(scores) else 0.0
        box = normalize_box(geom[idx], offset_x, offset_y, scale) if geom is not None and idx < len(geom) else [0, 0, 0, 0]
        lines.append({"text": text, "score": score, "box": box})
    lines.sort(key=lambda x: (x["box"][1], x["box"][0]))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selected-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    selected_root = Path(args.selected_root)
    output = Path(args.output)
    crop_root = output / "crops"
    raw_path = output / "paddle_ocr_raw.jsonl"
    output.mkdir(parents=True, exist_ok=True)

    ocr = PaddleOCR(
        lang="ch",
        enable_mkldnn=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        text_rec_score_thresh=0.0,
    )

    seen = set()
    if raw_path.exists():
        with raw_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["image"])
                except Exception:
                    pass

    frames = []
    for part in ["part1", "part2"]:
        frames.extend((part, p) for p in sorted((selected_root / part).glob("frame_*.jpg")))

    with raw_path.open("a", encoding="utf-8") as out:
        for idx, (part, frame) in enumerate(frames, 1):
            image_key = str(frame)
            if image_key in seen:
                continue
            crop_path = crop_root / part / f"{frame.stem}.png"
            offset_x, offset_y, scale = make_crop(frame, crop_path)
            lines = predict_lines(ocr, crop_path, offset_x, offset_y, scale)
            rec = {
                "part": part,
                "image": image_key,
                "crop": str(crop_path),
                "second": frame_second(frame),
                "line_count": len(lines),
                "mean_score": round(sum(x["score"] for x in lines) / max(len(lines), 1), 4),
                "lines": lines,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            if idx % 20 == 0:
                print(f"paddle OCR {idx}/{len(frames)}")
    print(f"wrote {raw_path}")


if __name__ == "__main__":
    main()
