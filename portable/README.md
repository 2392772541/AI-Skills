# 迁移工具边界

`skills_portable.py` 只使用 Python 标准库，不执行下载的技能脚本。

- export：读取现有共享库和各工具专用目录，保存独立 Git 快照；不修改活动技能。
- verify：检查清单、SHA256、额外文件与常见凭据模式。
- restore：只写入尚不存在的新目录；默认逐字节恢复，加 --relocate 才替换已登记路径。
- publish：重新导出（提供 --config 时）、验证、检查仓库私有、提交并普通推送；不强推。

新机器首先安装 Python、Git 及各 AI 工具。Codex 的 .system 与插件仍由原生管理器安装；不会从旧机覆盖新版系统技能。

密钥、认证、运行缓存、生成的成片和项目产物不入快照。部分 Skill 还需要本机 CLI、FFmpeg、Blender 或 Node/Python 依赖；迁移文件不代表这些软件也已安装。

目录联接在导出时展开为真实文件；同名但不同工具的版本独立保存，不自动覆盖或合并。当前电脑继续使用原有路径。本工具不在活动根调用 TeamAI pull，也不注入 MCP 或 Hooks。

这是在 TeamAI 源码研究后选择的兼容迁移层，不是修改版 TeamAI CLI。共享 skills/ 结构可供后续 TeamAI 试点使用，工具专属 profiles/ 必须通过本恢复工具处理。
