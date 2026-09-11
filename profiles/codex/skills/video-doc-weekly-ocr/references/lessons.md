# Lessons From 2026-07-07 Weekly Video Recovery

## What Worked

- 1 fps extraction gave enough temporal coverage for scrolling documents.
- Visual-diff selected frames reduced about 11,000 frames to a few hundred OCR targets.
- RapidOCR was fast and adequate for full selected-frame OCR.
- PaddleOCR produced better Chinese on small crops but was too slow for full-frame/full-video passes.
- The most effective link fix was source-frame recropping around the blue link line, upscaling 8x, sharpening, and OCRing only that strip.

## What Failed

- Treating short Douyin fragments as usable links. Links like `https://www.douyin.com/video/765557` click through to empty pages.
- Deleting partial links. They are useful anchors for recovering the full 19-digit ID.
- Scattering `待核对` in the main document. It made the report hard to read.
- Separating confirmed links and alternatives into different reports. Users want them under the same item.
- Letting local paths leak into `备选链接` by parsing OCR notes too broadly.
- Dropping source-visible summary paragraphs under article/resource titles. These gray/quoted paragraphs are part of the weekly report content and should be preserved between the title and URL.
- Treating each missing design/tool link as an isolated search problem. Several adjacent tool items may come from the same source article or weekly page; parse that page once and extract links by heading section.
- Relying on PowerShell `Get-Content` display for Chinese validity. Use Python UTF-8 reads.
- Making the item title itself a hyperlink in Feishu. The desired weekly format is title as title, then a separate raw URL row without a `链接：` prefix.
- Preserving OCR/source numbering in Feishu. Source numbers may duplicate or skip because OCR catches the left outline or a partially scrolled page. Re-number each section from 1.
- Assuming `readonly-block type="iframe"` can be created by `lark-cli`. Existing Feishu docs may fetch these blocks, but CLI write paths are not reliable for creating them.
- Mistaking Feishu's automatic page outline for a visible document-body directory. In the 2026-07-07 source screenshot, the left-side list is Feishu's outline/sidebar, so the main page must use real heading hierarchy.
- Recreating the left outline as a manual two-column table. That makes the body look split, but it prevents Feishu's own outline from matching the source. Prefer `<h2>` section headings plus `<h3>` item headings.
- Merging source-visible `# 工具与科技` items into `# 设计模块`. The 2026-07-07 source screenshot shows these as separate manual-directory sections.
- Using Feishu `<grid>` or `<table>` for the final directory layout. The desired layout is a single main page whose headings generate the left outline.

## Quality Gates

Run these checks on `report/document.md`:

```python
from pathlib import Path
import re
s = Path('report/document.md').read_text(encoding='utf-8')
short = [m.group(0) for m in re.finditer(r'https://www\.douyin\.com/video/(\d+)', s) if len(m.group(1)) != 19]
print('short_douyin', len(short))
print('local_path_leaks', bool(re.search(r'[A-Z]:\\|weekly_.*ocr_work', s)))
print('wait_count', s.count('待核对'))
print('confirmed', s.count('确定链接：'))
print('alternatives', s.count('备选链接：'))
```

Accept only if:

- `short_douyin == 0`
- `local_path_leaks == False`
- main document has no noisy review notes
- Feishu paste version is regenerated after final document changes

Run these checks after writing Feishu XML through `lark-cli`:

- the Feishu XML uses `<h2>` section headings and `<h3>` numbered item headings;
- no fake directory `<table>`/`<grid>`, `<ol>`, or `<li>` is used for the replicated layout;
- Feishu outline fetch contains the source-visible sections and item titles;
- source-visible categories such as `# 工具与科技` are preserved instead of being collapsed into nearby OCR sections.
- for the 2026-07-07 source screenshot, the Feishu replica title should be `且曼内刊 - Vol.283 20260707`, and source-visible sections should be ordered `本周最TOP`, `AI热点`, `AI基础`, `设计模块`, `工具与科技`, `星期快讯`.
- tool detail items with multiple links use labeled rows (`网站:`, `Figma 插件:`, `Github:`) when that matches the source.
- visible source descriptions and preview cards should be represented with gray description paragraphs, official OG/preview images via `<img href="...">` when available, and a Feishu `<bookmark>` block for clickable preview context.
- no-link design/tool items have either source-frame evidence, or a recorded source-page section extraction attempt using the matched heading and local links under it.
- title lines and raw URL link lines are separate;
- link count matches confirmed plus alternative links from the source document;
- do not require `readonly-block` to be present.

## Suggested Final Structure

```markdown
## AI热点

7. 什么时候买内存？我找到了答...
确定链接：https://www.douyin.com/video/7655741484096912719

14. Grill-me--让AI反问你澄清需...
确定链接：https://github.com/mattpocock/skills
备选链接：https://example.com/another-plausible-source
```

Do not use this in the main report:

```markdown
链接：https://www.douyin.com/video/765557
> 链接待核对：原始 OCR ... 来源 ...
```

Keep that evidence in review/completion files instead.

## Feishu CLI Format Lesson

Preferred Feishu XML page shape:

```xml
<title>周报标题</title>
<h2><span text-color="red"># 设计模块</span></h2>
<h3><span text-color="blue">1.</span> 条目标题</h3>
<p><a href="https://example.com">https://example.com</a></p>
```

Preferred item shape:

