#!/usr/bin/env python3
"""
MuseFlow 工作流自动化组装与导出工具 (MuseFlow Export 增强版)
适配原版 Chrome 扩展 (chrome-extension://...) 与本地独立服务 (http://127.0.0.1:8766)。
修复内容：
1. 节点数据字段修正：写入 localDataUrl 与完整 asset 对象，确保输入图片立即在节点中正常渲染显示；
2. 连线端口修正：输入图片连接到 generateVideo 的 "reference" 端口，提示词连接到 "prompt" 端口；
3. 画布坐标重构：横向 850px、纵向 620px 大网格排版，彻底消除节点堆叠与遮挡；
4. 时间线自动串联：自动注入 timeline 节点并将 9 个片段顺序编入 clipOrder。
"""

import os
import json
import base64
import argparse

def file_to_data_uri(file_path):
    """将本地图片转为 base64 data-uri"""
    ext = os.path.splitext(file_path)[1].lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'
    with open(file_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/{ext};base64,{data}"

def build_museflow_workflow(shots_dir, prompts_file=None, output_json="museflow_workflow.json", embed_images=True):
    image_files = sorted([
        f for f in os.listdir(shots_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ])

    if not image_files:
        raise FileNotFoundError(f"在 {shots_dir} 中未找到任何图片文件！")

    prompts = {}
    if prompts_file and os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.read().splitlines() if l.strip()]
            for i, line in enumerate(lines, start=1):
                prompts[i] = line

    nodes = []
    edges = []
    edge_id = 1
    created_video_ids = []

    # 优雅无重叠网格布局参数
    start_x = 80
    start_y = 80
    col_width = 860
    row_height = 620
    cols_per_row = 3

    for idx, img_name in enumerate(image_files, start=1):
        img_path = os.path.join(shots_dir, img_name)
        col = (idx - 1) % cols_per_row
        row = (idx - 1) // cols_per_row

        base_x = start_x + col * col_width
        base_y = start_y + row * row_height
        scene_label = f"场景 {idx:02d}"

        data_uri = file_to_data_uri(img_path) if embed_images else img_path
        camera_prompt = prompts.get(idx, f"分镜 {idx:02d}：微距平滑推进，主体自然律动，高精度植物学水彩光影变化，生动细节。")

        img_node_id = f"imageInput-{idx}"
        prompt_node_id = f"prompt-{idx}"
        video_node_id = f"genVideo-{idx}"
        created_video_ids.append(video_node_id)

        # 1. imageInput 节点（图片输入）
        nodes.append({
            "id": img_node_id,
            "type": "imageInput",
            "x": base_x,
            "y": base_y,
            "data": {
                "localDataUrl": data_uri,
                "asset": {
                    "id": f"asset-input-{idx}",
                    "kind": "image",
                    "url": data_uri,
                    "name": f"底图-{idx:02d}.png",
                    "sourceNodeId": img_node_id
                },
                "sceneLabel": scene_label
            }
        })

        # 2. prompt 节点（运镜词，位于图片下方，不重叠）
        nodes.append({
            "id": prompt_node_id,
            "type": "prompt",
            "x": base_x,
            "y": base_y + 270,
            "data": {
                "text": camera_prompt,
                "sceneLabel": scene_label
            }
        })

        # 3. generateVideo 节点（位于右侧，高度居中）
        nodes.append({
            "id": video_node_id,
            "type": "generateVideo",
            "x": base_x + 360,
            "y": base_y + 80,
            "data": {
                "model": "muse-video",
                "size": "9:16",
                "duration": 5,
                "continuity": (idx > 1),
                "status": "idle",
                "sceneLabel": scene_label
            }
        })

        # 连线 1: imageInput.image -> generateVideo.reference (精准端口！)
        edges.append({
            "id": f"edge-{edge_id}",
            "source": img_node_id,
            "sourcePort": "image",
            "target": video_node_id,
            "targetPort": "reference"
        })
        edge_id += 1

        # 连线 2: prompt.text -> generateVideo.prompt
        edges.append({
            "id": f"edge-{edge_id}",
            "source": prompt_node_id,
            "sourcePort": "text",
            "target": video_node_id,
            "targetPort": "prompt"
        })
        edge_id += 1

    # 4. 时间线底栏节点 (timeline)
    timeline_node_id = "timeline-main"
    num_rows = (len(image_files) + cols_per_row - 1) // cols_per_row
    nodes.append({
        "id": timeline_node_id,
        "type": "timeline",
        "x": 80,
        "y": start_y + num_rows * row_height + 40,
        "data": {
            "dockOnly": True,
            "clipOrder": created_video_ids,
            "durations": {vid: 5 for vid in created_video_ids}
        }
    })

    workflow_payload = {
        "nodes": nodes,
        "edges": edges,
        "settings": {
            "activeProvider": "mock",
            "timelineAutoAppend": True
        }
    }

    full_export = {
        "format": "26flow-workflow",
        "version": 1,
        "appVersion": "0.5.0",
        "exportedAt": "2026-10-27T11:00:00.000Z",
        "workflow": workflow_payload
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(full_export, f, ensure_ascii=False, indent=2)

    print(f"[✓] 成功输出适配原版插件与本地服务的标准 MuseFlow 工作流: {output_json}")
    print(f"    - 节点总数: {len(nodes)} (包含 {len(image_files)} 组图生视频 + 时间线)")
    print(f"    - 连线总数: {len(edges)} (底图->参考图片，提示词->提示词)")
    print(f"    - 连线端口已精准绑定: sourcePort='image' -> targetPort='reference'")
    return output_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成适配原版 Chrome 插件与本地服务的标准 MuseFlow 工作流")
    parser.add_argument("shots_dir", help="单镜头切片图片所在文件夹")
    parser.add_argument("-p", "--prompts", help="运镜提示词文本文件路径")
    parser.add_argument("-o", "--output", default="museflow_workflow.json", help="输出 json 路径")
    args = parser.parse_args()

    build_museflow_workflow(args.shots_dir, args.prompts, args.output)
