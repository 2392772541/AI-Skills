---
name: skill-doctor
description: "Codex Agent Skills 审核、优化、测试与验收系统。用于新建、导入或修改 Skill 后的交付前质量门禁，进行格式规范校验、触发描述优化、正文精炼、技能冲突排查与五级验证（A-E Matrix）。当用户提出审核技能、优化技能、检查技能规范、测试技能触发、修复技能或验收新技能时自动调用。"
metadata:
  short-description: Codex Skill 审核优化与质量门禁系统
---

# Skill Doctor (技能医生)

Skill Doctor 是 Codex 与 Agent Skills 技能生态的专业审核优化系统。针对新建、导入、修改或治理的 Skill，在最终交付前自动完成格式规范校验、触发质量评估优化、正文精炼、技能冲突检测、测试用例生成与五级验证闭环。

## 核心验证层级 (A-E Verification Matrix)

系统严格区分以下五个层级，绝不以低层级通过冒充高层级结果：

1. **Level A (静态规范校验)**：SKILL.md 存在性、YAML Frontmatter 语法、必填项与命名规范、禁用字符（如 `<` `>`）及本地链接完整性。
2. **Level B (技能发现识别)**：确认技能目录位于 Codex 或 AI-Skills 活跃加载目录，能够被系统注册表正常识别。
3. **Level C (显式脚本调用)**：校验 `scripts/` 下的代码语法无报错，提供可运行的执行测试。
4. **Level D (自然语言触发)**：评估触发描述（description）质量，确保包含明确问题定义、触发时机（Use when.../用于...）与自然用户表达，兼顾防误触。
5. **Level E (端到端真实执行)**：通过实际业务场景交付进行真实验证。未执行时严格标记为“未验证”。

## 执行工作流

### 步骤 1：执行全项审核 (Audit)

对目标技能目录运行确定性检测：

```bash
python "D:/AI-Skills/skills/skill-doctor/scripts/doctor.py" audit "<skill_path>"
```

### 步骤 2：自动安全修复 (Safe Auto-Fix)

针对明确、安全、可回滚的问题（如非法尖括号字符、命名格式、目录缺漏、明显描述弱点），执行自动安全修复。每次修改前系统会自动在 `D:/AI-Skills/_backups/doctor/<skill_name>/` 创建快照：

```bash
python "D:/AI-Skills/skills/skill-doctor/scripts/doctor.py" fix "<skill_path>"
```

若需回滚至上一版本：

```bash
python "D:/AI-Skills/skills/skill-doctor/scripts/doctor.py" rollback "<skill_path>"
```

### 步骤 3：冲突与重叠排查 (Conflict Check)

比对全库已有技能索引（`registry/skills.json`），重点排查：
- 同名冲突（重名遮蔽）
- 内容哈希完全重复
- 触发描述高相似度重叠（重合度 > 40% 或共享 5 个以上专属业务关键词）

### 步骤 4：生成与执行测试用例 (Test Suite)

自动为目标技能生成标准测试集（存放在目标技能 `tests/test_cases.json`）：
- 5 条正向自然语言用例（应触发，不直接泄漏技能名）
- 5 条反向测试用例（通用编程、生图、排障等，不应误触发）
- 3 条边界与歧义用例（仅提及概念但无操作意图）

查看测试集与验证矩阵：
```bash
python "D:/AI-Skills/skills/skill-doctor/scripts/doctor.py" test "<skill_path>"
```

### 步骤 5：最终验收与交付门禁

- 若存在 Level A 阻断性缺陷（Exit code 2），严禁标记为已验收，必须修复。
- 输出结构化审核报告，指导用户或模型完成最终确认。

## 异常与失败处理

1. **SKILL.md 读取或解析失败**：报告阻断性错误，建议重建 Frontmatter。
2. **脚本语法错误**：标明具体出错文件与行号，阻止自动化晋级。
3. **出现不可逆改动**：立即执行 `doctor.py rollback` 恢复原始文件状态。
