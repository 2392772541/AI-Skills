---
name: build-video-course-notes
description: Turn one or more uploaded/local course videos into a verified Obsidian Markdown learning guide using FFmpeg frame extraction, visual keyframe selection, Chinese speech transcription, OCR, screenshot embedding, practical synthesis, pitfalls, templates, and a reusable AI prompt. Use when the user asks to analyze video lessons, make study notes from videos, extract course screenshots, reconstruct PPT content, create an Obsidian course note, or says “参考之前的给我弄” for a video-learning workflow.
---

# Build Video Course Notes

Produce the finished files, not a plan. Treat uploaded videos as the source; do not ask the user to repeat local paths when attachments are available.

## Required inputs

Discover these from the request and local context:

- source videos or attachments;
- note destination;
- central image/assets destination;
- Obsidian vault root.

Infer the course title from filenames/content when omitted. Ask only when a destination or vault root cannot be discovered safely.

## Workflow

### 1. Inspect and stage

1. Resolve every uploaded video to a readable local file.
2. Sort episodes by numeric filename prefix, then natural filename order.
3. Run `ffprobe` and record file, duration, resolution, codecs, and audio presence.
4. Create a per-course work directory outside the vault:

```text
course_work/
  frames_1s/P01/
  keyframes/P01/
  audio/
  transcripts/
  ocr/
  report/
```

Preserve source videos. Do not overwrite unrelated vault files.

### 2. Extract evidence

Extract 1 fps frames:

```powershell
ffmpeg -hide_banner -nostdin -y -i INPUT -vf fps=1 -q:v 2 OUTPUT\frame_%06d.jpg
```

Run `scripts/select_keyframes.py` for each episode. Start with `--diff 7.5 --min-gap 2 --max-gap 15` for 1080p slide-heavy courses; tune after visually reviewing contact sheets.

Keep frames showing:

- complete frameworks, tables, models, cases, summaries, or UI steps;
- the final state of progressively revealed slides;
- sufficient context to prove ownership and meaning.

Reject black frames, transitions, blur, presenter-only repetition, and near-duplicates.

### 3. Transcribe and OCR

Extract mono 16 kHz PCM WAV:

```powershell
ffmpeg -hide_banner -nostdin -y -i INPUT -vn -ac 1 -ar 16000 -c:a pcm_s16le OUTPUT.wav
```

Run `scripts/transcribe_media.py`. Prefer GPU when available. If CUDA fails, inspect the actual missing DLL/runtime error, then use a local CUDA library path or fall back to CPU. Keep timestamped JSON and Markdown per episode.

Run `scripts/ocr_keyframes.py` on selected frames. Use RapidOCR for the bulk pass; use targeted crops or PaddleOCR only for unclear high-value text.

Cross-check:

- slide text against OCR;
- spoken explanations against transcript;
- unclear names/numbers against the original frame;
- repeated slides across adjacent episodes.

Never elevate OCR noise or ASR guesses into facts.

### 4. Synthesize the note

Read `references/note-outline.md` before drafting.

Write a self-contained learning guide, not a transcript dump. Separate:

- course-stated content;
- synthesis from course context;
- practical extensions;
- uncertain or unverified claims.

For each major topic explain the concept, meaning, steps, use cases, non-use cases, example, screenshot, pitfalls, and practical extension when relevant.

Include:

- course overview and evidence-processing method;
- a knowledge map or Mermaid flow when relationships benefit from it;
- detailed chapter notes;
- 1-8 generated Xiaohei explanatory illustrations, selected by note length and genuine cognitive value, using the installed `ian-xiaohei-illustrations` Skill;
- executable SOP;
- pitfalls/hidden risks with mitigations;
- reusable tables/checklists/templates;
- a master AI prompt that applies the course method;
- final operational checklist.

Browse only when a meaningful gap requires current or authoritative supplementation. Prefer primary sources, cite links near claims, and label additions as external supplements.

### 4.1 Generate Xiaohei explanatory illustrations

After the note structure and core claims are stable, use `ian-xiaohei-illustrations` to turn the strongest cognitive anchors into illustrations. Default to 4-8 images for a substantial note and 1-3 for a short note; do not add decorative filler.

Keep the evidence boundary explicit:

- extracted frames are source evidence from the video;
- Xiaohei images are AI-generated explanations of concepts;
- generated images must never substantiate quotations, numbers, interface states, or course claims.

Generate every image separately, visually inspect it, and regenerate images with broken Chinese text, unclear metaphors, crowded layouts, or off-style characters.

### 5. Place note and images

Copy only the final selected screenshots into:

```text
<vault-root>/assets/<course-slug>/
```

Save generated Xiaohei illustrations separately under:

```text
<vault-root>/assets/<course-slug>/illustrations/
```

Use ordered descriptive names such as:

```text
01-overview.jpg
02-core-model.jpg
03-case-study.jpg
```

Place the note in the user-specified note directory. Embed images with vault-root Wikilinks:

```markdown
![[assets/<course-slug>/01-overview.jpg]]

*图 1：内容说明（P1，约 01:20）*
```

Use explicit captions so readers cannot confuse evidence with interpretation:

```markdown
![[assets/<course-slug>/illustrations/01-core-concept.png]]

*AI 生成的小黑解释图：核心概念的通俗化表达，不是原视频画面。*
```

Do not put absolute paths, `file://` URLs, processing paths, or temporary filenames in the final note.

When moving an already-created note, preserve the vault-root Wikilinks and relocate the image folder to the central assets directory. Avoid silent overwrite: compare hashes/content and version conflicting files.

### 6. Validate before delivery

Run `scripts/validate_obsidian_note.py` with the vault root and note path.

Require:

- note exists in the requested directory;
- every `![[...]]` embed resolves from the vault root;
- missing embeds = 0;
- all final screenshots exist and are readable;
- all generated Xiaohei illustrations exist, are readable, have explicit AI-generated captions, and are visually inspected;
- YAML frontmatter exists;
- fenced code markers are balanced;
- at least three screenshots are visually inspected;
- no stale note/image copy remains after an explicit relocation;
- reported counts match actual files.

If validation fails, fix and rerun it. Do not report completion from copy success alone.

## Delivery

Report concisely:

- video count and total duration;
- extracted-frame and selected-keyframe counts;
- embedded screenshot count;
- generated Xiaohei illustration count;
- core note modules;
- clickable absolute note path;
- clickable absolute image-directory path;
- missing-embed count;
- any item that still needs human confirmation.

## Bundled scripts

- `scripts/select_keyframes.py`: Unicode-safe OpenCV visual-difference selection.
- `scripts/ocr_keyframes.py`: RapidOCR batch extraction with provenance.
- `scripts/transcribe_media.py`: timestamped faster-whisper transcription.
- `scripts/validate_obsidian_note.py`: deterministic Obsidian embed and Markdown checks.
