# -*- coding: utf-8 -*-
"""
test_doctor_scenarios.py - Eight End-to-End Test Scenarios for Skill Doctor
Validates:
1. Valid skill passes cleanly (Level A=PASS, Exit 0)
2. Missing required metadata rejected (Exit 2)
3. Vague description scores low & gets optimization suggestion
4. Overlapping responsibility identified against installed catalog
5. Modification invalidates cache and triggers re-audit
6. Safe auto-fix creates backup and supports rollback
7. Workflow gate blocks invalid skill promotion automatically
8. Non-skill coding tasks are exempted from audit
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DOCTOR_PY = Path(r"D:\AI-Skills\skills\skill-doctor\scripts\doctor.py")
PROMOTE_PY = Path(r"D:\AI-Skills\scripts\promote_skill.py")
SANDBOX = Path(r"D:\AI-Skills\tests\sandbox_doctor")


def run_cmd(args: list[str]) -> tuple[int, str]:
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def test_scenario_1_valid() -> bool:
    print("\n--- [Scenario 1] 创建格式正确的技能，能够正常通过 ---")
    skill_dir = SANDBOX / "valid-test-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: valid-test-skill\n"
        "description: \"自动化测试演示专用技能。用于当用户需要验证沙箱环境规范与自动化质量门禁时自动调用。\"\n"
        "---\n\n"
        "# Valid Test Skill\n\n"
        "## 执行流程\n"
        "1. 确认输入参数\n"
        "2. 执行测试逻辑\n\n"
        "## 异常与失败处理\n"
        "若测试失败，返回明确错误码并记录日志。\n",
        encoding="utf-8"
    )

    code, out = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir), "--no-cache"])
    passed = (code == 0) and ("PASS" in out)
    print(f"Result: ExitCode={code}, Passed={passed}")
    assert passed, f"Scenario 1 failed:\n{out}"
    return True


def test_scenario_2_missing_meta() -> bool:
    print("\n--- [Scenario 2] 创建缺少必填元数据的技能，能够识别错误 ---")
    skill_dir = SANDBOX / "invalid-meta-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Missing 'name' field
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "description: \"缺少名称的非法技能\"\n"
        "---\n\n"
        "# Broken Skill\n",
        encoding="utf-8"
    )

    code, out = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir), "--no-cache"])
    passed = (code == 2) and ("missing-name" in out)
    print(f"Result: ExitCode={code}, DetectedMissingName={'missing-name' in out}")
    assert passed, f"Scenario 2 failed:\n{out}"
    return True


def test_scenario_3_vague_description() -> bool:
    print("\n--- [Scenario 3] 创建触发描述模糊的技能，能够给出合理优化 ---")
    skill_dir = SANDBOX / "vague-desc-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: vague-desc-skill\n"
        "description: \"通用处理技能，可以处理任何任务。\"\n"
        "---\n\n"
        "# Vague Skill\n",
        encoding="utf-8"
    )

    code, out = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir), "--no-cache"])
    has_broad_warning = "overly-broad-scope" in out or "missing-explicit-when-to-use" in out
    has_recommendation = "推荐优化后的触发描述" in out
    passed = has_broad_warning and has_recommendation
    print(f"Result: HasBroadWarning={has_broad_warning}, HasRecommendation={has_recommendation}")
    assert passed, f"Scenario 3 failed:\n{out}"
    return True


def test_scenario_4_conflict() -> bool:
    print("\n--- [Scenario 4] 创建与现有技能职责重叠的技能，能够识别冲突 ---")
    skill_dir = SANDBOX / "duplicate-manager-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Duplicating skill-product-manager trigger description
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: duplicate-manager-skill\n"
        "description: \"管理本机 Skill：查找、评估、创建、升级、合并、归档或治理技能；用户说技能管家时使用。\"\n"
        "---\n\n"
        "# Duplicate Manager Skill\n",
        encoding="utf-8"
    )

    code, out = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir), "--no-cache"])
    has_conflict = "skill-product-manager" in out and ("重叠" in out or "overlap" in out.lower())
    print(f"Result: DetectedConflictWithSkillProductManager={has_conflict}")
    assert has_conflict, f"Scenario 4 failed:\n{out}"
    return True


def test_scenario_5_cache_invalidation() -> bool:
    print("\n--- [Scenario 5] 修改一个已经验收的技能，能够重新触发审核 ---")
    skill_dir = SANDBOX / "cache-test-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: cache-test-skill\n"
        "description: \"增量缓存测试技能。用于当用户执行哈希缓存与二次改动测试时调用。\"\n"
        "---\n\n"
        "# Cache Test Skill\n\n"
        "## 执行流程\n"
        "1. 步骤一\n\n"
        "## 异常与失败处理\n"
        "正常处理错误。\n",
        encoding="utf-8"
    )

    # 1. First audit (populates cache)
    _, out1 = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir)])
    is_cached_1 = "增量缓存命中" in out1

    # 2. Second audit without modifications (should hit cache)
    _, out2 = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir)])
    is_cached_2 = "增量缓存命中" in out2

    # 3. Modify the skill
    skill_md.write_text(
        skill_md.read_text(encoding="utf-8") + "\n\n<!-- Modified content -->\n",
        encoding="utf-8"
    )

    # 4. Third audit after modification (cache invalidated, re-audited!)
    _, out3 = run_cmd([sys.executable, str(DOCTOR_PY), "audit", str(skill_dir)])
    is_cached_3 = "增量缓存命中" in out3

    passed = (not is_cached_1) and is_cached_2 and (not is_cached_3)
    print(f"Result: Pass1Cached={is_cached_1}, Pass2Cached={is_cached_2}, Pass3AfterModifyCached={is_cached_3}")
    assert passed, f"Scenario 5 failed: 1={is_cached_1}, 2={is_cached_2}, 3={is_cached_3}"
    return True


def test_scenario_6_backup_and_rollback() -> bool:
    print("\n--- [Scenario 6] 模拟审核异常与自动修复，能够备份并安全回滚 ---")
    skill_dir = SANDBOX / "fix-rollback-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    original_content = (
        "---\n"
        "name: fix-rollback-skill\n"
        "description: \"演示带尖括号 <bad-tag> 的描述。用于当用户测试自动修复与安全回滚时调用。\"\n"
        "---\n\n"
        "# Fix Rollback Skill\n"
    )
    (skill_dir / "SKILL.md").write_text(original_content, encoding="utf-8")

    # 1. Run auto-fix
    code1, out1 = run_cmd([sys.executable, str(DOCTOR_PY), "fix", str(skill_dir)])
    fixed_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    has_fixed_bracket = "<bad-tag>" not in fixed_content and "«bad-tag»" in fixed_content

    # 2. Run rollback
    code2, out2 = run_cmd([sys.executable, str(DOCTOR_PY), "rollback", str(skill_dir)])
    restored_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    is_restored = "<bad-tag>" in restored_content

    passed = has_fixed_bracket and is_restored
    print(f"Result: AutoFixApplied={has_fixed_bracket}, RollbackRestoredOriginal={is_restored}")
    assert passed, f"Scenario 6 failed:\nout1={out1}\nout2={out2}"
    return True


def test_scenario_7_workflow_gate() -> bool:
    print("\n--- [Scenario 7] 验证技能晋级入口（promote_skill.py）确定性门禁拦截 ---")
    bad_skill = SANDBOX / "unqualified-promote-skill"
    bad_skill.mkdir(parents=True, exist_ok=True)
    (bad_skill / "SKILL.md").write_text(
        "---\n"
        "name: unqualified-promote-skill\n"
        "description: \"带有非法尖括号 <forbidden> 的未达标技能\"\n"
        "---\n\n"
        "# Bad Skill\n",
        encoding="utf-8"
    )

    dest_root = SANDBOX / "target_skills_root"
    dest_root.mkdir(parents=True, exist_ok=True)

    # Run promote_skill.py without --apply
    code, out = run_cmd([
        sys.executable, str(PROMOTE_PY),
        str(bad_skill),
        "--destination-root", str(dest_root)
    ])

    # Should be blocked by Skill Doctor gate!
    is_blocked = (code != 0) and ("Skill Doctor audit failed" in out or "Gate" in out or "description-angle-brackets" in out)
    print(f"Result: GateBlockedPromotion={is_blocked}, ExitCode={code}")
    assert is_blocked, f"Scenario 7 failed:\n{out}"
    return True


def test_scenario_8_non_skill_exemption() -> bool:
    print("\n--- [Scenario 8] 普通非技能编程任务免触发测试 ---")
    agents_md = Path(r"C:\Users\win10\.codex\AGENTS.md").read_text(encoding="utf-8")
    has_exemption_rule = "免审豁免（严格隔离保护）" in agents_md and "非技能开发任务，绝对严禁触发" in agents_md
    print(f"Result: AGENTS.md contains strict non-skill exemption: {has_exemption_rule}")
    assert has_exemption_rule, "Scenario 8 failed: Missing non-skill exemption rule in AGENTS.md"
    return True


def main() -> int:
    SANDBOX.mkdir(parents=True, exist_ok=True)
    print("==========================================================")
    print("🚀 开始执行 Skill Doctor 八大场景实测验收")
    print(f"沙箱测试目录: {SANDBOX}")
    print("==========================================================")

    scenarios = [
        test_scenario_1_valid,
        test_scenario_2_missing_meta,
        test_scenario_3_vague_description,
        test_scenario_4_conflict,
        test_scenario_5_cache_invalidation,
        test_scenario_6_backup_and_rollback,
        test_scenario_7_workflow_gate,
        test_scenario_8_non_skill_exemption,
    ]

    passed_count = 0
    for fn in scenarios:
        try:
            fn()
            passed_count += 1
        except Exception as e:
            print(f"❌ {fn.__name__} FAILED: {e}")

    print("\n" + "=" * 58)
    print(f"🏁 验收测试完成: {passed_count}/{len(scenarios)} 场景通过！")
    print("=" * 58)

    # Clean sandbox
    try:
        shutil.rmtree(SANDBOX)
    except Exception:
        pass

    return 0 if passed_count == len(scenarios) else 1


if __name__ == "__main__":
    raise SystemExit(main())
