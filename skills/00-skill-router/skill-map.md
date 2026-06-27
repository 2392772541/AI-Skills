# 🗺️ AI Skills 场景地图 (Skill Map)

本文件归纳整理了当前技能库中 80 个正式技能在 16 大核心生产力场景下的组合、触发词以及默认启动建议。

## 1. 核心生产力场景地图

### 🖥️ Remotion 页面与视觉复刻 (静态图转动态视频)
- **核心推荐技能**：
  - `remotion-video-replica`：分析参考图排版，拆解图层，制定复刻计划。
  - `remotion-video`：React 渲染视频主逻辑。
- **推荐技能组合**：
  - `remotion-video-replica` (分析海报) + `remotion-video` (搭建组件) + `remotion-best-practices` (规范结构) + `remotion-bits` (动效增强) + `gsap-core` / `gsap-react` (复杂非线性动效辅助)
- **常用触发词**：`复刻这张图`, `参考这张图做动画`, `按这张海报做 Remotion`, `把这个页面做成动态视频`, `根据截图还原`, `照着这个风格做`, `页面复刻`, `海报复刻`, `视觉复刻`, `图片转 Remotion`, `静态图转动态视频`
- **竖版视频参数建议**：对于 9:16 竖版视频，默认建议设置参数：`width: 1080`，`height: 1920`，`fps: 30`。

### 🎬 Remotion 动画与视频流制作 (从零创意)
- **核心推荐技能**：
  - `remotion-video`：核心React渲染服务端合成引擎。
  - `remotion-bits`：常用动效基础组件。
- **推荐技能组合**：
  - `remotion-video` (编写视频流) + `remotion-best-practices` (渲染优化) + `remotion-bits` (动效片段)。
- **常用触发词**：`video`, `remotion`, `render`, `mp4`, `animation`

### 🎨 交互动效与视觉设计
- **核心推荐技能**：
  - `gsap-core`：核心 ScrollTrigger、Timeline 动效调优。
  - `codex-ppt`：杂志级横向交互演示文稿。
- **推荐技能组合**：
  - `gsap-core` + `gsap-scrolltrigger` + `gsap-timeline`
  - `guizang-ppt-skill` + `json-canvas` (PPT展示及流程看板)
- **常用触发词**：`gsap`, `scrolltrigger`, `canva`, `ppt`, `figma`

### 🌾 农业宣传与图片营销
- **核心推荐技能**：
  - `imagegen`：商业级图片提示词渲染。
  - `bggg-creator-image2psd`：PSD 智能分层导出。
- **推荐技能组合**：
  - `imagegen` (海报生成) + `bggg-creator-image2psd` (UI切图)
- **常用触发词**：`image`, `draw`, `psd`, `poster`, `marketing`
- **⚠️ imagegen 商业生图边界说明**：
  - **优先推荐场景**：用户无参考图，需要从零生成底图/视觉资产；或者包含 `生成海报`、`做一张图` 等生图指令。
  - **降级/可选推荐场景**：若属于“复刻已有海报”、“根据截图还原”，`imagegen` 不作为第一优先级，只能作为次要辅助技能（如为已有海报补充额外的树木、光效粒子等细分背景资产）。

### ✍️ 新媒体公众号与文案写作
- **核心推荐技能**：
  - `khazix-writer`：卡兹克公众号爆款长文。
  - `defuddle`：文章素材网页无噪抓取。
- **推荐技能组合**：
  - `defuddle` (拉取素材) + `khazix-writer` (公众号长文排版)
- **常用触发词**：`write`, `writer`, `copywriting`, `newmedia`

### 📓 Obsidian 知识管理与文档转换
- **核心推荐技能**：
  - `obsidian-bases`：双链与多层数据库初始化。
  - `docx-to-md`：Word 转标准 Markdown。
- **推荐技能组合**：
  - `docx-to-md` + `obsidian-markdown` + `obsidian-cli`
- **常用触发词**：`obsidian`, `vault`, `docx`, `markdown`

### 🕊️ 飞书 (Lark) 协同生态
- **核心推荐技能**：
  - `lark-doc` / `lark-sheets` / `lark-base` / `lark-drive` / `lark-vc`
- **推荐技能组合**：
  - `lark-minutes` (妙记导出) + `lark-vc` (纪要归纳)
  - `lark-drive` (文档导入) + `lark-doc` (内容局部修改)
- **常用触发词**：`lark`, `feishu`, `base`, `sheets`, `docx`

### 🚀 命令行、社交自动发布与代码工程
- **核心推荐技能**：
  - sau 系列发布：`bilibili-upload`, `douyin-upload`, `kuaishou-upload`, `xiaohongshu-upload`
  - `review-bugbot` / `review-security`
- **推荐技能组合**：
  - `remotion-video` (视频导出) + `bilibili-upload` (Sau 自动上传)
  - `split-to-prs` + `review-bugbot` (开发审查组合)
- **常用触发词**：`upload`, `bilibili`, `sau`, `review`, `security`

---

## 2. 核心触发词与推荐组合速查

| 业务场景 | 触发词 | 推荐调用组合 | 冲突/不建议默认启用技能 |
| --- | --- | --- | --- |
| **视频复刻** | `复刻`, `还原`, `静态转动态` | `remotion-video-replica` + `remotion-bits` | `imagegen` (不作为主推荐) |
| **视频动效** | `remotion`, `gsap` | `remotion-video` + `gsap-core` | `hello-ping` (仅为测试脚本) |
| **文案排版** | `writer`, `copy` | `defuddle` + `khazix-writer` | `plugin-creator` (系统级) |
| **飞书协同** | `feishu`, `lark` | `lark-drive` + `lark-doc` | `skill-installer` (代码管理) |
| **开发工程** | `review`, `git` | `split-to-prs` + `review-bugbot`| `.tmp` 缓存版技能 |

## 3. 不建议默认启用的技能清单

以下技能为特殊场景定时测试或临时脚本，**不建议在全局配置中默认加载**，仅在有特定诉求时手动显式载入：
1. `hello-ping` (定时测试脚本，多余冗余)
2. `babysit` (分支自动 merge 守护进程，非日常交互所需)
3. `shell` (异步终端捕获，专为自动化框架内置，普通对话易引起死锁)
