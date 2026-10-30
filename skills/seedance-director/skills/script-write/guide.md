---
name: script-write
description: 当用户只有梗概、故事想法、beat 大纲或人物设定而没有成型剧本，需要从零写作剧本；或想逐场共创剧情、让 AI 给场次方案、说"帮我写这场戏""给我一个方案"时使用。以五元素戏剧引擎（Goal/Obstacle/Tactic/Reversal/Value Shift）驱动，支持从蓝图长全本的 WRITE 与逐场共创的 CO-WRITE 双模式，按标准剧本格式交付。产出 01-script/epNN.md 剧本，写完移交 script-adapt 做可实现性改造。
---

[任务]
    剧本适配的写作分支——script-adapt 判定输入为梗概与想法时启用——负责正向写作剧本：
        - WRITE 模式：从创作蓝图要素长出全本——场次大纲先行，用户点头后逐场写作；
        - CO-WRITE 模式：逐场共创——用户出想法或写初稿，本站以五元素引擎陪写陪改；
        - 交付场头、动作行、台词的标准剧本格式，落盘 01-script/epNN.md，写完回 script-adapt 主查可实现性，随后进 director-grill 剧作审计层，最终随立项收口的 ★适配确认定稿。
    上游：director-grill 访谈层的蓝图要素。下游：script-adapt。

[依赖检测]
    必需，缺了挡：
        - 00-bible/creative-brief.md——蓝图要素四件：片种、风格基调、story goal、叙事范围。story goal 是主角为之而战的那件唯一的事；叙事范围含单集或多集、时长量级。查该文件或其草案，文件没有就查本对话中 director-grill 访谈已确认的结论。
        - 缺 → 挡，指回上游站——director-grill 访谈层；story goal 未定不开写，五元素引擎没有 Goal 就没有引擎。
        - 用户的故事材料：梗概、点子、beat 列表、人物设定，任意粗细，一句话也算。缺 → 挡：请用户先给出想法，本站是写作分支不是发明分支。
    必需，有活干：
        - 先做模式判定，见 [双模式判定]。
    可选，缺了降级：
        - 00-bible/series-outline.md——多集时定本集在整季的位置与集尾钩子。缺 → 降级：单集直接写；多集则先产集结构草案并标注「待定稿进 series-outline.md」。
        - 00-bible/visual-style.md——有草案就读，取值范围写死三项：色彩语域、时代与世界锚、质感语言词表，只用来约束动作行取词——环境与物件的颜色、年代形制与器物口径、表面与材质词。DP 署名锚、摄影三件套、镜头性格、光逻辑一律不取，那是 shot-design 与 lighting 的所有权，写进剧本即撞本站 [禁止]。缺 → 降级：照常写，不自拟风格参数，取词等风格基准定稿后由下游对账。
        - 用户点名的参考作品与口味样本——缺 → 降级：按片种默认语感写。

[文件结构]
    script-write/
    ├── SKILL.md                             # 本文件：双模式判定、结构铺排、逐场写作循环、全本自检与移交
    ├── references/                          # 按需加载，不一次全读
    │   ├── five-element-engine.md           # 五元素写作侧用法：写前命名法 + 快检口径 + 多方案；定义权威在 grill 的审计件
    │   └── screenplay-format.md             # 剧本格式规范与动作行可视化写法，好动作行的唯一权威标准
    ├── templates/
    │   └── screenplay-format-template.md    # 剧本文件母版，两站共用
    └── examples/
        └── write-session-example.md         # WRITE 一场标杆 + CO-WRITE 交互片段，附「为什么这么编」注解
    读入：00-bible/creative-brief.md 取蓝图四要素 · 00-bible/visual-style.md 有草案则取色彩语域、时代与世界锚、质感语言词表三项约束动作行取词，取值范围见 [依赖检测] · 00-bible/series-outline.md 定本集主线与集尾钩子 · 01-script/source/ 用户给的梗概、大纲、人物设定原样落盘。
    写出：01-script/epNN.md 剧本，头部集信息块 + 场次正文，母版见 templates/screenplay-format-template.md、与 script-adapt 共用同一母版，单集项目也用 ep01 命名 · 00-bible/decisions.md 追记创作决策理由——为什么这条线这么走、为什么砍掉某方案，两件都是本站写出物。

[第一性原则]
    本环节是【导演思维】第 2 问「画面化」的展开：从第一行起就用可拍的画面讲故事——五元素管每场戏为什么存在，画面化管每一句怎么被拍出来。
    引擎定义特制且权威："These definitions are bespoke. Do not substitute textbook craft definitions."（这些定义是特制的，禁止用教科书定义替换。）判戏之前先重读定义。
    每场弱戏都烧真钱："On an AI film a weak scene costs real money."（AI 影片里，一场弱戏烧掉的是真金白银的生成成本。）过不了移除测试的场不写。
    最常见的真实剧作失败："A reversal that turns the plot but does not move the audience's verdict — it is inert."（只翻情节、不翻观众评判的反转，是死重。）每场写完先猎杀它。
    导演功课是人的活："Direct, don't describe."（去导演，别去描述。）事件、动机、目标、障碍、战术是模型无法代为发明的部分；五元素命名就是这份功课，写前必做。

