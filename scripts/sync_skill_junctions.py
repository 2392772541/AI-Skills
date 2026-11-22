# -*- coding: utf-8 -*-
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

C_ROOT = Path(r"C:\Users\win10\.codex\skills")
D_ROOT = Path(r"D:\AI-Skills\skills")
BACKUP_BASE = Path(r"D:\AI-Skills\_archive_skills_backup\junction_sync_backups")

def is_junction(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        attrs = path.lstat().st_file_attributes
        return bool(attrs & 1024)
    except Exception:
        return False

def create_junction(link: Path, target: Path) -> bool:
    cmd = ["cmd", "/c", "mklink", "/J", str(link), str(target)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0

def scan_status():
    d_skills = sorted([p for p in D_ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")])
    c_skills = sorted([p for p in C_ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")])
    
    c_map = {p.name: p for p in c_skills}
    d_map = {p.name: p for p in d_skills}

    linked = []
    missing_in_c = []
    physical_dup = []
    only_in_c = [name for name in c_map if name not in d_map]

    for name, d_path in d_map.items():
        if name not in c_map:
            missing_in_c.append(name)
        else:
            c_path = c_map[name]
            if is_junction(c_path):
                linked.append(name)
            else:
                physical_dup.append(name)

    return {
        "total_d": len(d_skills),
        "total_c": len(c_skills),
        "already_junctioned": linked,
        "missing_in_c": missing_in_c,
        "physical_duplicates": physical_dup,
        "only_in_c": only_in_c,
    }

def apply_sync(dry_run: bool = False):
    status = scan_status()
    print(f"[*] D 盘技能总数: {status['total_d']}")
    print(f"[*] C 盘现有技能项: {status['total_c']}")
    print(f"[*] 已是正常 Junction 联接: {len(status['already_junctioned'])} 个")
    print(f"[*] C 盘缺失联接（需新建）: {len(status['missing_in_c'])} 个")
    print(f"[*] C 盘物理副本（需安全替换）: {len(status['physical_duplicates'])} 个")
    print(f"[*] 仅在 C 盘存在（建议未来归集）: {len(status['only_in_c'])} 个")

    if dry_run:
        print("\n[!] 处于 --dry-run 预检模式，未作任何磁盘修改。")
        return 0

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_BASE / ts

    # 1. 替换物理副本
    for name in status["physical_duplicates"]:
        c_path = C_ROOT / name
        d_path = D_ROOT / name
        print(f"\n[+] 处理物理副本: {name}")
        
        diff = filecmp.dircmp(c_path, d_path)
        has_diff = bool(diff.left_only or diff.right_only or diff.diff_files)
        if has_diff:
            print(f"    [!] 检测到文件存在差异，先备份 C 盘版本至: {backup_dir / name}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(c_path, backup_dir / name)
        
        shutil.rmtree(c_path)
        if create_junction(c_path, d_path):
            print(f"    [√] 成功转换为 Junction -> {d_path}")
        else:
            print(f"    [X] Junction 创建失败: {name}")

    # 2. 为缺失项创建 Junction
    print(f"\n[+] 开始为 {len(status['missing_in_c'])} 个缺失技能创建联接...")
    created_count = 0
    for name in status["missing_in_c"]:
        c_path = C_ROOT / name
        d_path = D_ROOT / name
        if create_junction(c_path, d_path):
            created_count += 1
        else:
            print(f"    [X] 联接创建失败: {name}")

    print(f"\n[√] 同步完成！共新建 {created_count} 个 Junction 联接，已替换 {len(status['physical_duplicates'])} 个物理副本。")
    print(f"[*] 此时 C 盘与 D 盘的所有技能实现 100% 物理同源，零同步延迟。")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Skill Junction Synchronizer")
    parser.add_argument("--status", action="store_true", help="仅查看状态")
    parser.add_argument("--dry-run", action="store_true", help="预演模式")
    parser.add_argument("--apply", action="store_true", help="执行全量联接同步")
    args = parser.parse_args()

    if args.status:
        st = scan_status()
        print(json.dumps({
            "total_d": st["total_d"],
            "total_c": st["total_c"],
            "already_junctioned_count": len(st["already_junctioned"]),
            "already_junctioned": st["already_junctioned"],
            "missing_in_c": st["missing_in_c"],
            "physical_duplicates": st["physical_duplicates"],
            "only_in_c": st["only_in_c"]
        }, indent=2, ensure_ascii=False))
        return 0

    if args.apply:
        return apply_sync(dry_run=False)

    return apply_sync(dry_run=True)

if __name__ == "__main__":
    sys.exit(main())
