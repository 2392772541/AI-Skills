---
name: google-video-gen
description: 谷歌视频生成（Google Video Gen / 视频工坊）。用于 Google Flow 商业大片视频生成（16:9横屏大片/9:16竖屏短视频）、首尾帧刚性插值约束、商业级零AI畸变(Zero AI Distortion)产品包装复合、多Google账号隔离轮询、自动熔断换号与多维度质检交付。当用户提及“谷歌视频生成”、“首尾帧生视频”、“谷歌视频”、“视频工坊”、“google-video-gen”、“产品展示视频”、“宣传片视频制作”时调用。
metadata:
  short-description: 谷歌视频生成与多账号调度系统 (含零AI畸变商业大片管线)
---

# 谷歌视频生成与调度系统 (Google Video Gen / Video Farm)

本技能沉淀了基于 **Google Flow (Veo 3.1 + Nano Banana 2/Imagen 3)** 与 **Gemini 网页版** 的完整工业级视频制作与多账号调度经验。
核心攻克了商业宣传片中“**AI 生图篡改中文包装/商标乱码**”以及“**首尾帧生视频未真正生效/廉价贴图感**”的行业级痛点，实现了真正的 **Zero AI Distortion（零 AI 畸变）商业大片级视频生成管线**。

---

## 🎯 核心能力与适用场景

1. **零 AI 畸变商业大片管线 (Zero AI Distortion Pipeline)**：
   - 官方包装 100% 原始矢量/位图像素级保真，绝不容忍中文乱码、商标走样、规格变异。
   - AI 原生电影级展台与光影环境，彻底摒弃“廉价绿地贴图”。
2. **多规格双引擎视频生成**：
   - **16:9 横屏**（1280x720 24fps 8.0s）：企业宣传片、电商主图横幅、品牌 TVC。
   - **9:16 竖屏**（720x1280 24fps 8.0s）：抖音、小红书、快手、Reels 竖屏短视频。
   - **首尾帧刚性插值约束**：支持指定 Initial Frame 与 End Frame，强制视频首尾画面物理级闭环。
3. **多账号沙箱轮询与自动熔断 (Video Farm)**：
   - 独立 Chrome Profile 隔离，单账号任务互斥运行，物理规避 Google 异常活动风控（`UNUSUAL_ACTIVITY`）。
   - 实时探测账号额度与健康状态，遇冷却（Cooldown）无感跳过并换号重试。
   - 自动优先调度无可见水印（`clean`）的高等级 Profile。
4. **全自动闭环质检与归档 (Automated QA & Delivery)**：
   - `ffprobe` 逐帧级元数据检测（分辨率、帧率、真实播放时长、文件完整性）。
   - OpenCV 归一化互相关 (NCC) 物理首尾帧一致性核验。
   - 自动抽帧生成黄金中帧预览，一键打包交付并生成 Markdown 交付清单。

---

## 📍 本地运行环境与快速入口

- **项目根目录**：`C:\Users\win10\Documents\ChatGPT\视频制作`
- **一键双击启动**：`C:\Users\win10\Documents\ChatGPT\视频制作\启动视频工坊.bat`
- **Web 可视化控制台**：`http://127.0.0.1:8088/`
- **内置辅助脚本库**：`C:\Users\win10\.codex\skills\google-video-gen\scripts\`
  - `composite_product_scene.py`：多尺度模板匹配与像素级首帧复合工具
  - `batch_deliver_videos.py`：批量视频质检抽帧与归档交付工具
  - `api_client.py`：跨窗口/跨会话 Python 调度客户端

---

## 💎 核心方法论：Zero AI Distortion 商业大片 SOP

传统 AI 视频在商业产品展示中最大的问题是：**直接让 AI 画产品，文字必烂；直接把产品抠图贴在纯色/绿地上，质感廉价如山寨。**
本技能沉淀的“三阶工业化作业法”完美解决了这一矛盾：

```
[官方透明包装 PNG] 
       │
       ├─► 1. 参考垫图 / 纯文本 ──► Google Flow (Nano Banana 2) ──► 生成 16:9 电影级光影展台底图
       │                                                                  │
       ├─► 2. OpenCV 多尺度 NCC 模板匹配 ◄─────────────────────────────────┘
       │      (定位展台承重台面物理坐标与精准缩放比例)
       │                                  │
       ▼                                  ▼
