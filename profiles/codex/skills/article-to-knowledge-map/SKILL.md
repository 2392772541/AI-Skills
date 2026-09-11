---
name: article-to-knowledge-map
description: Turn Chinese articles, long-form notes, course transcripts, video learning notes, reports, or Obsidian Markdown into a high-information-density editable knowledge panorama in Excalidraw plus PNG. Use when the user asks for a knowledge panorama, technical infographic, knowledge architecture map, article summary image, one-page overview, 四维图, 全景图, 总结大图, or says to visualize a document like a supplied reference image.
---

# Article to Knowledge Map

Produce the finished editable diagram and rendered image, not an outline or a prompt-only answer.

## Required companion skills

- Use `excalidraw-diagram` for design, JSON structure, rendering, and visual validation.
- Use `obsidian-markdown` when embedding the result into an Obsidian note.
- For video learning notes, keep using `ian-xiaohei-illustrations` for local concept illustrations; the panorama is the whole-note overview and does not replace those illustrations.

## Workflow

### 1. Resolve the source and destination

Read the complete source material. Prefer the user's real file over summaries from conversation history. Infer the output title and slug from the source.

For an existing Obsidian note, create a preview outside the vault first unless the user explicitly asked to commit immediately. After approval, save assets under:

```text
<vault-root>/assets/<note-or-course-slug>/knowledge-map/
```

### 2. Build a content blueprint

Do not reduce a long source to a superficial chapter list. Extract:

- one central argument;
- 12-18 essential modules for substantial material; use 8-11 only when the source is genuinely short;
- the causal, temporal, hierarchical, comparison, feedback, or dependency relationships between modules;
- 6-12 concrete evidence anchors such as timestamps, section names, source paragraphs, examples, or verified facts;
- pitfalls, uncertainty, and boundaries that must remain visible.

Preserve the original source's narrative logic. Separate source claims, structural synthesis, external supplements, predictions, and unresolved uncertainty.

### 2.1 Enforce a learning-density floor

For long-form sources, the panorama must remain useful after the reader zooms in. Do not deliver a sparse overview poster.

- Give every major module at least 2-5 teaching details: mechanism, example, implication, boundary, or action.
- Include at least one terminology strip or local beginner explanation when the source is technical.
- Include at least one risk/uncertainty region and one evidence-anchor region.
- Audit the source headings after drafting; every major source theme must either appear in the diagram or be listed as intentionally omitted with a reason.
- Prefer expanding the logical canvas over shrinking text below comfortable zoom readability.
- Reject the draft if it only repeats chapter titles, one-line slogans, or equal cards without explaining relationships.

### 3. Explain terminology for beginners

Assume the reader is new to the topic. On first use, retain the original English term and add a short Chinese explanation of what it means and why it matters, for example:

```text
HBM（High Bandwidth Memory，高带宽内存：给 AI 芯片快速供给模型数据）
```

Do not overload the graphic. Move secondary definitions into a compact legend when five or more terms need explanation.

### 4. Design a visual argument

Choose structures that mirror meaning instead of placing every module in identical cards:

- sequence -> timeline;
- one cause with many effects -> fan-out;
- many constraints forming one outcome -> convergence;
- hierarchy -> tree or stacked tower;
- transformation -> assembly line;
- iteration -> cycle;
- comparison -> side-by-side contrast;
- uncertainty -> warning boundary.

Use three zoom levels in substantial diagrams:

1. central conclusion visible at a glance;
2. major regions that organize the source;
3. concrete evidence and examples that make the image teach.

Default to a 16:9 white canvas, readable Chinese, semantic color, generous spacing, and selective containers. Use hand-drawn roughness when the user's reference is informal or illustrated.

### 5. Create the editable diagram

Read the installed `excalidraw-diagram` Skill and its required references before generating. Build comprehensive diagrams section by section with descriptive element IDs. Keep every text property human-readable and preserve all terminology exactly.

Deliver both:

```text
<title>.excalidraw   # editable source
<title>.png          # rendered image
```

### 6. Render, inspect, and repair

Use the installed local renderer:

```powershell
uv run python render_excalidraw.py <diagram.excalidraw>
```

Run this from:

```text
C:\Users\win10\.codex\skills\excalidraw-diagram\references
```

View the PNG at original resolution. Repeat the render-view-fix loop for 2-4 passes until:

- no Chinese text is clipped, garbled, or too small;
- no shapes or labels overlap unintentionally;
- arrows land on the intended concepts and avoid unrelated elements;
- the eye follows a clear visual story;
- the central conclusion dominates without hiding detail;
- evidence and uncertainty remain distinguishable;
- the image is readable without opening the source article.
- zoomed regions teach concrete content rather than only naming topics;
- long-form diagrams meet the module, detail, evidence, glossary, and risk density floor.

### 7. Integrate with Obsidian

When committing the approved result, use a vault-root Wikilink:

```markdown
![[assets/<slug>/knowledge-map/<title>.png]]

*AI 生成的知识全景图：根据全文结构化整理，用于理解关系，不替代原始证据。*
```

Keep extracted video frames labeled `原视频截图`, Xiaohei images labeled `AI 生成的小黑解释图`, and panorama images labeled `AI 生成的知识全景图`. Never present generated graphics as source evidence.

Validate every embed and ensure no temporary or absolute processing path remains in the final note.

## Delivery

Report:

- source used;
- central argument and module count;
- editable file path;
- PNG preview path;
- render-review iteration count;
- whether the result is preview-only or already embedded in Obsidian;
- any remaining source uncertainty.
