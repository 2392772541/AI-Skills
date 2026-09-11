# 我的可迁移 Skills 仓库

现有电脑照常使用；Git 保存可验证、可恢复的技能快照。共享库与 Codex/Cursor 的同名差异独立保存，不自动合并。

## 当前电脑

照常在原目录编辑技能。要把最新内容同步到这个私有 GitHub 仓库：

```powershell
python "D:\AI-Skills\scripts\skillctl.py" git-sync
```

校验当前已生成的 Git 快照（不上传）：

```powershell
python "D:\AI-Skills\scripts\skillctl.py" git-verify
```

本机发布工作区为 `D:\AI-Skills-Portable`，源目录配置在其 `.local/source.json`，不提交到 Git。同步为显式执行，不会自动上传正在编辑的内容。现有 watcher 继续做本机审计与路由刷新。

## 换电脑恢复

先安装 Git、Python 和需要使用的 AI 工具，并登录有权限读取本私有仓库的 GitHub 账号。发布更新还需要 GitHub CLI（gh）登录。

```powershell
git clone https://github.com/2392772541/AI-Skills.git D:\AI-Skills-Portable
cd D:\AI-Skills-Portable
python portable\skills_portable.py verify
python portable\skills_portable.py restore --target D:\AI-Skills-Restored --relocate
python portable\skills_portable.py install --bundle D:\AI-Skills-Restored --user-root "$env:USERPROFILE"
```

`D:\AI-Skills-Restored` 必须尚不存在。restore 先在新目录恢复并核对全部哈希，再交付。`--relocate` 将已登记的旧技能路径替换为新路径；原始 Git 文件保持原样。

install 预检所有目标：同内容跳过，不同内容或目录联接立即停止，且在预检完成前不写文件。不会覆盖已有技能，也不触碰账号、MCP、Hooks 或系统配置。请保留恢复目录，技能中登记的脚本引用和治理工具会使用它。

这不是一键安装所有外部软件：依赖 FFmpeg、Blender、Node、Python 包或授权账号的技能，需要在新电脑安装依赖和重新登录。`portable/manifest.json` 记录文件及重定位映射；Codex 自带 .system 和插件通过原生安装恢复。

恢复后如需让新机器成为发布源，把 `portable/source.example.json` 复制为 `.local/source.json` 并填写新库及工具目录，然后运行：

```powershell
python portable\skills_portable.py publish --config .local\source.json
```

发布会确认远端仍为私有仓库；更新不使用强推，远端发生分叉时停止，由人合并。

## 仓库结构

- `skills/`：共享技能，兼容常见 Git 技能仓库布局。
- `profiles/codex/skills/`：Codex 本地技能及其独立版本。
- `profiles/cursor/skills/`：Cursor 本地技能及其独立版本。
- `governance/`：现有注册表生成、审计、路由测试和网页代码。
- `portable/`：导出、校验、恢复和安装工具，以及哈希清单。
- 原有历史目录仍保留，但不属于 portable manifest，也不会自动部署。

## 安全与回退

新同步只在发布工作区修改副本。当前电脑的技能、原有 Junction 与 MCP 均不由 TeamAI 接管。

生成的项目、成片、缓存、依赖安装目录、常见凭据文件不入快照。凭据扫描是常见模式检查，不是所有秘密的数学保证；新增内容仍应审核。少量第三方公开浏览器/遥测标识按完整文件哈希记录在 reviewed-public-identifiers.json，内容变化会重新触发检查。

需要撤销当前电脑的新入口，只需停止使用 git-sync；既有技能不依赖它。本次 `skillctl.py` 的原文件和改造前哈希清单备份在 `D:\AI-Skills\_backups\git-portable-20260911`。不删除联接目标、不重置原工作区，也不强推回退远端。

## 验证

```powershell
python -m unittest discover -s portable -p test_portable.py -v
python portable\skills_portable.py verify
```

测试覆盖独立版本恢复、重复安装、冲突零写入、已有目标保护、哈希篡改、路径穿越、凭据拦截和源目录缺失。具体交付验收见 portable/VALIDATION.md。