```xml
<h3><span text-color="blue">1.</span> 盘点125年诺贝尔文学奖</h3>
<p><span text-color="gray">来源页面中标题下方的摘要说明...</span></p>
<p><a href="https://www.douyin.com/video/7560248106559147323">https://www.douyin.com/video/7560248106559147323</a></p>
<p><span text-color="gray">备选：</span><a href="https://example.com">https://example.com</a></p>
```

Preferred multi-link tool item shape:

```xml
<h3><span text-color="blue">8.</span> 高质量SVG图标库: Reicon</h3>
<p><span text-color="gray">工具说明段落...</span></p>
<p>网站: <a href="https://reicon.dev">https://reicon.dev</a></p>
<p>Figma 插件: <a href="https://www.figma.com/community/plugin/1652983191908763066">https://www.figma.com/community/plugin/1652983191908763066</a></p>
<p>Github: <a href="https://github.com/dqev/reicon">https://github.com/dqev/reicon</a></p>
<p><bookmark name="Reicon Figma 插件" href="https://www.figma.com/community/plugin/1652983191908763066"></bookmark></p>
<img href="https://reicon.dev/og-image.png?v=4" width="700" name="Reicon preview"/>
```

Avoid this unless explicitly requested. It is wrong for the source-style Feishu weekly layout because it uses a Feishu ordered list and makes the title itself a link:

```xml
<ol><li seq="1"><a href="https://www.douyin.com/video/7560248106559147323">盘点125年诺贝尔文学奖</a></li></ol>
```

Useful command sequence:

```powershell
python scripts/make_feishu_weekly_xml.py report/document.md report/feishu_ready.xml
lark-cli docs +create --api-version v2 --as user --content "@report/feishu_ready.xml"
lark-cli docs +fetch --api-version v2 --doc "<test-doc-url>" --scope full --detail full --doc-format xml --format json
lark-cli docs +update --api-version v2 --as user --doc "<target-doc-url>" --command overwrite --content "@report/feishu_ready.xml"
```

## Additional Lessons From Design Module Audit

- A section with only one item is suspicious when the visible source document shows a long category later in the scroll. Re-scan source OCR for terms associated with that section.
- Design module terms to search for: `????`, `Figma`, `LottieFiles`, `Figma Motion`, `????`, `??`, `Icones`, `????`, `Landing Page`, `OpenPencil`, `Reicon`, `MCP / Claude Design / Codex / Google Stitch`.
- Do not assume every item after a section header belongs to that section forever. Long scrolls can show left outline, body content, and old/new section labels together. Use source-frame order and semantic terms to regroup.
- For missing links in tool/resource lists, look for the upstream source page and extract links by section heading. Example: Moonvy design weekly pages place `灵感网站推荐`, `Gradient Lab`, `Posts.design`, `Reicon`, and other entries in one article; each heading's body may contain multiple labeled links such as `官网`, `X 推文`, `GitHub`, or `Figma 插件`.
- When moving items between sections, regenerate the Feishu paste version immediately.
- After regrouping, run a fresh audit: section counts, no-link items, short Douyin count, path leak count, and `???` count.

## Lessons From 2026-07-14 Completeness And Feishu Audit

- The first report had the correct numbered-item count but still omitted the entire unnumbered `星球快讯` section. Compare section/subsection manifests, not just item totals.
- Generic outline text can hide a recoverable preview resource. `AI大事件` had an embedded Bilibili card whose exact title exposed the correct BV link.
- Public-page verification also corrects OCR wording. Examples included a missing question mark, `后训` being expanded incorrectly to `后训练`, and hyphen/spacing differences.
- A source-frame link must override a web alternative when ownership is clear. Keep the web result as an alternative only when useful.
- URL case matters. WeChat paths can break when one character changes case; compare against the source frame exactly.
- A Feishu local video attachment may have no external URL. Use a clean crop of the attachment card under the item and count it as a screenshot fallback.
- Track five completion states separately: source link, exact-title supplement, alternative, screenshot fallback, unresolved.
- Verify duplicates after all supplements, including alternative URLs. Use normalized exact-title and high-similarity checks, not only literal string equality.
- Feishu may escape unsupported `<quote>` tags. Use gray `<p><span text-color="gray">...</span></p>` summaries.
- Insert local images with `docs +media-insert`, then move the returned image block below the intended heading with `block_move_after`.
- Do not assume a newly created document belongs in Drive root. Resolve the requested folder token, move the document, and verify its folder-scoped presence. Search indexing can lag behind a successful move.

## Lessons From 2026-07-21 Screenshot Evidence Repair

- A fallback screenshot is evidence for one item, not decoration. Never reuse the same whole-page screenshot under multiple missing-link items.
- Produce a tight crop for each item and name it uniquely, for example `review_mystery.jpg` or `review_item_31.jpg`.
- Every fallback must carry a manual-review record: source video part, exact `HH:MM:SS` timestamp, source frame path, crop region, search status, and evidence type.
- Use evidence types explicitly:
  - `link_visible`: a complete URL is visible and owned by the item;
  - `preview_card`: a card title/provider is visible but the raw URL may still require recovery;
  - `title_only`: wording/numbering is visible, but the image is not link evidence.
- For `title_only`, state `不作为链接证据` in the user-facing review note. Do not imply that a black outline title proves no URL exists elsewhere.
- In Feishu, require the order `item heading -> matching crop -> review note -> next item`. Uploading an image to the document end is not completion.
- After replacement, fetch the affected range with block IDs and verify three things: all new filenames exist once, old generic images are absent, and each image is inside the correct item boundary.
- Strict audit should fail when a screenshot path is reused by multiple fallback items or when a fallback lacks a timestamped evidence-boundary note.
