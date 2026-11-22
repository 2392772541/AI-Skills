# -*- coding: utf-8 -*-
"""
validator.py - Skill Doctor Format and Specification Validator
Validates skill folder structure, SKILL.md frontmatter, naming, local references,
and Windows portability.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

NAME_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_MD_LINK_REGEX = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")
HARDCODED_ABSOLUTE_PATH_REGEX = re.compile(r"(?i)\b(?:[a-z]:[/\\]|(?:/home/|/Users/|/usr/))[^\s\"\'\`<>|*]+")
MAX_SKILL_NAME_LEN = 64
MAX_DESC_LEN = 1024
ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


@dataclass
class ValidationIssue:
    severity: str  # "critical", "warning", "info"
    code: str
    message: str
    file: str = "SKILL.md"
    line: int | None = None
    suggestion: str = ""


@dataclass
class ValidationResult:
    is_valid: bool
    skill_path: Path
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def critical_issues(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "critical"]

    @property
    def warning_issues(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def info_issues(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "info"]


def validate_skill(skill_dir: Path | str) -> ValidationResult:
    skill_dir = Path(skill_dir).resolve()
    result = ValidationResult(is_valid=True, skill_path=skill_dir)

    if not skill_dir.exists() or not skill_dir.is_dir():
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "dir-not-found", f"Skill directory does not exist: {skill_dir}")
        )
        return result

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "missing-skill-md", "SKILL.md file is missing in the skill root folder")
        )
        return result

    try:
        raw_text = skill_md.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "read-error", f"Failed to read SKILL.md: {e}")
        )
        return result

    clean_text = re.sub(r"^(?:\s*<!--.*?-->\s*)+", "", raw_text, flags=re.S)

    if not clean_text.startswith("---"):
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "missing-frontmatter", "SKILL.md must start with YAML frontmatter delimiter '---'")
        )
        result.body = clean_text
        return result

    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)(.*)$", clean_text, re.S)
    if not match:
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "invalid-frontmatter-delimiter", "Frontmatter is not properly closed with '---'")
        )
        return result

    frontmatter_raw, body_raw = match.group(1), match.group(2)
    result.body = body_raw

    try:
        fm = yaml.safe_load(frontmatter_raw)
        if not isinstance(fm, dict):
            result.is_valid = False
            result.issues.append(
                ValidationIssue("critical", "invalid-yaml-structure", "Frontmatter must be a YAML dictionary mapping")
            )
            return result
        result.frontmatter = fm
    except yaml.YAMLError as e:
        result.is_valid = False
        result.issues.append(
            ValidationIssue("critical", "yaml-parse-error", f"YAML frontmatter parsing failed: {e}")
        )
        return result

    # Check allowed properties
    extra_keys = set(fm.keys()) - ALLOWED_PROPERTIES
    if extra_keys:
        result.issues.append(
            ValidationIssue(
                "warning",
                "unexpected-frontmatter-keys",
                f"Unexpected keys in frontmatter: {sorted(extra_keys)}. Allowed: {sorted(ALLOWED_PROPERTIES)}",
                suggestion="Move internal configuration into Markdown body, metadata dict, or references/"
            )
        )

    # Check 'name'
    name = fm.get("name")
    if not name:
        result.issues.append(
            ValidationIssue("critical", "missing-name", "'name' field is required in frontmatter")
        )
    elif not isinstance(name, str):
        result.issues.append(
            ValidationIssue("critical", "invalid-name-type", f"'name' must be string, got {type(name).__name__}")
        )
    else:
        name = name.strip()
        if not NAME_REGEX.match(name):
            suggested_name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            result.issues.append(
                ValidationIssue(
                    "critical",
                    "invalid-name-format",
                    f"Skill name '{name}' must be hyphen-case (lowercase a-z, 0-9, and single hyphens)",
                    suggestion=f"Change to '{suggested_name}'"
                )
            )
        if len(name) > MAX_SKILL_NAME_LEN:
            result.issues.append(
                ValidationIssue(
                    "critical",
                    "name-too-long",
                    f"Skill name is {len(name)} chars; maximum is {MAX_SKILL_NAME_LEN}"
                )
            )
        folder_name = skill_dir.name
        if folder_name != name:
            result.issues.append(
                ValidationIssue(
                    "warning",
                    "name-folder-mismatch",
                    f"Skill folder name '{folder_name}' does not match declared name '{name}'",
                    suggestion=f"Rename folder to '{name}' or update declared name to '{folder_name}'"
                )
            )

    # Check 'description'
    desc = fm.get("description")
    if not desc:
        result.issues.append(
            ValidationIssue("critical", "missing-description", "'description' field is required in frontmatter")
        )
    elif not isinstance(desc, str):
        result.issues.append(
            ValidationIssue("critical", "invalid-description-type", f"'description' must be string, got {type(desc).__name__}")
        )
    else:
        desc = desc.strip()
        if "<" in desc or ">" in desc:
            result.issues.append(
                ValidationIssue(
                    "critical",
                    "description-angle-brackets",
                    "Description cannot contain angle brackets '<' or '>', which can cause prompt injection or parsing failures",
                    suggestion="Replace '<' with '«' or quotes, and '>' with '»' or quotes"
                )
            )
        if len(desc) > MAX_DESC_LEN:
            result.issues.append(
                ValidationIssue(
                    "critical",
                    "description-too-long",
                    f"Description length ({len(desc)}) exceeds maximum allowed ({MAX_DESC_LEN} characters)"
                )
            )
        if len(desc) < 25:
            result.issues.append(
                ValidationIssue(
                    "warning",
                    "description-too-short",
                    f"Description is very short ({len(desc)} characters). It may fail to trigger reliably.",
                    suggestion="Elaborate what the skill does and under what specific user requests it should trigger."
                )
            )

    # Check local markdown links
    for match_link in LOCAL_MD_LINK_REGEX.finditer(body_raw):
        link_target = match_link.group(1).split("#")[0].strip()
        if not link_target:
            continue
        target_path = (skill_dir / link_target).resolve()
        if not target_path.exists():
            result.issues.append(
                ValidationIssue(
                    "warning",
                    "broken-local-link",
                    f"Local link target not found on disk: '{link_target}'",
                    suggestion=f"Create '{link_target}' or update link in SKILL.md"
                )
            )

    # Check hardcoded absolute paths in instructions
    hardcoded_matches = HARDCODED_ABSOLUTE_PATH_REGEX.findall(body_raw)
    if hardcoded_matches:
        # Filter out common markdown table borders or standard environment variable mentions
        real_hardcoded = [p for p in hardcoded_matches if len(p) > 4 and not p.endswith("|")]
        if real_hardcoded:
            result.issues.append(
                ValidationIssue(
                    "warning",
                    "hardcoded-absolute-path",
                    f"Found {len(real_hardcoded)} hardcoded absolute path(s) in SKILL.md (e.g. '{real_hardcoded[0]}')",
                    suggestion="Use project-relative paths, environment variables ($CODEX_HOME, $AI_SKILLS_HOME), or scripts/"
                )
            )

    # Check recommended folder structure
    standard_dirs = ["scripts", "references", "assets"]
    has_any_standard = any((skill_dir / d).exists() for d in standard_dirs)
    if not has_any_standard:
        result.issues.append(
            ValidationIssue(
                "info",
                "monolithic-skill",
                "Skill contains only SKILL.md without scripts/, references/, or assets/ subfolders.",
                suggestion="Consider organizing complex scripts or references into dedicated subfolders for modularity."
            )
        )

    # Check for body misplacement of 'When to Use'
    if re.search(r"(?im)^#+\s*(?:何时使用|when to use|trigger|触发条件)", body_raw):
        result.issues.append(
            ValidationIssue(
                "warning",
                "body-trigger-section",
                "Found 'When to Use' section in Markdown body. Codex only reads YAML frontmatter 'description' for skill discovery! Body is loaded only AFTER triggering.",
                suggestion="Move all trigger criteria, user intention phrases, and conditions directly into YAML frontmatter 'description'."
            )
        )

    # Set overall is_valid
    result.is_valid = len(result.critical_issues) == 0
    return result
