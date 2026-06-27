---
name: docx-to-md
description: |
  将 Word 文档（.docx）转换为 Markdown 格式的 skill。当用户想把 docx 文件转成 md、将 Word 文档导入 Obsidian、或者说"帮我转换文档格式"时使用。触发词包括但不限于：docx转md、Word转Markdown、转换文档、导入Obsidian、把这个Word文件转一下。
---

# DOCX → Markdown 转换 Skill

你正在执行一个 Word 文档到 Markdown 的转换任务。

## 工作流程

### 第一步：确认输入

用户应提供以下信息（如果缺少，主动询问）：

1. **源文件路径**：`.docx` 文件的完整路径
2. **输出位置**（可选）：转换后 `.md` 文件的保存位置，默认与源文件同目录
3. **是否存入 vault**（可选）：是否将结果保存到 Obsidian vault 的 `01-收件箱/` 目录

### 第二步：执行转换

优先使用本 skill 自带的 `scripts/docx_to_md.py` 脚本执行转换：

```bash
python [skill目录]/scripts/docx_to_md.py "源文件.docx" "输出.md"
```

如果环境中安装了 pandoc，也可以作为备选方案：

```bash
pandoc "源文件.docx" -o "输出.md" --wrap=none --markdown-headings=atx
```

### 第三步：后处理

转换完成后：

1. **预览前几行**，确认格式正确
2. **询问用户**是否需要：
   - 添加 YAML frontmatter（标题、日期、标签等）
   - 存入 vault 的 `01-收件箱/` 目录
   - 进一步整理（清理多余空行、修正标题层级等）

## 转换规则

脚本的转换逻辑遵循以下规则：

| Word 格式 | Markdown 输出 |
|-----------|--------------|
| Heading 1 | `# 标题` |
| Heading 2 | `## 标题` |
| Heading 3 | `### 标题` |
| Heading 4-6 | `####` 及以下 |
| **粗体** | `**粗体**` |
| *斜体* | `*斜体*` |
| 有序列表 | `1. 条目` |
| 无序列表 | `- 条目` |
| 表格 | Markdown 表格语法 |
| 图片 | `![图片](图片文件名)` 并将图片提取到同目录 |
| 超链接 | `[文字](URL)` |
| 代码块 | ` ```代码``` ` |
| 普通段落 | 普通文本，段落间空行分隔 |

## 注意事项

- 复杂的 Word 排版（多栏、浮动文本框、艺术字）在转换中会丢失，转换后提示用户检查
- 图片会被提取为单独文件，保存在输出文件同目录的 `assets/` 文件夹中
- 脚本依赖 `python-docx`，已确认环境中可用

## 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 文件不存在 | 提示用户确认路径 |
| python-docx 未安装 | 运行 `pip install python-docx` |
| 文件被 Word 占用 | 提示用户关闭 Word 后重试 |
| 图片提取失败 | 跳过图片，在对应位置标注 `[图片：提取失败]` |
