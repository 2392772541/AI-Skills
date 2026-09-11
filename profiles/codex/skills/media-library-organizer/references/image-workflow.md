# Image content ingestion and viewing

## Catalog shape

Store `图片目录.json` as UTF-8:

```json
{
  "version": 1,
  "images": [
    {
      "file_name": "农药瓶_白底.png",
      "category": "产品",
      "content_tags": ["农药瓶", "白底", "正面"],
      "uses": ["产品展示", "主图", "详情页"],
      "orientation": "竖图",
      "width": 1200,
      "height": 1600,
      "colors": ["白色", "绿色"],
      "relative_path": "02_图片/产品/农药瓶_白底.png",
      "notes": "透明背景：否"
    }
  ]
}
```

Required fields: `file_name`, `category`, `content_tags`, `uses`, `relative_path`.

## Inspect the actual image

1. Read format, dimensions, alpha, EXIF orientation, and color profile.
2. Open the real image. Record visible subject, scene, action, text, angle, background, composition, and quality. Do not infer unseen content from the filename.
3. Use OCR when visible text matters. Keep OCR uncertainty explicit.
4. Assign category and production uses. Preserve the original; do not create copies for multiple tags.

## Controlled tags

- Category: `产品`, `人物`, `图标贴纸`, `背景`.
- Orientation: `横图`, `竖图`, `方图`, `超宽`, `超长`.
- Uses: `主图`, `详情页`, `产品展示`, `人物介绍`, `口播配图`, `知识讲解`, `封面`, `背景`, `贴纸叠加`, `转场遮罩`, `社媒配图`, `缩略图`.
- Content tags should name what is visibly present: subject, scene, action, angle, background, text, and style.

## Verify

Open `素材片段库.html` locally in Edge. Confirm thumbnail loading, content/use filtering, full-size lightbox viewing, correct aspect ratio, and no broken image paths.
