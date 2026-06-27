# 📋 开源工具 `npx skills` 迁移可行性评估报告

报告生成时间：2026-06-21 17:25:00
测试环境：Windows 10 / Node v25.2.1 / npm & npx v11.6.2

---

## 一、 当前环境与 Junction 状态检查

1. **环境可用性**：
   - Node.js：`v25.2.1` (正常)
   - npm & npx：`11.6.2` (正常)
2. **Junction 联接状态**：
   - `C:\Users\win10\.agents\skills` -> **Junction 目录联接**，指向 `D:\AI-Skills\skills` (正常)
   - `C:\Users\win10\.claude\skills` -> **Junction 目录联接**，指向 `D:\AI-Skills\skills` (正常)
   - 统一技能总库子目录数：**80 个** (正常)
3. **备份目录状态**：
   - Codex/agents 备份：存在 `C:\Users\win10\.agents\skills.backup-20260621-115020` (正常)
   - Claude 备份：存在 `C:\Users\win10\.claude\skills.backup-20260621-115439` (正常)

---

## 二、 `npx skills` 核心能力分析

经对 `npx skills --help` 等命令进行只读探测，该工具核心能力总结如下：

* **本地路径添加**：**不支持**。其设计主要面向网络源（如 GitHub 仓库或 https 链接）。
* **指定特定 Agent**：**完全支持**。提供 `--agent <agents>` (如 `claude-code`, `cursor`, `codex`) 选项。
* **链接方式选择 (symlink / copy)**：**完全支持**。默认采用 `symlink` (符号链接)，并提供 `--copy` 强制采用物理拷贝。
* **全局安装**：**完全支持**。带 `-g, --global` 会直接在用户级 Agent 目录中安装。
* **检查更新与升级**：**完全支持**。提供 `skills update` 命令行工具。
* **卸载与回滚**：提供 `skills remove` 选项进行卸载，但缺乏本地化一键回滚到历史指定版本的机制。

---

## 三、 与当前手动 Junction 方案的关系判定

1. **是否能直接接管本地 `D:\AI-Skills\skills`**：**不能**。`npx skills` 仅能从远程 GitHub 源拉取文件，无法把本地现成的非 Git 目录设为其统一分发主库。
2. **是否会覆盖或破坏 Junction**：**会破坏**。`npx skills` 在写入或升级技能时，底层的 Node `fs` API 会因为目标端存在已有的目录联接而冲突报错，或者会强行移除联接指针，导致 D 盘总库与 AI 客户端脱链。
3. **是否会把 Skill 复制到新目录**：**会**。它有自己默认的全局缓存目录（如用户文件夹下的 `.skills` 缓存区），不能把 `D:\AI-Skills\skills` 设为其默认缓存仓库。
4. **是否会和当前 Claude / Codex 识别状态冲突**：**会**。一旦由它接管，它会以自己拉取的技能覆盖现有目录，您微调过的 `00-skill-router` 及其规则将会直接被抹除或失效。
5. **回滚方式**：若切换失败，只需删除 `~/.agents/skills` 和 `~/.claude/skills` 下被强占的链接，并在 CMD 下重新运行 `mklink /J` 指向 D 盘即可。

---

## 四、 三套迁移方案深度比对

### 方案 1：不切换，只保留当前 Junction，npx skills 只作为新增 Skill 的下载工具 (强烈推荐 ⭐)
* **业务逻辑**：继续保持 `D:\AI-Skills\skills` 作为本地唯一的“单一事实源”，Junction 映射结构完全不作任何修改。当需要引入网上的开源技能时，使用 `npx skills` 将其下载到临时目录，经过筛选和安全核对后，手动复制到 `D:\AI-Skills\skills` 下。
* **优点**：
  - 极度稳健，零风险，100% 保持本地修改的实时生效性。
  - **00-skill-router 无任何损坏风险**，Claude 与 Codex 状态最安全。
* **缺点**：引入远程新技能时需要手动挑选并复制。
* **风险**：无风险。
* **是否推荐**：**强烈推荐**。
* **回滚方式**：无需回滚。

### 方案 2：半切换，保留 D:\AI-Skills\skills 和 Junction，同时使用 npx skills 往这个总库添加新 Skill (不推荐 ❌)
* **业务逻辑**：保留 Junction，同时使用 `npx skills add -g` 往挂载目录直接添加新技能。
* **优点**：能直接使用命令行安装。
* **缺点/风险**：`npx skills` 底层的写入机制会与 Junction 产生文件锁和路径冲突，极易引发写入失败并直接物理破坏原有的 Junction 联接，导致整个技能链路断裂。
* **是否推荐**：**不推荐**。

### 方案 3：完全切换，由 npx skills 接管 Claude / Codex 的 Skill 安装与 symlink 管理 (不建议执行 ⚠️)
* **业务逻辑**：废除 D 盘总库和所有的手动 Junction，完全由 `npx skills` 自动建立 symlink 并管理。为使用自定义技能，您必须把 `D:\AI-Skills` 托管到 GitHub 私有仓库中。
* **优点**：纯官方工具链管理，跨机器同步方便。
* **缺点**：
  - **本地开发循环极其低效**：每次微调本地代码（如修改 `00-skill-router` 规则），必须执行 `git commit + push` 并运行命令重新升级，无法实现“本地改完、AI 即时读取生效”的秒级反馈。
  - 存在隐私泄露风险（部分技能可能包含本地数据库路径或私人 API 细节）。
* **是否推荐**：**不推荐**。

---

## 五、 推荐的下一步执行计划

1. **保持现状**：坚决**不改动任何 Junction**，不使用 `npx skills` 覆盖已有的全局挂载目录。
2. **辅助下载**：如果未来有下载开源技能的需求，在独立的临时目录（如 `D:\AI-Skills\needs-review`）中运行 `npx skills use <package>` 提取所需的 `SKILL.md`，确认无安全及冲突风险后，再手动合入您的 `D:\AI-Skills\skills` 唯一事实源。
