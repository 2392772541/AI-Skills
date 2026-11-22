# AI Skills 治理系统使用说明

## 2026-09-12 技能目录状态

- 治理注册表共 213 条记录、172 个唯一技能名、35 个重复技能名；审计为 `critical=0`、`warning=90`。
- 个人技能台当前展示 201 条活跃记录、168 个唯一技能名，全部已有大白话说明：`pending=0`、`stale=0`。
- 新增整理 18 个 ChatCut 技能，以及 `manim-composer`、`manimce-best-practices`、`manimgl-best-practices`；并按视频策划、动效组件、检查导出、配音配乐、转写和发布等实际任务细分分类。
- 路由回归为 `22/23`；唯一失败仍是历史上缺失的 `seagull-reverse`，不是本次说明更新引入。
- `warning` 主要来自已知的目录名与声明名不一致、重复副本、超大说明和缺失本地引用；没有阻断技能加载的结构错误。

## Git 迁移与同步（2026-09-11）

现有编辑目录和工具入口继续使用。新增可迁移发布工作区 `D:\AI-Skills-Portable`，对应私有仓库 https://github.com/2392772541/AI-Skills 。它保存共享库、Codex/Cursor 独立版本和治理工具，不用 TeamAI 覆盖当前目录联接。

- 同步最新技能到 Git：`python "D:\AI-Skills\scripts\skillctl.py" git-sync`
- 校验已生成快照：`python "D:\AI-Skills\scripts\skillctl.py" git-verify`
- 也可运行根目录的 `sync-skills-git.ps1`。
- 换电脑：按发布仓库 README 执行 verify → restore → install；安装前完整检查冲突，已有不同内容会停止。
- 密钥、依赖安装目录和生成产物不上传，插件及系统 Skills 由原生安装恢复。

源目录映射保存在本机 `registry/portable-local.json` 与发布工作区 `.local/source.json`，不提交。同步为显式操作，不自动上传每次编辑。

## 已搭建能力

- 扫描 `D:\AI-Skills\skills` 和 `C:\Users\win10\.codex\skills`
- 生成机器可读注册表 `registry\skills.json`
- 自动生成索引 `skill-index.generated.md`
- 检查 frontmatter、名称冲突、备份目录、超大 Skill 和缺失引用
- 比较两个 Skill 的目录和 `SKILL.md` 差异
- 根据自然语言任务推荐 Skill
- 运行路由回归测试
- 将审核后的候选 Skill 安全晋级，默认 dry-run 且禁止覆盖同名目标
- 为 `00-skill-router` 生成能力目录

## 常用命令

### 全量验证

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\verify-governance.ps1"
```

### 刷新注册表

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" build
```

### 审计

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" audit
```

### 查询应该使用哪个 Skill

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" route "把课程视频整理成学习笔记"
```

### 比较两个同名 Skill

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" compare "C:\路径\skill-a" "D:\路径\skill-a" --output "D:\AI-Skills\_reports\compare.md"
```

### 安全晋级候选 Skill

默认只预演：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" promote "D:\AI-Skills\needs-review\candidate"
```

确认后真正复制：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\AI-Skills\skillctl.ps1" promote "D:\AI-Skills\needs-review\candidate" --apply
```

## 状态说明

审计返回 `critical=0` 表示没有阻止系统运行的结构错误。当前报告中的 warning 主要来自原有双目录重复、backup 目录和超大 `SKILL.md`，治理系统会报告它们，但不会擅自删除或覆盖用户现有文件。
## 自动运行（已安装）

本机通过两个 Windows 计划任务自动维护，不需要每次手工执行：`AI-Skills Governance Watcher` 负责监控和验证，`AI-Skills Governance Healthcheck` 负责定时检查并拉起前者。

- 每次登录 Windows 后自动启动，适用于重启后的正常使用。
- 后台启动，不弹 PowerShell 窗口。
- 启动后自动执行一次完整验证。
- 监控两个 Skill 目录以及治理脚本、测试和覆盖配置；文件修改停止 8 秒后自动验证并刷新注册表。
- 主任务保留 Windows 自带的失败重启设置；另有独立健康检查任务每 2 分钟检查一次，发现停止、崩溃或超过 5 分钟没有心跳就重新启动。
- 在电池供电状态下也会启动并持续运行。

查看运行状态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\AI-Skills\status-governance-autostart.ps1"
```

重新安装或修复自动启动：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\AI-Skills\install-governance-autostart.ps1"
```

卸载自动启动（不会删除任何 Skill）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\AI-Skills\uninstall-governance-autostart.ps1"
```

运行日志：`D:\AI-Skills\_logs\governance-watcher.log`

状态文件：`D:\AI-Skills\_logs\governance-status.json`

## 技能管家网页

本机控制台地址：

http://127.0.0.1:8765

桌面快捷方式：技能管家.url。

网页提供：总览、Skill 搜索、自然语言任务路由、重复项与审计问题查看、注册表刷新和完整治理自检。网页只监听 127.0.0.1，只能从本机访问。计划任务 AI-Skills Web Console 在登录后自动启动；AI-Skills Governance Healthcheck 每 2 分钟检查并在异常时拉起。
