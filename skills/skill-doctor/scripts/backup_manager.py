# -*- coding: utf-8 -*-
"""
backup_manager.py - Manages automated backups, safe rollbacks, and incremental hash caches
for skills undergoing audit and optimization.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BACKUP_BASE = Path("D:/AI-Skills/_backups/doctor")
DEFAULT_CACHE_FILE = Path("D:/AI-Skills/_reports/doctor-cache.json")
FALLBACK_BACKUP_BASE = Path.home() / ".codex" / "doctor_backups"
FALLBACK_CACHE_FILE = Path.home() / ".codex" / "doctor_cache.json"


def get_backup_dir(skill_name: str) -> Path:
    if Path("D:/AI-Skills").exists():
        b_dir = DEFAULT_BACKUP_BASE / skill_name
    else:
        b_dir = FALLBACK_BACKUP_BASE / skill_name
    b_dir.mkdir(parents=True, exist_ok=True)
    return b_dir


def get_cache_file() -> Path:
    if Path("D:/AI-Skills/_reports").exists():
        return DEFAULT_CACHE_FILE
    FALLBACK_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    return FALLBACK_CACHE_FILE


def compute_skill_tree_hash(skill_dir: Path | str) -> str:
    """Computes a composite SHA256 hash of all files in the skill folder."""
    skill_dir = Path(skill_dir).resolve()
    hasher = hashlib.sha256()

    if not skill_dir.exists():
        return ""

    # Sort paths for deterministic hash
    all_candidates = [p for p in skill_dir.rglob("*") if p.is_file() and not p.name.startswith(".")]
    all_files = sorted(
        [
            p for p in all_candidates
            if not any(part in {"tests", "__pycache__", ".git", ".doctor_backups"} for part in p.relative_to(skill_dir).parts)
        ],
        key=lambda x: str(x.relative_to(skill_dir))
    )

    for f in all_files:
        rel_path = str(f.relative_to(skill_dir)).replace("\\", "/")
        hasher.update(rel_path.encode("utf-8"))
        try:
            content = f.read_bytes()
            hasher.update(content)
        except Exception:
            pass

    return hasher.hexdigest()


def create_backup(skill_dir: Path | str, reason: str = "pre-optimization") -> Path:
    """Creates a timestamped snapshot of the skill directory."""
    skill_dir = Path(skill_dir).resolve()
    skill_name = skill_dir.name
    backup_base = get_backup_dir(skill_name)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = backup_base / f"{ts}_{reason}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # Copy tree excluding temporary or backup directories
    for item in skill_dir.iterdir():
        if item.name in {".git", ".doctor_backups", "__pycache__"}:
            continue
        dest = snapshot_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    manifest = {
        "skill_name": skill_name,
        "source_path": str(skill_dir),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "content_hash": compute_skill_tree_hash(skill_dir),
        "files_count": len(list(snapshot_dir.rglob("*")))
    }
    (snapshot_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return snapshot_dir


def rollback_skill(skill_dir: Path | str, snapshot_id: str | None = None) -> tuple[bool, str]:
    """Restores skill from the latest or specified backup snapshot."""
    skill_dir = Path(skill_dir).resolve()
    skill_name = skill_dir.name
    backup_base = get_backup_dir(skill_name)

    if not backup_base.exists():
        return False, f"No backups found for {skill_name}"

    snapshots = sorted([d for d in backup_base.iterdir() if d.is_dir()], key=lambda x: x.name)
    if not snapshots:
        return False, f"No snapshots available in {backup_base}"

    target_snapshot = snapshots[-1]
    if snapshot_id:
        matched = [s for s in snapshots if snapshot_id in s.name]
        if matched:
            target_snapshot = matched[-1]
        else:
            return False, f"Snapshot '{snapshot_id}' not found"

    # Create safety backup of current state before rolling back
    create_backup(skill_dir, reason="pre-rollback-safety")

    # Restore files from snapshot
    for item in target_snapshot.iterdir():
        if item.name == "manifest.json":
            continue
        dest = skill_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    return True, f"Successfully rolled back {skill_name} from snapshot {target_snapshot.name}"


def read_cache(skill_dir: Path | str) -> dict[str, Any] | None:
    cache_file = get_cache_file()
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8-sig", errors="replace"))
        key = str(Path(skill_dir).resolve())
        entry = data.get(key)
        if not entry:
            return None
        current_hash = compute_skill_tree_hash(skill_dir)
        if entry.get("content_hash") == current_hash:
            return entry
    except Exception:
        pass
    return None


def update_cache(skill_dir: Path | str, report_dict: dict[str, Any]) -> None:
    cache_file = get_cache_file()
    key = str(Path(skill_dir).resolve())
    current_hash = compute_skill_tree_hash(skill_dir)

    data = {}
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8-sig", errors="replace"))
        except Exception:
            data = {}

    data[key] = {
        "content_hash": current_hash,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "report": report_dict
    }
    try:
        cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