[双模式判定]
    用户要全本自动 → WRITE；想逐场参与、已自己动笔、对情节有强主张 → CO-WRITE，不明确问一句。判定后把梗概、设定原样存 01-script/source/。

[蓝图吸收 · story goal 钉死]
    读 creative-brief 取四要素，多集读 series-outline 定本集主线与集尾钩子；story goal 一句话钉死并复述给用户——主目标全剧不变，后面全部场次都挂在它的因果链上。

[sequence 结构铺排]
    WRITE 全量、CO-WRITE 只排当前 sequence。sequence = 某一危局从开启到解决的场次段落，可嵌套，每个预埋至少一处 Reversal；产出场次大纲每场一行——场号、场头、一句话事件、五元素速记——呈用户轻过目，方向不对此刻改最便宜。

[逐场写作]
    写前命名五项（工作单见 references/five-element-engine.md [写前命名法]）；落笔照 references/screenplay-format.md，动作行逐句过「画面里具体看见什么」；写后注一行——哪个 Reversal 落地、产生什么 Value Shift。
        - CO-WRITE 循环细则：
            1. 定场卡——与用户共同命名五项，亮工作单对齐方向；
            2. 执笔——用户写则本站审改，本站写则用户改；
            3. 快检——随写随跑五元素；发现弱点只指最弱单点。修复遵循三档口径：1 号最小修，只动最弱单点、保用户原稿；2 号干净修，完整可行的重写；3 号可选，真有增益才给。格式权威见 director-grill 的 five-elements-audit.md，改写句段一律按剧本格式交付；
            4. 定稿写入 epNN.md；
            5. 下一场。
    出多方案规则：方案之间必须差在 Tactic 与/或 Reversal 从而 Value Shift 不同，不许只差语气与文笔。

[全本自检 · 三查]
    sequence 逐个查——至少一个非 inert 的 Reversal，每个都写得出 before-verdict → after-verdict，Value Shift 轨迹是设计过的；移除测试全场跑——删掉该场因果链仍成立 → 该场重写或删，"No orphan scenes."（没有孤儿场。）；格式检——场头三要素齐、时间地点无歧义、超长独白已标记。

[落盘与移交]
    剧本写 01-script/epNN.md，关键取舍补记 decisions.md；移交 script-adapt 并告知可视化已内建、主查可实现性雷区；后续 → director-grill 剧作审计复核 → 适配确认。

[完成标准]
    确定性自检动手做：本站产物里可数、可对照的项逐一核过，不凭「看起来对」；查出的当场修，修完才交。
    1. 每场五元素可命名，全场过移除测试，无孤儿场。
    2. 每个 sequence 至少一个 Reversal；每个 Reversal 的 Value Shift 能写出 before-verdict → after-verdict；整体轨迹递深。
    3. 全文剧本格式合规：场头三要素、动作行现在时可拍、台词归位、人物首次出场带括注。
    4. 已落盘 01-script/epNN.md，source 已存档，decisions.md 已补记关键取舍。
    5. WRITE 模式：场次大纲经用户过目后才展开全本；CO-WRITE 模式：每场定稿用户点过头——这是共创的天然节奏。
    6. 已移交 script-adapt；未经可实现性改造的剧本不算完成。

[禁止]
    - 禁止用教科书三幕论、救猫咪节拍表等外部定义顶替五元素定制定义——判戏前重读 director-grill 的 five-elements-audit.md 判据卡。
    - 禁止写 inert reversal 不标不修——只翻情节不翻观众评判。
    - 禁止多方案只差语气与文风。
    - 禁止 story goal 未定就开写；禁止写作途中偷偷更换主目标——主角只会错在战术，永不搞错目标。
    - 禁止在剧本里写镜号、景别、运镜、提示词参数；禁止写 BGM 与后期指令——画面内的源内音乐除外，如收音机与街头艺人。
    - 禁止用情绪副词与表情结论替代可见动作——"悲伤地""露出愤怒的表情"这类。
    - 禁止跳过 script-adapt 直接交给 script-breakdown——可实现性未查的剧本不下传。
    - 禁止越站代工：蓝图访谈是 director-grill 的活，要素缺口时转站，不自行脑补片种与风格。

[初始化]
    执行 [依赖检测]。先 [双模式判定] 与 [蓝图吸收]，再 [sequence 结构铺排]，循环 [逐场写作]，过 [全本自检] 后 [落盘与移交]。
