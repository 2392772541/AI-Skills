import json, subprocess, sys, pathlib

def inspect_media(video_path: pathlib.Path):
    """使用 ffprobe 获取完整媒体流参数"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,codec_type,width,height,duration,r_frame_rate,pix_fmt",
        "-show_entries", "format=format_name,duration,size,bit_rate",
        "-of", "json",
        str(video_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe 解析失败: {res.stderr}")
    return json.loads(res.stdout)

def verify_decode(video_path: pathlib.Path):
    """使用 ffmpeg 进行全帧硬解码测试，确保无损坏"""
    cmd = [
        "ffmpeg", "-v", "error", "-xerror",
        "-i", str(video_path),
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0, res.stderr

def concat_videos(video_list: list[pathlib.Path], output_path: pathlib.Path):
    """流式硬拼接多段视频并合流"""
    concat_txt = output_path.parent / "concat_list.tmp.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for v in video_list:
            f.write(f"file '{v.resolve()}'\n")
    
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if concat_txt.exists():
        concat_txt.unlink()
        
    if res.returncode != 0:
        # 若 copy 失败（如时间戳或参数微小不一致），平滑降级为 re-encode 对齐
        cmd_fallback = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            str(output_path)
        ]
        with open(concat_txt, "w", encoding="utf-8") as f:
            for v in video_list:
                f.write(f"file '{v.resolve()}'\n")
        res_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True)
        if concat_txt.exists():
            concat_txt.unlink()
        if res_fallback.returncode != 0:
            raise RuntimeError(f"FFmpeg 拼接合成失败: {res_fallback.stderr}")
            
    return inspect_media(output_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="视频解码校验与多段流式拼接工具")
    parser.add_argument("inputs", nargs="+", help="输入的一或多个 MP4 视频路径")
    parser.add_argument("-o", "--output", help="合成成片的输出路径")
    args = parser.parse_args()

    input_paths = [pathlib.Path(p) for p in args.inputs]
    for p in input_paths:
        if not p.exists():
            print(f"[!] 文件不存在: {p}")
            sys.exit(1)

    if len(input_paths) == 1 and not args.output:
        target = input_paths[0]
        info = inspect_media(target)
        ok, err = verify_decode(target)
        print(f"[*] 目标视频: {target.name}")
        print("Media Info:", json.dumps(info, indent=2))
        print("Decode Status:", "PASS" if ok else f"FAIL ({err})")
    else:
        out_target = pathlib.Path(args.output) if args.output else input_paths[0].parent / "concat_output.mp4"
        print(f"[*] 正在拼接 {len(input_paths)} 段分镜视频 -> {out_target.name}...")
        final_info = concat_videos(input_paths, out_target)
        ok, err = verify_decode(out_target)
        print(f"[+] 拼接完成！成片时长: {final_info.get("format", {}).get("duration")}s")
        print("成片硬解码质检:", "PASS" if ok else f"FAIL ({err})")