[像素级对齐复合] ──────────────────► [无损高质感首帧 prod_*_first_frame.png]
                                          │
                                          ▼
                                    Google Flow (Veo 3.1)
                                    微距推轨/环绕运镜 + 动态粒子氛围
                                          │
                                          ▼
                               [100% 正品包装保真 + 电影级光影流动成片]
```

### 步骤详解与实操指令

#### 第一阶段：AI 电影级展台与光影环境生成
- **核心原则**：提示词专注刻画**展台物理材质、环境景深、丁达尔光束与氛围粒子**，为产品留出中央视觉重心。
- **推荐模型**：`nano2` (Nano Banana 2) 或 `nano-pro`。
- **经典大片 Prompt 模版**：
  - *极简高奢白调*：`极简纯白科技空间，正中央圆形悬浮发光白色大理石展台，柔和摄影棚顶光，后景虚焦晨风麦浪与淡雅绿意，景深极浅，极简留白，电影级写实渲染，商业摄影，16:9`
  - *暗调微观科技*：`高级暗调科技感空间，正中央多面切割发光深色玄武岩基台，幽蓝粒子微光在空气中漂浮，背景微观高科技纳米结构，丁达尔冷光穿透，电影级写实渲染，16:9`
  - *生物基因实验*：`未来生物工程实验室，正中央发光钛金冷金属展台，晶莹剔透玻璃器皿与蓝色DNA全息光斑，微距浅景深，超高清商业质感，16:9`
- **提交命令 (通过 Client)**：
  ```powershell
  python "C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py" image `
    --prompt "极简纯白科技空间，正中央圆形悬浮发光白色大理石展台..." `
    --ref "E:/公司素材/产品包装.png" `
    --aspect "16:9" `
    --model "nano2" `
    --wait
  ```

#### 第二阶段：毫米级承重定位与像素级复合
- **算法核心**：调用 `composite_product_scene.py`。
- **匹配模式 (match)**：若生图时提供了原包装作为参考垫图，AI 展台上会有一个带变形文字的包装雏形。算法采用 OpenCV `cv2.matchTemplate(..., TM_CCOEFF_NORMED)` 在多尺度（高 300px~700px）下扫描，秒级锁定最佳匹配中心坐标与精确缩放比。
- **底座吸附模式 (dock)**：若底图为空展台，算法按画幅比例自动计算中央承重基线，将包装无缝贴于展台支撑面。
- **执行命令**：
  ```powershell
  python "C:\Users\win10\.codex\skills\google-video-gen\scripts\composite_product_scene.py" `
    --scene "video_farm_data/outputs/scene_raw.jpg" `
    --product "E:/公司素材/产品包装.png" `
    --out "video_farm_data/uploads/scenes/prod_first_frame.png" `
    --mode match
  ```

#### 第三阶段：Veo 电影级微距动效与运镜调度
- **动静分离核心原则**：
  - **主体必须绝对静止**：在提示词中明确锁定包装（“中央产品包装保持静止在展台上，形状、材质、文字标签和商标完全保持一致，不发生任何变形与变色”）。
  - **动态赋予镜头与环境**：让镜头缓速推进、微距环绕，让背景光影流动、空气微粒漂浮（“摄影机缓慢顺时针微距环绕推轨，金色丁达尔晨光在空间中流淌，空气中金色微光粒子缓慢升腾，背景虚焦自然律动”）。
- **推荐模型**：`veo-lite` (速度极快、动作稳定) 或 `veo-2.0-generate-001`。
- **提交生成命令**：
  ```powershell
  python "C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py" video `
    --start "video_farm_data/uploads/scenes/prod_first_frame.png" `
    --prompt "中央产品包装静止在展台上，文字与外观保持完全一致不变形。摄影机缓慢微距平滑推进，晨曦柔光自然漫射，空气中浮光微粒缓缓升腾，电影级景深虚化，商业宣传片质感。" `
    --aspect "16:9" `
    --duration 8 `
    --model "veo-lite" `
    --wait
  ```

