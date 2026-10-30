#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应动态 N 镜双轨流水线工作流装配器 (Dual-Track Pipeline Workflow Assembler)
彻底解决“有了全局固定资产、逐镜分镜图就没了”与“核心参考图有的能参考上、有的参考不上”的致命缺陷。

核心架构（双轨共存，三层参考直通网）：
1. 轨一：全局固定资产 (Global Master Reference Assets, x=80 列)
   - 放置 1~4 张全局基准大图（如：全片风格、主角三视图、配角人设、核心场景道具）；
2. 轨二：逐镜剧情分镜流水线 (Per-Shot Storyboard Pipeline, 从 x=580 列展开)
   - 每一个镜头 i 必须严格具备 4 联体节点：
     ① node_shot_{i:02d}_img_prompt (生图提示词)
     ② node_shot_{i:02d}_img_gen    (分镜底图，内置具体镜头专属 shot_{i:02d}.png 高清 Base64，绝不遗漏！)
     ③ node_shot_{i:02d}_v_prompt   (运镜提示词)
     ④ node_shot_{i:02d}_video      (生成视频)
3. 三层参考图直通网 (Three-Tier Reference Network，解决有的参考上有参考不上)：
   - 第一层（必须 100% 直通）：本镜分镜底图 -> 视频参考端口 (主力起手参考首帧！)
   - 第二层（必须 100% 直通）：全片风格基准母图 -> 所有视频参考端口 (全景画风锁，全片画风绝不漂移！)
   - 第三层（语义智能精准连线）：根据镜头台词/提示词内容，精准将出场的主角/配角/道具资产连入视频参考端口！
4. 轨三：全局时间线锁排 (Global Timeline, 最右侧)
   - clipOrder 严格按照 1 至 N 镜升序锁定。
