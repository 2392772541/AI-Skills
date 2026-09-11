from __future__ import annotations

import argparse
import json
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("keyframes_root", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    parser.add_argument("--min-score", type=float, default=0.0)
    args = parser.parse_args()

    parts = sorted(path for path in args.keyframes_root.iterdir() if path.is_dir())
    if not parts:
        raise SystemExit(f"No episode directories found in {args.keyframes_root}")

    engine = RapidOCR()
    frames = [(part, frame) for part in parts for frame in sorted(part.glob("*.jpg"))]
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    with args.output_jsonl.open("w", encoding="utf-8", buffering=1) as output:
        for number, (part, frame) in enumerate(frames, 1):
            result, elapsed = engine(str(frame))
            rows = [
                {"box": box, "text": text, "score": float(score)}
                for box, text, score in (result or [])
                if float(score) >= args.min_score
            ]
            digits = "".join(character for character in frame.stem if character.isdigit())
            second = int(digits[-6:]) if digits else None
            output.write(
                json.dumps(
                    {
                        "part": part.name,
                        "second": second,
                        "frame": str(frame.resolve()),
                        "elapsed": elapsed,
                        "rows": rows,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            if number % 20 == 0 or number == len(frames):
                print(f"ocr={number}/{len(frames)}", flush=True)


if __name__ == "__main__":
    main()