---

## 🚀 跨会话调用指南与接口速查

在任何 Codex 会话窗口中，只要后台服务启动，即可通过 REST API 或 Python 客户端无感交互。

### 1. 服务静默守护拉起
若 `http://127.0.0.1:8088/` 未响应，在终端中执行：
```powershell
cd "C:\Users\win10\Documents\ChatGPT\视频制作"
Start-Process -FilePath "启动视频工坊.bat" -WindowStyle Hidden
```

### 2. Python 快捷客户端 (`scripts/api_client.py`)
```powershell
# 1. 检查调度器运行状态
python C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py status

# 2. 查询各 Google 账号健康与水印状态
python C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py profiles

# 3. 提交 16:9 横屏生视频任务并等待完成
python C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py video `
  --prompt "镜头平滑微距环绕，光影流动..." `
  --start "D:/my_first_frame.png" `
  --aspect "16:9" `
  --duration 8 `
  --wait

# 4. 提交 9:16 首尾帧刚性插值任务
python C:\Users\win10\.codex\skills\google-video-gen\scripts\api_client.py video `
  --prompt "保持主体一致，平滑过渡到尾帧构图..." `
  --start "D:/start.png" `
  --end "D:/end.png" `
  --aspect "9:16" `
  --duration 8 `
  --wait
```

### 3. 原生 HTTP REST API 规格
- **GET** `/api/overview`：返回当前并发总数、空闲 Profile 数、排队中与完成的任务统计。
- **GET** `/api/profiles`：返回所有账号沙箱列表、`watermark_mode`（`clean` 无水印 / `forced_visible` 有水印）、`cooldown_until` 熔断时间。
- **POST** `/api/tasks/create`（`multipart/form-data`）：
  - `prompt`: 提示词字符串（必填）
  - `engine`: `flow`（默认）或 `gemini_web`
  - `model`: `veo-lite` / `veo-2.0-generate-001` / `veo-3.1-generate-preview`
  - `start_image_path`: 本地首帧图片绝对路径
  - `end_image_path`: 本地尾帧图片绝对路径（可选，尾帧约束）
  - `aspect_ratio`: `16:9` 或 `9:16`
  - `duration_sec`: `8`（秒）
  - `priority`: 优先级整数（默认 10）
- **POST** `/api/tasks/create-image`（`multipart/form-data`）：
  - `prompt`: 生图提示词
  - `model`: `nano2` / `nano-pro` / `imagen-3.0-generate-002`
  - `aspect_ratio`: `16:9` 或 `9:16`
  - `ref_image_path`: 垫图参考原图绝对路径（可选）
- **GET** `/api/tasks/{task_id}`：获取单任务状态与成片产物路径（`output_video_path`）。

---

## 📦 自动化质检与打包交付 (`batch_deliver_videos.py`)

生成结束后，严禁将未经验证的散乱临时文件直接交付用户。必须调用交付归档脚本：
```powershell
python "C:\Users\win10\.codex\skills\google-video-gen\scripts\batch_deliver_videos.py" `
  --src "C:/Users/win10/Documents/ChatGPT/视频制作/video_farm_data/outputs" `
  --out "C:/Users/win10/Documents/ChatGPT/视频制作/video_farm_data/deliveries/正式交付成品" `
  --title "福联生物 核心产品 16:9 商业大片宣传片交付报告"
```
交付脚本将全自动执行：
1. **ffprobe 严格质检**：确认视频是否存在丢帧、编码异常、黑屏，核实实际分辨率（1280x720）与时长（8.0s）。
2. **黄金中帧抽样**：在 4.0s 处自动提取高分辨率 WebP/PNG 预览帧存入 `previews/`。
3. **隔离归档**：将高清视频与合成首帧规范化命名并复制到交付专区。
4. **生成交付台账**：输出图文并茂的 `DELIVERY_REPORT.md`，包含每一款产品的规格、文件体积、场景设计理念与预览链接。

---

## ⚠️ 真实开发沉淀：核心避坑法则 (Hard-Learned Traps)

