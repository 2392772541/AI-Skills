# 工作流与冲突裁决

## 融合优先级

用户要求和原文事实 → 已采纳的人物/风格/故事设定 → 本融合入口和专项约定 → 专业手册 → 示例。

来源包不是未经改造的可执行规则全集。以下冲突已经在融合版明确裁决：

| 来源包的规定 | 本版采用的规则 |
|---|---|
| 站站审核后必须用户点头、开场固定拷问 | 已授权范围自主推进；重大创作选择或必要缺失信息才问 |
| 审核必须 fresh 子代理 | 默认串行自检；用户明确允许独立代理才调用，并如实区分检查类型 |
| 只能服务 Seedance 2.5、每条必须遵循固定容量 | 默认参考 Seedance，具体模型、入口、模式由项目能力表确定；未验证不得写死 |
| 三格必同脸、必须去头、每人必须笑版 | 可选参考资产策略，按镜头需要制作并真实核验 |
| 七维全填满、规定数量的五官细节 | 小墨六要素做证据提取；七维只补有信息增量的体型、行为和质感 |
| 原资产一字不能改、变体像素一定不变 | 支持纠错修订、留旧版；编辑结果必须实测 |
| 人物姓名一律禁用、固定全局负向尾缀 | 工作表允许角色名和项目编号；模型提示采用平台支持的名称和绑定语法，负向按工具需要最小化 |
| 所有声音必须写进模型、禁止后期补声音 | 服从用户制作流程；可分开制作或后期添加，清楚写交付边界 |
| 色调永不变化、反差镜头有固定配额 | 保持全片视觉逻辑，允许有明确依据的时段、场域和情绪变化 |
| 不许固定/长镜头、机位和运镜有配额 | 叙事、物理可行性和节奏优先，不按比例硬凑 |
| 科普片也必须人物为主 | 科普与产品片按内容决定；可全程无人，无需虚构人物 |
| 不查就不能用任何表外风格 | 用户提供可分析视觉参考时先分析；只有需要外部事实才按环境能力核实 |
| 20 个子技能必须全装到平台 | 仅安装一个融合入口；20 个手册按需读取，避免重复触发 |

## 完整制作

定需求与风格 → 原文内容段与事件拆解 → 小墨人物提取 → Seedance 资产登记 → 完整镜头表 → 按平台编译 → 结构校验与语义审阅 → 交付待验证项。

简短内容可合并阶段；已有剧本无需重写，已有角色无需重画。长片按明确集数或场次处理，交付范围外内容列出而不声称完成。重排某场检查相邻场；不重排全片。

## 专业手册路由

以下路径都相对技能目录；只读当前需要的一份 `guide.md` 及其引用，示例按需查看。20 个专业模块来自上传的 Seedance 包；character-design 为融合版重写。

| 工序 | 手册路径 |
|---|---|
| 目标定义 | references/seedance/goal-creator/guide.md |
| 导演需求、风格讨论 | references/seedance/director-grill/guide.md |
| 剧本创作 | references/seedance/script-write/guide.md |
| 剧本适配 | references/seedance/script-adapt/guide.md |
| 剧本拆解 | references/seedance/script-breakdown/guide.md |
| 人物资产 | references/seedance/character-design/guide.md |
| 场景资产 | references/seedance/scene-design/guide.md |
| 道具资产 | references/seedance/prop-design/guide.md |
| 镜头表 | references/seedance/shot-design/guide.md |
| 摄影机 | references/seedance/camera/guide.md |
| 空间与调度 | references/seedance/blocking/guide.md |
| 光影 | references/seedance/lighting/guide.md |
| 人物表演 | references/seedance/performance/guide.md |
| 声音 | references/seedance/sound-writing/guide.md |
| 控制图 | references/seedance/control-image/guide.md |
| 视频提示词编译 | references/seedance/motion-compile/guide.md |
| 连续性 | references/seedance/continuity/guide.md |
| 审核 | references/seedance/review/guide.md |
| 局部修复 | references/seedance/retake/guide.md |
| 可选代码预演 | references/seedance/previz/guide.md |

## 工程权威文件

- 原文：`01-script/source/`，保持原样。
- 创作意图和已采纳决定：`00-bible/creative-brief.md`、`decisions.md`。
- 风格：`00-bible/visual-style.md`，版本化。
- 内容段、事件与生成单元草案：`02-breakdown/ep01-breakdown.md`。
- 人物/道具/场景的已采纳事实、编号和图片状态：`04-assets/reference-index.md`。
- 镜头数、镜序、镜头时长、动作和衔接：`03-shots/ep01-shots.md`。
- 图像提示词：`04-assets/characters-prompts.md`、`scenes-prompts.md`、`props-prompts.md`。
- 控制图：`05-control-prompts/`；视频提示词：`06-motion-prompts/`。
- 连续性台账：`07-continuity/ledger.md`；审核记录：`08-review/`。
- `project.json` 是上述文件的派生核查快照；不得成为另一套创意事实来源。

跨集使用相同资产编号，文件名里的 ep01 按集号替换。目录按需要创建，不强制空目录骨架。不能创建文件时，在回复中按对应栏目交付，并给出当前覆盖范围。
