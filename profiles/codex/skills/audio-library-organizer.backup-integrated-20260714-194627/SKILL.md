---
name: audio-library-organizer
description: Organize and maintain a portable local audio-material library. Use for new or unidentified MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, WMA, APE, or AIFF files; song identification, renaming, language classification, whole-track tags, time-segment cutting/annotation, emotion and production-use labels, voiceover suitability, updating 歌曲目录.json / 素材清单 / 片段清单, rebuilding 按情绪和用途找歌.html, repairing playback, or verifying local Edge seeking and segment-only stopping.
---

# Audio Library Organizer

Treat the latest concrete request as authorization to inspect, classify, rename, move, index, rebuild, and verify audio inside the supplied library. Preserve originals until the preview passes conflict checks.

## Definition of done for new audio

A new confirmed track is not complete until all of these are true:

- preserve one original audio file; do not physically duplicate or split it unless the user explicitly requests exported clips;
- identify title, artist, language, duration, codec, and confidence;
- listen to or technically analyze the real audio structure instead of assigning boundaries by fixed percentages;
- persist useful time ranges in `歌曲目录.json` under `segments` with emotion, production use, scenes, intensity, voiceover fit, vocal presence, and annotation source;
- rebuild the HTML, CSV, XLSX, and segment index;
- verify local `file://` playback in Edge, including seek-to-segment and exact segment-end stopping.

Automatic first-pass sections are allowed only for legacy backlog or temporary preview. They do not count as completed segmentation for newly imported audio.

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
6. Read [references/segment-workflow.md](references/segment-workflow.md), analyze the actual audio, and persist the recommended ranges. Preserve manually verified ranges on later rebuilds.
7. Build a preview table containing old path, proposed filename, target path, identification confidence, track tags, segment count, segment coverage, and conflicts. Do not overwrite an existing target.
8. Rename confirmed full songs as `Artist - Title.ext`. Move them by language under `03_音频/01_歌曲`. Move a file under `03_音频/02_剪辑BGM` only when the imported file itself is an excerpt; virtual segment ranges remain attached to the original song.
9. Update the root `歌曲目录.json` using [references/catalog-schema.md](references/catalog-schema.md). Keep paths relative to the library root and use `/` separators.
10. Run:

```powershell
python <skill-dir>/scripts/rebuild_library.py --root <library-root>
python <skill-dir>/scripts/rebuild_library.py --root <library-root> --check-only
```

11. Verify all moved files with `ffprobe` or an equivalent decoder. Open the generated `按情绪和用途找歌.html` directly as a local file in Edge. Require every player to show a finite duration and at least one track to play with increasing `currentTime`. A screenshot alone is not playback verification.
12. Verify segment behavior: apply a production-use filter such as `口播垫底`, start a result, confirm playback jumps inside its persisted start/end range, and confirm the timeline highlights that range. With `只播放此片段` enabled, playback must stop at the exact segment end.
13. Report moved files, pending files, conflicts, invalid media, catalog count, persisted versus automatic segment counts, generated outputs, and the actual playback result.

## Tagging rules

- Separate emotion, intensity, atmosphere, and usage. `夜晚`, `雨夜`, and `城市` are atmosphere, not emotion.
- Prefer existing controlled tags. Add a tag only when no existing term represents the meaning.
- Allow multiple tags without copying the audio file.
- Treat suggested video uses as analysis, not an official claim by the artist.
- Keep identification confidence separate from emotion confidence.
- Keep segment-boundary confidence separate from emotion confidence. Label web-researched context as research and actual listening as listening evidence.

## Safety rules

- Never delete source audio as a cleanup shortcut.
- Never overwrite a same-name destination.
- Never guess a song identity to force completion.
- Keep failed or uncertain files in `待识别` with a clear reason.
- Use a temporary output and atomic replacement when regenerating catalog artifacts.
- Keep the HTML standalone and free of a CSP or sandbox that blocks local media.
- Keep the bundled Font Awesome webfont under `assets/fonts/` when copying or installing the skill so icons continue to render offline.
- Do not use a simple HTTP server as the final seek test; servers without byte-range support can make a correct local player look broken.

## Rebuilding only

If the user asks to repair the filter, refresh tags, or regenerate indexes without new audio, validate `歌曲目录.json`, run the rebuild script, and perform the same path and playback checks. Do not move media unnecessarily or replace persisted manual segments with automatic ones.
