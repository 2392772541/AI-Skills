# Segment ingestion workflow

Use this workflow for every newly confirmed song or imported excerpt.

## 1. Preserve the source

- Keep one original audio file.
- Represent reusable parts as time ranges in `歌曲目录.json`; do not create duplicate MP3 files for every tag.
- Physically export clips only when the user asks for deliverable clip files.

## 2. Analyze the real audio

Use `ffprobe` for duration and stream metadata. Use waveform/energy analysis to find candidate transitions, then listen around every proposed boundary.

Do not force a fixed number of sections. Prefer musically meaningful changes such as:

- intro or texture change;
- vocal entry or exit;
- verse, chorus, bridge, instrumental, drop, or solo;
- clear intensity rise, release, or outro;
- a stable low-interference bed suitable for narration.

Recommended reusable ranges are usually 15–60 seconds. Shorter ranges are acceptable for transitions, hits, or an imported excerpt. Longer ranges are acceptable when the texture is genuinely stable.

## 3. Persist each useful range

Write `segments` into the track object. For every range record:

- `id`, `label`, `start`, `end`;
- `core_emotions`, `fine_emotions`, `intensity`, `atmosphere`;
- production `uses` and concrete `scenes`;
- `voiceover_fit` and `vocal_presence`;
- `annotation`, using `人工试听确认`, `波形分析 + 人工试听`, or another honest source.

Use controlled labels from [tag-taxonomy.md](tag-taxonomy.md). A segment can inherit a track tag only when the actual range supports it.

## 4. Voiceover standard

- `优秀`: stable bed, limited vocal competition, and predictable dynamics at a low mix level.
- `可用`: usable after lowering the music or selecting a quieter subsection.
- `不建议`: prominent lyric, dense lead, sudden dynamics, or climax masks narration.

Do not label a section `口播垫底` solely because it is an intro or outro. Listen for vocal presence, transients, density, and stability.

## 5. Coverage and confidence

- Segments do not need to cover the entire song. Store useful editing ranges, not filler.
- Ranges must be ordered, non-overlapping, inside the media duration, and long enough to audition.
- Preserve manually verified ranges on rebuild.
- Automatic fallback ranges must say `自动初标 · 建议试听后微调边界` and remain visibly distinguishable from completed annotations.

## 6. Rebuild and verify

Run the rebuild and check commands from `SKILL.md`, then open the generated HTML directly in local Edge.

Verify at least:

1. every audio file exposes a finite duration;
2. emotion and production-use filters return segment rows;
3. clicking a row starts inside that row's `start`/`end` range;
4. the correct colored timeline section becomes active;
5. `只播放此片段` stops at the exact `end` value;
6. no console or media errors occur in the local-file workflow.

Report persisted manual ranges and automatic fallback ranges separately.
