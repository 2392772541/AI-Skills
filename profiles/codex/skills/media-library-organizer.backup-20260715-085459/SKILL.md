---
name: media-library-organizer
description: Organize and maintain a portable local creative-media library containing audio, video, and images. Use for new or unidentified media; song identification; audio and video time-segment cutting/annotation; image content inspection; emotion, scene, production-use, voiceover, shot, camera-motion, orientation, and content tags; updating 歌曲目录.json, 视频目录.json, 图片目录.json, CSV/XLSX indexes; rebuilding 素材片段库.html; repairing local preview; or verifying Edge playback, seeking, segment stopping, image viewing, and portable installation.
---

# Media Library Organizer

Treat the latest concrete request as authorization to inspect, classify, rename, move, index, rebuild, and verify media inside the supplied library. Preserve originals until conflict checks pass.

## Locate the library

Find the root in this order:

1. A user-supplied path containing any two of `歌曲目录.json`, `视频目录.json`, `图片目录.json`.
2. An ancestor of `skills/media-library-organizer` containing `01_视频`, `02_图片`, and `03_音频`.
3. The current directory when it contains the same media folders.

Never depend on a fixed drive letter. Pass the resolved root to scripts with `--root`.

## Route by media type

- Audio: read [tag-taxonomy.md](references/tag-taxonomy.md), [segment-workflow.md](references/segment-workflow.md), and [catalog-schema.md](references/catalog-schema.md).
- Video: read [video-workflow.md](references/video-workflow.md) before detecting shots, annotating ranges, or updating `视频目录.json`.
- Image: read [image-workflow.md](references/image-workflow.md) before inspecting content or updating `图片目录.json`.

## Required workflow

1. Scan `00_待整理`, `01_视频`, `02_图片`, `03_音频/01_歌曲/待识别`, and category folders recursively.
2. Read real metadata before labeling:
   - audio/video: duration, codec, bitrate, dimensions, frame rate, and embedded metadata with `ffprobe`;
   - images: format, width, height, orientation, alpha, and EXIF when available.
3. Identify content from embedded metadata and filenames first. Inspect or listen to the actual media before content, emotion, or use judgments. Use current web sources only when identity or contextual research is needed.
4. Build a conflict-safe preview containing old path, proposed name, target path, confidence, tags, segment count, and conflicts. Never overwrite an existing target.
5. Preserve one original file:
   - record reusable audio/video parts as virtual time ranges;
   - do not export physical clips unless the user asks;
   - allow multiple tags without duplicating media files.
6. Persist results:
   - audio tracks and segments in `歌曲目录.json`;
   - video files and shot ranges in `视频目录.json`;
   - image content and usage tags in `图片目录.json`.
7. New audio/video is not complete until useful ranges are based on real listening/viewing. Automatic proportional sections are legacy fallback only and must remain marked as automatic.
8. Run:

```powershell
python <skill-dir>/scripts/rebuild_library.py --root <library-root>
python <skill-dir>/scripts/rebuild_library.py --root <library-root> --check-only
```

9. Open `素材片段库.html` directly as a local file in Edge and verify all three workspaces:
   - audio: finite duration, increasing `currentTime`, seek-to-range, timeline highlight, exact segment-end stop;
   - video: finite duration, visible frame, seek-to-shot, correct range, exact segment-end stop;
   - image: thumbnail loads, full preview opens, content and use filters work.
10. Report moved and pending files, conflicts, invalid media, catalog counts, persisted versus automatic ranges, generated files, and actual browser verification.

## Definition of done

- Audio: identity and metadata confirmed; track tags and persisted useful ranges complete; voiceover suitability is honest.
- Video: metadata confirmed; meaningful shot or scene ranges persisted with content, shot type, motion, use, quality, and annotation source.
- Image: dimensions and format confirmed; visible content, category, orientation, color, and use tags persisted; preview verified.
- Integrated page: audio, video, and image are available from one webpage; empty media types show a usable empty state.

## Safety and portability

- Never delete originals as cleanup.
- Never guess identity or content to force completion; keep uncertain media pending with a reason.
- Use relative `/` paths and atomic replacements for generated artifacts.
- Preserve manually verified ranges on rebuild.
- Keep `assets/media-library.html`, `assets/fonts/fa-solid-900.woff2`, and its license in the Skill package.
- Use local `file://` for final seek verification. A simple HTTP server without byte-range support can produce false failures.
- Keep the root portable ZIP current after any Skill change.
