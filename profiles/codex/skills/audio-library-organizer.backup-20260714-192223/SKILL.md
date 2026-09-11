---
name: audio-library-organizer
description: Organize a portable audio material library from newly added MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, WMA, APE, or AIFF files. Use when the user asks to identify songs, batch整理音频, rename and classify music, complete emotion or usage tags, update 歌曲目录.json / 素材清单, rebuild 按情绪和用途找歌.html, repair local audio playback, or process files in 00_待整理 and 待识别 folders.
---

# Audio Library Organizer

Treat the latest concrete request as authorization to inspect, classify, rename, move, index, rebuild, and verify audio inside the supplied library. Preserve originals until the preview passes conflict checks.

## Locate the library

Find the library root in this order:

1. A user-supplied path containing `歌曲目录.json`.
2. An ancestor of `skills/audio-library-organizer` containing `03_音频`.
3. The current directory if it contains `00_待整理` and `03_音频`.

Never depend on a fixed drive letter. Pass the resolved root to scripts with `--root`.

## Required workflow

1. Scan `00_待整理` and `03_音频/01_歌曲/待识别` recursively for supported audio.
2. Read duration, codec, bitrate, and embedded title/artist/album with `ffprobe` when available. Fall back to filenames and file metadata without inventing values.
3. Identify title, artist, and language from embedded tags first, then filename, then current web sources when needed. Mark uncertain fields `待确认` and keep the file pending.
4. Detect excerpts and abnormal files. A short duration is evidence, not proof; label a file as a clip only when duration and context support it.
5. Read [references/tag-taxonomy.md](references/tag-taxonomy.md) before assigning emotions. For every confirmed track assign:
   - 1-3 core emotions;
   - 3-5 fine emotions;
   - intensity level and change curve;
   - atmosphere keywords separate from emotions;
   - 2-4 video uses.
   For every recommended time range, also assign start/end, structure label, segment-specific emotions, intensity, uses, suitable visuals, voiceover fit, vocal presence, and annotation source. Preserve manually verified segments. If the song has no segment analysis yet, allow the rebuild script to create clearly marked first-pass sections instead of inventing precise manual verification.
6. Build a preview table containing old path, proposed filename, target path, identification confidence, tags, and conflicts. Do not overwrite an existing target.
7. Rename confirmed full songs as `Artist - Title.ext`. Move them by language under `03_音频/01_歌曲`. Move confirmed excerpts intended for editing under `03_音频/02_剪辑BGM` and mark the duration in the name.
8. Update the root `歌曲目录.json` using [references/catalog-schema.md](references/catalog-schema.md). Keep paths relative to the library root and use `/` separators.
9. Run:

```powershell
python <skill-dir>/scripts/rebuild_library.py --root <library-root>
python <skill-dir>/scripts/rebuild_library.py --root <library-root> --check-only
```

10. Verify all moved files with `ffprobe` or an equivalent decoder. Open the generated `按情绪和用途找歌.html` in a real local browser. Require all players to show finite durations and require at least one track to play with increasing `currentTime`. A screenshot alone is not playback verification.
11. Verify segment behavior: apply a production-use filter such as `口播垫底`, start a result, confirm playback jumps within its start/end range, and confirm the timeline highlights that exact segment. With `只播放此片段` enabled, playback must not continue past the segment end.
11. Report moved files, pending files, conflicts, invalid media, catalog count, generated outputs, and the actual playback result.

## Tagging rules

- Separate emotion, intensity, atmosphere, and usage. `夜晚`, `雨夜`, and `城市` are atmosphere, not emotion.
- Prefer existing controlled tags. Add a tag only when no existing term represents the meaning.
- Allow multiple tags without copying the audio file.
- Treat suggested video uses as analysis, not an official claim by the artist.
- Keep identification confidence separate from emotion confidence.

## Safety rules

- Never delete source audio as a cleanup shortcut.
- Never overwrite a same-name destination.
- Never guess a song identity to force completion.
- Keep failed or uncertain files in `待识别` with a clear reason.
- Use a temporary output and atomic replacement when regenerating catalog artifacts.
- Keep the HTML standalone and free of a CSP or sandbox that blocks local media.
- Keep the bundled Font Awesome webfont under `vendor/` when copying or installing the skill so icons continue to render offline.

## Rebuilding only

If the user asks to repair the filter, refresh tags, or regenerate indexes without new audio, validate `歌曲目录.json`, run the rebuild script, and perform the same path and playback checks. Do not move media unnecessarily.
