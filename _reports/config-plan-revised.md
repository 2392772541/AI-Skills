# 📋 AI 技能库分阶段配置与回滚执行计划 (修订版)

报告生成时间：2026-06-21 11:41:00
统一技能总库路径：`D:\AI-Skills\skills` (当前共包含 80 个技能目录)

---

## 一、 重新评估三种配置方案

| 方案 | 操作描述 | 优点 | 缺点 | 评估结果与建议 |
| :--- | :--- | :--- | :--- | :--- |
| **方案 A**<br>复制技能 | 将 `D:\AI-Skills\skills` 中的 80 个技能全部手动复制到各个 AI 工具的默认 skills 目录中。 | 1. 兼容性最好，不依赖文件系统链接。<br>2. 互不干扰，故障隔离度高。 | 1. 造成多份副本，无法实现“统一管理”。<br>2. 技能更新繁琐，极易产生版本偏差。<br>3. 占用多倍磁盘空间。 | **【作为后备方案】**<br>仅当方案 B 出现不可解决的工具兼容性故障时，才考虑采用。 |
| **方案 B**<br>目录联接 (`mklink /J`) | 将各个 AI 工具的默认 skills 目录通过目录联接 (Directory Junction) 指向 `D:\AI-Skills\skills`。 | 1. 实现**单一事实来源 (Single Source of Truth)**。<br>2. **不修改任何 AI 配置文件**，规避软件损坏风险。<br>3. Windows 下创建 Junction **不需要管理员权限**。<br>4. 回滚极快，删除联接文件绝对不伤及 D 盘源文件。 | 1. 对操作系统的链接解析机制有极低概率的兼容性依赖（某些极严格沙箱环境可能会限制访问链接）。 | **【强烈推荐执行】**<br>此方案最符合“保守、安全、可回滚”的开发规范，是目前首选。 |
| **方案 C**<br>修改配置文件 (`config.toml`) | 修改 Codex 的 `config.toml` 配置文件，在其中指定自定义技能目录 `skills_dir = "D:\AI-Skills\skills"`。 | 1. 原生配置管理，不涉及文件系统链接。 | 1. **官方文档未确认支持**：本机现有配置或官方标准文档中均未明确证实可以通过 `config.toml` 指定 `skills_dir`。<br>2. 强行写入未支持参数可能导致 Codex 启动解析异常、崩溃甚至配置损坏。 | **【不建议执行，予以否决】**<br>不将任何不确定支持的配置写入核心配置文件，本阶段绝不修改任何配置文件。 |

---

## 二、 推荐更稳的执行顺序 (分阶段配置)

为了将风险降到最低，防止所有 AI 工具同时出现故障，我们采用灰度逐步推进的顺序：

* 🚀 **阶段 1：只配置 Codex / agents 用户级技能目录**
  * **目标目录**：`C:\Users\win10\.agents\skills`
  * **推荐方式**：先物理重命名备份原目录，再使用 CMD 的 `mklink /J` 建立指向 `D:\AI-Skills\skills` 的目录联接。
* 🧪 **阶段 2：测试 Codex 技能识别与决策路由能力**
  * 在 Codex 中测试是否能识别 `00-skill-router`、`remotion`、`imagegen` 等核心技能，并在会话中触发决策路由以评估链接目录的穿透效率。
* 🔄 **阶段 3：Codex 测试成功后，再考虑 Claude Code**
  * **目标目录**：`C:\Users\win10\.claude\skills`
  * 验证 Codex 表现无误后，以同样方式桥接 Claude。
* ⚙️ **阶段 4：Claude 测试成功后，再配置 Cursor / Hermes / Qoder**
  * 最终将技能库分步同步至 Cursor 专有目录及其他轻量工具，确保全生态打通。

---

## 三、 阶段 1：Codex 技能重定向具体执行计划 (只做方案，绝不执行)

此阶段操作仅针对：`C:\Users\win10\.agents\skills`

