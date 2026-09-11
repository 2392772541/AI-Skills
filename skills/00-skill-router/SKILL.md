---
name: 00-skill-router
version: 1.1.0
description: "This skill routes tasks to the correct Agent Skills. For visual replication, screenshot-to-Remotion, poster replication, page replication, image-to-Remotion, or static image to dynamic video tasks, prioritize remotion-video-replica and related Remotion skills. Do not recommend imagegen first when the user already has a reference image, screenshot, poster, or page to replicate. Recommend imagegen first only when the user needs to generate new images, posters, visual assets, or image prompts without an existing reference."
---

# 00-skill-router (v1.1.0)

本技能为统一技能库的**决策大脑**，用于解析并匹配当前复杂的业务开发、媒体剪辑或视觉复刻场景，路由到最佳技能目录中。

## 📥 输入任务识别与分类规则

当面临以下用户的 17 大工作场景之一时，必须优先启动本 Router 按照**固定格式**进行决策响应：

1. **Remotion 动画制作** -> 关联：`remotion-video`, `remotion-best-practices`, `remotion-bits`
2. **Remotion 页面/视觉复刻** -> 关联：`remotion-video-replica`, `remotion-video`, `remotion-best-practices`, `remotion-bits`, `gsap-core` / `gsap-react`
3. **GSAP 动效** -> 关联：`gsap-core`, `gsap-scrolltrigger`, `gsap-timeline`
4. **农业产品宣传视频** -> 关联：`remotion-video` + sau 自动上传
5. **农业产品海报 / 产品营销图** -> 关联：`imagegen` + `bggg-creator-image2psd` (切图)
6. **图片提示词生成** -> 关联：`loop`
7. **公众号文章 / 新媒体长文** -> 关联：`khazix-writer`
8. **短视频口播脚本** -> 关联：`khazix-writer` (脚本风格), `defuddle` (抓取素材)
9. **Obsidian 知识库整理** -> 关联：`obsidian-bases`, `obsidian-cli`, `obsidian-markdown`
10. **Word / Markdown / 文档转换** -> 关联：`docx-to-md`, `defuddle`
11. **飞书 / Lark 文档、表格、云盘、会议、妙记** -> 关联：`lark-` 开头的 27 个飞书专用技能
12. **B站 / 抖音 / 快手 / 小红书自动发布** -> 关联：sau 系列上传工具 (`bilibili-upload`, `douyin-upload` 等)
13. **PPT / 演示文稿生成** -> 关联：`codex-ppt`, `guizang-ppt-skill`, `json-canvas`
14. **技能安装、技能检索、技能创建** -> 关联：`find-skills`, `skill-installer`, `skill-creator`
15. **代码审查、安全审查、PR 拆分** -> 关联：`review-bugbot`, `review-security`, `split-to-prs`
16. **子 Agent 创建和工作流拆解** -> 关联：`create-subagent`, `create-skill`
17. **深度研究 / 系统性调研 / 竞品分析** -> 关联：`hv-analysis` + `agent-reach`

---

## 🎯 核心场景匹配规则微调

### 1. 复刻类任务匹配细则
当用户任务中出现以下表达时，判定为**复刻类任务**：
* 复刻这张图
* 参考这张图做动画
* 按这张海报做 Remotion
* 把这个页面做成动态视频
* 根据截图还原
* 照着这个风格做
* 页面复刻
* 海报复刻
* 视觉复刻
* 图片转 Remotion
* 静态图转动态视频

**【推荐策略】**：
- **优先推荐**：`remotion-video-replica`、`remotion-video`、`remotion-best-practices`、`remotion-bits`、`gsap-core` 或 `gsap-react`。
- **参数提示**：若任务明确是 **9:16 短视频**，必须在决策中明确提示用户设置默认视频渲染参数：
  - `width: 1080`
  - `height: 1920`
  - `fps: 30`

