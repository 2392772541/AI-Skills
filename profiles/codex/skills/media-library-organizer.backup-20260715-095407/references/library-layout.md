# Portable library layout

Keep the root focused on daily use:

```text
创作素材库/
├─ 00_待整理/
├─ 01_视频/
├─ 02_图片/
├─ 03_音频/
├─ 04_项目/
├─ 05_素材库管理/
│  ├─ 01_目录数据/       # 歌曲目录.json, 视频目录.json, 图片目录.json
│  ├─ 02_导出清单/       # CSV and XLSX outputs
│  ├─ 03_旧版资料/       # superseded pages, installers, reports, and backups
│  └─ skills/media-library-organizer/
├─ 素材片段库.html
├─ 使用说明.md
├─ 安装素材整理Skill.ps1
└─ media-library-organizer-skill-backup.zip
```

Rules:

- Do not put generated catalogs or CSV/XLSX exports back in the root.
- Keep only the current portable Skill ZIP in the root; archive superseded packages under `03_旧版资料`.
- Keep `素材片段库.html` in the root because media paths are relative to it.
- Preserve the numbered media folders and their names.
- Run `rebuild_library.py` after a layout change and verify the local page in Edge.
