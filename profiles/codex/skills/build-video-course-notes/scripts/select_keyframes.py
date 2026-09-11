from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

import cv2
import numpy as np


def signature(path: Path) -> np.ndarray:
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError(f"Cannot read image: {path}")
    height, width = image.shape
    cropped = image[
        int(height * 0.03) : int(height * 0.97),
        int(width * 0.02) : int(width * 0.98),
    ]
    return cv2.resize(cropped, (160, 90), interpolation=cv2.INTER_AREA)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--diff", type=float, default=7.5)
    parser.add_argument("--min-gap", type=int, default=2)
    parser.add_argument("--max-gap", type=int, default=15)
    args = parser.parse_args()

    frames = sorted(args.input_dir.glob("frame_*.jpg"))
    if not frames:
        raise SystemExit(f"No frame_*.jpg files found in {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    last_signature: np.ndarray | None = None
    last_index = -(10**9)
    selected: list[tuple[int, str, float]] = []

    for index, frame in enumerate(frames):
        current = signature(frame)
        delta = (
            999.0
            if last_signature is None
            else float(np.mean(cv2.absdiff(current, last_signature)))
        )
        gap = index - last_index
        if (
            last_signature is None
            or gap >= args.max_gap
            or (gap >= args.min_gap and delta >= args.diff)
        ):
            shutil.copy2(frame, args.output_dir / frame.name)
            selected.append((index + 1, frame.name, delta))
            last_signature = current
            last_index = index

    manifest = args.output_dir / "keyframe_manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["second", "frame", "delta"])
        writer.writerows(
            (second, filename, f"{delta:.2f}")
            for second, filename, delta in selected
        )

    print(f"selected={len(selected)} total={len(frames)} manifest={manifest}")


if __name__ == "__main__":
    main()
