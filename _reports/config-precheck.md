# 📋 AI 技能库配置前探测与备份方案预检报告

预检执行时间：2026-06-21 11:34:31

## 一、 统一技能库状态确认
- 统一技能总库根目录 `D:\AI-Skills`: ✅ 存在
- 物理技能目录 `D:\AI-Skills\skills`: ✅ 存在
- 智能决策路由 `00-skill-router` 技能: ✅ 存在
- 技能清单索引表 `D:\AI-Skills\skill-index.md`: ✅ 存在
- 报告归档目录 `D:\AI-Skills_reports`: ✅ 存在
- **正式技能总数**: **80** 个

## 二、 各 AI 工具当前技能目录探测结果
| 工具名称 | 物理技能目录路径 | 是否存在 | 技能目录数 | SKILL.md 数 |
| --- | --- | :---: | :---: | :---: |
| Claude | `~\.claude\skills` | ✅ 是 | 35 | 35 |
| agents | `~\.agents\skills` | ✅ 是 | 37 | 37 |
| Codex | `~\.codex\skills` | ✅ 是 | 18 | 16 |
| Codex.system | `~\.codex\skills\.system` | ✅ 是 | 5 | 5 |
| cc-switch | `~\.cc-switch\skills` | ✅ 是 | 52 | 52 |
| Cursor | `~\.cursor\skills-cursor` | ✅ 是 | 18 | 18 |
| Hermes | `~\.hermes\skills` | ✅ 是 | 51 | 51 |
| Qoder | `~\.qoder\skills` | ✅ 是 | 31 | 31 |

## 三、 各 AI 工具配置文件只读探测
### 📄 配置文件：Codex config.toml (✅ 存在)
- 物理路径：`~\.codex\config.toml`
```toml
NODE_REPL_NODE_MODULE_DIRS = 'C:\Users\win10\AppData\Local\OpenAI\Codex\runtimes\cua_node\a89897d3d9baa117\bin\node_modules'
NODE_REPL_NODE_PATH = 'C:\Users\win10\AppData\Local\OpenAI\Codex\runtimes\cua_node\a89897d3d9baa117\bin\node.exe'
NODE_REPL_TRUSTED_CODE_PATHS = 'C:\Users\win10\.codex'
NODE_REPL_INSTRUCTIONS_USE_CASE_BROWSER = "Control the in-app browser in conjunction with the Browser Plugin."
NODE_REPL_INSTRUCTIONS_USE_CASE_CHROME = "Control the Chrome browser in conjunction with the Chrome Plugin. Prefer this method of controlling Chrome over alternatives (such as Computer Use) unless the user explicitly mentions an alternative."
SKY_CUA_NATIVE_PIPE_DIRECTORY = '\\.\pipe\codex-computer-use-74345885-c1dd-4016-9320-8884196e2f49'
CODEX_CLI_PATH = 'C:\Users\win10\AppData\Local\OpenAI\Codex\bin\8e55c2dd143b6354\codex.exe'
[plugins."remotion@openai-curated"]
[plugins."figma@openai-curated"]
[plugins."heygen@openai-curated"]
[plugins."github@openai-curated"]
[plugins."canva@openai-curated"]
[plugins."gmail@openai-curated"]
[plugins."codex-security@openai-curated"]
[plugins."chrome@openai-bundled"]
[plugins."browser@openai-bundled"]
[projects.'e:\工程项目\codex项目合集\爱马仕agent']
```

### 📄 配置文件：Claude settings.json (✅ 存在)
- 物理路径：`~\.claude\settings.json`
```toml
(未检测到与 skills 或 path 相关的配置项)
```

