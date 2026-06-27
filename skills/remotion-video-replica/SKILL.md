---
name: remotion-video-replica
description: Use when the user wants to imitate, recreate, replicate, clone, or make a high-similarity Remotion version of an uploaded/reference video. Applies to video-to-Remotion workflows, video frame analysis, shot-by-shot reconstruction, animation matching, and requests like "仿制视频", "复刻这个视频", "按原片做 Remotion", or "高相似度复刻". This skill requires step-by-step user confirmation before moving between phases.
---

# Remotion Video Replica

## Core Rule

This is a gated workflow. After each phase, stop and ask the user whether to continue. Do not start the next phase until the user explicitly approves it.

Use short confirmations such as:

```text
第 N 步已完成。是否继续第 N+1 步？
```

If the user says to proceed automatically, still pause at the two major gates: after `shot_timeline.json` and after the first sample render.

## Workflow

### Phase 1: Intake And Goal Lock

Clarify only what is necessary:

- Source video path or uploaded file.
- Target fidelity: high-similarity replica, style reference, or loose remake.
- Target output: Remotion project only, preview sample, full MP4, or all.
- Sampling FPS, default `24fps`.
- Whether to reuse original audio, default yes when available.

Then summarize the plan and ask for confirmation before extracting frames.

### Phase 2: Probe And Extract Frames

Run `ffprobe` and extract frames with FFmpeg.

Expected artifacts:

- `ffprobe.json`
- `frames_24fps/frame_%05d.jpg`
- `contact_sheets/sheet_%03d.jpg`
- `frame_index_24fps.csv`

Use a stable output folder named like:

```text
video_analysis_<source-name>/
```

After extraction, report:

- duration
- original fps
- output fps
- resolution
- frame count
- artifact paths

Ask whether to continue to shot breakdown.

### Phase 3: Shot Timeline Breakdown

Analyze the contact sheets and key frames. Create `shot_timeline.json`.

Each shot should capture:

- start/end frame
- start/end timestamp
- scene purpose
- visible text
- layout
- foreground elements
- background elements
- phone/UI state
- motion notes
- transition in/out
- similarity-critical details

For the schema, read `references/shot_timeline_schema.md`.

After creating the timeline, summarize the scene list and ask the user to approve or correct it. Do not code yet.

### Phase 4: Reference Asset Pack

Extract or prepare reference assets needed for visual similarity.

Common assets:

- logo/end card
- phone UI screenshots
- input bar
- keyboard frame
- profile/share card
- lifestyle montage reference frames
- important background frames

Put them under the Remotion project, usually:

```text
public/reference/
```

Prefer extracted stills for high similarity. Use programmatic drawing only for simple shapes or when the user wants a clean rebuild rather than a close replica.

After preparing assets, show the asset list and ask whether to continue to the sample build.

### Phase 5: First 15 Seconds Sample

Do not implement the whole video first. Build the first 10-15 seconds as a quality bar.

The sample should test:

- typography scale and weight
- dark background texture
- title timing
- phone position and motion
- UI density
- transition language
- animation density

Render several stills at matching frames, and optionally a short MP4 sample.

Compare original frames with Remotion frames. Report concrete mismatches:

- composition
- brightness/contrast
- text size
- phone size/position
- missing UI details
- motion timing

Ask the user whether the sample quality is good enough to extend to the full video.

### Phase 6: Full Remotion Build

Only after sample approval, implement the full composition.

Rules:

- Match source fps and duration unless the user asks otherwise.
- Drive animation through `useCurrentFrame()`, `interpolate()`, `spring()`, `Sequence`, and `AbsoluteFill`.
- Avoid CSS animations/transitions.
- Keep scene code modular enough for shot-level edits.
- Use original/reference assets when they materially improve similarity.
- Add many small motions, not only large scene transitions.

Expected files usually include:

- `src/Root.tsx`
- `src/Composition.tsx`
- optional `src/scenes/*`
- optional `src/components/*`
- `public/reference/*`

Run typecheck/lint if available.

Ask before final render.

### Phase 7: Render And Review

Render the final MP4.

Validate with `ffprobe`:

- resolution
- fps
- frame count
- duration
- audio stream when applicable

Render stills at important frames and compare against original. Give a concise review with:

- what now matches
- what still differs
- suggested next refinements

## Quality Heuristics

When the user says "像原片", prioritize in this order:

1. Timing and shot boundaries
2. Layout and element positions
3. Text content, size, and rhythm
4. Asset fidelity and UI density
5. Motion density and micro-animations
6. Code cleanliness

Avoid calling a piece "done" just because it renders. A rendered structural remake is not the same as a high-similarity replica.

## Confirmation Checklist

Use this checklist during the workflow:

- Phase 1 approved: goals and output path
- Phase 2 approved: frame extraction artifacts
- Phase 3 approved: shot timeline
- Phase 4 approved: reference assets
- Phase 5 approved: first sample quality
- Phase 6 approved: full implementation
- Phase 7 complete: final render and review

## Common User Trigger Phrases

- "帮我复刻这个视频"
- "按这个视频做 Remotion"
- "仿制这个动画"
- "高相似度复刻"
- "不要只做结构仿片"
- "先抽帧再做"
- "每一步问我再继续"
