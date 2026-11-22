# -*- coding: utf-8 -*-
"""
test_generator.py - Generates natural language test cases (5 positive, 5 negative, 3 boundary)
and manages Level A-E verification tracking for skills.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class TestCase:
    id: str
    category: str  # "positive", "negative", "boundary"
    prompt: str
    expected_trigger: bool
    rationale: str
    verified_status: str = "unverified"  # "pass", "fail", "unverified"


@dataclass
class VerificationMatrix:
    skill_name: str
    level_a_format: str = "unverified"      # Static format & schema
    level_b_discovery: str = "unverified"   # Discovered in skill roots
    level_c_explicit: str = "unverified"    # Direct tool/script invocation
    level_d_nl_trigger: str = "unverified"  # Natural language triggering
    level_e_e2e_exec: str = "unverified"    # Full task completion
    notes: dict[str, str] = field(default_factory=dict)


def generate_test_cases(skill_name: str, description: str, body: str = "") -> list[TestCase]:
    """
    Generates 5 positive, 5 negative, and 3 boundary test prompts
    without leaking the skill name in trigger prompts.
    """
    cases: list[TestCase] = []
    clean_name = skill_name.replace("-", " ")

    # Extract domain nouns and verbs
    desc_text = f"{description} {body[:500]}"
    is_chinese = bool(re.search(r"[\u4e00-\u9fff]", desc_text))

    if is_chinese:
        # Extract Chinese domain keywords
        keywords = re.findall(r"[\u4e00-\u9fff]{2,4}", description)
        kw1 = keywords[0] if len(keywords) > 0 else "自动化"
        kw2 = keywords[1] if len(keywords) > 1 else "规范处理"
        kw3 = keywords[2] if len(keywords) > 2 else "工作流"

        # 5 Positive cases (Natural language, NO skill name)
        positive_prompts = [
            (f"请帮我针对这个项目执行一次深度的 {kw1}，排查其中的潜在问题。", f"核心功能正例：涉及 {kw1}"),
            (f"我刚做完修改，需要自动完成 {kw2} 并给出优化建议。", f"工作流正例：调用 {kw2}"),
            (f"检查当前目录下的相关配置与资源，确保符合最新的 {kw1} 标准。", f"标准检查正例：验证与合规"),
            (f"帮我梳理并执行 {kw3}，处理所有的边界和异常情况。", f"端到端执行正例：完整流程"),
            (f"按照最佳工程实践，审核并优化我们现有的 {kw1} 方案。", f"工程优化正例：方案与质量提升"),
        ]
        for i, (p, r) in enumerate(positive_prompts, 1):
            cases.append(TestCase(id=f"POS-00{i}", category="positive", prompt=p, expected_trigger=True, rationale=r))

        # 5 Negative cases (Unrelated tasks, should NOT trigger this skill)
        negative_prompts = [
            ("帮我写一个快速排序算法的 Python 实现并测试性能。", "纯算法编程任务，应由标准编程或代码能力处理"),
            ("把这段中文产品介绍翻译成地道的英文商务邮件。", "语言翻译与文案任务，与本技能领域无关"),
            ("分析一下当前系统的内存占用，看看哪个进程占了最高 CPU。", "系统运维与性能分析任务，不应触发该领域技能"),
            ("帮我画一张赛博朋克风格的猫咪头像，要有霓虹灯光效。", "绘图/生图任务，应由 imagegen 处理"),
            ("请帮我修改网页的 CSS 样式，让导航栏在滚动时悬浮固定。", "前端样式微调任务，不应误调用本技能"),
        ]
        for i, (p, r) in enumerate(negative_prompts, 1):
            cases.append(TestCase(id=f"NEG-00{i}", category="negative", prompt=p, expected_trigger=False, rationale=r))

        # 3 Boundary cases (Ambiguous scope)
        boundary_prompts = [
            (f"这个文件里提到了 {kw1}，但只是纯文本笔记，不需要做任何实质处理。", "仅包含关键词但无执行诉求的边界用例"),
            (f"我想了解一下行业里目前有哪些工具支持 {kw1} 的最新规范？", "泛行业调研咨询，应优先普通回答而非立即执行复杂动作"),
            (f"检查这行代码有没有语法错误：print('hello world')", "极简代码查看，不应过度触发重型专项技能流程"),
        ]
        for i, (p, r) in enumerate(boundary_prompts, 1):
            cases.append(TestCase(id=f"BND-00{i}", category="boundary", prompt=p, expected_trigger=False, rationale=r))

    else:
        # English prompts
        positive_prompts = [
            (f"Please help me inspect and optimize the current {clean_name} setup.", "Core domain positive task"),
            (f"Review these files to make sure they follow the proper {clean_name} standards.", "Compliance and validation task"),
            (f"Run an automated workflow for our new {clean_name} assets.", "Automated pipeline task"),
            (f"Can you diagnose why our recent changes broke the {clean_name} configuration?", "Troubleshooting task"),
            (f"Generate the full {clean_name} test and execution suite for this project.", "Generation task"),
        ]
        for i, (p, r) in enumerate(positive_prompts, 1):
            cases.append(TestCase(id=f"POS-00{i}", category="positive", prompt=p, expected_trigger=True, rationale=r))

        negative_prompts = [
            ("Implement a simple binary search tree in TypeScript.", "Generic programming task, should not trigger"),
            ("Translate this user feedback email into fluent French.", "Translation task, out of scope"),
            ("Why is my Docker container running out of disk space?", "Infrastructure debugging, out of scope"),
            ("Generate a photorealistic illustration of a sunset over mountains.", "Image generation, out of scope"),
            ("Adjust the button hover colors in this CSS file to match the theme.", "Frontend styling, out of scope"),
        ]
        for i, (p, r) in enumerate(negative_prompts, 1):
            cases.append(TestCase(id=f"NEG-00{i}", category="negative", prompt=p, expected_trigger=False, rationale=r))

        boundary_prompts = [
            (f"I am writing a blog post discussing the history of {clean_name}.", "Educational inquiry without execution intent"),
            (f"Compare whether {clean_name} or an alternative tool is better for startups.", "Product comparison question"),
            ("Just check if there is a typo in this single comment line.", "Trivial text edit, should avoid heavy skill overhead"),
        ]
        for i, (p, r) in enumerate(boundary_prompts, 1):
            cases.append(TestCase(id=f"BND-00{i}", category="boundary", prompt=p, expected_trigger=False, rationale=r))

    return cases


def save_test_suite(skill_dir: Path, cases: list[TestCase], matrix: VerificationMatrix | None = None) -> Path:
    test_dir = skill_dir / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)

    cases_file = test_dir / "test_cases.json"
    data = {
        "skill_name": skill_dir.name,
        "generated_cases_count": len(cases),
        "cases": [asdict(c) for c in cases],
        "verification_matrix": asdict(matrix) if matrix else None
    }
    cases_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return cases_file
