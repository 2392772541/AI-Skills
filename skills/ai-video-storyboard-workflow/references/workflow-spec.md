# 26Flow / MuseFlow 自适应流水线工作流规范 (Adaptive Pipeline Flow Specification)

## 1. 核心架构与直通拓扑 (Pipeline Topology)
工作流坚决摒弃早期“生图与视频分离、端口悬空、手动另存上传”的断裂割裂模式，统一采用正统工业级直通流水线（Pipeline Flow）：

```
[01·生图提示词] ──(text)──> [01·生成图片 (预置底图)] ──(image)──┐
                                                                ▼
[01·运镜提示词] ──(text)─────────────────────────────────> [01·生成视频] ──(video)──> [时间线 (严格升序 1~N)]
                                                                │
                                                            (endFrame 递归传递)
                                                                ▼
                                                          [02·生成视频 参考端口]
```

## 2. 动态 N 镜节点与连线法则 (Mathematical Formula)
针对任意镜头总数 $N$（如 8 镜、12 镜、15 镜、18 镜等）：
- **节点总数公式**：$4N + 1$
  - 生图提示词节点 (`prompt`)：$N$ 个，ID 规则为 `node_shot_{i:02d}_img_prompt`
  - 生图节点 (`generateImage`)：$N$ 个，ID 规则为 `node_shot_{i:02d}_img_gen`，内嵌对应 `shot_{i:02d}.png` 的独立 Base64
  - 运镜提示词节点 (`prompt`)：$N$ 个，ID 规则为 `node_shot_{i:02d}_v_prompt`
  - 视频生成节点 (`generateVideo`)：$N$ 个，ID 规则为 `node_shot_{i:02d}_video`
  - 全局时间线节点 (`timeline`)：1 个，ID 为 `node_timeline`
- **连线总数公式**：$3N$
  - `edge_prompt_to_img_{i:02d}`：生图词 ➔ 生图 (`text` -> `prompt`)
  - `edge_img_to_video_{i:02d}`：生图 ➔ 视频 (`image` -> `reference`)
  - `edge_prompt_to_video_{i:02d}`：运镜词 ➔ 视频 (`text` -> `prompt`)

## 3. 时间线严格保序 (Strict Timeline Order)
时间线 `clipOrder` 必须动态生成为升序数组：
`["node_shot_01_video", "node_shot_02_video", ..., "node_shot_{N:02d}_video"]`，
锁死整片时间线播放次序，彻底杜绝镜头错位与乱序。

## 4. 三道物理断言防线 (Three Physical Guardrails)
在导出工作流 JSON 之前，装配脚本必须执行：
1. **连续性断言**：`shot_01.png` 到 `shot_{N:02d}.png` 必须完整存在，且编号连续；
2. **排重唯一性断言**：计算所有底图的 MD5 哈希，严禁存在完全一致的重复图片；
3. **拓扑数量断言**：严格核实 `len(nodes) == 4N + 1` 与 `len(edges) == 3N`。
