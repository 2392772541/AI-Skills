---
name: skill-product-manager
description: "管理本机 Skill：查找、评估、创建、升级、合并、归档或治理技能；用户说技能管家时使用。"
---

# 技能管家

先查本机现有能力，再决定复用、升级或新建。只执行具体业务任务时，直接使用对应技能。默认库为 `D:\AI-Skills`，可由 `AI_SKILLS_HOME` 指定。

## 决策与执行

1. 明确产物、复用场景和完成边界；先检查 `registry/skills.json`。技能新增、修改、删除或注册表已过时时运行 `python "D:\AI-Skills\scripts\skillctl.py" build`；盘点或治理时再运行 `audit`。普通推荐无需每次重建全库。
2. 比较已有技能的触发条件、资源和版本。按 [决策政策](references/decision-policy.md) 选择 NO_SKILL / REUSE / UPGRADE / EXTERNAL / COMPOSE / CREATE，不能仅凭目录名判断。
3. 修改在扫描根目录外的候选目录进行；复用已安装能力。只有本机存在能力缺口且需要引入外部实现时，比较可得的相关候选；不足三个时说明限制，不为数量引入无关候选。
4. 创建时使用当前可用的 `skill-creator`；升级只改影响目标的文件。description 简短说明做什么、何时用；正文保留关键约束和按需入口，把细节放 references/scripts。避免全局 MUST USE、重复流程和固定停在建议阶段的要求。
5. 按 [验证与边界](references/quality-gates.md) 验证本次改动。结果通过后，在用户已授权的范围内备份、检查 diff 并应用；已有授权不因“候选”或“晋级”再询问。正式技能不得无备份覆盖，备份不放在活动扫描根目录。
6. 回读实际文件；改到发现或启用配置时核对实际加载结果。继续完成用户要求，最后给出结果、差异、验证限制和回滚入口。

## 按需参考

- 缺少会影响设计的关键信息：[采访指南](references/interview-guide.md)。事实先查本机，可逆默认值直接采用。
- 新建、外部引入或大幅重构：[需求模板](references/requirement-template.md)、[决策记录](references/decision-record-template.md)、[候选评分](references/evaluation-rubric.md)。评分仅供比较，不代替行为验证。
- 只需路由：`python "D:\AI-Skills\scripts\skillctl.py" route "用户任务"`。
- 路由回归：`python "D:\AI-Skills\scripts\skillctl.py" test`。
- 新名称外部候选：先 `skillctl.py promote "候选目录"` dry-run；确认无冲突且已授权后加 `--apply`。已有技能升级采用逐文件备份和 diff。

报告按任务复杂度展开，不要求每次输出完整模板。至少说明决策与原因、实际结果、验证、未解决的问题和回滚路径。结构检查、关键词路由、模型行为 eval 分别报告，未执行不得写通过。