### 📄 配置文件：Claude .claude.json (✅ 存在)
- 物理路径：`~\.claude.json`
```toml
"powershell-tool-env": 32,
    "custom-agents": 32,
    "agent-flag": 8,
    "subagent-fanout-nudge": 36,
      "StrReplaceBasedEditTool": 30000,
      "BashSearchTool": 20000
    "tengu_read_dedup_killswitch": false,
    "tengu_streaming_tool_execution2": true,
    "tengu_agent_list_attach": false,
      "path": "/api/event_logging/v2/batch"
    "tengu_skills_dashboard_enabled": false,
    "tengu_tool_pear": false,
      "toolCallsBetweenUpdates": 10
    "tengu_malformed_tool_use_clean_retry": false,
    "claude_code_skills_dashboard_enabled_cli": false,
    "tengu_plugin_official_mkt_git_fallback": true,
      "plugins": [
        "pr-review-toolkit",
        "skill-creator",
        "plugin-dev",
        "agent-sdk-dev",
        "memdir_relevance",
        "agent_classifier",
    "tengu_fg_left_arrow_agents": true,
    "tengu-fable-off-switch": {
    "tengu_mcp_subagent_prompt": false,
    "tengu_gha_plugin_code_review": false,
    "tengu_tool_search_unsupported_models": [
      "guideTemplate": "# Welcome to [Team Name]\n\n## How We Use Claude\n\nBased on [name]'s usage over the last [N] days:\n\nWork Type Breakdown:\n  [Category 1]  [ascii bar]  [N]%\n  [Category 2]  [ascii bar]  [N]%\n  [Category 3]  [ascii bar]  [N]%\n  ...\n\nTop Skills & Commands:\n  [/command]  [ascii bar]  [N]x/month\n  ...\n\nTop MCP Servers:\n  [Server]  [ascii bar]  [N] calls\n  ...\n\n## Your Setup Checklist\n\n### Codebases\n- [ ] [repo-name] — [repo url]\n...\n\n### MCP Servers to Activate\n- [ ] [Server] — [what it's for]. [How to get access]\n...\n\n### Skills to Know About\n- [/command] — [what it does, when the team uses it]\n...\n\n## Team Tips\n\n_TODO_\n\n## Get Started\n\n_TODO_\n\n<!-- INSTRUCTION FOR CLAUDE: A new teammate just pasted this guide for how the\nteam uses Claude Code. You're their onboarding buddy — warm, conversational,\nnot lecture-y.\n\nOpen with a warm welcome — include the team name from the title. Then: \"Your\nteammate uses Claude Code for [list all the work types]. Let's get you started.\"\n\nCheck what's already in place against everything under Setup Checklist\n(including skills), using markdown checkboxes — [x] done, [ ] not yet. Lead\nwith what they already have. One sentence per item, all in one message.\n\nTell them you'll help with setup, cover the actionable team tips, then the\nstarter task (if there is one). Offer to start with the first unchecked item,\nget their go-ahead, then work through the rest one by one.\n\nAfter setup, walk them through the remaining sections — offer to help where you\ncan (e.g. link to channels), and just surface the purely informational bits.\n\nDon't invent sections or summaries that aren't in the guide. The stats are the\nguide creator's personal usage data — don't extrapolate them into a \"team\nworkflow\" narrative. -->",
        "marketplace": "claude-plugins-official",
        "plugin": "discord"
        "marketplace": "claude-plugins-official",
        "plugin": "telegram"
        "marketplace": "claude-plugins-official",
        "plugin": "fakechat"
        "marketplace": "claude-plugins-official",
        "plugin": "imessage"
    "tengu_slim_subagent_claudemd": true,
    "tengu-off-switch": {
      "allowedTools": [],
      "lastToolDuration": 0,
      "allowedTools": [],
      "lastToolDuration": 0,
      "allowedTools": [],
      "lastToolDuration": 3946,
        "pre_tool_hook_duration_ms_count": 12,
        "pre_tool_hook_duration_ms_min": 0,
        "pre_tool_hook_duration_ms_max": 0,
        "pre_tool_hook_duration_ms_avg": 0,
        "pre_tool_hook_duration_ms_p50": 0,
        "pre_tool_hook_duration_ms_p95": 0,
        "pre_tool_hook_duration_ms_p99": 0,
      "allowedTools": [],
  "skillUsage": {
    "find-skills": {
    "subagent-fanout-nudge": 1,
  "pluginUsage": {
    "anthropic-skills@inline": {
```

### 📄 配置文件：Cursor dir (✅ 存在)
- 物理路径：`~\.cursor`
```toml
该路径是目录，包含文件: ['.gitignore', 'agents', 'ai-tracking', 'argv.json', 'extensions', 'plugins', 'projects', 'skills-cursor']
```

### 📄 配置文件：Hermes dir (✅ 存在)
- 物理路径：`~\.hermes`
```toml
该路径是目录，包含文件: ['.env', 'config.yaml', 'skills']
```

