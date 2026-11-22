# -*- coding: utf-8 -*-
"""
doctor.py - Skill Doctor CLI and Core Orchestrator
Comprehensive audit, optimization, conflict detection, test generation, and acceptance gating
for Codex and Agent Skills.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from validator import validate_skill, ValidationResult
from trigger_optimizer import analyze_trigger_description, TriggerAnalysis
from content_optimizer import audit_skill_content, ContentAuditReport
from conflict_detector import detect_conflicts, ConflictReport
from test_generator import generate_test_cases, save_test_suite, VerificationMatrix
from backup_manager import (
    create_backup, rollback_skill, read_cache, update_cache,
    compute_skill_tree_hash, get_backup_dir
)

MAX_OPTIMIZATION_ROUNDS = 3


def run_audit(
    skill_path: Path | str,
    auto_fix: bool = False,
    strict: bool = False,
    use_cache: bool = True,
    registry_path: Path | None = None
) -> dict[str, Any]:
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        return {
            "status": "error",
            "message": f"Skill directory not found: {skill_dir}",
            "exit_code": 2
        }

    # Check incremental cache
    if use_cache and not auto_fix:
        cached = read_cache(skill_dir)
        if cached and cached.get("report"):
            rep = cached["report"]
            rep["is_cached"] = True
            return rep

    # 1. Validation (Level A)
    val_res = validate_skill(skill_dir)
    skill_name = val_res.frontmatter.get("name", skill_dir.name)
    description = val_res.frontmatter.get("description", "")
    content_hash = compute_skill_tree_hash(skill_dir)

    # 2. Trigger Quality Assessment
    trigger_res = analyze_trigger_description(skill_name, description, val_res.body)

    # 3. Content Audit
    content_res = audit_skill_content(val_res.body, skill_dir)

    # 4. Conflict Detection
    conflict_res = detect_conflicts(
        candidate_name=skill_name,
        candidate_description=description,
        candidate_path=skill_dir,
        content_hash=content_hash,
        registry_path=registry_path
    )

    # 5. Test Generation & Multi-Level Matrix
    test_cases = generate_test_cases(skill_name, description, val_res.body)

    # Evaluate Level Statuses
    level_a = "PASS" if len(val_res.critical_issues) == 0 else "FAIL"

    # Level B: Check if inside known skill roots or registry
    level_b = "PASS" if any(p in str(skill_dir).replace("\\", "/") for p in ["/skills", "/.codex/skills", "/.agents/skills"]) else "WARN"

    # Level C: Check scripts compilation
    scripts_dir = skill_dir / "scripts"
    level_c = "PASS"
    if scripts_dir.exists():
        py_scripts = list(scripts_dir.glob("*.py"))
        for ps in py_scripts:
            import py_compile
            try:
                py_compile.compile(str(ps), doraise=True)
            except Exception:
                level_c = "FAIL"
                break
    else:
        level_c = "N/A"

    # Level D: Heuristic Trigger Score
    level_d = "EVALUATED_PASS" if trigger_res.score >= 70 else "EVALUATED_WARN"

    # Level E: End-to-end (strict distinction: cannot claim pass without execution)
    level_e = "UNVERIFIED"

    matrix = VerificationMatrix(
        skill_name=skill_name,
        level_a_format=level_a,
        level_b_discovery=level_b,
        level_c_explicit=level_c,
        level_d_nl_trigger=level_d,
        level_e_e2e_exec=level_e,
        notes={
            "level_a": f"{len(val_res.critical_issues)} critical, {len(val_res.warning_issues)} warnings",
            "level_d": f"Trigger score: {trigger_res.score}/100",
            "level_e": "Pending interactive/end-to-end task run"
        }
    )
    save_test_suite(skill_dir, test_cases, matrix)

    # Auto-fix execution if requested
    fixes_applied: list[str] = []
    if auto_fix:
        fixes_applied = apply_safe_fixes(skill_dir, val_res, trigger_res)
        if fixes_applied:
            # Re-audit after fixes
            return run_audit(skill_dir, auto_fix=False, strict=strict, use_cache=False, registry_path=registry_path)

    # Determine overall status and exit code
    has_critical = len(val_res.critical_issues) > 0 or conflict_res.has_critical_conflict
    has_warning = len(val_res.warning_issues) > 0 or len(conflict_res.findings) > 0 or trigger_res.score < 70

    exit_code = 0
    if has_critical:
        exit_code = 2
    elif has_warning and strict:
        exit_code = 1

    report_data = {
        "status": "failed" if has_critical else ("warning" if has_warning else "passed"),
        "exit_code": exit_code,
        "skill_name": skill_name,
        "skill_path": str(skill_dir),
        "content_hash": content_hash,
        "is_cached": False,
        "summary": {
            "critical_count": len(val_res.critical_issues) + (1 if conflict_res.has_critical_conflict else 0),
            "warning_count": len(val_res.warning_issues) + len(conflict_res.findings),
            "trigger_score": trigger_res.score,
            "level_matrix": asdict(matrix)
        },
        "validation": {
            "is_valid": val_res.is_valid,
            "critical_issues": [asdict(i) for i in val_res.critical_issues],
            "warning_issues": [asdict(i) for i in val_res.warning_issues],
            "info_issues": [asdict(i) for i in val_res.info_issues]
        },
        "trigger_optimization": asdict(trigger_res),
        "content_audit": asdict(content_res),
        "conflict_detection": {
            "has_critical": conflict_res.has_critical_conflict,
            "findings": [asdict(f) for f in conflict_res.findings],
            "total_compared": conflict_res.total_skills_compared
        },
        "test_suite": {
            "positive_count": 5,
            "negative_count": 5,
            "boundary_count": 3
        },
        "fixes_applied": fixes_applied
    }

    if not has_critical:
        update_cache(skill_dir, report_data)

    return report_data


def apply_safe_fixes(skill_dir: Path, val_res: ValidationResult, trigger_res: TriggerAnalysis) -> list[str]:
    """
    Applies safe, non-destructive automated fixes:
    - Replaces '<' and '>' in SKILL.md description
    - Normalizes uppercase or underscore skill names to hyphen-case
    - Creates missing recommended folders (references, scripts, assets)
    Always backs up before touching any file.
    """
    fixes: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return fixes

    raw_text = skill_md.read_text(encoding="utf-8-sig", errors="replace")
    new_text = raw_text

    # Create safety backup
    create_backup(skill_dir, reason="auto-fix-safe")

    # Fix 1: Angle brackets in description
    if "<" in raw_text or ">" in raw_text:
        # Replace angle brackets within frontmatter
        match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)(.*)$", new_text, re.S)
        if match:
            fm_text, body = match.group(1), match.group(2)
            fixed_fm = fm_text.replace("<", "«").replace(">", "»")
            new_text = f"---\n{fixed_fm}\n---\n{body}"
            fixes.append("Replaced forbidden angle brackets '<>' with '«»' in frontmatter")

    # Fix 2: Name format (hyphen-case)
    name = val_res.frontmatter.get("name", "")
    if name and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
        fixed_name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        new_text = re.sub(rf"(?m)^name:\s*[\"']?{re.escape(name)}[\"']?", f"name: {fixed_name}", new_text)
        fixes.append(f"Normalized skill name from '{name}' to hyphen-case '{fixed_name}'")

    # Fix 3: Low trigger score description enhancement
    if trigger_res.score < 60 and trigger_res.recommended_description:
        escaped_rec = trigger_res.recommended_description.replace('"', '\\"')
        new_text = re.sub(
            r'(?m)^description:\s*([\'"].*?[\'"]|.+)$',
            f'description: "{escaped_rec}"',
            new_text,
            count=1
        )
        fixes.append(f"Auto-enhanced trigger description (rationale: {trigger_res.rationale})")

    if new_text != raw_text:
        skill_md.write_text(new_text, encoding="utf-8")

    # Fix 4: Create standard folders if missing
    for d in ["scripts", "references"]:
        target_d = skill_dir / d
        if not target_d.exists():
            target_d.mkdir(parents=True, exist_ok=True)
            fixes.append(f"Created standard subfolder '{d}/'")

    return fixes


def render_terminal_report(report: dict[str, Any]) -> None:
    status_badge = {
        "passed": "\033[92m[PASS 通过]\033[0m",
        "warning": "\033[93m[WARN 警告]\033[0m",
        "failed": "\033[91m[FAIL 阻断]\033[0m"
    }.get(report.get("status", ""), "[UNKNOWN]")

    print("\n" + "=" * 65)
    print(f"🩺  Codex Skill Doctor 审核报告 {status_badge}")
    print("=" * 65)
    print(f"📌 技能名称: {report.get('skill_name')}")
    print(f"📂 技能路径: {report.get('skill_path')}")
    if report.get("is_cached"):
        print("⚡ [增量缓存命中] 文件哈希未变，直接返回上一次已验证审计结论")

    sumry = report.get("summary", {})
    print("-" * 65)
    print(f"📊 质量概览: 严重缺陷: {sumry.get('critical_count', 0)} | 改进警告: {sumry.get('warning_count', 0)} | 触发得分: {sumry.get('trigger_score', 0)}/100")

    # Verification Matrix
    matrix = sumry.get("level_matrix", {})
    print("\n🏷️  五级验证闭环状态 (A-E Matrix):")
    print(f"   [A] 静态规范校验 : {matrix.get('level_a_format', 'N/A')}")
    print(f"   [B] 技能发现识别 : {matrix.get('level_b_discovery', 'N/A')}")
    print(f"   [C] 显式脚本执行 : {matrix.get('level_c_explicit', 'N/A')}")
    print(f"   [D] 自然语言触发 : {matrix.get('level_d_nl_trigger', 'N/A')}")
    print(f"   [E] 端到端实际执行: {matrix.get('level_e_e2e_exec', 'UNVERIFIED')} (严格区分，绝不拿A/B冒充)")

    # Validation details
    val = report.get("validation", {})
    if val.get("critical_issues"):
        print("\n❌ 严重阻断缺陷 (必须修复方可交付):")
        for issue in val["critical_issues"]:
            print(f"   • [{issue.get('code')}] {issue.get('message')}")
            if issue.get("suggestion"):
                print(f"     💡 修复建议: {issue.get('suggestion')}")

    if val.get("warning_issues"):
        print("\n⚠️  规范改进项:")
        for issue in val["warning_issues"]:
            print(f"   • [{issue.get('code')}] {issue.get('message')}")

    # Trigger optimization
    trig = report.get("trigger_optimization", {})
    print(f"\n🎯 触发质量深度分析 (Score: {trig.get('score', 0)}/100):")
    if trig.get("strengths"):
        for s in trig["strengths"]:
            print(f"   ✅ {s}")
    if trig.get("issues"):
        for i in trig["issues"]:
            print(f"   ⚠️  {i}")
    if trig.get("recommended_description") and trig.get("score", 100) < 85:
        print(f"\n💡 推荐优化后的触发描述 (Description):")
        print(f"   \"{trig.get('recommended_description')}\"")
        print(f"   依据: {trig.get('rationale')}")

    # Conflict findings
    conf = report.get("conflict_detection", {})
    if conf.get("findings"):
        print(f"\n🔄 技能冲突与重叠排查 (对比了全库 {conf.get('total_compared', 0)} 个技能):")
        for f in conf["findings"]:
            sev_icon = "❌" if f.get("severity") == "critical" else "⚠️"
            print(f"   {sev_icon} [{f.get('conflict_type')}] 与现有技能 '{f.get('existing_skill_name')}' 发生重叠")
            print(f"     描述: {f.get('description')}")
            print(f"     建议: {f.get('resolution_suggestion')}")
    else:
        print(f"\n✅ 技能冲突排查: 独占性良好，与现有 {conf.get('total_compared', 0)} 个技能无核心冲突")

    # Fixes applied
    if report.get("fixes_applied"):
        print("\n🛠️  已执行的安全自动修复 (已自动安全备份):")
        for fix in report["fixes_applied"]:
            print(f"   • {fix}")

    print("=" * 65 + "\n")


def render_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        f"# 🩺 Skill Doctor 审核报告: {report.get('skill_name')}",
        "",
        f"- **审核时间**: {report.get('summary', {}).get('level_matrix', {}).get('notes', {}).get('level_a', '')}",
        f"- **技能路径**: `{report.get('skill_path')}`",
        f"- **综合判定**: **{report.get('status').upper()}** (Exit Code: {report.get('exit_code')})",
        f"- **触发评分**: {report.get('summary', {}).get('trigger_score')}/100",
        "",
        "## 五级验证闭环矩阵 (A-E Verification Matrix)",
        "",
        "| 验证层级 | 维度名称 | 状态判定 | 验证手段与依据 |",
        "|---|---|---|---|",
    ]
    matrix = report.get("summary", {}).get("level_matrix", {})
    lines.append(f"| **Level A** | 静态规范与元数据 | `{matrix.get('level_a_format')}` | AST / YAML 解析与边界规则 |")
    lines.append(f"| **Level B** | Codex 加载与注册发现 | `{matrix.get('level_b_discovery')}` | 技能目录结构与环境变量探测 |")
    lines.append(f"| **Level C** | 脚本显式调用验证 | `{matrix.get('level_c_explicit')}` | 脚本语法与入口执行编译 |")
    lines.append(f"| **Level D** | 自然语言触发能力 | `{matrix.get('level_d_nl_trigger')}` | 触发关键词、动词与边界防误触打分 |")
    lines.append(f"| **Level E** | 真实任务端到端交付 | `{matrix.get('level_e_e2e_exec')}` | 真实业务任务执行（不冒充通过） |")
    lines.append("")

    # Issues
    val = report.get("validation", {})
    lines.append("## 发现与建议")
    if val.get("critical_issues"):
        lines.append("### ❌ 阻断性缺陷")
        for i in val["critical_issues"]:
            lines.append(f"- **[{i.get('code')}]** {i.get('message')}")
            if i.get("suggestion"):
                lines.append(f"  - *建议*: {i.get('suggestion')}")
    if val.get("warning_issues"):
        lines.append("### ⚠️ 规范与质量警告")
        for i in val["warning_issues"]:
            lines.append(f"- **[{i.get('code')}]** {i.get('message')}")

    trig = report.get("trigger_optimization", {})
    if trig.get("recommended_description"):
        lines.append("### 🎯 推荐优化触发描述")
        lines.append(f"> {trig.get('recommended_description')}")
        lines.append(f"\n*优化理由*: {trig.get('rationale')}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    # Convenience shortcut: if first arg is a valid directory path, insert 'audit'
    if len(sys.argv) > 1 and sys.argv[1] not in {"-h", "--help", "audit", "fix", "rollback", "test", "optimize-trigger"}:
        if Path(sys.argv[1]).exists() or sys.argv[1].startswith("."):
            sys.argv.insert(1, "audit")

    parser = argparse.ArgumentParser(description="Skill Doctor - Codex Agent Skills Audit and Optimization System")
    subparsers = parser.add_subparsers(dest="command")

    # Audit command
    audit_p = subparsers.add_parser("audit", help="Run comprehensive audit on a skill directory")
    audit_p.add_argument("skill_path", type=str, help="Path to the skill folder")
    audit_p.add_argument("--auto-fix", action="store_true", help="Automatically fix safe issues with rollback backup")
    audit_p.add_argument("--strict", action="store_true", help="Fail with exit code 1 if warnings are found")
    audit_p.add_argument("--no-cache", action="store_true", help="Bypass incremental cache")
    audit_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    audit_p.add_argument("--report", type=str, default="", help="Path to output markdown report")

    # Fix command
    fix_p = subparsers.add_parser("fix", help="Automatically repair safe issues and re-audit")
    fix_p.add_argument("skill_path", type=str, help="Path to the skill folder")

    # Rollback command
    rb_p = subparsers.add_parser("rollback", help="Rollback skill to previous snapshot")
    rb_p.add_argument("skill_path", type=str, help="Path to the skill folder")
    rb_p.add_argument("--snapshot", type=str, default=None, help="Snapshot ID to restore")

    # Test command
    test_p = subparsers.add_parser("test", help="Display test suite and verification matrix")
    test_p.add_argument("skill_path", type=str, help="Path to the skill folder")

    # Optimize trigger
    opt_p = subparsers.add_parser("optimize-trigger", help="Deep dive into trigger description quality")
    opt_p.add_argument("skill_path", type=str, help="Path to the skill folder")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "rollback":
        success, msg = rollback_skill(args.skill_path, args.snapshot)
        print(msg)
        return 0 if success else 2

    if args.command == "fix":
        rep = run_audit(args.skill_path, auto_fix=True, use_cache=False)
        render_terminal_report(rep)
        return rep.get("exit_code", 0)

    if args.command in {"audit", "test", "optimize-trigger"}:
        auto_fix = getattr(args, "auto_fix", False)
        strict = getattr(args, "strict", False)
        no_cache = getattr(args, "no_cache", False)

        rep = run_audit(args.skill_path, auto_fix=auto_fix, strict=strict, use_cache=not no_cache)

        if getattr(args, "json", False):
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            render_terminal_report(rep)

        report_file = getattr(args, "report", "")
        if report_file:
            render_markdown_report(rep, Path(report_file))
            print(f"📄 Markdown 报告已写入: {report_file}")

        return rep.get("exit_code", 0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
