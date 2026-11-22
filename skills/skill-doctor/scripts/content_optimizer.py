# -*- coding: utf-8 -*-
"""
content_optimizer.py - Skill Doctor SKILL.md Body and Instruction Optimizer
Analyzes instructions structure, context efficiency, error handling completeness,
and tool boundary clarity without sacrificing necessary domain logic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

DANGEROUS_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+[/~]"), "Dangerous recursive root deletion command"),
    (re.compile(r"\bRemove-Item\s+-Recurse\s+['\"]?[A-Za-z]:[/\\]?['\"]?\b"), "Unsafe recursive drive-root deletion in PowerShell"),
    (re.compile(r"\bchmod\s+-R\s+777\b"), "Overly permissive permission escalation"),
    (re.compile(r"\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}['\"]"), "Possible hardcoded credential or token"),
]


@dataclass
class ContentAuditReport:
    total_chars: int
    estimated_tokens: int
    has_clear_title: bool
    has_step_workflow: bool
    has_error_handling: bool
    has_tool_boundaries: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def audit_skill_content(body: str, skill_path: Path | None = None) -> ContentAuditReport:
    total_chars = len(body)
    # Rough estimate: ~3.5 chars per token for mixed EN/ZH text
    estimated_tokens = max(1, int(total_chars / 3.5))

    issues: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    # 1. Title & Objective
    has_clear_title = bool(re.search(r"(?m)^#\s+.+", body))
    if not has_clear_title:
        warnings.append("missing-h1-title: Markdown body does not have a top-level '# Title' heading.")
        recommendations.append("Add a clear '# Skill Title' at the beginning of the body.")

    # 2. Sequential steps or workflow
    has_step_workflow = bool(re.search(r"(?im)(?:^###?\s+(?:步骤|step|流程|阶段|1\.|2\.)|^\s*\d+\.\s+)", body))
    if not has_step_workflow:
        warnings.append("lacks-structured-workflow: No clearly numbered steps or phase headers detected.")
        recommendations.append("Organize the execution path into sequential steps (Step 1, Step 2, ...) to guide Codex execution.")

    # 3. Error handling & Fallback
    error_keywords = ["error", "fail", "fallback", "retry", "exception", "异常", "失败", "重试", "报错", "回退", "回滚"]
    has_error_handling = any(w in body.lower() for w in error_keywords)
    if not has_error_handling:
        warnings.append("missing-error-handling: No error recovery, retry, or failure handling guidelines found.")
        recommendations.append("Add an '异常与失败处理' section outlining what to do if commands or dependencies fail.")

    # 4. Tool & Command Boundaries
    tool_keywords = ["tool", "script", "command", "bash", "powershell", "python", "工具", "命令", "脚本", "运行"]
    has_tool_boundaries = any(w in body.lower() for w in tool_keywords)

    # 5. Token Efficiency & Context Bloat
    if total_chars > 20000:
        warnings.append(f"large-skill-body: Body is {total_chars} chars (~{estimated_tokens} tokens). This consumes significant context window on every trigger.")
        recommendations.append("Move verbose reference tables, catalogs, or extensive documentation into 'references/' and link them.")
    elif total_chars < 150:
        warnings.append(f"sparse-skill-body: Body is very brief ({total_chars} chars). Codex may lack sufficient domain context.")
        recommendations.append("Provide concrete procedures, examples, or constraints in the Markdown instructions.")

    # 6. Dangerous commands / credentials
    for pattern, desc in DANGEROUS_PATTERNS:
        if pattern.search(body):
            issues.append(f"dangerous-instruction: {desc}")

    # 7. Check for duplicate sections
    headers = [h.strip().lower() for h in re.findall(r"(?m)^#+\s+(.+)$", body)]
    seen_headers = set()
    duplicates = []
    for h in headers:
        if h in seen_headers:
            duplicates.append(h)
        seen_headers.add(h)
    if duplicates:
        warnings.append(f"duplicate-headings: Found duplicate section titles: {duplicates}")
        recommendations.append("Consolidate duplicate sections to avoid contradictory directives.")

    return ContentAuditReport(
        total_chars=total_chars,
        estimated_tokens=estimated_tokens,
        has_clear_title=has_clear_title,
        has_step_workflow=has_step_workflow,
        has_error_handling=has_error_handling,
        has_tool_boundaries=has_tool_boundaries,
        issues=issues,
        warnings=warnings,
        recommendations=recommendations
    )
