# -*- coding: utf-8 -*-
"""
conflict_detector.py - Skill Doctor Conflict and Overlap Detector
Lightweight comparison against the existing installed skill catalog (via registry/skills.json)
detecting name collisions, duplicate content, and description overlap.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path("D:/AI-Skills/registry/skills.json")


@dataclass
class ConflictFinding:
    conflict_type: str  # "name-collision", "exact-duplicate", "semantic-overlap", "router-conflict"
    severity: str       # "critical", "warning", "info"
    existing_skill_name: str
    existing_skill_path: str
    similarity_score: float = 0.0
    description: str = ""
    resolution_suggestion: str = ""


@dataclass
class ConflictReport:
    has_critical_conflict: bool
    findings: list[ConflictFinding] = field(default_factory=list)
    total_skills_compared: int = 0


def tokenize_for_similarity(text: str) -> set[str]:
    """Extracts meaningful terms for lightweight similarity comparison."""
    words = re.findall(r"[\u4e00-\u9fff]{2,4}|[a-zA-Z0-9_-]{3,}", text.lower())
    stopwords = {
        "this", "that", "with", "when", "user", "using", "from", "into", "skill",
        "codex", "used", "guide", "helps", "provides", "用于", "当用户", "可以", "帮助",
        "进行", "使用", "支持", "通过", "对应"
    }
    return {w for w in words if w not in stopwords}


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def detect_conflicts(
    candidate_name: str,
    candidate_description: str,
    candidate_path: Path | str,
    content_hash: str = "",
    registry_path: Path | None = None
) -> ConflictReport:
    candidate_path = Path(candidate_path).resolve()
    reg_path = registry_path or DEFAULT_REGISTRY
    findings: list[ConflictFinding] = []

    entries: list[dict[str, Any]] = []
    if reg_path.exists():
        try:
            data = json.loads(reg_path.read_text(encoding="utf-8-sig", errors="replace"))
            entries = data.get("entries", [])
        except Exception:
            entries = []

    cand_tokens = tokenize_for_similarity(f"{candidate_name} {candidate_description}")
    cand_norm_name = candidate_name.strip().lower()

    for entry in entries:
        entry_path = Path(entry.get("path", "")).resolve()
        # Skip comparing with itself
        if entry_path == candidate_path:
            continue

        existing_name = entry.get("name", "").strip().lower()
        existing_desc = entry.get("description", "")
        existing_hash = entry.get("content_hash", "")

        # 1. Exact name collision
        if existing_name == cand_norm_name:
            cand_md = candidate_path / "SKILL.md"
            exist_md = entry_path / "SKILL.md"
            is_exact_mirror = False
            if cand_md.exists() and exist_md.exists():
                try:
                    is_exact_mirror = (cand_md.read_bytes() == exist_md.read_bytes())
                except Exception:
                    pass
            sev = "warning" if is_exact_mirror else "critical"
            c_type = "duplicate-exact-mirror" if is_exact_mirror else "name-collision-divergent"
            desc_msg = (
                f"Skill exists identically in both roots (mirror detected at {entry_path})."
                if is_exact_mirror else
                f"Skill name '{candidate_name}' conflicts with a divergent version at {entry_path}."
            )
            sugg_msg = (
                "Recommend consolidating to D:/AI-Skills/skills and archiving secondary copy to avoid dual-loading."
                if is_exact_mirror else
                f"Resolve version mismatch: update or rename '{candidate_name}' to avoid overshadowing."
            )
            findings.append(
                ConflictFinding(
                    conflict_type=c_type,
                    severity=sev,
                    existing_skill_name=entry.get("name", ""),
                    existing_skill_path=str(entry_path),
                    description=desc_msg,
                    resolution_suggestion=sugg_msg
                )
            )
            continue

        # 2. Exact content duplicate
        if content_hash and existing_hash and content_hash == existing_hash:
            findings.append(
                ConflictFinding(
                    conflict_type="exact-duplicate",
                    severity="critical",
                    existing_skill_name=entry.get("name", ""),
                    existing_skill_path=str(entry_path),
                    description=f"Skill content is identical (SHA256 match) to existing skill '{entry.get('name')}'.",
                    resolution_suggestion="Reuse the existing skill directly instead of duplicating it in the library."
                )
            )
            continue

        # 3. Router conflict check
        # Only flag if a third-party/new skill tries to usurp router roles
        if cand_norm_name not in {"00-skill-router", "skill-product-manager"} and any(w in cand_norm_name for w in ["skill-router", "skills-router"]):
            findings.append(
                ConflictFinding(
                    conflict_type="router-conflict",
                    severity="critical",
                    existing_skill_name=entry.get("name", ""),
                    existing_skill_path=str(entry_path),
                    description="Candidate skill attempts to replace or conflict with the core skill routing infrastructure.",
                    resolution_suggestion="Integrate routing rules into the existing 00-skill-router rather than creating competing router skills."
                )
            )
            continue

        # 4. Semantic overlap in trigger description
        existing_tokens = tokenize_for_similarity(f"{existing_name} {existing_desc}")
        sim = jaccard_similarity(cand_tokens, existing_tokens)
        shared_key_terms = sorted(cand_tokens & existing_tokens)

        # Overlap threshold: Jaccard > 0.40 or 4+ highly specific domain keywords
        if sim >= 0.40 or len(shared_key_terms) >= 5:
            findings.append(
                ConflictFinding(
                    conflict_type="semantic-overlap",
                    severity="warning",
                    existing_skill_name=entry.get("name", ""),
                    existing_skill_path=str(entry_path),
                    similarity_score=round(sim, 2),
                    description=f"High semantic overlap ({round(sim*100)}%) with '{entry.get('name')}'. Shared keywords: {shared_key_terms[:5]}.",
                    resolution_suggestion=(
                        f"Differentiate triggers: clarify that '{candidate_name}' handles specific sub-tasks "
                        f"or specific file types, while '{entry.get('name')}' handles general or upstream workflows."
                    )
                )
            )

    has_critical = any(f.severity == "critical" for f in findings)
    return ConflictReport(
        has_critical_conflict=has_critical,
        findings=findings,
        total_skills_compared=len(entries)
    )