### 📄 配置文件：Qoder dir (✅ 存在)
- 物理路径：`~\.qoder`
```toml
该路径是目录，包含文件: ['argv.json', 'cache', 'canvas', 'extensions', 'memories', 'plugins', 'projects', 'session-env', 'settings.json', 'skills']
```

## 四、 三套配置方案深度比对
### 方案 A：保守复制方案 (Physical Copy)
- **执行逻辑**：使用脚本把 `D:\AI-Skills\skills` 目录下的 80 个技能物理复制到每个检测到存在的工具默认目录中。
- **优点**：完全依赖工具自身默认机制，不需要修改系统注册表或使用高级快捷链接，不会因权限缺失报错，兼容性 100%。
- **缺点**：创建了多份物理拷贝。以后每次修改或新增一个自定义技能，都需要在多处进行二次复制对齐，极易引发版本不同步。
- **风险**：磁盘文件冗余，多版本不一致引起 Agent 路由混乱。
- **回滚方式**：直接物理删除各个默认目录下的复制文件夹。

### 方案 B：软链接方案 (Directory Junction)
- **执行逻辑**：清空各工具的默认 `skills` 目录，然后创建指向 `D:\AI-Skills\skills` 的目录联接 (Windows Junction)。
- **优点**：物理文件只维护 `D:\AI-Skills\skills` 这唯一一份。所有工具的调用请求都被物理重定向到此，修改一处，全局瞬时生效。
- **缺点**：在 Windows 下如果创建软链接 (`mklink /D`)，需要管理员权限，普通终端容易报错。
- **优化解决（关键技术）**：应在命令中指定创建**目录联接 (`mklink /J`)**。目录联接在 Windows 下**不需要**任何管理员特权，普通用户命令行即可执行，且兼容性极强。
- **风险**：如果不慎物理删除了软链接所指代的外层目录，某些脆弱的客户端可能无法启动。
- **回滚方式**：直接删除默认目录下的目录联接实体（Windows Junction 只是快捷指针，删除 Junction 决不会影响并删除 `D:\AI-Skills\skills` 源文件），然后重新建回空目录即可。

### 方案 C：配置文件指定路径方案 (Path Config Override)
- **执行逻辑**：修改配置文件（如 Codex 的 `config.toml`），把 `skills_dir` 属性重定向到 `D:\AI-Skills\skills`。
- **优点**：最纯净、最优雅的代码级配置。完全不需要对物理目录做任何“手术”，也不涉及链接权限问题。
- **缺点**：并不是所有的 AI 客户端都公开支持在配置文件中指定 `skills_dir`。例如 Claude Code 和 Cursor 默认写死读取其专属隐藏文件夹，无此配置入口。
- **风险**：写错配置文件格式（如未对 Windows 反斜杠进行双斜杠转义 `D:\\AI-Skills`）可能导致工具无法解析配置。
- **回滚方式**：将配置文件中的 `skills_dir` 属性改回默认值或删除此项。

## 五、 推荐最终方案与理由
### 🌟 推荐：【方案 C + 方案 B 混合部署方案】
1. **针对 Codex**：**优先采用 方案 C**。修改 `C:\Users\win10\.codex\config.toml`，指定 `skills_dir = "D:\\AI-Skills\\skills"`。这最安全，也最符合 Codex 的规范设计。
2. **针对 Claude Code, Cursor, Hermes, Qoder**：**采用 方案 B (mklink /J)**。由于这些工具只读取其默认目录，我们清空其默认 skills 目录并建立联接重定向至 `D:\AI-Skills\skills`。

**推荐理由**：
- 完美满足**“只维护一份核心技能，修改处处同步”**的核心目标。
- 采用 `/J` 目录联接参数，**完全规避了 Windows 管理员权限问题**。
- 对原有工具物理目录的破坏最小，回滚极度方便，只需删除快捷重定向，重新建回空目录即可。

## 六、 回滚与防灾应急预案
在后续真正执行配置前，我们会自动为各 AI 工具的配置文件（如 `config.toml`）在原地生成 `.bak` 备份文件（如 `config.toml.bak`）。若发生任何异常，只需物理复制回滚覆盖，即可 100% 恢复初始状态。

## 七、 下一步评估建议
- 本报告已将所有探测数据物理在位呈现。
- **红线确认**：本次执行阶段**未修改任何配置文件，未创建软链接，未执行复制**。
- 下一步当您确认此报告后，回复 **“确认方案，开始配置”**，我将为您一键生成安全备份并配置完毕。