### 2. 限制 `imagegen` 的使用场景
**`imagegen` 仅在以下情况作为第一优先级推荐**：
1. 用户没有提供参考图，需要先生成视觉底图。
2. 用户明确说“生成海报”、“生成图片”、“做一张图”、“出图提示词”。
3. 用户需要图片提示词、视觉资产、海报底图。

**【边界限制】**：
- 如果用户已经提供参考图、截图、网页、设计稿，或者明确使用“复刻”、“还原”字眼，**`imagegen` 绝对不能作为第一优先级**。它只能作为可选的辅助技能（如用于补充背景点缀素材或生成替代性视觉材质）。

---

## 📋 路由响应输出格式规范 (必须严格保持此结构)

当你被调用以判断任务时，你必须返回且仅返回以下结构化报告：

### 【任务类型】
[指出当前用户任务属于 16 大场景中的哪一类或哪几类]

### 【推荐 Skill】
[列出建议调用的一个或多个技能文件夹名称，以 `00-skill-router` 规范的技能名为准]

### 【推荐原因】
[说明为什么选择这几个技能，以及它们将如何帮助解决问题]

### 【调用顺序】
[如果涉及到多步骤复杂场景，详细列出 Skill 1 -> Skill 2 的调用链路]

### 【不建议使用的 Skill】
[列出用户当前极易用错的、容易产生冲突的同类技能，并给出规避理由，防止误用]

### 【下一步提示词】
[给出可以直接复制给 Claude / Codex / Cursor 的**标准技能执行提示词**。格式为：
`以 D:\AI-Skills\skills\<技能名> 的 SKILL.md 为规则，执行：<具体子任务说明>`]

### 【是否需要新建 Skill】
[如果当前已有的技能无法完美覆盖此需求，在此说明应新建何种功能的 SKILL.md，否则写“否”]

---

## 📖 “复刻类任务”标准输出示例

**任务**：
“我要用 Remotion 复刻一张科技感农业海报，并做成 9:16 动态视频。”

**推荐输出**：

### 【任务类型】
Remotion 视觉复刻 / 静态图转动态视频

### 【推荐 Skill】
* remotion-video-replica
* remotion-video
* remotion-best-practices
* remotion-bits
* gsap-core / gsap-react

### 【推荐原因】
任务要求根据参考海报复刻动态视频，属于典型的“视觉复刻”。应优先分析参考图的图层排版、文字和背景光效，用 Remotion 还原其 React 组件结构，再引入粒子、发光与扫描线动效。无需使用生图工具重新生成整体视觉。

### 【调用顺序】
1. **remotion-video-replica**：分析参考海报并进行图层拆分（背景、主体、文字、光效等）。
2. **remotion-video**：搭建视频 Composition，对于 9:16 竖版视频建议设置默认参数为：`width: 1080`，`height: 1920`，`fps: 30`。
3. **remotion-best-practices**：配置渲染及项目目录结构。
4. **remotion-bits**：引入发光字、科技感网格、扫描效果等动画片段。
5. **gsap-core / gsap-react**：辅助控制某些精细或复杂的非线性动画时间轴。

### 【不建议使用的 Skill】
* **imagegen**：用户已拥有参考海报，`imagegen` 不作为第一优先级（仅在需要为视频背景补充非预设的次级素材时可做辅助）。
* **lark-***：与多媒体视频及海报视觉无关。
* **plugin-creator**：非执行视频任务的技能。

### 【下一步提示词】
请使用 `remotion-video-replica`、`remotion-video`、`remotion-best-practices`、`remotion-bits`，分析我提供的参考图，将其复刻为 9:16 Remotion 动态视频（设置参数建议为：width: 1080, height: 1920, fps: 30）。请先拆分背景层、主体层、文字层、光效层、粒子层 and 镜头运动，再输出组件结构和实现计划，暂时不要直接写完整代码。

### 【是否需要新建 Skill】
否


## Generated capability catalog

Before routing broad or ambiguous tasks, consult `references/generated-catalog.md`, which is generated from the local Skill registry. For requests to find, evaluate, create, upgrade, merge, import, or govern Skills, route first to `skill-product-manager` rather than directly creating or installing a Skill.
