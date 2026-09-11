#!/usr/bin/env python3
"""
Edge TTS 音频生成脚本

特性：
- 免费、无需 API Key
- 支持多种中文语音
- 自动获取音频时长

用法：
    python scripts/generate_audio_edge.py

依赖：
    pip install edge-tts
"""

import asyncio
import subprocess
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("❌ 请先安装 edge-tts: pip install edge-tts")
    exit(1)

# 场景配置
SCENES = [
    {"id": "01-intro", "text": "欢迎观看本期视频..."},
    {"id": "02-main", "text": "今天我们来讲..."},
]

# 推荐语音
# zh-CN-YunyangNeural - 云扬（专业播音腔，推荐）
# zh-CN-XiaoxiaoNeural - 晓晓（温暖自然）
# zh-CN-YunxiNeural - 云希（阳光少年）
VOICE = "zh-CN-YunyangNeural"

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "audio"


def get_audio_duration(file_path: Path) -> float:
    """用 ffprobe 获取音频时长"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip()) if result.stdout.strip() else 0


async def generate_audio(scene: dict, output_dir: Path) -> dict:
    """生成单个场景的音频"""
    output_file = output_dir / f"{scene['id']}.mp3"
    communicate = edge_tts.Communicate(scene["text"], VOICE)
    await communicate.save(str(output_file))

    duration = get_audio_duration(output_file)
    frames = round(duration * 30)  # 30fps
    return {"id": scene["id"], "file": f"{scene['id']}.mp3", "duration": duration, "frames": frames}


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"🎙️  Edge TTS (Voice: {VOICE})")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("=" * 60)

    results = []
    for i, scene in enumerate(SCENES, 1):
        print(f"[{i}/{len(SCENES)}] {scene['id']}: 生成中...", end=" ", flush=True)
        try:
            result = await generate_audio(scene, OUTPUT_DIR)
            results.append(result)
            print(f"✅ {result['duration']:.2f}s ({result['frames']} frames)")
        except Exception as e:
            print(f"❌ {e}")

    print("=" * 60)
    print(f"✅ 完成: {len(results)} 个音频文件")

    # 输出配置供 Remotion 使用
    print("\n📝 audioConfig 数据:")
    for r in results:
        print(f'  {{ id: "{r["id"]}", file: "{r["file"]}", frames: {r["frames"]} }},')


if __name__ == "__main__":
    asyncio.run(main())
