# Obsidian course-note outline

Use the smallest structure that preserves the course. Omit irrelevant sections rather than padding them.

```markdown
---
title: <course>｜学习笔记与实战指南
aliases:
  - <short title>
tags:
  - 学习笔记
  - <domain>
source: <course>
created: YYYY-MM-DD
status: 已完成
---

# <course>｜学习笔记与实战指南

> [!abstract] 一句话结论
> <the course's central idea and decision value>

## 这份笔记怎么来的
- video count and duration
- frame/keyframe counts
- OCR/ASR cross-check method

## 课程知识地图
<overview and optional Mermaid>

## <chapter/topic>
<concept, plain-language explanation, procedure, applicability>

![[assets/<course-slug>/NN-description.jpg]]

*图 N：<what it proves>（Pxx，约 MM:SS）*

> [!warning] 坑点
> <failure mode and mitigation>

## 可执行 SOP
<input → action → output → decision rule → verification>

## 坑点与隐患总表
| 坑点/隐患 | 可能后果 | 识别方式 | 处理方式 |
|---|---|---|---|

## 可复用模板
<evidence table, analysis sheet, decision log, report template>

## AI 总提示词
<role, inputs, steps, evidence rules, prohibitions, output, acceptance>

## 最终检查清单
- [ ] ...
```

Quality rules:

- Lead with conclusions.
- Make the note useful without replaying the videos.
- Keep facts, interpretations, inferences, and recommendations distinct.
- Attach each important screenshot near the text it supports.
- Give source episode and approximate timestamp in captions.
- Define scope, failure modes, privacy/copyright/authorization risks, and version drift.
- Do not use a model/framework merely because it appears in the course; explain when it helps.
- End recommendations with owner, deadline, dependency, and validation metric when the topic is operational.
