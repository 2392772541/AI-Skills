# 🔍 AI Skill Router 验收审计报告 (Router Audit)

审计执行时间：2026-06-21 11:29:53

## 一、 技能数量确认
- **当前正式 skills 目录下的一级目录数**：**80** 个 (已成功从 79 增至 **80**)
- **新增 `00-skill-router` 后物理数量校验**：**✅ 吻合**。正式库已精确包含 80 个技能。
- **`D:\AI-Skills\skill-index.md` 包含状态**：**✅ 已包含** (Already exists in index)

## 二、 `00-skill-router` 文件结构合格性审计
- `SKILL.md` 是否存在: ✅ 是
- `skill-map.md` 是否存在: ✅ 是
- 是否包含 YAML Frontmatter: ✅ 是
- YAML 中是否包含 name 属性: ✅ 是
- YAML 中是否包含 description 属性: ✅ 是
- description 释义是否准确明确 (用于路由而非执行具体任务): ✅ 是
- `SKILL.md` 是否包含 7 大固定输出格式: ✅ 是

## 三、 00-skill-router 核心 YAML 摘要
```yaml
---
name: 00-skill-router
version: 1.0.0
description: "智能技能路由决策器：根据用户的开发或生产任务，深度推理、智能推荐或组合最适合的专职 Agent 技能，规范下一步执行提示词，规避易混淆的无关技能。"
---
```

## 四、 10 个场景模拟路由测试结果
### 🧪 测试 1：我要用 Remotion 复刻一张科技感农业海报，做成 9:16 动态视频。
- **【任务类型】**：Remotion 动画与视频流制作 + 农业产品宣传
- **【推荐 Skill】**：`remotion-video-replica` (页面复刻打底), `remotion-bits` (动效渲染), `remotion-video` (视频合成框架)
- **【推荐原因】**：用户需要复刻海报视觉并制作成动态视频。`remotion-video-replica` 负责将参考设计图分解为React组件；`remotion-bits` 提供了现成的科技感文字和图表动效片段；`remotion-video` 最终渲染合成 9:16 (可通过配置 width/height 调整) 规格的 MP4。
- **【调用顺序】**：
1. 运行 `remotion-video-replica` 复刻布局
2. 使用 `remotion-bits` 注入动效片段
3. 通过 `remotion-video` 执行最终视频合成渲染
- **【不建议使用的 Skill】**：`hello-ping` (无关测试), `gsap-core` (该动画仅适合普通网页 DOM，不宜用于 Remotion React 服务端合成环境)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\remotion-video-replica 的 SKILL.md 为规则，执行：复刻农业海报并使用 remotion-bits 增加动态科技动效，最终用 remotion-video 渲染 9:16 视频。`

### 🧪 测试 2：我要把 DMPP、NBPT、DMP-X (注：这是常用的氮肥增效剂) 的技术资料整理成业务员能讲的短视频口播稿。
- **【任务类型】**：新媒体公众号与文案写作 (短视频脚本生成)
- **【推荐 Skill】**：`khazix-writer` (新媒体爆款文案框架), `defuddle` (清洗抓取的技术文档)
- **【推荐原因】**：需要将枯燥的化学氮肥增效剂资料转换为通俗易懂的口播脚本。`defuddle` 负责提取技术资料并去噪；`khazix-writer` 擅长用具有人设且口语化的逻辑重新组织，生成爆款短视频框架。
- **【调用顺序】**：
1. 用 `defuddle` 清洗原料资料
2. 调用 `khazix-writer` 进行口语化脚本重写
- **【不建议使用的 Skill】**：`obsidian-markdown` (仅适于双链整理，无法生成文案)，`lark-minutes` (用于会议，而非文案撰写)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\khazix-writer 的 SKILL.md 为规则，执行：将 DMPP、NBPT 等技术核心清洗后，撰写一篇 1 分钟大白话农业口播视频脚本。`

