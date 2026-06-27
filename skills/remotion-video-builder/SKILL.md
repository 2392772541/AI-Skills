---
name: remotion-video-builder
description: Build, refine, preview, and render Remotion video projects with React. Use when Codex needs to create or edit Remotion compositions, launch Remotion Studio, add frame-driven animation, sequence scenes, render MP4 or still previews, or turn generic React ideas into deterministic Remotion code.
---

# Remotion Video Builder

Use this skill to work inside a Remotion project or to create one from scratch.

## Quick Start

1. Confirm whether a Remotion project already exists.
2. If the folder is empty, scaffold one with:

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
```

3. Install dependencies if needed:

```bash
npm install
```

4. Start Studio when interactive preview helps:

```bash
npx remotion studio
```

5. Render a still or video to verify the result:

```bash
npx remotion still <composition-id> out/preview.png --frame=30 --scale=0.5
npx remotion render <composition-id> out/output.mp4
```

## Working Rules

- Drive every animation from `useCurrentFrame()`.
- Use `useVideoConfig()` when `fps`, `durationInFrames`, `width`, or `height` are needed.
- Prefer `interpolate()` for explicit timing curves and `spring()` for elastic motion.
- Clamp interpolations by default with `extrapolateLeft: "clamp"` and `extrapolateRight: "clamp"`.
- Keep renders deterministic. Do not use `Math.random()`. Use `random()` from `remotion` with a stable seed.
- Use `AbsoluteFill` for layered scenes and overlays.
- Use `Sequence` or `Series` to stage content over time.
- Do not rely on CSS animations or transitions. They do not render correctly in Remotion. Animate through frame-based values instead.
- Treat Remotion components as pure visual render functions. Avoid interactive UI patterns such as clicks, hovers, `useState()`-driven UI, or side-effect-heavy logic.

## Composition Defaults

Use these defaults unless the project already establishes something else:

- `fps`: `30`
- `width`: `1920`
- `height`: `1080`
- `durationInFrames`: fit the creative intent, often `120` for a short demo

## Asset Rules

- Use `OffthreadVideo` for videos.
- Use `Img` for still images.
- Use `Audio` for audio tracks.
- Prefer `staticFile()` for assets stored in `public/`.
- When a remote asset is acceptable, pass a URL directly.

## Preferred Workflow

1. Inspect `src/Root.tsx` to see which compositions already exist.
2. Identify whether the request is:
   - a new composition,
   - an edit to an existing composition,
   - a render-only request,
   - or a Studio preview request.
3. Implement animation with small deterministic helpers and clear scene timing.
4. Run typecheck or lint if the project provides it.
5. Render a still first when layout or timing needs a quick check.
6. Render the final MP4 or image artifact.

## Scene Patterns

- Use one composition per deliverable idea when the concepts differ a lot.
- Split longer demos into scene components if timing becomes hard to read.
- Reuse one normalized progress value across related properties when multiple elements share the same timing.
- Favor bold typography, distinct visual direction, and intentional motion over generic UI-card layouts.

## References

- Read [references/remotion-gist-rules.md](references/remotion-gist-rules.md) when you need the adapted rules from the supplied gist, including asset component choices, sequencing patterns, and determinism reminders.
