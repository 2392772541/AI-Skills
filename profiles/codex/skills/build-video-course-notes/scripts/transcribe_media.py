from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from faster_whisper import WhisperModel


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]


def stamp(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("media_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--model", default="small")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    media = []
    for extension in ("*.wav", "*.mp3", "*.m4a", "*.mp4", "*.mov", "*.mkv"):
        media.extend(args.media_dir.glob(extension))
    media = sorted(set(media), key=natural_key)
    if not media:
        raise SystemExit(f"No supported media found in {args.media_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
    )

    index = []
    for number, source in enumerate(media, 1):
        part = f"P{number:02d}"
        json_path = args.output_dir / f"{part}_transcript.json"
        if json_path.exists() and not args.overwrite:
            print(f"SKIP {part} existing transcript", flush=True)
            continue

        print(f"START {part} {source.name}", flush=True)
        segments, info = model.transcribe(
            str(source),
            language=args.language,
            beam_size=1,
            best_of=1,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )
        records = [
            {"start": item.start, "end": item.end, "text": item.text.strip()}
            for item in segments
            if item.text.strip()
        ]
        payload = {
            "part": part,
            "source": str(source.resolve()),
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": records,
        }
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (args.output_dir / f"{part}_transcript.md").write_text(
            f"# {source.stem}\n\n"
            + "\n".join(
                f"- `{stamp(row['start'])}-{stamp(row['end'])}` {row['text']}"
                for row in records
            )
            + "\n",
            encoding="utf-8",
        )
        index.append(
            {"part": part, "source": source.name, "segments": len(records)}
        )
        print(f"DONE {part} segments={len(records)}", flush=True)

    (args.output_dir / "transcript_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
