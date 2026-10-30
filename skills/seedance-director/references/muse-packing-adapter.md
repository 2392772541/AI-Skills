# Muse 10s 电影化分镜与单镜精修规范 (Cinematic One-to-One Shot Design & Muse 10s Adapter)

本规范解决三大痛点：
1. 以前分镜切得太碎（一句话切成两三个 2 秒的静态看图说话），既没有电影感，又白白多跑好几次生成；
2. 如果在生成阶段把多个独立分镜硬塞进同一个视频节点“合拍再拆开”，会导致第 2 张分镜底图无法生效、AI 切镜秒数不可控、画布节点错乱无法精修；
3. Muse 每次固定产出 10.0 秒原片，如何让每一镜的 10 秒原片既有完整电影调度、又方便用户单镜精细修改与后期剪辑。

---

## 一、 核心铁律：源头少切碎镜，画布严格「1 镜 = 1 底图 = 1 视频节点」

1. **画布永远保持 1:1:1 纯净对应，绝不搞“节点合并再拆开”**：
   - **1 个分镜（Shot） = 1 张独立分镜参考图（`shot_XX.png`） = 1 个 Muse 10s 视频节点**。
   - なぜ不能把多张分镜图塞进同一个 Muse 视频任务再按秒数拆开？因为 Muse 一次生成只能以**第 1 张分镜图**作为起手首帧，第 2 张分镜图根本无法在第 3 秒精准生效，且 AI 动作耗时并非严格卡死在 3.0 秒。
   - 保持 `1 镜 = 1 图 = 1 视频节点`，哪一镜画面或动作不满意，直接在对应节点换图、改词、点「↺ 补做」，完全不影响前后任何镜头，精细修改成本最低。

2. **在「导演拆镜源头」消灭 2 秒静态碎镜（用“单镜内部连续运镜”替代“碎切”）**：
   - **严禁把同一场景内的一句话拆成两三个 2 秒的静态展示镜头！**
   - 凡是同一物理空间、同一人物连贯动作（例如“展示卧室熟睡 ➔ 看后方绿屏部署成功 ➔ 翻身微笑”），在**排分镜表（`03-shots`）时就直接设计为 1 个 5~8 秒的完整运动镜头（一镜到底推摇调度）**，只画 1 张最具张力的起手构图底图，在 1 次 10 秒生成内通过摄影机推拉摇移完成景别变化！
   - 只有真正发生**空间切换、机位反打、视觉奇观跳变或核心特写强调**时，才切分为新的独立镜头。

---

## 二、 电影化镜头语言强制六要素（消灭“幻灯片看图说话”）

每一镜在分镜表中必须显式具备以下 6 项，禁止只写“中景，某人做某事”：
1. **单镜内景别演进与镜间景别反差**：
   - 单镜内部充分利用 10 秒容量写出景别演进（如 `全景起幅 ➔ 顺势缓推至中近景 ➔ 上摇定焦屏幕特写`）；
   - 相邻两个镜头之间必须有明确的景别跨度（严禁连续 3 镜同景别）。
2. **摄影机六槽调度（Camera Choreography）**：`方向+速度的运动`（缓推/急拉/顺势上摇/横移跟拍） + `机位高低角度` + `可观测光学景深结果`（24mm 广角空间纵深 / 85mm 浅景深焦外虚化 / 焦点转移 Rack Focus）。
3. **起幅状态（In-Frame，0~2s）**：画面从分镜底图（`Image 1`）如何起动，承接上一镜什么动势或视线。
4. **触发 ➔ 反应 ➔ 主动作因果链（Core Action，2~7s）**：先有什么视觉/声音触发，主体再做出什么微表情或肢体动作，摄影机如何跟随动作响应。
5. **落幅余量（Out-Frame Hold，7~10s）**：动作完成后的稳定停留与余韵（为后期剪辑留出充足的场记余量 Handles，方便用户在 10 秒原片中自由选取最佳 3~6 秒切点）。
6. **镜间衔接机制（Transition Seam）**：
   - 显式写明本镜落幅与下一镜起幅的咬合方式：`动作匹配剪辑 (Match Cut)`、`前景遮挡转场 (Wipe/Smoke Transition)`、`视线/光斑引导 (Eye-Trace)`、`声画先行 (J-Cut)`。
   - **硬性铁律**：凡拥有自身独立分镜底图的镜头，**一律关闭 `continuity`（上一片段尾帧死锁）**，确保本镜自己的分镜底图永远排在 `Image 1`，绝不允许上一镜尾帧挤占 `Image 1` 导致多镜视频重复。

---

## 三、 Muse 10 秒单镜三段式提示词公式（保存 10s 原片，后期自由精剪）

每个视频节点固定向 Muse 请求并保存完整的 **10 秒原片**，提示词统一按「起幅建立 ➔ 核心运镜与动作演变 ➔ 落幅余韵留白」三段式编写，确保 10 秒内画面饱满、头尾稳健，方便后期随时裁取最佳片段：

