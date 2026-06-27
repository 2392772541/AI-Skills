# Remotion Gist Rules

Source adapted from the user-provided gist:
[Remotion Claude.MD by ThariqS](https://gist.github.com/ThariqS/3d446e7c7aa9eb94f468194deb73028f)

Use this reference when you need the detailed rules that were carried over from the gist.

## Core Structure

- A composition is registered in `src/Root.tsx`.
- A composition needs `id`, `component`, `durationInFrames`, `width`, `height`, and `fps`.
- `useCurrentFrame()` is the base clock for animation.
- `useVideoConfig()` is the source of truth for video dimensions, duration, and frame rate.

## Media Components

- `OffthreadVideo`: Use for videos. `startFrom`, `endAt`, and `volume` are available.
- `Img`: Use for still images.
- `Audio`: Use for sound. `startFrom`, `endAt`, and `volume` are available.
- `staticFile()`: Use for files in `public/`.

## Layout and Timing

- `AbsoluteFill`: Use for full-frame layout and stacking layers.
- `Sequence`: Use to place content at a specific frame offset.
- `Series`: Use to chain sections one after another.
- `TransitionSeries`: Use when the project includes `@remotion/transitions` and a scene transition is needed.

## Animation

- `interpolate()`: Use for direct mappings from frame or progress to values.
- `spring()`: Use for elastic or overshooting motion.
- Clamp interpolations unless there is a strong reason not to.

## Determinism

- Do not use `Math.random()`.
- Use `random(seed)` from `remotion` when decorative randomness is needed.
- Keep the component pure and reproducible for rendering.

## React Mindset Shift

Remotion components are not interactive app components.

- Avoid hover, click, focus, and form logic.
- Avoid `useEffect()` for time-based animation.
- Avoid UI state that changes because of user interaction.
- Build visuals as a pure function of frame number and props.
