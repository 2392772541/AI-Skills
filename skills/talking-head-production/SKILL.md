---
name: talking-head-production
description: 编排口播视频的转写、内容粗剪、受控视觉包装、预览验收与最终渲染。用户提供口播视频或素材目录并要求自动剪辑、删除停顿口癖、生成字幕、添加克制动画或输出竖版/横版时使用。该 Skill 只负责编排，不复制 video-use、chuk-motion 或 Remotion 的实现规则。
---

# Talking Head Production

## 固定路径

- 工作台：`E:\工程项目\codex项目合集\个人用\talking-head-studio`
- 内容剪辑候选：`D:\AI-Skills\incoming\video-use`
- 视觉系统候选：`D:\AI-Skills\incoming\chuk-motion`
- 默认配置：`talking-head-studio\config\profile.yaml`
- 组件政策：`talking-head-studio\config\component-policy.json`

## 工作流

1. 保留原素材，创建独立项目目录。
2. 执行词级转写并复用缓存。
3. 生成中文 `edit-plan.md` 和 `edl.json`，先让用户确认。
4. 生成 `animation-plan.json`，只允许组件政策中的 allowed 组件；reviewRequired 必须说明理由；disabled 一律拒绝。
5. 先渲染 720p 预览和联系表，不直接输出最终版。
6. 检查切口、爆音、字幕同步、安全区、字体、颜色、动画密度和组件重叠。
7. 用户确认后才渲染最终版。

## 失败处理

- 缺 ElevenLabs Key：完成素材盘点和项目创建，停止真实转写，不猜测密钥。
- chuk-motion 不可用：使用本机 `remotion-video-builder` 和相同组件政策降级实现。
- 动画组件不存在：退回 `TextOverlay`、`ImageContent` 或纯人物画面，禁止临时生成花哨组件。
- 高清渲染失败：保留 EDL 和预览，输出完整日志与重试命令。

## 验收

- 原素材未覆盖。
- 字幕最多两行、按语义断行并最后压制。
- 每个剪口有 padding 和音频 fade。
- 禁用组件未出现。
- 预览和联系表均完成审查。
- 最终输出尺寸、帧率、响度与配置一致。
