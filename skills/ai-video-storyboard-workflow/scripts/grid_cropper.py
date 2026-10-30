#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多宫格分镜大图智能切片工具 (Grid Cropper 进阶版)
用于将一张或多张宫格大图连续切割为 N 张独立的单镜头高清起手底图 (shot_01 ~ shot_N)。
支持动态行数与列数、起始镜头编号 (--start-index)、最大提取镜头数 (--max-shots)、
以及剔除底部文字标签 (--crop-bottom)。
"""

import os
import sys
import argparse
from PIL import Image

def crop_grid(image_path, output_dir, rows=3, cols=3, crop_bottom_pct=0.0, start_index=1, max_shots=None):
    """
    切片主函数
    :param image_path: 输入的大图路径
    :param output_dir: 输出目录
    :param rows: 行数 (默认 3)
    :param cols: 列数 (默认 3)
    :param crop_bottom_pct: 裁去单个单元格底部的比例 (如 0.08 表示去掉底部 8% 的文字标注条)
    :param start_index: 起始镜头编号 (如第二张图传入 10，自动切出 shot_10 开始)
    :param max_shots: 本张大图最多提取多少个镜头 (例如 15 镜任务的第二张图只需提取 6 镜)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"未找到输入图片: {image_path}")

    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(image_path)
    width, height = img.size
    print(f"[*] 载入大图: {image_path} (尺寸: {width}x{height}, 网格: {rows}行{cols}列)")

    cell_w = width / cols
    cell_h = height / rows

    results = []
    index = start_index
    count = 0

    for r in range(rows):
        for c in range(cols):
            if max_shots is not None and count >= max_shots:
                break

            left = int(c * cell_w)
            top = int(r * cell_h)
            right = int((c + 1) * cell_w)
            bottom = int((r + 1) * cell_h)

            if crop_bottom_pct > 0:
                effective_h = bottom - top
                bottom = top + int(effective_h * (1.0 - crop_bottom_pct))

            crop_box = (left, top, right, bottom)
            cropped = img.crop(crop_box)

            out_name = f"shot_{index:02d}.png"
            out_path = os.path.join(output_dir, out_name)
            cropped.save(out_path, quality=95)
            print(f"  [+] 已生成第 {index:02d} 镜: {out_name} (分辨率: {cropped.size[0]}x{cropped.size[1]})")
            results.append(out_path)
            
            index += 1
            count += 1
        if max_shots is not None and count >= max_shots:
            break

    print(f"[✓] 成功切出 {len(results)} 张分镜底图 (编号 shot_{start_index:02d} ~ shot_{index-1:02d}) 保存至: {output_dir}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="多宫格分镜大图智能切片")
    parser.add_argument("image", help="宫格图片路径")
    parser.add_argument("-o", "--output", default="shots_output", help="输出文件夹路径")
    parser.add_argument("--rows", type=int, default=3, help="行数 (默认 3)")
    parser.add_argument("--cols", type=int, default=3, help="列数 (默认 3)")
    parser.add_argument("--crop-bottom", type=float, default=0.0, help="去除各分镜底部文字标签的比例 (如 0.08)")
    parser.add_argument("--start-index", type=int, default=1, help="起始镜头编号 (如第二张图传入 10)")
    parser.add_argument("--max-shots", type=int, default=None, help="本图最多提取镜头数 (达到后立即停止)")
    args = parser.parse_args()

    crop_grid(args.image, args.output, args.rows, args.cols, args.crop_bottom, args.start_index, args.max_shots)
