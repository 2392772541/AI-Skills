# Skill 产品决策记录

- 日期：2026-08-25
- 需求：把每周视频周报制作、联网补链、截图 fallback、飞书写入和目录归档固定成一次执行，并自动吸收上周错误。
- 本机候选：`video-doc-weekly-ocr`（核心流程已覆盖）；`agent-reach`（联网检索）；`lark-doc`（正文写入）；`lark-drive`（目录/重复文档治理）。
- 外部候选：未调研；本机已有能力覆盖核心工作，不满足外部引入前提。
- 重复与冲突：直接新建完整 OCR Skill 会复制现有能力；采用编排层只记录顺序、状态、门禁和记忆，不复制子 Skill 正文。
- 评分：87/100（匹配 18/18，互补 9/10，发现契约 11/12，工作流强制 14/15，证据化 12/12，Eval 9/12，安全维护 9/10，可移植 5/6，来源 0/5；候选为本机自有组合，不计外部来源分）。
- 决策：COMPOSE
- 推荐架构：`video-doc-weekly-orchestrator` -> `video-doc-weekly-ocr` -> `agent-reach` -> `lark-doc` + `lark-drive`。
- 测试计划：本地交付门禁、Python 编译、正/负向路由样例、旧问题回归、skillctl 路由测试。
- 风险：候选尚未晋级正式技能；平台登录/风控状态可能变化；删除重复文档仍需单独确认。
- 回滚方法：不执行 promote --apply；删除或移走 `D:\AI-Skills\incoming\video-doc-weekly-orchestrator` 即可回滚，不影响现有正式 Skill。
- 最终状态：候选通过本周真实产物验证，待用户确认后晋级。