### 1. 执行前只读检查命令
在 PowerShell 中运行以下命令以确认环境安全：
```powershell
# 1. 检查 Codex 默认 skills 目录是否存在
Test-Path "C:\Users\win10\.agents\skills"

# 2. 检查 D 盘统一技能库是否存在，且下一级目录数量是否为 80 (确认 00-skill-router 已在内)
(Get-ChildItem -Path "D:\AI-Skills\skills" -Directory).Count
```

### 2. 安全备份命令 (物理重命名)
若上一步确认 `C:\Users\win10\.agents\skills` 存在，在 PowerShell 中执行以下命令进行备份：
* **动态时间戳命令**：
  ```powershell
  $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
  Rename-Item -Path "C:\Users\win10\.agents\skills" -NewName "skills.backup-$timestamp"
  ```
* **静态示例命令 (基于当前时间 2026-06-21 11:40:49)**：
  ```powershell
  Rename-Item -Path "C:\Users\win10\.agents\skills" -NewName "skills.backup-20260621-114049"
  ```

### 3. 创建目录联接命令
备份完成后，打开 **普通的命令提示符 (CMD)** 执行以下命令（**无需管理员权限**）：
```cmd
mklink /J "C:\Users\win10\.agents\skills" "D:\AI-Skills\skills"
```

### 4. 阶段 1 验证命令
在 PowerShell 中执行以下命令，验证目录联接重定向是否成功，以及是否能正常读取核心技能：
```powershell
# 1. 验证联接目录下的技能子目录数量是否为 80
(Get-ChildItem -Path "C:\Users\win10\.agents\skills" -Directory).Count

# 2. 验证三个核心技能的 SKILL.md 是否在位且能读取
Test-Path "C:\Users\win10\.agents\skills\00-skill-router\SKILL.md"
Test-Path "C:\Users\win10\.agents\skills\remotion\SKILL.md"
Test-Path "C:\Users\win10\.agents\skills\imagegen\SKILL.md"
```

### 5. 阶段 1 应急回滚命令
如若在验证或后续使用中遇到任何问题，在 PowerShell 中执行以下两步即可 100% 无损回滚：
```powershell
# 1. 强制删除目录联接 (仅删除联接指针，不会伤害 D:\AI-Skills\skills 源文件)
Remove-Item -Path "C:\Users\win10\.agents\skills" -Force

# 2. 恢复备份的原始技能目录 (请根据实际备份的时间戳目录名进行替换，此处以 20260621-114049 为例)
Rename-Item -Path "C:\Users\win10\.agents\skills.backup-20260621-114049" -NewName "skills"
```

---

## 四、 阶段 2：Codex 智能路由测试提示词
配置成功后，在 Codex 客户端新建会话，输入以下提示词来测试 `00-skill-router` 技能的载入和执行能力：

```text
我刚刚把统一技能库挂载到了你这里。请调用 00-skill-router 技能，帮我分析这个任务：
“我要用 Remotion 复刻一张科技感农业海报，做成 9:16 动态视频。”
请严格按照决策器的规定格式输出推荐结果。
```

---

## 五、 后续 Claude / Cursor / Hermes / Qoder 暂缓配置原因

1. **避免多点并发崩溃**：若一次性把 5 个工具全部做目录链接映射，一旦操作系统或特定杀毒软件对 Junction 产生权限策略拦截，会导致所有 AI 工具同时不可用，影响核心排产。
2. **需要验证链接文件可读性**：某些 Agent 工具是基于 Docker 或特殊虚拟机沙箱运行的，对 Windows 本地的目录联接（Junction）解析可能存在路径解析死循环或权限不足的问题。先在 Codex 上跑通一到两天，可确认目录联接的安全性。
3. **沉淀配置最佳实践**：不同工具（如 Cursor `skills-cursor`，Claude Code `.claude/skills`）其物理文件结构和配置加载可能略有差异，Codex 的灰度试验结果将为其余工具提供直接的避坑指南。

---

## 六、 安全合规确认

- **当前修改状态**：未修改任何配置文件，未创建软链接，未移动/复制任何技能。
- **配置意图确认**：本执行方案为**只读报告**。任何物理变更（重命名备份、`mklink` 目录联接）必须在您在会话中回复“确认方案，开始配置”后，方可开展。