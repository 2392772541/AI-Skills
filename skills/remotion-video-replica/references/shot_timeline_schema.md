# shot_timeline.json Schema

Use this shape for high-similarity video-to-Remotion reconstruction.

```json
{
  "source": {
    "video_path": "C:/path/to/source.mp4",
    "duration_seconds": 54.1,
    "source_fps": 30,
    "analysis_fps": 24,
    "width": 1280,
    "height": 720
  },
  "shots": [
    {
      "id": "s01_intro_title",
      "start_frame": 1,
      "end_frame": 192,
      "start_time": "00:00:00.000",
      "end_time": "00:00:07.958",
      "purpose": "Launch title",
      "visible_text": [
        "响指HaiSnap APP正式上线",
        "写文案、做PPT、做报告、做设计、开发应用"
      ],
      "layout": {
        "background": "dark blue-black gradient",
        "text_position": "center",
        "phone_position": null,
        "safe_area_notes": "text stays centered and small logo sits below"
      },
      "elements": [
        {
          "name": "main title",
          "type": "text",
          "position": "center x, slightly above center y",
          "size_notes": "thin white Chinese sans-serif, large"
        }
      ],
      "motion": [
        {
          "element": "main title",
          "frames": [12, 48],
          "action": "fade in with tiny scale-up"
        }
      ],
      "transition_in": "fade from black",
      "transition_out": "soft crossfade",
      "reference_frames": [
        "frames_24fps/frame_00096.jpg"
      ],
      "remotion_notes": "Use AbsoluteFill dark stage and frame-based opacity/scale."
    }
  ]
}
```

## Field Guidance

- `start_frame` and `end_frame` are 1-based frame numbers from the extracted sequence.
- Keep each shot narrow enough that motion is describable. Split when layout, copy, phone state, or transition changes.
- `reference_frames` should include 1-3 representative extracted frames.
- `motion` should describe micro-animation, not only scene-level movement.
- `remotion_notes` should mention implementation details only when they matter.

## Similarity Review Table

Use this table when comparing source frames to Remotion renders:

```markdown
| Frame | Source Ref | Remotion Ref | Composition | Text | UI Detail | Motion | Notes |
|---:|---|---|---|---|---|---|---|
| 96 | frame_00096.jpg | preview-0096.png | close | close | n/a | close | title needs slightly more spacing |
```
