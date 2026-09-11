import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


def frame_vector(path: Path) -> np.ndarray:
    with Image.open(path) as img:
        img = img.convert("L")
        w, h = img.size
        crop = img.crop((470, 82, min(w, 980), max(82, h - 28)))
        crop = crop.resize((64, 64), Image.Resampling.BILINEAR)
        return np.asarray(crop, dtype=np.float32)


def select_frames(frame_dir: Path, selected_dir: Path, threshold: float, min_gap: int):
    selected_dir.mkdir(parents=True, exist_ok=True)
    frames = sorted(frame_dir.glob("frame_*.jpg"))
    last_vec = None
    last_selected_idx = -10**9
    selected = []

    for idx, frame in enumerate(frames):
        try:
            vec = frame_vector(frame)
        except Exception as exc:
            print(f"skip {frame}: {exc}")
            continue

        if last_vec is None:
            should_select = True
        else:
            diff = float(np.mean(np.abs(vec - last_vec)))
            should_select = diff >= threshold and (idx - last_selected_idx) >= min_gap

        if should_select:
            target = selected_dir / frame.name
            if not target.exists():
                shutil.copy2(frame, target)
            selected.append(target)
            last_vec = vec
            last_selected_idx = idx

    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", action="append", required=True, help="part=input_dir")
    parser.add_argument("--output", required=True)
    parser.add_argument("--threshold", type=float, default=40.0)
    parser.add_argument("--min-gap", type=int, default=5)
    args = parser.parse_args()

    output = Path(args.output)
    for spec in args.part:
        name, path = spec.split("=", 1)
        selected = select_frames(
            Path(path),
            output / "selected_frames" / name,
            threshold=args.threshold,
            min_gap=args.min_gap,
        )
        print(f"{name}: selected {len(selected)} frames")


if __name__ == "__main__":
    main()
