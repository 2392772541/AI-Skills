# -*- coding: utf-8 -*-
import os
import shutil
import json
from datetime import datetime, timezone
from pathlib import Path

c_root = Path(r"C:\Users\win10\.codex\skills")
d_root = Path(r"D:\AI-Skills\skills")
archive_dest = Path(r"C:\Users\win10\.codex\archived_skills\20261027_duplicates")
backup_dest = Path(r"D:\AI-Skills\_archive_skills_backup\c_codex_duplicates_20261027")

archive_dest.mkdir(parents=True, exist_ok=True)
backup_dest.mkdir(parents=True, exist_ok=True)

c_dirs = {x.name for x in c_root.iterdir() if x.is_dir() and not x.name.startswith(".")}
d_dirs = {x.name for x in d_root.iterdir() if x.is_dir() and not x.name.startswith(".")}
common = sorted(list(c_dirs & d_dirs))

print(f"准备归档 {len(common)} 个位于 C 盘的重复技能副本...")

archived_list = []
for name in common:
    src = c_root / name
    if not src.exists():
        continue

    # 1. Backup copy to D:\AI-Skills\_archive_skills_backup
    bak = backup_dest / name
    if bak.exists():
        shutil.rmtree(bak)
    shutil.copytree(src, bak)

    # 2. Move to C:\Users\win10\.codex\archived_skills
    dest = archive_dest / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(src, dest)

    archived_list.append({
        "name": name,
        "original_path": str(src),
        "backup_path": str(bak),
        "archive_path": str(dest)
    })
    print(f"📦 已安全归档: {name}")

manifest = {
    "archived_at": datetime.now(timezone.utc).isoformat(),
    "total_count": len(archived_list),
    "skills": archived_list
}
(archive_dest / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n✅ 归档完毕！共安全迁移 {len(archived_list)} 个技能。清单已写入 {archive_dest / 'manifest.json'}")
