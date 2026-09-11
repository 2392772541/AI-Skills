---
name: commerce-material-archive
description: Archive product media into E:\2.国际站资料 or E:\1.1688资料 product folders and update 视频任务统计.md plus 更新日志.md. Use when the user asks to put videos/images/main images/detail pages into corresponding international-site or 1688 folders, update logs, charts, icons, 看板, 图标, 统计, or mentions 国际站资料, 1688资料, 主图, 英文详情, 中文详情, 产品视频, 粉末视频, 横屏, 英文版, 中文版, 复制, 移动, 保留原文件.
---

# Commerce Material Archive

Use this skill when handling the user's recurring workflow:

- move or copy product videos/images into `E:\2.国际站资料` or `E:\1.1688资料`;
- map source filenames to product folders;
- update `视频任务统计.md`;
- update `更新日志.md`;
- verify source/target files and dashboard counts.

## Core Rules

- Inspect before acting. Always list source files, target directory structure, existing target files, current `视频任务统计.md`, and `更新日志.md`.
- Do not rely only on screenshots. Use real filesystem names from `Get-ChildItem`.
- If the user says `复制`, `复制过去`, `保留原文件`, or similar, use `Copy-Item` and verify the source count is unchanged.
- If the user says `移动`, `放到`, `归档`, or does not specify preservation, infer from recent context:
  - for generated library/source collections, prefer copy when the user says source should remain;
  - for staging folders like `E:\视频\新`, moving is acceptable if they ask to put files away.
- Never overwrite an existing target file silently. If a destination exists, skip it and record "已存在，未覆盖" in the log.
- Preserve user/manual checkbox state. Only change statuses directly affected by files handled in the current task.
- Treat `图标`, `图表`, `看板`, and `统计` as `视频任务统计.md` updates unless the user explicitly points to a different file.
- Use absolute Windows paths in commands and final file references.

## Common Roots

International site:

- Root: `E:\2.国际站资料`
- Stats: `E:\2.国际站资料\视频任务统计.md`
- Log: `E:\2.国际站资料\更新日志.md`
- Categories:
  - `01_原药部`
  - `02_化工中间体`
  - `03_制剂`
  - `04_肥料助剂`
  - `05_肥料制剂`

1688:

- Root: `E:\1.1688资料`
- Stats: `E:\1.1688资料\视频任务统计.md`
- Log: `E:\1.1688资料\更新日志.md`
- Categories use the same numbered category folders.

Product subfolders usually contain:

```text
图片\
  主图\
  英文详情页\
  中文详情页\
视频\
```

## Source Intake Workflow

1. Read source files:

```powershell
Get-ChildItem -LiteralPath '<source>' -File | Select-Object Name,FullName,Length,LastWriteTime
```

2. Read current root state:

```powershell
Get-ChildItem -LiteralPath 'E:\2.国际站资料' -Force
Get-ChildItem -LiteralPath 'E:\1.1688资料' -Force
```

3. Search likely target products:

```powershell
Get-ChildItem -LiteralPath '<root>' -Recurse -Directory |
  Where-Object { $_.Name -match '<product-keywords>' } |
  Select-Object FullName
```

4. Search stats entries:

```powershell
Select-String -LiteralPath '<root>\视频任务统计.md' -Pattern '<product-keywords>' -Context 0,4 -Encoding UTF8
```

5. Check every destination before copying/moving:

```powershell
Test-Path -LiteralPath '<destination-file>'
```

## Mapping Rules

Map by product meaning, not exact string only.

Common international/1688 mappings observed:

