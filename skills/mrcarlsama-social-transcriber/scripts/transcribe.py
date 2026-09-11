# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "faster-whisper>=1.1.0",
# ]
# ///

#!/usr/bin/env python3
"""Transcribe a local audio file using faster-whisper."""
import sys
from pathlib import Path

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from asr import transcribe_audio

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [model_name]")
        sys.exit(1)

    audio_file = Path(sys.argv[1])
    model_name = sys.argv[2] if len(sys.argv) > 2 else "large-v3"

    if not audio_file.exists():
        print(f"Error: File {audio_file} not found")
        sys.exit(1)

    output_dir = Path(r"E:\工程项目\claude项目\remotion\outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    meta_dir = output_dir / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    title = audio_file.stem

    print(f"Transcribing: {audio_file.name}")
    print(f"Model: {model_name}")
    print(f"Output directory: {output_dir}")
    print()

    result = transcribe_audio(
        audio=audio_file,
        output_dir=output_dir,
        meta_dir=meta_dir,
        title=title,
        model_name=model_name,
    )

    print("\nTranscription completed!")
    print(f"Language: {result['language']} ({result['language_probability']:.2%})")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"Segments: {result['segments']}")
    print(f"Words: {result['words']}")
    print()
    print("Output files:")
    for key, filename in result['files'].items():
        print(f"  {key}: {output_dir / filename}")

if __name__ == "__main__":
    main()