"""

import os
import sys
import json
import base64
import hashlib
import pathlib
import re
import argparse

def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def file_to_data_url(file_path):
    ext = file_path.suffix.lower().replace('.', '')
    if ext == 'jpg': ext = 'jpeg'
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/{ext};base64,{b64}'

def match_semantic_refs(prompt_text, title, global_asset_nodes):
    combined = (prompt_text + " " + title).lower()
    matched = []
    
    # 风格图：必须 100% 全覆盖所有镜头
    for gid in global_asset_nodes:
        if "style" in gid.lower() or "风格" in gid:
            matched.append(gid)
            
    # 主角匹配
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["lauren", "main", "主角", "char_01"]):
            if any(kw in combined for kw in ["lauren", "主角", "大厨", "程序员", "极客", "主厨", "睡", "猫", "翻身", "工牌", "灭火", "响指", "卧室"]):
                matched.append(gid)
                
    # 配角机器人匹配
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["robot", "sub", "配角", "char_02", "小厨师"]):
            if any(kw in combined for kw in ["robot", "机器人", "小厨师", "发条", "助手", "小手", "炒", "探头", "灯泡", "近道", "滑倒", "排队", "挥手"]):
                matched.append(gid)
                
    # 核心道具装置匹配
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["prop", "device", "道具", "装置"]):
            if any(kw in combined for kw in ["screen", "屏幕", "大屏", "弹窗", "全息", "警报", "说明书", "蓝图", "验菜", "打回", "放行", "防呆", "闸", "激光", "传送带", "宝箱", "徽章", "车间", "流水线", "垃圾山"]):
                matched.append(gid)
                
    return list(dict.fromkeys(matched))

def assemble_workflow(shots_dir, prompts_file=None, global_assets_dir=None, out_file="adaptive_pipeline_workflow.json", aspect_ratio="16:9", default_duration=10, strict_dedup=False):
    shots_path = pathlib.Path(shots_dir)
    if not shots_path.exists():
        raise FileNotFoundError(f"底图目录不存在: {shots_dir}")

    # 1. 查找所有符合 shot_XX.png / shot_XX.jpg 的分镜底图
    shot_files = sorted(
        [f for f in shots_path.glob("shot_*.*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']],
        key=lambda p: int(re.search(r'\d+', p.stem).group()) if re.search(r'\d+', p.stem) else 999
    )
    
    total_shots = len(shot_files)
    if total_shots == 0:
        raise ValueError(f"在 {shots_dir} 下未找到任何 shot_01 开头的分镜底图文件！")

    print(f"[*] 发现逐镜分镜底图: 共 {total_shots} 张")
    
    # 物理断言 1: 连续性校验
    indices = []
    for f in shot_files:
        m = re.search(r'shot_(\d+)', f.name)
        if m:
            indices.append(int(m.group(1)))
    expected_indices = list(range(1, total_shots + 1))
    if indices != expected_indices:
        missing = set(expected_indices) - set(indices)
        raise ValueError(f"分镜底图编号不连续！实际发现: {indices}, 缺失编号: {sorted(list(missing))}")
    print(f"  [✓] 断言一 (连续性) 通过: shot_01 至 shot_{total_shots:02d} 完整连续无缺漏")

    # 物理断言 2: 底图唯一性排重校验 (杜绝偷懒用同一张图充数)
    md5_map = {}
    duplicates = []
    for f in shot_files:
        h = get_file_md5(f)
        if h in md5_map:
            duplicates.append((f.name, md5_map[h]))
        else:
            md5_map[h] = f.name
    if duplicates:
        err_msg = f"发现 {len(duplicates)} 组完全重复的底图文件 (MD5完全一致): {duplicates}！这会导致视频画面重复！"
        if strict_dedup:
            raise ValueError(f"严格排重报错: {err_msg}")
        else:
            print(f"  [!] 警告: {err_msg}")
    else:
        print(f"  [✓] 断言二 (排重性) 通过: 全部 {total_shots} 张分镜底图均为独立视觉内容")

    # 2. 解析提示词文件
    img_prompts = {}
    v_prompts = {}
    titles = {}
    shot_edit_durations = {}
    if prompts_file and os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as pf:
            content = pf.read()
        
        for idx in range(1, total_shots + 1):
            pattern = rf'###\s*\[?(?:条目\s*{idx:02d}|条目\s*{idx}|ep\d+-{idx:02d}|第\s*{idx}\s*镜)\]?([^\n]*)(.*?)(?=(?:###|\Z))'
            m = re.search(pattern, content, re.DOTALL)
            if m:
                raw_title = m.group(1).strip(' ：:-[]')
                body = m.group(2)
                titles[idx] = raw_title if raw_title else f"第{idx}镜"
                dm = re.search(r'(?:推荐时长|建议时长|时长)\s*[*:：]*\s*(\d+(?:\.\d+)?)\s*秒', body)
                if dm:
                    shot_edit_durations[idx] = float(dm.group(1))
                
                pm = re.search(r'```(?:text)?\s*(.*?)\s*```', body, re.DOTALL)
                if pm:
                    v_prompts[idx] = pm.group(1).strip()
                else:
                    pm2 = re.search(r'提示词.*?[:：]\s*([^\n]+)', body)
                    if pm2:
                        v_prompts[idx] = pm2.group(1).strip()

    nodes = []
    edges = []

    # 3. 轨一：构建全局固定资产节点 (若存在)
    global_asset_nodes = []
    global_assets_x = 80
    if global_assets_dir and os.path.exists(global_assets_dir):
        ga_path = pathlib.Path(global_assets_dir)
        ga_files = sorted([f for f in ga_path.glob("*.*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']])
        for g_idx, gaf in enumerate(ga_files, start=1):
            g_id = f"node_ref_asset_{g_idx:02d}"
            # 语义化命名
            lower_name = gaf.stem.lower()
            if "style" in lower_name or "风格" in lower_name:
                g_id = "node_ref_style"
            elif any(k in lower_name for k in ["lauren", "main", "主角"]):
                g_id = "node_ref_char_lauren"
            elif any(k in lower_name for k in ["robot", "sub", "配角", "小厨师"]):
                g_id = "node_ref_char_robot"
            elif any(k in lower_name for k in ["prop", "device", "道具", "装置"]):
                g_id = "node_ref_prop_devices"
                
            g_data_url = file_to_data_url(gaf)
            g_name = gaf.stem
            global_asset_nodes.append(g_id)
            nodes.append({
                'id': g_id,
                'type': 'imageInput',
                'x': global_assets_x,
                'y': (g_idx - 1) * 320 + 80,
                'data': {
                    'localDataUrl': g_data_url,
                    'asset': {
                        'id': f'asset-global-{g_idx}',
                        'kind': 'image',
                        'url': g_data_url,
                        'name': f'【全局资产】{g_name}.png',
                        'sourceNodeId': g_id
                    },
                    'sceneLabel': f'全局参考·{g_name}'
                }
            })
        print(f"  [✓] 轨一装配完毕: 生成 {len(global_asset_nodes)} 个全局固定资产节点 (位于 x={global_assets_x})")

    # 4. 轨二：构建逐镜剧情流水线 (每个镜头 4 联体，分镜底图 100% 存在！)
    pipeline_start_x = 580 if global_asset_nodes else 80
    y_spacing = 620
    video_ids = []

    for i, img_file in enumerate(shot_files, start=1):
        shot_id = f'{i:02d}'
        base_y = (i - 1) * y_spacing + 50
        
        img_prompt_id = f'node_shot_{shot_id}_img_prompt'
        img_gen_id = f'node_shot_{shot_id}_img_gen'
        v_prompt_id = f'node_shot_{shot_id}_v_prompt'
        v_node_id = f'node_shot_{shot_id}_video'
        video_ids.append(v_node_id)
        
        data_url = file_to_data_url(img_file)
        title = titles.get(i, f"第{i}镜")
        v_prompt_text = v_prompts.get(i, f"第{shot_id}镜：平滑推镜头，主体自然律动，高细节光影。")
        img_prompt_text = img_prompts.get(i, f"Cozy warm gouache 3D animation, shot {shot_id}: {title}. High aesthetic, 16:9 widescreen.")

        # 4.1 生图提示词节点 (左上)
        nodes.append({
            'id': img_prompt_id,
            'type': 'prompt',
            'x': pipeline_start_x,
            'y': base_y,
            'data': {
                'text': img_prompt_text,
                'sceneLabel': f'{shot_id}·生图提示词'
            }
        })
        
        # 4.2 生成图片节点 (中上) —— 必须存在！内置专属分镜底图 Base64！
        nodes.append({
            'id': img_gen_id,
            'type': 'generateImage',
            'x': pipeline_start_x + 360,
            'y': base_y,
            'data': {
                'model': 'gpt-image-2.5',
                'size': aspect_ratio,
                'status': 'completed',
                'asset': {
                    'kind': 'image',
                    'name': f'第{i}镜-{title}.png',
                    'url': data_url,
                    'width': 1920 if aspect_ratio == '16:9' else 1080,
                    'height': 1080 if aspect_ratio == '16:9' else 1920
                },
                'sceneLabel': f'{shot_id}·分镜底图'
            }
        })
        
        # 4.3 运镜提示词节点 (左下)
        nodes.append({
            'id': v_prompt_id,
            'type': 'prompt',
            'x': pipeline_start_x,
            'y': base_y + 270,
            'data': {
                'text': v_prompt_text,
                'sceneLabel': f'{shot_id}·运镜提示词'
            }
        })
        
        # 4.4 生成视频节点 (右侧)
        edit_dur = shot_edit_durations.get(i, min(float(default_duration), 4.0))
        nodes.append({
            'id': v_node_id,
            'type': 'generateVideo',
            'x': pipeline_start_x + 800,
            'y': base_y + 90,
            'data': {
                'model': 'muse-video',
                'size': aspect_ratio,
                'duration': 10,
                'editDuration': edit_dur,
                'trimStart': 0.0,
                'trimEnd': edit_dur,
                'continuity': False,
                'status': 'idle',
                'sceneLabel': f'{shot_id}·生成视频',
                'subShots': [{
                    'shotNumber': i,
                    'title': title,
                    'imgNodeId': img_gen_id,
                    'promptNodeId': v_prompt_id,
                    'singlePrompt': v_prompt_text,
                    'trimStart': 0.0,
                    'trimEnd': edit_dur,
                    'editDuration': edit_dur
                }]
            }
        })
        
        # 连线 A: 生图词 ──> 分镜底图
        edges.append({
            'id': f'edge_prompt_to_img_{shot_id}',
            'source': img_prompt_id,
            'sourcePort': 'text',
            'target': img_gen_id,
            'targetPort': 'prompt'
        })
        
        # 连线 B (第一层核心防线): 分镜底图 ──(直通贯穿)──> 视频参考图端口 (主力首帧起手参考！)
        edges.append({
            'id': f'edge_shot_img_to_video_{shot_id}',
            'source': img_gen_id,
            'sourcePort': 'image',
            'target': v_node_id,
            'targetPort': 'reference'
        })
        
        # 连线 C: 运镜词 ──> 生成视频
        edges.append({
            'id': f'edge_v_prompt_to_video_{shot_id}',
            'source': v_prompt_id,
            'sourcePort': 'text',
            'target': v_node_id,
            'targetPort': 'prompt'
        })
        
        # 连线 D (第二层与第三层参考图注入): 全片风格基准 + 语义匹配角色道具
        if global_asset_nodes:
            matched_refs = match_semantic_refs(v_prompt_text + " " + img_prompt_text, title, global_asset_nodes)
            for m_ref_id in matched_refs:
                edges.append({
                    'id': f'edge_{m_ref_id}_to_video_{shot_id}',
                    'source': m_ref_id,
                    'sourcePort': 'image',
                    'target': v_node_id,
                    'targetPort': 'reference'
                })

    # 5. 轨三：全局时间线节点 (自动锁排 1~N 镜顺序)
    durations = {f'node_shot_{i:02d}_video': shot_edit_durations.get(i, min(float(default_duration), 4.0)) for i in range(1, total_shots + 1)}
    trims = {f'node_shot_{i:02d}_video': {'trimStart': 0.0, 'trimEnd': shot_edit_durations.get(i, min(float(default_duration), 4.0))} for i in range(1, total_shots + 1)}
    timeline_x = pipeline_start_x + 1350
    nodes.append({
        'id': 'node_timeline',
        'type': 'timeline',
        'x': timeline_x,
        'y': 450,
        'data': {
            'label': f'全片时间线 ({total_shots}镜全量贯通)',
            'clipOrder': video_ids,
            'durations': durations,
            'trims': trims,
            'clips': [{'nodeId': vid, 'shotNumber': idx + 1, 'duration': durations[vid], 'trimStart': 0.0, 'trimEnd': durations[vid]} for idx, vid in enumerate(video_ids)],
            'aspectRatio': aspect_ratio
        }
    })

    # 拓扑断言
    expected_pipeline_nodes = 4 * total_shots + 1
    total_expected_nodes = len(global_asset_nodes) + expected_pipeline_nodes
    assert len(nodes) == total_expected_nodes, f"节点总数不符: 期望 {total_expected_nodes}, 实际 {len(nodes)}"
    
    # 必须确保每个镜头至少连有 1 根分镜底图参考线
    ref_edges = [e for e in edges if e['targetPort'] == 'reference']
    assert len(ref_edges) >= total_shots, f"参考图连线不足: 实际 {len(ref_edges)}, 最少需 {total_shots}"
    print(f"  [✓] 断言三 (双轨与连线防线) 通过: 节点总数 {len(nodes)} (全局资产x{len(global_asset_nodes)} + 分镜四联体x{total_shots} + 时间线x1)，连线总数 {len(edges)}")

    workflow_json = {
        'appVersion': '0.5.0',
        'format': '26flow-workflow',
        'version': 1,
        'exportedAt': '2026-10-29T19:40:00.000Z',
        'workflow': {
            'nodes': nodes,
            'edges': edges,
            'settings': {
                'totalShots': total_shots,
                'hasGlobalAssets': len(global_asset_nodes) > 0,
                'pipelineFlow': True,
                'lockedSequence': True
            }
        }
    }

    out_path = pathlib.Path(out_file)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_json, f, ensure_ascii=False, indent=2)

    mb_size = out_path.stat().st_size / (1024 * 1024)
    print(f"[✓] 成功输出自适应双轨工作流: {out_file} ({mb_size:.2f} MB)")
    return out_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="自适应 N 镜双轨流水线装配器")
    parser.add_argument("shots_dir", help="包含 shot_01 ~ shot_N 逐镜分镜底图的目录")
    parser.add_argument("-p", "--prompts", help="运镜/分镜提示词文件 (md/txt)")
    parser.add_argument("-g", "--global-assets", help="全局固定资产大图目录 (风格/主角/道具)")
    parser.add_argument("-o", "--output", default="adaptive_pipeline_workflow.json", help="输出 json 路径")
    parser.add_argument("-a", "--aspect-ratio", default="16:9", help="画幅 (16:9 或 9:16)")
    parser.add_argument("-d", "--duration", type=int, default=5, help="单镜时长 (秒)")
    parser.add_argument("--strict", action="store_true", help="严格排重模式 (发现重复底图立即报错)")
    args = parser.parse_args()

    assemble_workflow(args.shots_dir, args.prompts, args.global_assets, args.output, args.aspect_ratio, args.duration, args.strict)
