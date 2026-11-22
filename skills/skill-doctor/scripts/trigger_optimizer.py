# -*- coding: utf-8 -*-
"""
trigger_optimizer.py - Evaluates and optimizes Skill description triggering quality.
Scores descriptions, detects common antipatterns (overly broad, overly narrow,
missing 'when to use', skill name dependency), and generates actionable rewrite recommendations.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

TRIGGER_KEYWORDS_EN = [
    "use when", "use this", "trigger when", "when user", "when the user",
    "for tasks", "designed to", "helps with", "intended for", "useful when"
]

TRIGGER_KEYWORDS_ZH = [
    "用于", "当用户", "当需要", "适用场景", "在以下情况", "针对", "帮助用户", "当提出"
]

OVERLY_BROAD_INDICATORS = [
    "any task", "all tasks", "anything", "general purpose", "everything",
    "always use", "必须调用", "任何任务", "所有任务", "处理任何", "通用"
]

ACTION_VERBS = [
    "create", "build", "generate", "analyze", "audit", "optimize", "convert",
    "review", "test", "inspect", "manage", "deploy", "export", "extract",
    "生成", "创建", "分析", "审核", "优化", "转换", "审查", "测试", "检查", "排查", "导出", "提取", "管理"
]


@dataclass
class TriggerAnalysis:
    score: int  # 0 to 100
    issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    original_description: str = ""
    recommended_description: str = ""
    rationale: str = ""
    extracted_keywords: list[str] = field(default_factory=list)


def analyze_trigger_description(skill_name: str, description: str, body: str = "") -> TriggerAnalysis:
    desc = (description or "").strip()
    desc_lower = desc.lower()
    clean_name = skill_name.lower().replace("-", " ")

    issues: list[str] = []
    strengths: list[str] = []
    score = 100

    if not desc:
        return TriggerAnalysis(
            score=0,
            issues=["empty-description"],
            original_description="",
            recommended_description=f"Provide specialized capabilities for {skill_name}. Use when...",
            rationale="Description is completely missing."
        )

    # 1. Length check
    if len(desc) < 30:
        score -= 25
        issues.append("description-too-short (less than 30 characters)")
    elif len(desc) > 800:
        score -= 15
        issues.append("description-approaching-limit (>800 chars, max is 1024)")
    else:
        strengths.append(f"Appropriate description length ({len(desc)} characters)")

    # 2. Angle brackets check
    if "<" in desc or ">" in desc:
        score -= 20
        issues.append("contains-angle-brackets (< or > will break XML model formatting)")

    # 3. Trigger condition / When-to-use check
    has_trigger_clause = any(k in desc_lower for k in TRIGGER_KEYWORDS_EN) or any(k in desc for k in TRIGGER_KEYWORDS_ZH)
    if not has_trigger_clause:
        score -= 25
        issues.append("missing-explicit-when-to-use (lacks 'Use when...' or '用于.../当用户...')")
    else:
        strengths.append("Contains explicit trigger clause ('Use when...' / '用于...')")

    # 4. Action verbs check (Problem definition)
    found_actions = [v for v in ACTION_VERBS if v in desc_lower or v in desc]
    if not found_actions:
        score -= 15
        issues.append("missing-action-verbs (unclear what action the skill actually performs)")
    else:
        strengths.append(f"Clear action capabilities: {', '.join(found_actions[:4])}")

    # 5. Overly broad check (False positive risk)
    broad_matches = [w for w in OVERLY_BROAD_INDICATORS if w in desc_lower or w in desc]
    if broad_matches:
        score -= 30
        issues.append(f"overly-broad-scope (uses catch-all words: {broad_matches})")

    # 6. Skill name dependency check
    # If description only triggers if user types "/skill-name" or "call skill-name"
    if f"/{skill_name}" in desc_lower or f"调用 {skill_name}" in desc_lower or f"invoke {skill_name}" in desc_lower:
        score -= 20
        issues.append("skill-name-dependency (users speak in natural language, rarely type exact skill names)")

    # 7. Angle bracket replacement & normalization
    clean_desc = desc.replace("<", "«").replace(">", "»")

    # Extract key domain tokens
    words = re.findall(r"[\u4e00-\u9fff]{2,4}|[a-zA-Z0-9_-]{3,}", desc)
    stop_words = {"this", "that", "with", "when", "user", "using", "from", "into", "skill", "codex", "用于", "当用户", "可以"}
    extracted = [w for w in words if w.lower() not in stop_words][:8]

    # Generate recommended optimization
    recommended, rationale = generate_optimized_description(skill_name, desc, body, issues)

    score = max(0, min(100, score))

    return TriggerAnalysis(
        score=score,
        issues=issues,
        strengths=strengths,
        original_description=desc,
        recommended_description=recommended,
        rationale=rationale,
        extracted_keywords=extracted
    )


def generate_optimized_description(skill_name: str, desc: str, body: str, issues: list[str]) -> tuple[str, str]:
    """
    Deterministically generates an improved description incorporating best practices.
    """
    # If description has angle brackets, fix them
    base_desc = desc.replace("<", "«").replace(">", "»").strip()

    # Check if Chinese or English
    is_chinese = bool(re.search(r"[\u4e00-\u9fff]", base_desc + body))

    rationale_points = []

    if is_chinese:
        # Extract primary intent from body title if available
        title_match = re.search(r"(?m)^#\s+(.+)$", body)
        skill_title = title_match.group(1).strip() if title_match else skill_name

        if "missing-explicit-when-to-use" in " ".join(issues):
            if not (base_desc.startswith("用于") or "适用" in base_desc):
                base_desc = f"{base_desc}。用于当用户提出与 {skill_title} 相关的任务、需求或故障排查时自动调用。"
                rationale_points.append("补充了明确的触发引导词（'用于当用户提出...'）")
        if "overly-broad-scope" in " ".join(issues):
            base_desc = re.sub(r"(任何任务|所有任务|通用|必须调用)", "对应领域任务", base_desc)
            rationale_points.append("收敛了过于宽泛的全局修饰词，防止无谓误触发")
        if "description-too-short" in " ".join(issues):
            base_desc = f"{skill_title} 专业处理能力。{base_desc} 当用户需要进行该项操作或咨询时调用。"
            rationale_points.append("扩充了核心领域功能与具体触发场景")
    else:
        if "missing-explicit-when-to-use" in " ".join(issues):
            if "use when" not in base_desc.lower():
                base_desc = f"{base_desc}. Use when the user requests or needs assistance with {skill_name.replace('-', ' ')} workflows."
                rationale_points.append("Added explicit 'Use when...' clause to improve Codex auto-selection")
        if "overly-broad-scope" in " ".join(issues):
            base_desc = re.sub(r"(?i)\b(any task|all tasks|always use|everything)\b", "specific domain tasks", base_desc)
            rationale_points.append("Narrowed catch-all language to avoid interfering with normal tasks")

    if not rationale_points:
        rationale_points.append("保留原意并确保无非法字符与适当触发强度")

    return base_desc, "; ".join(rationale_points)
