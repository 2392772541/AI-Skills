# Catalog schema

The library root contains `歌曲目录.json` encoded as UTF-8.

```json
{
  "version": 2,
  "tracks": [
    {
      "file_name": "Artist - Title.mp3",
      "type": "歌曲",
      "language": "英文",
      "core_emotions": ["伤感回忆"],
      "fine_emotions": ["遗憾", "思念"],
      "intensity": "中等 · 渐强",
      "atmosphere": ["夜色", "都市"],
      "uses": ["感情回忆", "人物故事"],
      "source": "用户导入",
      "license_status": "未知",
      "duration": "03:30",
      "relative_path": "03_音频/01_歌曲/英文/Artist - Title.mp3",
      "segments": [
        {
          "id": "s1",
          "label": "开场铺垫",
          "start": 0,
          "end": 38.5,
          "core_emotions": ["伤感回忆"],
          "fine_emotions": ["孤独", "克制"],
          "intensity": "低",
          "atmosphere": ["夜色", "都市"],
          "uses": ["口播垫底", "片头铺垫", "夜景氛围"],
          "scenes": ["城市空镜", "人物背影"],
          "voiceover_fit": "优秀",
          "vocal_presence": "轻人声或器乐",
          "annotation": "人工试听确认"
        }
      ],
      "notes": "用途为分析推断"
    }
  ]
}
```

Required fields are `file_name`, `type`, `language`, `core_emotions`, `fine_emotions`, `intensity`, `atmosphere`, `uses`, `relative_path`.

`segments` is optional for backward compatibility. When omitted, `rebuild_library.py` creates five practical first-pass sections (opening, narrative, build, climax, close) and marks them as automatic annotations. Manually supplied segments override automatic sections.

Rules:

- Paths must be relative, must not contain `..`, and must use `/` separators.
- `relative_path` and `file_name` must be unique.
- Arrays must contain non-empty unique strings.
- Keep unknown source or license values as `未知`; do not omit them to hide uncertainty.
- The JSON catalog is the source of truth. HTML, CSV, and XLSX are generated views.
- Segment times are seconds from the start of the audio file, must be ordered, and must not overlap.
- Segment tags should describe that time range, not blindly copy the whole-track judgment.
