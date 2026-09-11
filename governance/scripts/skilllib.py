from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")

CATEGORY_RULES = {
    "video": ["video", "remotion", "\u89c6\u9891", "\u5b57\u5e55", "caption"],
    "knowledge": ["knowledge", "notes", "obsidian", "\u77e5\u8bc6", "\u7b14\u8bb0", "lecture", "transcript"],
    "design": ["design", "figma", "image", "illustration", "poster", "\u89c6\u89c9", "\u63d2\u56fe", "\u6d77\u62a5"],
    "development": ["code", "review", "sdk", "tdd", "debug", "\u5f00\u53d1", "\u4ee3\u7801"],
    "security": ["security", "pentest", "reverse", "memory", "ctf", "\u5b89\u5168", "\u9006\u5411"],
    "lark": ["lark", "feishu", "\u98de\u4e66"],
    "documents": ["docx", "pdf", "markdown", "document", "\u6587\u6863"],
    "automation": ["automate", "workflow", "upload", "automation", "\u81ea\u52a8\u5316", "\u5de5\u4f5c\u6d41"],
    "skill-management": ["skill", "plugin", "\u6280\u80fd", "\u63d2\u4ef6"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    issues: list[str] = []
    if not text.startswith("---"):
        return {}, ["missing-frontmatter"]
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", text, re.S)
    if not match:
        return {}, ["invalid-frontmatter"]
    block = match.group(1)
    result: dict[str, str] = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw in {">", "|", ">-", "|-"}:
            chunks = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                chunks.append(lines[i].strip())
                i += 1
            result[key] = " ".join(x for x in chunks if x)
            continue
        result[key] = raw.strip("\"'")
        i += 1
    if not result.get("name"):
        issues.append("missing-name")
    if not result.get("description"):
        issues.append("missing-description")
    return result, issues


def infer_categories(name: str, description: str) -> list[str]:
    hay = f"{name} {description}".lower()
    found = [cat for cat, words in CATEGORY_RULES.items() if any(w.lower() in hay for w in words)]
    return found or ["other"]


def load_overrides(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    return json.loads(read_text(path))


def collect_local_links(skill_md: Path, text: str) -> list[str]:
    missing = []
    for raw in LOCAL_LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip().replace("%20", " ")
        if not target or re.match(r"^[A-Za-z]:[/\\]", target):
            continue
        if not (skill_md.parent / target).exists():
            missing.append(target)
    return sorted(set(missing))


def discover_skills(roots: Iterable[Path], overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    entries = []
    roots = [p.resolve() for p in roots if p.exists()]
    for root in roots:
        for skill_md in sorted(root.rglob("SKILL.md")):
            # Archived vendor snapshots below a skill are not independent active skills.
            if any(part in {"node_modules", ".git", "archived"} for part in skill_md.parts):
                continue
            data = skill_md.read_bytes()
            text = data.decode("utf-8-sig", errors="replace")
            fm, issues = parse_frontmatter(text)
            folder_name = skill_md.parent.name
            declared_name = str(fm.get("name", "")).strip()
            name = declared_name or folder_name
            description = str(fm.get("description", "")).strip()
            if declared_name and declared_name != folder_name:
                issues.append("name-folder-mismatch")
            if declared_name and not NAME_RE.match(declared_name):
                issues.append("invalid-name")
            if ".backup" in folder_name or "backup-" in folder_name:
                issues.append("backup-in-active-root")
            if len(data) > 30000:
                issues.append("large-skill-md")
            missing_links = collect_local_links(skill_md, text)
            if missing_links:
                issues.append("missing-local-links")
            try:
                relative = skill_md.parent.relative_to(root).as_posix()
            except ValueError:
                relative = skill_md.parent.as_posix()
            ov = overrides.get(name, {})
            categories = ov.get("categories") or infer_categories(name, description)
            scripts = sorted(p.relative_to(skill_md.parent).as_posix() for p in skill_md.parent.rglob("*") if p.is_file() and "scripts" in p.parts)
            references = sorted(p.relative_to(skill_md.parent).as_posix() for p in skill_md.parent.rglob("*") if p.is_file() and "references" in p.parts)
            entry = {
                "id": sha256_bytes(str(skill_md.parent.resolve()).lower().encode("utf-8"))[:16],
                "name": name,
                "declared_name": declared_name,
                "folder_name": folder_name,
                "description": description,
                "path": str(skill_md.parent.resolve()),
                "skill_md": str(skill_md.resolve()),
                "root": str(root),
                "relative_path": relative,
                "content_hash": sha256_bytes(data),
                "byte_size": len(data),
                "file_count": sum(1 for p in skill_md.parent.rglob("*") if p.is_file()),
                "scripts": scripts,
                "references": references,
                "missing_links": missing_links,
                "categories": categories,
                "triggers": ov.get("triggers", []),
                "patterns": ov.get("patterns", []),
                "aliases": ov.get("aliases", []),
                "priority": int(ov.get("priority", 0)),
                "status": ov.get("status", "active"),
                "issues": sorted(set(issues)),
                "is_system": ".system" in skill_md.parts,
            }
            entries.append(entry)
    by_name: dict[str, list[dict]] = {}
    for entry in entries:
        by_name.setdefault(entry["name"], []).append(entry)
    duplicates = []
    for name, group in sorted(by_name.items()):
        if len(group) > 1:
            duplicates.append({
                "name": name,
                "count": len(group),
                "exact_content": len({e["content_hash"] for e in group}) == 1,
                "entry_ids": [e["id"] for e in group],
                "paths": [e["path"] for e in group],
            })
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "roots": [str(r) for r in roots],
        "entry_count": len(entries),
        "unique_name_count": len(by_name),
        "duplicate_name_count": len(duplicates),
        "entries": entries,
        "duplicates": duplicates,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_registry(path: Path) -> dict:
    return json.loads(read_text(path))


def active_preferred_entries(registry: dict) -> list[dict]:
    """Choose one representative per name, preferring non-system D:/AI-Skills entries."""
    grouped: dict[str, list[dict]] = {}
    for e in registry.get("entries", []):
        if e.get("status") == "archived":
            continue
        grouped.setdefault(e["name"], []).append(e)
    chosen = []
    for name, group in grouped.items():
        group.sort(key=lambda e: (
            0 if "D:\\AI-Skills" in e["path"] else 1,
            1 if e.get("is_system") else 0,
            len(e.get("issues", [])),
            e["path"],
        ))
        chosen.append(group[0])
    return sorted(chosen, key=lambda e: e["name"])