```text
PRIMARY SHOT KEYFRAME: Attached image 1 is the dedicated storyboard keyframe for THIS shot.
[Visual Style & Aspect Ratio], 10 seconds cinematic shot.
- [0.0s - 2.0s] (In-Frame & Pre-Roll): Start directly from image 1 composition. {Initial atmosphere & subtle movement}.
- [2.0s - 7.5s] (Core Camera Choreography & Action Beat): {Full camera movement from scale A to scale B} as {Trigger -> Subject Reaction -> Main Physical Action}.
- [7.5s - 10.0s] (Out-Frame Hold for Editing): Camera settles smoothly into {Out-frame state}, holding steady with natural ambient motion for clean post-editing.
AUDIO IS REQUIRED: Synchronized ambient sound and action SFX ({Audio cues}).
```

---

## 三、 电影化镜头语言强制六要素（消灭“幻灯片看图说话”）

每一镜在分镜表中必须显式具备以下 6 项，禁止只写“中景，某人做某事”：
1. **景别变化（Shot Scale Progression）**：严禁连续 3 镜使用同一景别；同一生成包内必须形成景别呼吸（如 `EWS/WS 全景交代 ➔ ECU/CU 核心细节特写 ➔ MCU 人物反应近景`）。
2. **摄影机六槽调度（Camera Choreography）**：`方向+速度的运动`（缓推/急拉/顺势上摇/横移跟拍） + `机位高低角度` + `可观测光学景深结果`（24mm 广角空间纵深 / 85mm 浅景深焦外虚化 / 焦点转移 Rack Focus）。
3. **起幅状态（In-Frame）**：0.0 秒画面定格在哪里、承接上一镜什么动势或视线。
4. **触发 ➔ 反应 ➔ 主动作因果链（Causal Action Beat）**：先有什么视觉/声音触发，主体再做出什么微表情或肢体动作，摄影机如何跟随动作响应。
5. **落幅状态（Out-Frame）**：镜头结束时的位置、朝向、持物、动势余量与视觉重心落点。
6. **镜间衔接机制（Transition Seam）**：
   - **包内衔接（Intra-Job）**：`连续推摇变焦 (Continuous Pan/Tilt & Rack Focus)`、`动作跟随顺接 (Follow-Action)`；
   - **跨包衔接（Inter-Job）**：`动作匹配剪辑 (Match Cut)`、`前景遮挡转场 (Wipe/Smoke Transition)`、`视线/光斑引导 (Eye-Trace)`、`声画先行/滞后 (J-Cut / L-Cut)`。
   - **硬性铁律**：凡拥有自身起手分镜底图的生成包，**一律关闭 `continuity`（上一片段尾帧死锁）**，确保当前生成包自己的分镜底图永远作为 `Image 1`，跨包靠上述导演转场手法自然咬合。

---

## 四、 Muse 10 秒提示词融合公式

### 1. 多镜合并包（Multi-Shot Continuous Pack，2~3 镜合 1 个 10s Job）
```text
PRIMARY SHOT KEYFRAME: Attached image 1 is the opening keyframe for this scene.
[Visual Style & Aspect Ratio], 10 seconds continuous camera choreography in the same [Scene Name].
- [0.0s - {T1}s] (Shot {A} - {Scale A}): Start from image 1 composition. {Camera Move A}. {Subject Action & Lighting A}.
- [{T1}s - {T2}s] (Shot {B} - {Scale B}): Without cutting rooms, camera {Continuous Transition Move, e.g., smoothly tilts up / racks focus / dollys in} to {Scale B}. {Subject/Object Action B}.
- [{T2}s - 10.0s] (Shot {C} - {Scale C}): Camera {Move C} to settle on {Reaction / Out-frame Hold C}.
AUDIO IS REQUIRED: Synchronized ambient sound and action SFX ({Audio cues}).
```

### 2. 单镜精品包（Single-Shot Hero Pack，1 镜独占 1 个 10s Job，后期裁取黄金段）
即使成片只需要 3~4 秒，也绝不在 Prompt 里只写 3 秒静止画面，而是把 10 秒写成完整的三段式微电影，后期取中间最稳的 `[trim_start_s, trim_end_s]`：
```text
PRIMARY SHOT KEYFRAME: Attached image 1 is the dedicated storyboard keyframe for this shot.
[Visual Style & Aspect Ratio], 10 seconds cinematic shot.
- [0.0s - 2.0s] (Entry & Pre-Roll): Establish frame from image 1 with {initial subtle motion & atmosphere}.
- [2.0s - 7.0s] (Core Dramatic Action & Camera Move): {Full 6-slot camera movement + causal action climax}.
- [7.0s - 10.0s] (Out-Frame Hold & Breathing Room): Motion settles naturally into {Out-frame state}, holding steady for clean editorial cutting.
```
