# Lark CLI Insertion Workflow

Use these commands as patterns. Always read the installed `lark-doc` and `lark-shared` skills when doing live Feishu writes.

## Resolve A Screenshot-Selected Document

Search by exact or distinctive title:

```powershell
lark-cli drive +search --as user --query '文档标题' --only-title --doc-types 'docx,wiki,doc' --page-size 10 --format json
```

If the result is a wiki URL, unwrap it:

```powershell
lark-cli drive +inspect --as user --url 'https://my.feishu.cn/wiki/xxx' --format json
```

Use `data.token` when type is `docx`, or `data.wiki_node.obj_token` after wiki unwrapping.

## Fetch Candidate Anchors

Use keyword search when the desired insertion points are known from the shot list:

```powershell
lark-cli docs +fetch --api-version v2 --as user --doc '<DOCX_TOKEN>' `
  --scope keyword `
  --keyword '关键词1|关键词2|关键词3' `
  --context-before 2 --context-after 3 `
  --detail with-ids --format json
```

Use outline first when the document structure is unknown:

```powershell
lark-cli docs +fetch --api-version v2 --as user --doc '<DOCX_TOKEN>' `
  --scope outline --max-depth 3 --detail with-ids --format json
```

## Upload Images

`docs +media-insert` requires a relative file path. Set the working directory to the image folder:

```powershell
lark-cli docs +media-insert --as user --doc '<DOCX_TOKEN>' `
  --file '.\01-topic.png' --width 800 --align center --format json
```

Record the returned `data.block_id` for each uploaded image. The shortcut initially appends the image to the document end.

If CLI logs wrap JSON with progress text, extract the final JSON object from the output manually. Do not assume upload failed just because naive JSON parsing failed.

## Move Uploaded Image Blocks

Move each uploaded image block after the intended anchor block:

```powershell
lark-cli docs +update --api-version v2 --as user --doc '<DOCX_TOKEN>' `
  --command block_move_after `
  --block-id '<ANCHOR_BLOCK_ID>' `
  --src-block-ids '<IMAGE_BLOCK_ID>' `
  --format json
```

Suggested map format while working:

```text
01 image_block -> after anchor_block // theme
02 image_block -> after anchor_block // theme
```

## Verify Placement

Fetch around anchors:

```powershell
lark-cli docs +fetch --api-version v2 --as user --doc '<DOCX_TOKEN>' `
  --scope keyword `
  --keyword '锚点关键词1|锚点关键词2' `
  --context-before 1 --context-after 2 `
  --detail with-ids --format json
```

Confirm the expected `<img id="...">` block appears immediately after, or within the intended context after, each anchor.

## Common Pitfalls

- PowerShell may split comma-separated CLI values. Wrap comma lists in single quotes, e.g. `--doc-types 'docx,wiki,doc'`.
- Absolute paths are rejected for `--file`; use relative paths from the image directory.
- A wiki search result title may point to a docx object token hidden inside `icon_info` or returned by `drive +inspect`.
- For multi-paragraph examples stored as `<pre>` or `<blockquote>`, use that whole block ID as the anchor.
- Never delete uploaded media blocks as cleanup unless the user explicitly approves deletion.
