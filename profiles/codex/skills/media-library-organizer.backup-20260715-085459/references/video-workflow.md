# Video ingestion and segmentation

## Catalog shape

Store `视频目录.json` as UTF-8:

```json
{
  "version": 1,
  "videos": [
    {
      "file_name": "雨夜街道_空镜.mp4",
      "category": "风景空镜",
      "content_tags": ["雨夜", "街道", "车流"],
      "uses": ["口播背景", "情绪转场"],
      "orientation": "横屏",
      "resolution": "1920×1080",
      "fps": 25,
      "duration": "00:24",
      "relative_path": "01_视频/风景空镜/雨夜街道_空镜.mp4",
      "segments": [
        {
          "id": "v1",
          "label": "雨夜街道全景",
          "start": 0,
          "end": 8.4,
          "content_tags": ["雨夜", "街道", "车流"],
          "shot_type": "全景",
          "camera_motion": "固定",
          "uses": ["口播背景", "氛围铺垫"],
          "quality": "优选",
          "annotation": "场景检测 + 人工查看"
        }
      ],
      "notes": ""
    }
  ]
}
```

Required video fields: `file_name`, `category`, `content_tags`, `uses`, `duration`, `relative_path`.

## Analyze real shots

1. Use `ffprobe` to confirm duration, resolution, frame rate, codec, and orientation.
2. Run `scripts/suggest_video_segments.py` to obtain scene-change candidates and representative frames.
3. Inspect frames around every candidate. Merge false cuts caused by flashes, fast motion, or exposure changes.
4. Persist useful ranges; do not force full coverage or a fixed number of segments.

## Controlled tags

- Category: `产品`, `人物`, `动画特效`, `风景空镜`.
- Shot type: `特写`, `近景`, `中景`, `全景`, `远景`, `俯拍`, `航拍`, `屏幕录制`.
- Camera motion: `固定`, `推进`, `拉远`, `横移`, `跟拍`, `环绕`, `摇镜`, `手持`, `延时`, `慢动作`.
- Uses: `口播背景`, `知识讲解`, `产品展示`, `人物故事`, `Vlog日常`, `片头铺垫`, `氛围转场`, `情绪递进`, `高潮快剪`, `片尾收束`, `遮罩叠加`, `演示说明`.
- Quality: `优选`, `可用`, `备用`, `不建议`.

## Boundary rules

- Use actual visual changes, subject/action continuity, and edit usefulness.
- Short action inserts may be 1–5 seconds. Stable B-roll is commonly 5–20 seconds.
- Ranges must be ordered, non-overlapping, and inside the duration.
- Automatic fallback must say `自动初标 · 需逐镜头确认`; it is not completed ingestion.

## Verify

Open `素材片段库.html` locally in Edge. Select a video range, confirm the player seeks inside it, the timeline highlights it, and playback stops exactly at its `end`.
