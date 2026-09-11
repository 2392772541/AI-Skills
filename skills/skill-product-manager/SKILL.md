---
name: skill-product-manager
description: >
  作为“技能管家”管理本机 Agent Skills 的完整生命周期。用户说“技能管家”时优先使用。用户希望寻找、评估、创建、升级、合并、拆分、引入、归档或治理 Skill 时使用；用户描述一个重复工作流并询问是否值得 Skill 化时也使用。必须先检查本机注册表和已有 Skill，再决定不需要、直接复用、升级、外部引入、组合或从零创建，禁止一上来就新建重复 Skill。
---

# Skill Product Manager

把用户的真实工作流转化为低重复、可测试、可维护的 Skill 系统。高质量 Skill 不是提示词合集，而是带触发边界、强制工作流、反偷懒约束和证据化完成标准的执行规范。

## 什么时候使用

- 用户要寻找、评估、创建、升级、合并、拆分、引入或归档 Skill。
- 用户给出一个重复工作流，希望判断是否值得 Skill 化。
- 用户要求研究外部 Skill 仓库并优化本机体系。

不适用于一次性执行任务本身；如果现有执行 Skill 已经能直接完成，应路由到该 Skill，而不是继续做治理设计。

## 工作原则

1. 先解决问题，再决定是否 Skill 化。
2. 先查本机，再查外部；先复用，再升级；最后才新建。
3. 把确定性工作交给脚本，把产品判断留给模型。
4. 不直接覆盖正式 Skill；候选先进入 `incoming` 或 `needs-review`。
5. 所有升级都保留 Git diff、测试结果和回滚路径。
6. 描述负责“发现”，正文负责“执行”；不要把完整流程塞进 description，避免 Agent 只读摘要不读正文。
7. 每个流程约束都要能落到检查项、失败信号或测试；不能验证的口号不算质量门禁。
8. 主动记录 Agent 常见偷懒理由、可观察红旗和停止条件，防止提前宣布完成。

## 本机环境

默认技能库根目录为 `D:\AI-Skills`。如果环境变量 `AI_SKILLS_HOME` 存在，优先使用该路径。

使用统一入口：

```powershell
python "D:\AI-Skills\scripts\skillctl.py" build
python "D:\AI-Skills\scripts\skillctl.py" audit
python "D:\AI-Skills\scripts\skillctl.py" route "用户任务"
python "D:\AI-Skills\scripts\skillctl.py" test
```

## 标准流程

### 1. 明确需求

提取：用户真正要解决的问题、输入输出、使用频率、当前步骤、耗时环节、外部依赖和自动化边界。

只在缺少会改变架构的关键信息时问一个简短问题。其他情况采用可逆默认值继续。读取 [interview-guide.md](references/interview-guide.md) 获取采访规则。

### 2. 刷新本机注册表

```powershell
python "D:\AI-Skills\scripts\skillctl.py" build
python "D:\AI-Skills\scripts\skillctl.py" audit
```

检查已有 Skill 是否直接满足、是否存在同名或近似重复、是否有版本分叉、哪些 Skill 可以组合、目标 Skill 是否异常。不得仅凭记忆判断本机没有某个 Skill。

### 3. 做产品决策

最终只能选择：

- `NO_SKILL`：一次性任务，直接完成
- `REUSE`：直接复用现有 Skill
- `UPGRADE`：升级现有 Skill
- `EXTERNAL`：评审后引入外部 Skill
- `COMPOSE`：组合多个现有 Skill
- `CREATE`：从零创建

按照 [decision-policy.md](references/decision-policy.md) 作出决策，并使用 [evaluation-rubric.md](references/evaluation-rubric.md) 评分。设计或升级前还必须读取 [quality-gates.md](references/quality-gates.md)，明确触发、边界、流程、反偷懒、验证和 eval 覆盖。

### 4. 外部调研

只有本机不存在合适能力时才搜索外部方案。至少比较三个候选，检查来源、维护情况、工作流匹配度、脚本和网络行为、依赖、许可证以及与本机能力的重复程度。

外部候选先放入 `D:\AI-Skills\incoming`，不要直接写入正式 `skills`。

### 5. 实现

- `REUSE`：交给 `00-skill-router` 或目标执行 Skill。
- `UPGRADE`：复制到隔离分支或候选目录，修改后运行校验。
- `COMPOSE`：建立编排 Skill，只保留顺序、状态、错误处理和交接规则，不复制子 Skill 正文。
- `CREATE`：调用 `skill-creator`，使用初始化脚本创建目录。
- `EXTERNAL`：完成安全审计和评审单后进入 `needs-review`。

使用 [requirement-template.md](references/requirement-template.md) 记录需求，使用 [decision-record-template.md](references/decision-record-template.md) 记录决策。

### 6. 验证

至少完成：

1. `SKILL.md` 结构校验
2. 脚本语法或单元测试
3. 一个典型成功场景
4. 一个边界或失败场景
5. 路由回归测试
6. Git diff 检查
7. 正向触发样例：真实用户表达能路由到目标 Skill
8. 负向触发样例：相邻任务不会误触发
9. 行为 eval：Agent 在时间压力、权威压力或“先跳过测试”等诱导下仍遵守核心门禁

```powershell
python "D:\AI-Skills\scripts\skillctl.py" build
python "D:\AI-Skills\scripts\skillctl.py" audit
python "D:\AI-Skills\scripts\skillctl.py" test
```

### 7. 晋级

先执行 dry-run：

```powershell
python "D:\AI-Skills\scripts\skillctl.py" promote "候选Skill目录"
```

确认目标不存在且校验通过后才增加 `--apply`。不得默认覆盖已有正式 Skill。

## 输出格式

每次产品决策至少输出：

```text
真实问题：
使用频率：
本机候选：
重复/冲突：
最终决策：NO_SKILL / REUSE / UPGRADE / EXTERNAL / COMPOSE / CREATE
推荐结构：
测试要求：
维护成本：低 / 中 / 高
质量门禁覆盖：发现 / 边界 / 工作流 / 反偷懒 / 验证
Eval 覆盖：结构 / 路由正向 / 路由负向 / 行为
下一步：
```

## 禁止事项

- 不得只因为用户说“做个 Skill”就直接创建。
- 不得根据目录名猜测功能而不读取注册表或 `SKILL.md`。
- 不得把外部 Skill 直接安装到正式库。
- 不得覆盖同名正式 Skill。
- 不得把 backup 目录留在活动 Skill 扫描根目录。
- 不得把网页界面当作事实来源；注册表和 Git 才是事实来源。
## 完成标准

- [ ] 已刷新本机注册表并检查重复/冲突。
- [ ] 产品决策属于六种标准决策之一，且理由可追踪。
- [ ] 候选修改位于隔离目录，正式 Skill 未被无备份覆盖。
- [ ] 已运行结构、典型成功、失败/边界和路由回归测试。
- [ ] 已报告 critical、warning 和行为质量缺口，未把其中一个冒充全部清零。
- [ ] 已提供 diff、测试证据、晋级方式和回滚路径。