1. **`gflow-cli --json` 多行缩进输出陷阱**：
   - `gflow-cli` 命令行工具在成功生成时输出的是格式化带缩进的多行 JSON。
   - **错误做法**：使用单行正则 `r"\{.*?\}"` 或 `re.search(r"\{.+\}")` 匹配，会因为换行直接失效报错。
   - **正确做法**：对全部 stdout 进行整块提取或标准 `json.loads`；或者通过专用正则提取目标字段：
     ```python
     m = re.search(r'"local_path":\s*"([^"]+)"', stdout)
     ```
   - **切忌关联最新文件**：绝不能用“扫描 outputs 目录下最新生成的 mp4”来当作任务结果，多账号并发运行时会导致任务错乱关联！

2. **Windows 平台中文路径 `cv2` 静默失败陷阱**：
   - Windows 环境下如果图片路径包含中文字符（如 `E:/公司素材/最新定稿图/促保利素.png`），调用原生 `cv2.imread(path)` 会**静默返回 None**，`cv2.imwrite(path, img)` 会**静默返回 False** 且不创建文件。
   - **唯一标准解法**：必须使用 NumPy 内存缓冲区绕过系统编码：
     ```python
     # 读
     img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
     # 写
     is_ok, buf = cv2.imencode('.png', img)
     buf.tofile(out_path)
     ```

3. **Google Flow 迁移与项目 ID (flow_project_id) 注入**：
   - Google 已将项目由 `labs.google` 迁移至 `flow.google.com`。直接调用不带 `--project-id` 的命令行可能触发旧链路的 tRPC 404 错误。
   - 调度系统已内置自愈逻辑：在拉起 gflow 前探测本地已有 project 或自动传入有效的 `--project-id`，保证稳定走新架构。

4. **单 Profile 串行互斥与风控防线**：
   - 单个 Chrome Profile（账号）同一时刻**绝对只能执行一个任务**，高频连续提交会触发 Google 的 `PUBLIC_ERROR_UNUSUAL_ACTIVITY`。
   - 系统在调度器层面做到了单个 Profile 互斥锁，多并发完全依靠不同独立 Profile 平行调度。

5. **水印模式治理**：
   - Google Flow 账号分为支持关闭可见水印的 `clean` 账号与强制带标的 `forced_visible` 账号。
   - 商业宣传片交付必须确保优先筛选 `watermark_mode == 'clean'` 的 Profile 执行。若账号未关闭可见水印，需在 Chrome 设置中手动关闭并重新校准状态。

---

## 🛡️ 安全合规底线

1. **绝对禁止**将 Chrome Profile 或 Cookie 提取导出、明文打印或提交至公共 Git 仓库。
2. **绝对禁止**使用侵入性浏览器指纹破解或代理轮换对抗手段；严格使用原生 Chrome 沙箱操作。
3. 所有本地任务数据库、视频产物与密钥配置文件已由 `.gitignore` 全面隔离。


---

## ⚡ 全自动端到端成片流水线 (Production Pipeline Engine)

针对“从素材到最终母片耗时近一个小时、每次现场写临时脚本”的痛点，本技能已将全链路固化为**零手写代码**的工业级流水线引擎：

### 1. 核心提速理念
- **算力其实极快**：Veo 3.1 生成 3 个 8s 片段仅需 2 分钟，FFmpeg 渲染母片仅需 8 秒。
- **痛点在“重新发明轮子”**：过去时间全部浪费在现场手写切图、TTS 对齐、运镜滤镜、混音脚本与反复排错上。
- **现已实现流水线化**：输入分镜文件夹/产品图 ➔ 自动切除网格与边框 ➔ 微软 Edge-TTS 毫秒对齐 ➔ Ken Burns 微运镜 ➔ 人声避让混音 (-18dB) ➔ ASS 电影级字幕 ➔ 1080p 母片输出，**全程 2~3 分钟闭环**。

### 2. 两种极简调用方式
- **方式一：Web 可视化控制台 (推荐)**
  - 访问 `http://127.0.0.1:8088/` ➔ 顶部切换至 **【🚀 一键全自动成片 (Pipeline)】**。
  - 填入素材目录（如 `E:\IDM下载\压缩\6BA_45s_science_video_package\6BA_45s_video_package`）。
  - 点击“启动全自动流水线”，界面实时流式输出切图、配音、运镜、字幕进度，完成后直接在网页内播放和下载。
