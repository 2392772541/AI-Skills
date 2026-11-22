# 按交付物选技能

| 请求 | 首选与边界 |
|---|---|
| 按参考视频高相似度复刻 Remotion 视频 | remotion-video-replica；用于原片抽帧、镜头与动画匹配，按该技能约定处理审片 |
| 将静态海报／截图做成 Remotion 动画，或编辑已有 Remotion 工程 | remotion-video-builder；按参考图拆解布局、文字和层级再制作动画；9:16 无其他要求可用 1080×1920、30fps |
| 已有 Remotion、Blender 或 HyperFrames 项目 | 保留已有框架，选对应编辑／渲染技能；只有明确要求迁移时读迁移技能 |
| 静态图片生成或编辑 | imagegen；给了参考图不意味着要做视频 |
| 网页／截图转网站代码 | 当前可用的 product-design 对应技能；不自动改做 Remotion 视频 |
| GSAP 页面动效 | gsap-core，React／滚动／时间轴分别按需用对应技能 |
| 素材库音视频图片整理 | media-library-organizer；保留原素材和人工标注 |
| 短视频口播、已有口播素材重剪 | talking-head-production 或 talking-head-recut，按用户要的脚本／剪辑产物区分 |
| Obsidian 笔记／数据库／画布 | obsidian-markdown／obsidian-bases／json-canvas 按目标文件选择 |
| Word 转 Markdown／网页正文提取 | docx-to-md／defuddle |
| 飞书内容处理 | 对应 lark 服务技能，不预加载全部飞书技能 |
| 平台发布 | 对应 bilibili-upload、douyin-upload、kuaishou-upload 或 xiaohongshu-upload；先确认任务包含真实发布授权 |
| PPT 文件 | codex-ppt、guizang-ppt-skill 或 ppt-master，按风格和可编辑要求选一个主流程 |
| 长文写作 | khazix-writer，仅在需要该写作风格时使用 |
| 中文文章／评论去套话润色、去除模板化表达且严格保留事实与确定程度 | humanizer-zh（专注中文文本润色、消除模板化套话并严格保护原文结构）；与 shuorenhua 互为补充 |
| 水球泡/且曼周报制作、多渠道找链、B站/抖音批量分类收藏与链接转预览 | video-doc-weekly-orchestrator；一条龙聚合执行型流水线，统一管理录屏还原、多渠道补链、互斥截图门禁、双平台分类真实收藏与终末飞书链接转原生预览播放器，杜绝碎片化多对话执行 |
| 代码审查／安全审查／拆 PR | 对应 review、review-security 或 split-to-prs |
| 系统研究／竞品分析 | hv-analysis；联网资料获取按专用工具和右侧 GPT 全局偏好处理 |
| 新建／升级／治理技能 | skill-product-manager；不直接安装一组重叠技能 |

正向：用户问“该用哪个 Skill”时路由；“照截图做 Remotion 视频”选 remotion-video-builder；“按原片高相似度复刻”选 remotion-video-replica；“把截图实现为网页”选网站实现。
负向：“只改一个按钮文字”直接改；“图片加一个物体”用图像编辑；“现有 Remotion 调字体”不迁移 HyperFrames；普通计划不进入反复访谈。
