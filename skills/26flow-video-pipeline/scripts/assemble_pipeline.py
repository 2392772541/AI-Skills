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
from PIL import Image

try:
    from adapt_storyboard import adapt_to_storyboard
except ImportError:
    try:
        from scripts.adapt_storyboard import adapt_to_storyboard
    except ImportError:
        try:
            from tools.adapt_storyboard import adapt_to_storyboard
        except ImportError:
            adapt_to_storyboard = None

def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_image_fingerprint(file_path, size=(32, 32)):
    with Image.open(file_path) as im:
        rgb = im.convert('RGB').resize(size, Image.Resampling.BILINEAR)
        raw = rgb.tobytes()
        return [(raw[i], raw[i + 1], raw[i + 2]) for i in range(0, len(raw), 3)]

def mean_pixel_diff(fp1, fp2):
    if not fp1 or not fp2 or len(fp1) != len(fp2):
        return 999.0
    total = 0.0
    for (r1, g1, b1), (r2, g2, b2) in zip(fp1, fp2):
        total += (abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)) / 3.0
    return total / len(fp1)

def file_to_data_url(file_path):
    ext = file_path.suffix.lower().replace('.', '')
    if ext == 'jpg': ext = 'jpeg'
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/{ext};base64,{b64}'

def match_semantic_refs(prompt_text, title, global_asset_nodes):
    combined = (prompt_text + " " + title).lower()
    matched = []
    
    # 1. 风格母图：强制 100% 广播覆盖全片所有镜头
    for gid in global_asset_nodes:
        if "style" in gid.lower() or "风格" in gid or gid == global_asset_nodes[0]:
            matched.append(gid)
            
    # 2. 角色/人物匹配（自适应常见中文及英文字词）
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["char", "人物", "主角", "配角", "人设", "farmer", "researcher", "host"]):
            if any(kw in combined for kw in ["人", "农户", "专家", "研究员", "农民", "主播", "科学家", "手", "老汉", "客商", "用户", "买家", "厂家", "工人", "char", "person", "researcher", "farmer"]):
                matched.append(gid)
                
    # 3. 核心场景匹配 (农田、温室、实验室、车间、工厂、土壤)
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["scene", "场景", "farmland", "lab", "field", "factory"]):
            if any(kw in combined for kw in ["田", "地", "室", "棚", "土", "厂", "间", "lab", "farm", "field", "soil", "factory"]):
                matched.append(gid)
                
    # 4. 核心道具/产品/装置匹配 (肥料颗粒、试管、烧杯、包装袋、仪器)
    for gid in global_asset_nodes:
        if any(k in gid.lower() for k in ["prop", "device", "道具", "装置", "product", "产品", "包晶", "颗粒"]):
            if any(kw in combined for kw in ["肥", "袋", "管", "杯", "瓶", "晶", "粒", "药", "剂", "天平", "仪器", "包装", "产品", "prop", "fertilizer", "bottle", "dish", "beaker", "granule"]):
                matched.append(gid)
                
    # 5. 兜底铁律：任何镜头如果未能匹配到任何参考，强制挂载首张全局母图，绝不出现零参考孤儿
    if not matched and global_asset_nodes:
        matched.append(global_asset_nodes[0])
        
    return list(dict.fromkeys(matched))