- **方式二：一键命令行 CLI**
  ```bash
  python scripts/pipeline_storyboard_to_master.py --dir "E:\素材目录" --duration 45.0
  ```


---

## 🎬 连续长视频工作台与工业级时间线规范 (Continuity Studio & Timeline IR)

针对“目前只能每次最多生成 10 秒，想要三四十秒甚至一分钟连续剧，市面上长镜头生成到底如何解决画面不飘、镜头如何连到一块”的工业难题，本技能正式确立并上线了**行业标准长视频工业级工作流**：

### 1. 行业标准长视频三大底层真相
1. **物理限制客观存在**：无论是 Runway Gen-3、即梦 (Seedance)、可灵 (Kling) 还是 Google Veo 3.1、Sora，当前扩散模型**单次物理生成窗口均为 5~10 秒**。市面所有 30s/60s 商业长片无一例外都是**多镜头时空衔接装配**。
2. **单纯尾帧接力必然漂移 (Error Accumulation)**：如果一直单向“生成8秒 ➔ 抽尾帧 ➔ 再生成8秒”，微小误差会逐级放大（人物脸部走样、物体比例失衡、光影变质）。
3. **行业成熟标准解法：锚点先行 (Keyframe Anchoring) + 尾帧咬合 + 四维 DNA 锁 + 0算力分镜预演 (Animatic)**。

### 2. 四维连续性锚点资产 (DNA Lock)
在生成前一次性锁定四大核心要素，系统自动将其编译为各分镜头的强一致性 Prompt 前缀：
- **主体锚点 (Subject Anchor)**：锁定角色面容特征、官方产品包装图、瓶型、Logo，严禁重绘或变形。
- **场景锚点 (Scene Anchor)**：锁定统一环境、空间基准与光源色温（如“商业极简金属展台，柔和冷光”）。
- **风格锚点 (Style Anchor)**：锁定摄影画质与影调（如“8K电影级超高清，通透景深，商业广告质感”）。
- **状态锚点 (State Anchor)**：锁定主体空间姿态、朝向与持物手势，防止前后镜头道具错位跳变。

### 3. 五大镜头连接器语义 (Joint Connectors)
在双层时间轴中，镜头与镜头之间的衔接点不再是生硬拼接，而是拥有严谨的物理衔接模式：
| 连接模式 | 适用场景 | 机械行为 |
|---|---|---|
| **cut (影视切镜)** | 场景转换、机位大跳变、景别交替 | 独立渲染，平滑硬切 |
| **continue (尾帧接力)** | 连贯运动、一镜到底、同一动作延续 | 自动提取上一镜最后稳定帧作为当前镜首帧 |
| **anchor (关键帧插值)** | 严格始发地到目的地、商业产品状态转变 | 首帧(入点)与尾帧(出点)两张关键帧刚性插值生成 |
| **re_anchor (重新锚定)** | 连续接力 2~3 段后的视觉校准 | 重新注入四维主体资产，消除累积漂移 (系统自动飘黄预警) |
| **extend (模型续写)** | 云端连续延展 | 调用服务端媒体上下文直接延长 |

### 4. 0 算力 5 秒极速分镜预演 (Animatic)
无需调用任何大模型、无需消耗账号额度与等待排队：
- 点击时间轴右上角 **【⚡ 极速分镜预演 (Animatic)】**；
- 5 秒内全本地合成包含配音、BGM、Ken Burns 微运镜与字幕的粗剪小样，先核验故事节奏与文案时长；
- 确认无误后再点击 **【🚀 确认方案并开始生产】** 调度 Google Flow / Veo 真实算力。

### 5. 跨端通用 Job Spec 协议
支持将当前分镜与参数导出为一份跨机器、可持久化的标准声明式 JSON（点击 **【📄 导出 Job Spec】** 与 **【📥 导入 Job Spec】**），在任何环境均可 100% 精确复现。