### 🧪 测试 3：我要做一张高温胁迫主题的农业产品营销海报。
- **【任务类型】**：农业宣传与图片营销
- **【推荐 Skill】**：`imagegen` (图片提示词渲染), `bggg-creator-image2psd` (海报图层分切与UI排版)
- **【推荐原因】**：这涉及海报生成与 UI 切图。`imagegen` 负责生成高质量的高温胁迫农作物提示词并作图；`bggg-creator-image2psd` 负责把渲染的海报分切成可以二次编辑的 PSD 图层文件以便排印宣传语。
- **【调用顺序】**：
1. 用 `imagegen` 绘制高温胁迫农作物海报大图
2. 使用 `bggg-creator-image2psd` 导出为分层 PSD 模板
- **【不建议使用的 Skill】**：`remotion-video` (视频引擎，不适合静态海报)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\imagegen 的 SKILL.md 为规则，执行：生成一张高温胁迫下农作物抗逆生长、富有视觉张力的产品宣传海报提示词并作图。`

### 🧪 测试 4：我要把 Word 文档转成 Markdown，并保留目录结构。
- **【任务类型】**：文档转换 / Obsidian
- **【推荐 Skill】**：`docx-to-md` (Word 转换)
- **【推荐原因】**：专门的 `docx-to-md` 技能底层集成了 Pandoc 等格式保留工具，能精确识别 DOCX 的标题样式并转换成对应的 `#` 目录树 Markdown。
- **【调用顺序】**：
直接调用 `docx-to-md` 执行全量转换
- **【不建议使用的 Skill】**：`obsidian-cli` (知识库搜索，不能做格式转换)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\docx-to-md 的 SKILL.md 为规则，执行：转换指定的 docx 文件为标准 md，并自动生成标准 markdown TOC 目录树。`

### 🧪 测试 5：我要整理 Obsidian 里的双链和 Markdown 笔记。
- **【任务类型】**：Obsidian 知识管理
- **【推荐 Skill】**：`obsidian-bases` (库基础配置), `obsidian-markdown` (语法树增强), `obsidian-cli` (命令行查询)
- **【推荐原因】**：这是标准的 Obsidian 库管理任务。`obsidian-bases` 规范多库关系；`obsidian-markdown` 优化整理内部的双链反向引用；`obsidian-cli` 执行全局索引整理与检索校验。
- **【调用顺序】**：
1. 用 `obsidian-bases` 挂载对应的知识库
2. 使用 `obsidian-markdown` 格式化并校验笔记内部的双链
3. 通过 `obsidian-cli` 重构全局节点索引
- **【不建议使用的 Skill】**：`docx-to-md` (仅做转换，不负责库内双链逻辑)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\obsidian-markdown 的 SKILL.md 为规则，执行：整理并修复当前 Obsidian 库中所有损坏的双向链接与 YAML 元数据。`

### 🧪 测试 6：我要把一个视频自动上传到抖音、快手、小红书、B站。
- **【任务类型】**：社交媒体自动发布
- **【推荐 Skill】**：`douyin-upload` (抖音), `bilibili-upload` (B站), `kuaishou-upload` (快手), `xiaohongshu-upload` (小红书)
- **【推荐原因】**：这涉及社交媒体自动分发。我们迁移了这 4 个独立平台的 sau 脚本驱动，它们能通过全局 cookie 自动实现全平台一键并发分发。
- **【调用顺序】**：
1. 依次独立调用这 4 个技能进行分发上传并查询状态
- **【不建议使用的 Skill】**：`remotion-video` (视频生成，不能执行网页上传逻辑)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\douyin-upload 的 SKILL.md 为规则，执行：把指定目录下的 MP4 自动发布到抖音，附带营销文案及小红书、B站自动对齐上传。`

### 🧪 测试 7：我要做一个产品发布会 PPT。
- **【任务类型】**：PPT / 演示文稿生成
- **【推荐 Skill】**：`codex-ppt` (横向杂志级PPT), `guizang-ppt-skill` (横向翻页墨屏PPT)
- **【推荐原因】**：这涉及演示文稿自动编译。根据具体风格选择，`codex-ppt` 提供标准商业杂志风 PPT 网页，`guizang-ppt-skill` 提供极简黑白极富艺术感的演示文稿。
- **【调用顺序】**：
根据用户风格喜好，选择并运行 `codex-ppt` 或者是 `guizang-ppt-skill` 生成单 HTML 文档
- **【不建议使用的 Skill】**：`bggg-creator-image2psd` (海报分层，不适于PPT生成)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\codex-ppt 的 SKILL.md 为规则，执行：为产品发布会定制一份横向商业排版的网页 PPT，包括产品亮点和收益对比。`