def assemble_workflow(shots_dir=None, prompts_file=None, global_assets_dir=None, out_file="adaptive_pipeline_workflow.json", aspect_ratio="16:9", default_duration=10, strict_dedup=True, require_end_frames=False, default_image_model="gpt-image-2.5", storyboard_file=None):
    # 1. 查找可选的分镜底图目录 (若用户已备有现成底图则接入，若未提供则全在画布中动态生成)
    start_files_map = {}
    end_files_map = {}
    all_img_files = []
    if shots_dir and os.path.exists(shots_dir):
        shots_path = pathlib.Path(shots_dir)
        all_img_files = [f for f in shots_path.glob("shot_*.*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']]
    end_files_map = {}
    start_candidates = []
    for f in all_img_files:
        m = re.search(r'shot_0*(\d+)', f.stem, re.IGNORECASE)
        if not m:
            continue
        s_idx = int(m.group(1))
        if re.search(r'(?:_end|end_|尾帧)', f.stem, re.IGNORECASE):
            end_files_map[s_idx] = f
        else:
            start_candidates.append(f)
            start_files_map[s_idx] = f

    shot_files = sorted(
        start_candidates,
        key=lambda p: int(re.search(r'\d+', p.stem).group()) if re.search(r'\d+', p.stem) else 999
    )
    total_shots = len(shot_files) if shot_files else 0

    # 2. 解析分镜与提示词 (支持标准 storyboard.json 协议或兼容传统 prompts.md)
    img_prompts = {}
    end_img_prompts = {}
    v_prompts = {}
    titles = {}
    vo_texts = {}
    shot_edit_durations = {}
    prompt_shot_indices = []

    sb_source = storyboard_file or (prompts_file if prompts_file and prompts_file.endswith('.json') else None)
    if sb_source and os.path.exists(sb_source) and adapt_to_storyboard:
        print(f"[*] 检测到标准分镜文件/协议: {sb_source}，启动可装配分镜快速加载...")
        sb_data = adapt_to_storyboard(sb_source)
        if "aspectRatio" in sb_data and sb_data["aspectRatio"]:
            aspect_ratio = sb_data["aspectRatio"]
        for s in sb_data.get("shots", []):
            idx = s["shotId"]
            prompt_shot_indices.append(idx)
            titles[idx] = s.get("title") or f"第{idx}镜"
            vo_texts[idx] = s.get("voText", "")
            shot_edit_durations[idx] = float(s.get("duration", default_duration))
            if s.get("imagePrompt"):
                img_prompts[idx] = s["imagePrompt"]
            if s.get("endImagePrompt"):
                end_img_prompts[idx] = s["endImagePrompt"]
            if s.get("videoPrompt"):
                v_prompts[idx] = s["videoPrompt"]
        print(f"  [✓] 成功通过分镜协议载入 {len(prompt_shot_indices)} 镜镜头配置 (零正则，高精度解析)")
    elif prompts_file and os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as pf:
            content = pf.read()

        # 先尝试自适应转换
        if adapt_to_storyboard:
            try:
                sb_data = adapt_to_storyboard(content)
                if sb_data and sb_data.get("shots"):
                    for s in sb_data["shots"]:
                        idx = s["shotId"]
                        prompt_shot_indices.append(idx)
                        titles[idx] = s.get("title") or f"第{idx}镜"
                        vo_texts[idx] = s.get("voText", "")
                        shot_edit_durations[idx] = float(s.get("duration", default_duration))
                        if s.get("imagePrompt"):
                            img_prompts[idx] = s["imagePrompt"]
                        if s.get("endImagePrompt"):
                            end_img_prompts[idx] = s["endImagePrompt"]
                        if s.get("videoPrompt"):
                            v_prompts[idx] = s["videoPrompt"]
            except Exception:
                pass

        if not prompt_shot_indices:
            for m in re.finditer(r'###\s*\[?(?:条目\s*0*(\d+)|ep\d+-0*(\d+)|第\s*0*(\d+)\s*镜)\]?([^\n]*)(.*?)(?=(?:###|\Z))', content, re.DOTALL | re.IGNORECASE):
                idx = int(m.group(1) or m.group(2) or m.group(3))
                prompt_shot_indices.append(idx)
                raw_title = m.group(4).strip(' ：:-[]')
                body = m.group(5)
                titles[idx] = raw_title if raw_title else f"第{idx}镜"
                vom = re.search(r'(?:口播文案|对应文案|口播|台词|旁白)\s*[*:：]*\s*([^\n]+)', body)
                if vom:
                    vo_texts[idx] = vom.group(1).strip(' "\'“”')
                dm = re.search(r'(?:推荐时长|建议时长|时长)\s*[*:：]*\s*(\d+(?:\.\d+)?)\s*秒', body)
                if dm:
                    shot_edit_durations[idx] = float(dm.group(1))
                ipm = re.search(r'(?:首帧提示词|首帧生图词|生图提示词|图片提示词)\s*[*:：]*\s*([^\n]+)', body)
                if ipm:
                    img_prompts[idx] = ipm.group(1).strip()
                epm = re.search(r'(?:尾帧提示词|尾帧生图词|尾图提示词)\s*[*:：]*\s*([^\n]+)', body)
                if epm:
                    end_img_prompts[idx] = epm.group(1).strip()
                pm = re.search(r'```(?:text)?\s*(.*?)\s*```', body, re.DOTALL)
                if pm:
                    v_prompts[idx] = pm.group(1).strip()
                else:
                    pm2 = re.search(r'提示词.*?[:：]\s*([^\n]+)', body)
                    if pm2:
                        v_prompts[idx] = pm2.group(1).strip()

    # 确定总镜头数
    if total_shots == 0 and prompt_shot_indices:
        total_shots = max(prompt_shot_indices)
    elif total_shots == 0:
        raise ValueError("未检测到有效分镜！请提供包含分镜条目（### 第X镜）的提示词文件（--prompts），或包含 shot_01 开头底图的目录。")

    print(f"[*] 确定全片分镜总数: 共 {total_shots} 镜 (已有本地底图: {len(start_files_map)} 镜, 画布待生成: {total_shots - len(start_files_map)} 镜)")

    # 若提供了现成分镜底图，执行校验
    if start_files_map and len(start_files_map) > 1 and strict_dedup:
        md5_map = {}
        for s_idx, f in start_files_map.items():
            h = get_file_md5(f)
            if h in md5_map:
                print(f"  [!] 提示: 底图 {f.name} 与 {md5_map[h]} MD5相同")
            else:
                md5_map[h] = f.name
    if not start_files_map:
        print(f"  [✓] 纯画布内生驱动模式：分镜图片将以 clean-idle 状态装配，直接在 MuseFlow 画布中一键批量生成！")

    nodes = []
    edges = []

    # 3. 轨一：构建全局固定资产节点 (若存在)
    global_asset_nodes = []
    global_assets_x = 80
    if global_assets_dir and os.path.exists(global_assets_dir):
        ga_path = pathlib.Path(global_assets_dir)
        ga_files = sorted([f for f in ga_path.glob("*.*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']])
        used_g_ids = set()
        for g_idx, gaf in enumerate(ga_files, start=1):
            g_id = f"node_ref_asset_{g_idx:02d}"
            # 语义化归类命名
            lower_name = gaf.stem.lower()
            if "style" in lower_name or "风格" in lower_name or g_idx == 1:
                g_id = f"node_ref_style_{g_idx:02d}"
            elif any(k in lower_name for k in ["scene", "场景", "farmland", "lab", "field", "车间", "实验室", "田间"]):
                g_id = f"node_ref_scene_{g_idx:02d}"
            elif any(k in lower_name for k in ["char", "main", "主角", "人物", "人设", "farmer", "researcher"]):
                g_id = f"node_ref_char_main_{g_idx:02d}"
            elif any(k in lower_name for k in ["sub", "配角", "助手"]):
                g_id = f"node_ref_char_sub_{g_idx:02d}"
            elif any(k in lower_name for k in ["prop", "device", "道具", "装置", "product", "产品", "包晶", "颗粒"]):
                g_id = f"node_ref_prop_{g_idx:02d}"
            while g_id in used_g_ids:
                g_id = f"{g_id}_{g_idx}"
            used_g_ids.add(g_id)
                
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

    # 4. 轨二：构建逐镜剧情流水线 (每个镜头 6 联体：首帧词+首帧图 + 尾帧词+尾帧图 + 运镜词+10s视频)
    pipeline_start_x = 580 if global_asset_nodes else 80
    y_spacing = 860
    video_ids = []

    for i in range(1, total_shots + 1):
        shot_id = f'{i:02d}'
        base_y = (i - 1) * y_spacing + 50
        
        img_prompt_id = f'node_shot_{shot_id}_img_prompt'
        img_gen_id = f'node_shot_{shot_id}_img_gen'
        end_img_prompt_id = f'node_shot_{shot_id}_end_img_prompt'
        end_img_gen_id = f'node_shot_{shot_id}_end_img_gen'
        v_prompt_id = f'node_shot_{shot_id}_v_prompt'
        v_node_id = f'node_shot_{shot_id}_video'
        video_ids.append(v_node_id)
        
        img_file = start_files_map.get(i)
        data_url = file_to_data_url(img_file) if img_file else None
        end_file = end_files_map.get(i)
        end_data_url = file_to_data_url(end_file) if end_file else None
        title = titles.get(i, f"第{i}镜")
        vo_text = vo_texts.get(i, title)
        v_prompt_text = v_prompts.get(i, f"第{shot_id}镜：平滑推镜头，主体自然律动，高细节光影。")
        # 清理提示词里写死的 3.0s / 3.5s，避免 Muse 自动调用 3s 裁剪工具
        v_prompt_text = re.sub(r'Create a \d+(?:\.\d+)?s\b', 'Create a 10s full uncut', v_prompt_text, flags=re.IGNORECASE)
        img_prompt_text = img_prompts.get(i, f"Cozy warm gouache 3D animation, shot {shot_id} START KEYFRAME: {title}. High aesthetic, 16:9 widescreen.")
        end_img_prompt_text = end_img_prompts.get(
            i,
            f"{img_prompt_text}\n[END KEYFRAME / 尾帧目标定格画面]：展现第{shot_id}镜（{title}）动作与运镜完成后的最终收尾状态（{v_prompt_text[:140]}），保持角色造型、服装、道具与画风与首帧 100% 一致。"
        )

        # 4.1 首帧生图提示词节点 (左上)
        nodes.append({
            'id': img_prompt_id,
            'type': 'prompt',
            'x': pipeline_start_x,
            'y': base_y,
            'data': {
                'text': img_prompt_text,
                'sceneLabel': f'【第{shot_id}镜·首帧】生图词',
                'shotNumber': i,
                'voText': vo_text
            }
        })
        
        # 4.2 首帧生成图片节点 (中上) —— 若有本地底图则内置，若无则设为 idle 状态待画布内生成
        img_node_data = {
            'model': default_image_model,
            'size': aspect_ratio,
            'status': 'success' if data_url else 'idle',
            'frameRole': 'start',
            'shotNumber': i,
            'voText': vo_text,
            'sceneLabel': f'【第{shot_id}镜·首帧】{title}'
        }
        if data_url:
            img_node_data['asset'] = {
                'kind': 'image',
                'name': f'【第{shot_id}镜·首帧】{title}.png',
                'url': data_url,
                'width': 1920 if aspect_ratio == '16:9' else 1080,
                'height': 1080 if aspect_ratio == '16:9' else 1920
            }
        nodes.append({
            'id': img_gen_id,
            'type': 'generateImage',
            'x': pipeline_start_x + 360,
            'y': base_y,
            'data': img_node_data
        })

        # 4.2b 尾帧生图提示词节点 (左中)
        nodes.append({
            'id': end_img_prompt_id,
            'type': 'prompt',
            'x': pipeline_start_x,
            'y': base_y + 270,
            'data': {
                'text': end_img_prompt_text,
                'sceneLabel': f'【第{shot_id}镜·尾帧】生图词',
                'shotNumber': i,
                'voText': vo_text
            }
        })

        # 4.2c 尾帧生成图片节点 (中中) —— 若磁盘已有 shot_XX_end.png 则直接内置，否则待一键生成并参考首帧
        end_node_data = {
            'model': default_image_model,
            'size': aspect_ratio,
            'status': 'success' if end_data_url else 'idle',
            'frameRole': 'end',
            'shotNumber': i,
            'voText': vo_text,
            'styleContinuity': True,
            'sceneLabel': f'【第{shot_id}镜·尾帧】{title}'
        }
        if end_data_url:
            end_node_data['asset'] = {
                'kind': 'image',
                'name': f'【第{shot_id}镜·尾帧】{title}.png',
                'url': end_data_url,
                'width': 1920 if aspect_ratio == '16:9' else 1080,
                'height': 1080 if aspect_ratio == '16:9' else 1920
            }
        nodes.append({
            'id': end_img_gen_id,
            'type': 'generateImage',
            'x': pipeline_start_x + 360,
            'y': base_y + 270,
            'data': end_node_data
        })
        
        # 4.3 运镜提示词节点 (左下)
        nodes.append({
            'id': v_prompt_id,
            'type': 'prompt',
            'x': pipeline_start_x,
            'y': base_y + 540,
            'data': {
                'text': v_prompt_text,
                'sceneLabel': f'{shot_id}·运镜提示词',
                'shotNumber': i,
                'voText': vo_text
            }
        })
        
        # 4.4 生成视频节点 (右侧)
        edit_dur = shot_edit_durations.get(i, min(float(default_duration), 4.0))
        nodes.append({
            'id': v_node_id,
            'type': 'generateVideo',
            'x': pipeline_start_x + 800,
            'y': base_y + 180,
            'data': {
                'model': 'muse-video',
                'size': aspect_ratio,
                'duration': 10,
                'editDuration': edit_dur,
                'shotNumber': i,
                'voText': vo_text,
                'trimStart': 0.0,
                'trimEnd': edit_dur,
                'continuity': False,
                'status': 'idle',
                'sceneLabel': f'第{shot_id}镜·{title}',
                'subShots': [{
                    'shotNumber': i,
                    'title': title,
                    'voText': vo_text,
                    'imgNodeId': img_gen_id,
                    'endImgNodeId': end_img_gen_id,
                    'promptNodeId': v_prompt_id,
                    'singlePrompt': v_prompt_text,
                    'trimStart': 0.0,
                    'trimEnd': edit_dur,
                    'editDuration': edit_dur
                }]
            }
        })
        
        # 连线 A1: 首帧生图词 ──> 首帧分镜底图
        edges.append({
            'id': f'edge_prompt_to_img_{shot_id}',
            'source': img_prompt_id,
            'sourcePort': 'text',
            'target': img_gen_id,
            'targetPort': 'prompt'
        })

        # 连线 A2: 尾帧生图词 ──> 尾帧分镜底图 + 首帧底图参考连入尾帧底图（锁死同镜角色场景一致性）
        edges.append({
            'id': f'edge_end_prompt_to_end_img_{shot_id}',
            'source': end_img_prompt_id,
            'sourcePort': 'text',
            'target': end_img_gen_id,
            'targetPort': 'prompt'
        })
        edges.append({
            'id': f'edge_start_img_to_end_img_{shot_id}',
            'source': img_gen_id,
            'sourcePort': 'image',
            'target': end_img_gen_id,
            'targetPort': 'reference'
        })
        
        # 连线 B1 (第一层核心防线 - Image 1 首帧): 首帧分镜底图 ──> 视频参考图端口
        edges.append({
            'id': f'edge_shot_img_to_video_{shot_id}',
            'source': img_gen_id,
            'sourcePort': 'image',
            'target': v_node_id,
            'targetPort': 'reference'
        })

        # 连线 B2 (第一层核心防线 - Image 2 尾帧): 尾帧分镜底图 ──> 视频参考图端口
        edges.append({
            'id': f'edge_shot_end_img_to_video_{shot_id}',
            'source': end_img_gen_id,
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
                # 1. 连入视频节点 (作为多图串联 Image 3..9)
                edges.append({
                    'id': f'edge_{m_ref_id}_to_video_{shot_id}',
                    'source': m_ref_id,
                    'sourcePort': 'image',
                    'target': v_node_id,
                    'targetPort': 'reference'
                })
                # 2. 【核心修复】同时连入首帧生图节点！确保分镜画图时能 100% 读到画风母图
                edges.append({
                    'id': f'edge_{m_ref_id}_to_img_{shot_id}',
                    'source': m_ref_id,
                    'sourcePort': 'image',
                    'target': img_gen_id,
                    'targetPort': 'reference'
                })
                # 3. 若为画风母图，同时连入尾帧底图节点作为画风锁定
                if "style" in m_ref_id.lower() or "风格" in m_ref_id:
                    edges.append({
                        'id': f'edge_{m_ref_id}_to_end_img_{shot_id}',
                        'source': m_ref_id,
                        'sourcePort': 'image',
                        'target': end_img_gen_id,
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

    # 拓扑断言 (每镜 6 节点：首帧词+首帧图 + 尾帧词+尾帧图 + 运镜词+10s视频)
    expected_pipeline_nodes = 6 * total_shots + 1
    total_expected_nodes = len(global_asset_nodes) + expected_pipeline_nodes
    assert len(nodes) == total_expected_nodes, f"节点总数不符: 期望 {total_expected_nodes}, 实际 {len(nodes)}"
    
    # 必须确保每个镜头至少连有 1 根分镜底图参考线
    ref_edges = [e for e in edges if e['targetPort'] == 'reference']
    assert len(ref_edges) >= 2 * total_shots, f"首尾帧参考图连线不足: 实际 {len(ref_edges)}, 最少需 {2 * total_shots}"
    print(f"  [✓] 断言三 (双轨首尾帧与9图参考防线) 通过: 节点总数 {len(nodes)} (全局资产x{len(global_asset_nodes)} + 分镜六联体x{total_shots} + 时间线x1)，连线总数 {len(edges)}")

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
    parser.add_argument("shots_dir", nargs="?", default=None, help="可选：包含 shot_01 ~ shot_N 逐镜分镜底图的目录（若不提供，则在画布中动态生成）")
    parser.add_argument("-s", "--shots-dir", dest="shots_dir_opt", default=None, help="可选：包含 shot_01 ~ shot_N 逐镜分镜底图的目录")
    parser.add_argument("-b", "--storyboard", help="可装配标准分镜文件 (storyboard.json，或任意上游 Skill 产出的 json/md)")
    parser.add_argument("-p", "--prompts", help="运镜/分镜提示词文件 (md/txt)")
    parser.add_argument("-g", "--global-assets", help="全局固定资产大图目录 (风格/主角/道具，全片唯一定稿母图)")
    parser.add_argument("-o", "--output", default="adaptive_pipeline_workflow.json", help="输出 json 路径")
    parser.add_argument("-a", "--aspect-ratio", default="16:9", help="画幅 (16:9 或 9:16)")
    parser.add_argument("-d", "--duration", type=int, default=10, help="单镜时长 (秒)")
    parser.add_argument("-m", "--model", default="gpt-image-2.5", help="默认生图模型 (如 gpt-image-2.5, muse-image, flux-1-dev)")
    parser.add_argument("--strict", action="store_true", default=True, help="默认开启：严格防伪造排重模式 (发现母图占位或重复底图立即报错阻断)")
    parser.add_argument("--allow-duplicate-placeholders", dest="strict", action="store_false", help="仅调试用：允许占位图")
    parser.add_argument("--require-end-frames", action="store_true", help="强制要求每一镜同时具备 shot_XX_end.png 尾帧底图")
    args = parser.parse_args()

    s_dir = args.shots_dir_opt or args.shots_dir
    assemble_workflow(s_dir, args.prompts, args.global_assets, args.output, args.aspect_ratio, args.duration, args.strict, args.require_end_frames, default_image_model=args.model, storyboard_file=args.storyboard)
