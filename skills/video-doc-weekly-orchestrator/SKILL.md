---
name: video-doc-weekly-orchestrator
description: Orchestrate a recurring weekly report workflow from local screen-recorded videos into one verified Feishu document in a user-specified Drive folder, with persistent issue memory, deep link recovery, duplicate-document prevention, screenshot fallbacks, and post-publish location/content verification. Use when the user says 每周周报、视频周报、补全链接、联网找链接、写入飞书、放到指定目录、避免重复文档, or asks to make the weekly process automatic and stop repeating prior corrections.
---

# Weekly Report Orchestrator

This is an orchestration layer. It composes the existing `video-doc-weekly-ocr`, `agent-reach`, `lark-doc`, and `lark-drive` skills. It does not copy their OCR, web-search, document, or Drive syntax.

## Use / Do Not Use

Use for recurring weekly reports reconstructed from one or more local videos and published to Feishu. Use when the user expects prior mistakes to be remembered and prevented.

Do not use for a one-off transcript summary, ordinary meeting minutes, or editing an already-finished Feishu document without new source videos. Route those to the narrower skill.

## Fixed Contract

Inputs:

- current week's video files or source screenshots;
- the destination Drive folder, resolved by name or supplied URL;
- prior issue ledger and any existing same-week Feishu documents.

Outputs:

- one local `weekly_YYYY_MM_DD/report/document.md`;
- one `document_feishu_paste.md`, XML, media manifest, and audit;
- one Feishu docx in the requested folder;
- a post-publish verification record containing document token, revision, folder token, item/link counts, fallback count, and duplicate checks.

## Mandatory Order

1. **Preflight and memory**
   - Read this skill, `video-doc-weekly-ocr`, `agent-reach`, `lark-doc`, and `lark-drive`.
   - Load `.weekly-report-state/issue-ledger.json` if present; otherwise create it.
   - Record the current week's source paths and hash/size metadata. Never reuse older week's OCR as content.
   - Resolve the destination folder before any document create/update. Store `folder_token` and canonical folder URL.

2. **Duplicate guard**
   - Search Drive by the weekly title and inspect all same-title docx results.
   - If a complete same-week doc exists, update that token; do not create another.
   - If multiple exist, choose the one with the newest verified content and move incomplete duplicates to a reversible `维护` subfolder. Never delete without explicit user confirmation.

3. **Source reconstruction**
   - Delegate extraction/OCR/outline-body diff/link recovery to `video-doc-weekly-ocr`.
   - Apply every applicable rule from the issue ledger before declaring a link missing.
   - Use `agent-reach` for exact-title and platform searches. Search Bilibili, Douyin, Xiaohongshu, and general web as available, respecting each platform's cooldown circuit breaker.

4. **Evidence classification**
   Every item must end in exactly one state:

   - `linked_source`: URL directly visible in the owning source frame or exact public ownership closure;
   - `linked_public_match`: exact public title/page match, visibly labeled as non-source-original;
   - `screenshot_fallback`: item-owned crop with source part/timestamp and explicit `不作为链接证据`;
   - `unresolved`: only after the deep-search gate and source-frame recheck fail. Unresolved items block publication unless the user explicitly accepts them.

   A URL near a title is not ownership evidence. Adjacent-item URLs, generic-topic results, and short Douyin URLs are rejected.

5. **Local gates before Feishu**
   Run `scripts/validate_weekly_delivery.py <report-dir>`. Publication is blocked when any of these are true:

   - duplicate URLs or title collisions;
   - malformed/short Douyin URLs;
   - unresolved items;
   - screenshot fallback without source timestamp, evidence boundary, or unique item-owned path;
   - local processing paths leaked into the clean document;
   - audit counts differ from the current document build.

6. **Feishu write and location**
   - Generate XML from the clean local document.
   - Update the chosen existing docx, or create exactly one document only when no same-week doc exists.
   - Insert fallback images under their owning headings, then fetch with IDs and verify heading -> image -> review note -> next item order.
   - Move/verify the docx in the resolved destination folder. Folder placement is part of success, not a later cleanup.

7. **Post-publish verification and memory**
   - Fetch the live doc and folder listing. Verify title, revision, folder token, all primary URLs, fallback media, item order, and duplicate count.
   - Append failures and fixes to `.weekly-report-state/issue-ledger.json` with date, symptom, root cause, prevention rule, and verification command. Do not record cookies, tokens, or secrets.
   - A successful API response without live fetch and folder verification is `partial`, never complete.

## Issue Ledger Rules

Use `references/issue-ledger.md`. The ledger is a prevention checklist, not a narrative diary. Each entry must become one of: a preflight check, a script assertion, a required search query family, or a post-publish verification.

Known entries from the 2026-08-25 run:

- resolve the Drive folder before writing;
- search for same-title existing docs before create;
- do not bind a URL from the next/adjacent item;
- do deep platform search before screenshot fallback;
- distinguish source URL, public match, and title-only screenshot;
- move the fallback image under its owning heading;
- verify the live folder listing after moving the doc.

## Anti-Skipping Rules

- “时间紧” does not waive the duplicate guard or live verification.
- “链接看起来像” is not ownership evidence; require source-frame binding or exact public closure.
- “上传成功” is not media placement proof; fetch block order.
- “本地审计通过” is not Feishu publication proof; fetch the live document and folder.
- Never announce all links complete while any item is only a screenshot fallback; report the split explicitly.

## Eval Expectations

Positive prompts route here: “每周用视频做周报，自动补链接并放进水球泡周报，记住上周的问题”。

Negative prompts must route elsewhere: “把这段会议录音总结成三点”；“只修改飞书文档中的一个错别字”。

Required evidence for a completed run: local audit JSON, issue-ledger update, live Feishu revision, canonical folder token, folder listing showing exactly one current-week final doc, and a fetched block-order check for every fallback image.
