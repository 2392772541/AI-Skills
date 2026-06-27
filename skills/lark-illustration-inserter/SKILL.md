---
name: lark-illustration-inserter
description: Generate article illustrations for Feishu/Lark docs and insert them into the right document positions. Use when the user provides a Feishu/Lark document URL, token, wiki node, screenshot-selected doc, or pasted article content and asks to generate/insert images, illustrations, shot-list based visuals, 小黑/Ian style drawings, or place generated images into a specified Feishu document.
---

# Lark Illustration Inserter

## Purpose

Turn a Feishu/Lark document or pasted article into a small set of article illustrations, generate the images, upload them with `lark-cli`, and place each image after the most relevant paragraph or block.

This skill orchestrates other capabilities. Use `ian-xiaohei-illustrations` for Ian 小黑 style planning/generation when the user wants that style. Use `lark-doc` / `lark-drive` skills for Feishu document reading, search, upload, and editing.

## Default Workflow

1. Resolve the target document.
   - If the user gives a docx/wiki URL or token, inspect or fetch it directly.
   - If the user gives only a screenshot-selected document title, search Drive by title and choose the exact match. Prefer `docx` unwrapped from `wiki`.
   - If multiple close matches exist, ask one concise clarification before writing.

2. Read the relevant content.
   - For known keywords or sections, use targeted `docs +fetch --scope keyword|section --detail with-ids`.
   - For unknown structure, fetch outline first, then targeted sections.
   - Preserve block IDs for insertion anchors.

3. Plan the illustrations before generating.
   - If the user has not already approved a shot list, produce a concise 4-8 item shot list.
   - Each shot must include: target anchor, theme, core idea, structure type, what 小黑 does, suggested elements, and Chinese labels.
   - If the user says "都做" or directly asks to generate, proceed without another confirmation.

4. Generate one image per shot.
   - Use `image_gen`; do not combine multiple shots into one image.
   - For Ian 小黑 style, follow `ian-xiaohei-illustrations` prompt rules: 16:9, pure white, black hand-drawn lines, sparse red/orange/blue Chinese handwritten notes, lots of whitespace, 小黑 performing the core action.
   - Avoid left-top titles, PPT/course-slide diagrams, dense flowcharts, commercial vector style, and cute mascot posters.

5. Save local copies.
   - Copy generated images into the current workspace under:
     `assets/<doc-or-article-slug>-illustrations/`
   - Name files in insertion order, e.g. `01-user-say-vs-do.png`.
   - Leave original generated files in place.

6. Insert into Feishu/Lark.
   - Read `references/lark-cli-insertion.md` before writing.
   - Upload local images with `docs +media-insert` from the image directory using relative paths.
   - Move each created image block with `docs +update --command block_move_after` to the selected anchor block.
   - Insert from bottom-to-top only if using direct insertion commands that affect sibling indexes. If uploading to the end and moving by block ID, normal shot order is fine.

7. Verify.
   - Fetch each anchor area with `--detail with-ids --context-after 2`.
   - Confirm every expected `<img>` block appears after the intended paragraph/block.
   - Report what was inserted, where, and the local asset directory.

## Anchor Selection Rules

Prefer anchors at the end of the idea being illustrated, not at the start of a section.

- For a short highlighted conclusion, insert after that highlighted paragraph.
- For a multi-paragraph example, insert after the example block/pre/code block.
- For a list, insert after the list if the illustration summarizes the whole list.
- For a quote/callout, insert after the quote/callout if the illustration explains the quoted idea.
- Avoid inserting between a heading and its first explanatory paragraph unless the image introduces the section.

## Safety And Recovery

- This is a write workflow. The user asking to insert into their specified Feishu document is sufficient intent for normal `docs +update` write commands.
- Do not use high-risk destructive commands. If `lark-cli` returns `confirmation_required`, stop and ask.
- If media upload succeeds but movement fails, keep the uploaded image blocks and continue diagnosing. Do not delete without explicit user approval.
- If absolute file paths are rejected by `lark-cli`, change `workdir` to the image directory and pass `--file .\name.png`.
- If search cannot uniquely identify a screenshot-selected doc, ask for the document URL/token.

## Useful References

- `references/lark-cli-insertion.md`: concrete CLI sequence for search, inspect, fetch, upload, move, and verify.