- `赤霉酸`, `GA3` -> `01_原药部\01_赤霉素_GA3`
- `苄氨基嘌呤`, `6-BA` -> `01_原药部\02_苄氨基嘌呤_6-BA`
- `糠氨基嘌呤`, `Kinetin`, `KT` -> `01_原药部\03_糠氨基嘌呤_6-KT`
- `吲哚丁酸`, `IBA` -> `01_原药部\04_吲哚丁酸_IBA`
- `氨基寡糖素` raw material -> `01_原药部\05_氨基寡糖素COS_Chitosan oligosaccharide；85%TC`
- `14-羟基芸苔素甾醇` raw material -> `01_原药部\11_14-羟基芸苔素甾醇_14-hydroxylated brassinosteroid`
- `矮壮素`, `CCC` raw material -> `01_原药部\13_矮壮素_CCC`
- `乙烯利70%` -> `01_原药部\16_乙烯利_Ethephon；70%`
- `调环酸钙` -> `01_原药部\17_调环酸钙_Calcium cyclodipertentate`
- `氯吡脲`, `CPPU` -> `01_原药部\19_氯吡脲_KT-30,CPPU`
- `防落素`, `4-CPA` -> `01_原药部\20_防落素_4-CPA`
- `胺鲜酯`, `DA-6` raw material -> `01_原药部\21_胺鲜酯_DA-6`
- `吲哚乙酸`, `IAA` -> `01_原药部\22_吲哚乙酸_IAA`
- `多效唑` raw material -> `01_原药部\23_多效唑_Paclobutrazol`
- `甲哌鎓`, `PIX` -> `01_原药部\24_甲哌鎓_PIX`
- `诱抗素`, `ABA` -> `01_原药部\25_诱抗素_ABA`
- `肌醇`, `Inose` -> `02_化工中间体\01_肌醇_Inose`
- `肌苷`, `Carnine` -> `02_化工中间体\02_肌苷_Carnine`
- `次黄嘌呤`, `Hypoxanthine` -> `02_化工中间体\03_次黄嘌呤_Hypoxanthine`
- `腺苷` -> `02_化工中间体\04_腺苷_Adenosin`
- `腺嘌呤` -> `02_化工中间体\05_腺嘌呤_Adenine`
- `D-核糖` -> `02_化工中间体\06_D-核糖_D-ribose`
- `6-氯嘌呤` -> `02_化工中间体\07_6-氯嘌呤_6-Chloropurine`
- `吲哚` -> `02_化工中间体\08_吲哚_Indole`
- `甘氨酸盐` -> `02_化工中间体\10_甘氨酸盐_Glycinate`
- `吲丁`, `萘乙酸` formulation -> `03_制剂\01_吲丁_萘乙酸`
- `苄嘌呤`, `吲哚丁` formulation -> `03_制剂\02_苄嘌呤_吲哚丁`
- `氨基寡糖素 · 三十烷醇` -> `03_制剂\03_氨基寡糖素_三十烷醇`
- `14-羟基芸苔素甾醇` formulation -> `03_制剂\04_14-羟基芸苔素甾醇` unless the file clearly belongs to another numbered duplicate.
- `多效唑·14-BL` -> `03_制剂\07_多效唑_14-BL`
- `28-高芸 · 寡糖` -> `03_制剂\08_28-高芸_寡糖`
- `三十烷醇·28-高芸苔素` -> `03_制剂\09_三十烷醇_28-高芸苔素`
- `28-高芸·矮壮素` -> `03_制剂\10_28-高芸_矮壮素`
- `矮壮素·甲派鎓` -> `03_制剂\12_矮壮素_甲派鎓`
- `矮壮素·抗倒酯` -> `03_制剂\13_矮壮素_抗倒酯`
- `矮壮素·氯化胆碱` -> `03_制剂\14_矮壮素_氯化胆碱`
- `胺鲜脂·柠檬酸盐`, `胺鲜酯·柠檬酸盐` -> `03_制剂\15_胺鲜脂_柠檬酸盐`
- `寡糖 · 嘧菌酯` -> `03_制剂\22_寡糖_嘧菌酯`
- `5-氨基乙酰丙酸`, `5-ALA` fertilizer additive -> `04_肥料助剂\01_5-氨基乙酰丙酸_5-ALA`
- `DMPP` liquid/oil -> `04_肥料助剂\02_硝化抑制剂_50%油剂`
- `DMPP` powder -> `04_肥料助剂\03_硝化抑制剂_DMPP`
- `褐藻寡糖`, `海藻酸寡糖`, `Alginate Oligosaccharide` powder -> `04_肥料助剂\10_褐藻寡糖_90%粉剂`
- `聚谷氨酸`, `PGA` -> `04_肥料助剂\12_聚谷氨酸_PGA`
- `植物防卫素`, `诱导子`, `Plant Defense Factor` -> `04_肥料助剂\17_免疫蛋白_immune proteins`
- `膨果安`, `膨果胺` -> `04_肥料助剂\26_膨果胺`

If no product folder exists, do not guess. Leave the source file in place and add a "未找到对应产品目录，暂未处理" note to the log.

## Destination Selection

- Video files (`.mp4`, `.mov`) -> `<product>\视频\`
- Main images / product cutouts / 抠图 / 主图 (`.png`, `.jpg`, `.jpeg`, `.webp`) -> `<product>\图片\主图\`
- English detail pages -> `<product>\图片\英文详情页\`
- Chinese detail pages -> `<product>\图片\中文详情页\`

If the user says "英文版视频" it is still a video and goes under `视频`.

## Updating Stats

Read and update `视频任务统计.md` after file operations.

International stats columns may include:

```markdown
| 板块分类 | 总产品数 | 主图就绪 | 中文详情就绪 | 英文详情就绪 | 视频就绪 |
```

or older variants without `中文详情就绪`. Preserve the current column shape. Do not reintroduce deleted columns.

1688 stats columns use:

```markdown
| 板块分类 | 总产品数 | 主图就绪 | 产品信息参数图就绪 | 包装图就绪 | 产品视频就绪 |
```

Update only affected categories and the total row.

Checkbox mapping:

- Main image copied -> set product's `主图已就绪` to `[x]`.
- English detail copied -> set `英文详情页已就绪` to `[x]`.
- Chinese detail copied -> set `中文详情页已就绪` to `[x]`.
- Video copied/moved -> set `视频已剪辑完成` or `产品视频已就绪` to `[x]`.

Counting rule:

- Count per product, not per file.
- Multiple files for one product only add one completed product.
- If product was already checked before the task, do not increase summary count again.
- If a destination file already existed and the product was already checked, record no count change.

## Updating Logs

Always update `<root>\更新日志.md`.

Use today's date from the environment. Add newest date section above older dates.

Log template:

```markdown
## YYYY-MM-DD

### 今日更新

- 复制/归档 N 个/张 <素材类型> 到对应产品目录，源文件保留在 `<source>`：
  - `<relative target path>`
- <Optional> `<target>` 已存在，本次未覆盖。
- <Optional> 本批未找到对应产品目录，暂未处理：`file1`、`file2`。
- 更新 `视频任务统计.md`：<category> <metric> 由 `old/total` 调整为 `new/total`，总<metric>由 `old/106` 调整为 `new/106`。
```

If the same date already exists, append the new task under that date. Keep chronological order inside the date when possible.

## Verification Checklist

After operations, verify:

1. Source still exists when copying was requested:

```powershell
Get-ChildItem -LiteralPath '<source>' -File | Select-Object Name,Length
```

2. Every target file exists:

```powershell
Test-Path -LiteralPath '<target-file>'
```

3. Stats table top rows show expected counts.
4. Affected product rows have expected checkboxes.
5. Log has today's entry and correct counts.

Final response must include:

- operation type: copied or moved;
- count of processed files and skipped/existing/unmatched files;
- updated stats numbers;
- confirmation that source files were preserved when requested.

