#!/usr/bin/env python3
"""Suggest video scene ranges with FFmpeg; candidates require human visual review."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


PTS_RE = re.compile(r"pts_time:([0-9]+(?:\.[0-9]+)?)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--threshold", type=float, default=0.32, help="FFmpeg scene score threshold")
    parser.add_argument("--min-gap", type=float, default=1.0, help="Minimum seconds between cuts")
    parser.add_argument("--output", type=Path, help="Write JSON suggestions")
    parser.add_argument("--frames-dir", type=Path, help="Extract one representative JPG per range")
    return parser.parse_args()


def run(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, encoding="utf-8", errors="replace")


def probe_duration(ffprobe: str, video: Path) -> float:
    completed = run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video)])
    return float(completed.stdout.strip())


def scene_times(ffmpeg: str, video: Path, threshold: float) -> list[float]:
    expression = f"select=gt(scene\\,{threshold})"
    completed = run([ffmpeg, "-hide_banner", "-i", str(video), "-vf", f"{expression},showinfo", "-an", "-f", "null", "-"])
    return [float(match.group(1)) for match in PTS_RE.finditer(completed.stderr)]


def collapse(times: list[float], duration: float, min_gap: float) -> list[float]:
    kept = [0.0]
    for value in sorted(value for value in times if 0 < value < duration):
        if value - kept[-1] >= min_gap and duration - value >= 0.25:
            kept.append(round(value, 3))
    kept.append(round(duration, 3))
    return kept


def build_ranges(boundaries: list[float]) -> list[dict]:
    ranges = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        ranges.append({
            "id": f"v{index}",
            "label": f"镜头 {index}",
            "start": start,
            "end": end,
            "content_tags": ["待人工查看"],
            "shot_type": "待确认",
            "camera_motion": "待确认",
            "uses": ["待确认"],
            "quality": "待确认",
            "annotation": "FFmpeg场景检测候选 · 需人工查看",
        })
    return ranges


def extract_frames(ffmpeg: str, video: Path, ranges: list[dict], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for segment in ranges:
        midpoint = (segment["start"] + segment["end"]) / 2
        target = output / f"{segment['id']}_{midpoint:.2f}s.jpg"
        run([ffmpeg, "-v", "error", "-ss", f"{midpoint:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", "-y", str(target)], timeout=60)


def main() -> int:
    args = parse_args()
    video = args.video.expanduser().resolve()
    if not video.is_file():
        print(f"视频不存在: {video}", file=sys.stderr)
        return 1
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        print("需要 ffmpeg 和 ffprobe", file=sys.stderr)
        return 1
    try:
        duration = probe_duration(ffprobe, video)
        boundaries = collapse(scene_times(ffmpeg, video, args.threshold), duration, args.min_gap)
        ranges = build_ranges(boundaries)
        if args.frames_dir:
            extract_frames(ffmpeg, video, ranges, args.frames_dir.expanduser().resolve())
    except (ValueError, subprocess.SubprocessError) as exc:
        print(f"分析失败: {exc}", file=sys.stderr)
        return 1
    payload = {"video": video.name, "duration": round(duration, 3), "threshold": args.threshold, "segments": ranges}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.expanduser().resolve().write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
