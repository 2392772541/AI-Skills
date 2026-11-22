# 工程核查快照 1.0

`project.json` 是从完整镜头表、角色索引和拆解文档派生的机器检查快照；权威文件见工作流。不以它代替面向人的完整分镜。以 `assets/project.example.json` 查看完整可运行示例，复制到工程后更新所有内容，不把示例人物带入用户项目。

## 顶层字段

| 字段 | 类型与含义 |
|---|---|
| schema_version | 固定 "1.0" |
| source_text | 本轮完整原文，不用摘要替代 |
| source_segments | `{id,text,required}`；text 是原文逐字片段；required=false 时加 exclusion_reason |
| project | title、status、target_duration_s、platform |
| characters | id、name、appearance、variants、evidence |
| props | id、name、initial_owner_id（无或非角色持有为 null） |
| scenes | id、name；昼夜变体可增加字段 |
| references | id、purpose、status、path，人物图附 character_id、variant_id |
| shots | id、scene_id、duration_s、source_ids、purpose、visual_action、start_state、end_state |
| generation_units | id、shot_ids、duration_s、reference_ids、bindings |

可以增加创作字段；不能改动上述字段的类型。所有数组必须存在，确实无人、无道具或无图片时用空数组。

## 项目和平台

`status=draft` 表示可审阅的文字方案，允许参考图待生成和平台未核实。`ready` 只表示本核查快照具备明确能力和已可用的绑定资产，不能代表已生成视频。

platform 字段：name、model、capabilities_verified、binding_verified、max_duration_s、max_reference_images；未知上限写 null。capabilities_verified 和 binding_verified 只有查过当前入口或有当前会话验证证据才可 true；另记录 evidence（证据来源、时间与适用模式）。脚本只能检查标志和数字，不能代替事实核实。

## 人物与依据

appearance 包含 age、gender、skin、hair、face、costume 六项，值为字符串或 null。不能把未知误写成事实。

variants 为 `{id,description}` 数组，至少一项基础装束。变体归属由所在角色确定；跨角色不共享同一变体 ID。

evidence 的每项为：
- explicit：原文明确，填写 feature 与 quote（原文逐字引文）。
- inferred：合理推导，填写 feature 与 reason。
- proposed：设计建议，填写 feature 与 reason、采纳状态。

脚本能验证引文存在，不能理解引文是否确实支持某个结论；语义对账仍需执行。

## 图片与绑定

`planned`=待生成；`available`=实际存在且经人工/视觉审核采用；`rejected`=不采用。

available 的 path 使用工程内文件路径。工程外图片先经授权复制或由用户放入工程；脚本不联网、不下载、不移动图片，只查本地存在。

每个生成单元的 reference_ids 就是上传清单；bindings 每项为 `{reference_id,token}`，token 使用平台真正支持的值。draft 可留空并交待绑定草稿，ready 必须完整一一对应。角色图、场景图、控制图均计入本检查器的参考图片数；视频和音频参考另外人工核对。

## 镜头状态

start_state 和 end_state 为人物数组，每项包含：
`character_id、variant_id、position、orientation、holding（道具 ID 数组）、state（状态文字）`。

无人物镜头用空数组。道具位于桌面等场景位置时补写 object_states；不要虚构一个持有角色。共同搬抬或多人共同接触不是独占持有，只在 holding 指定当前主要持有者，另写 shared_interactions 解释。

每镜必须引用原文段或提供 adaptation_reason；重要原文段至少被一镜覆盖。镜头时长总和应等于项目已采纳目标；需要调整时同步记录预算修改。

连续接点填 continuous_from=前镜 ID，脚本比较同一角色的变体、持物、位置、朝向和状态。镜内发生动作应体现在 end_state；镜间省略或场景跳转引起的变化写 transition_reason。补理由不能掩盖不合逻辑的变化，仍需语义审核。

生成单元按完整镜头表连续排序，每镜只属于一个单元；单元时长等于镜头之和。超平台上限回上游拆分，不静默压缩动作。

## 命令

`python "<技能目录>/scripts/validate_project.py" "<工程目录>/project.json"`

退出码 0=无结构错误（可能有待验证警告），1=存在错误或输入无效。warnings 不能写成真实生成通过。必须同时阅读 not_checked。