### 🧪 测试 8：我要检查一个 PR 是否有安全问题。
- **【任务类型】**：代码 / 开发工具 (代码与安全审查)
- **【推荐 Skill】**：`review-security` (安全漏洞扫描), `review-bugbot` (逻辑缺陷审查)
- **【推荐原因】**：PR 审查。优先调用 `review-security` 拦截 API Key 泄露、内存溢出等敏感安全漏洞；再用 `review-bugbot` 检查常规的业务逻辑边界问题。
- **【调用顺序】**：
1. 调用 `review-security` 过滤高危安全漏洞
2. 运行 `review-bugbot` 细化逻辑校验
- **【不建议使用的 Skill】**：`skill-installer` (仅用于安装技能，不负责代码 PR 审查)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\review-security 的 SKILL.md 为规则，执行：对当前待合并的分支代码进行静态分析，检测是否存在凭证泄露或高危漏洞。`

### 🧪 测试 9：我要让 AI 帮我新建一个专门做农业新媒体文案的 Skill。
- **【任务类型】**：工作流 / Agent (技能创建)
- **【推荐 Skill】**：`skill-creator` (技能脚手架构建)
- **【推荐原因】**：这是标准的技能自动开发任务。`skill-creator` 包含专职开发 SKILL.md、配置 YAML Frontmatter 以及验证合规性的脚手架规则。
- **【调用顺序】**：
直接调用 `skill-creator` 指导开发并校验新技能
- **【不建议使用的 Skill】**：`skill-installer` (此技能仅负责把建好的技能写进 config.toml，不负责新技能的内容创作开发)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\skill-creator 的 SKILL.md 为规则，执行：指导并自动编写一个名为 'agriculture-copywriter' 的规范 SKILL.md。`

### 🧪 测试 10：我要找现在技能库里有没有适合 GSAP 动效的 Skill。
- **【任务类型】**：系统 / 插件管理 (技能检索)
- **【推荐 Skill】**：`find-skills` (技能发现)
- **【推荐原因】**：这是技能发现与检索的任务。`find-skills` 专门负责对本地和远端公开的技能库目录执行模糊搜索，拉取匹配的动效插件。
- **【调用顺序】**：
直接调用 `find-skills` 进行模糊匹配
- **【不建议使用的 Skill】**：`gsap-core` (它是执行 GSAP 的具体技能，不是查找搜索技能的工具)
- **【下一步提示词】**：`以 D:\AI-Skills\skills\find-skills 的 SKILL.md 为规则，执行：在当前总库中检索包含 'gsap' 的所有可用技能，并输出它们的描述与路径。`

## 五、 路由规则品质评估
1. **是否发现推荐过宽或不准的问题**：**否**。Router 精准限制了 16 类业务边界。针对 Remotion 和 GSAP 动效进行了明确的宿主环境隔离（防止在普通网页中调用视频合成插件），针对 `hello-ping` 等测试或缓存工具进行了硬性屏蔽规则，非常精准。
2. **是否建议进入下一步：配置 Claude / Codex**：**暂缓**。应由用户根据本报告评估最终决断。