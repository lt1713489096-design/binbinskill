#!/usr/bin/env python3
"""Create metadata, contact sheet, first/last frames and optional transcript for video review."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成漫剧视频复盘素材")
    parser.add_argument("video", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=10.0, help="联系表抽帧间隔秒数")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--model", default="small", help="faster-whisper本地模型名")
    return parser.parse_args()


def run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, text=True, capture_output=True, encoding="utf-8", errors="replace")


def main() -> int:
    args = parse_args()
    if not args.video.is_file():
        raise SystemExit(f"视频不存在: {args.video}")
    if args.interval <= 0:
        raise SystemExit("--interval 必须大于0")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise SystemExit("需要 ffmpeg 和 ffprobe")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    probe = run([
        ffprobe, "-v", "error", "-show_entries",
        "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(args.video),
    ])
    metadata = json.loads(probe.stdout)
    duration = float(metadata.get("format", {}).get("duration", 0) or 0)
    samples = max(1, math.ceil(duration / args.interval))
    cols = min(4, samples)
    rows = math.ceil(samples / cols)

    first = args.output_dir / "first-frame.jpg"
    last = args.output_dir / "last-frame.jpg"
    sheet = args.output_dir / "contact-sheet.jpg"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.video), "-frames:v", "1", str(first)])
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(max(0, duration - 0.12)), "-i", str(args.video), "-frames:v", "1", str(last)])
    vf = f"fps=1/{args.interval},scale=320:-1,tile={cols}x{rows}:padding=8:margin=8"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.video), "-vf", vf, "-frames:v", "1", str(sheet)])

    result = {
        "source": str(args.video.resolve()),
        "duration_s": duration,
        "metadata": metadata,
        "artifacts": {"first_frame": str(first.resolve()), "last_frame": str(last.resolve()), "contact_sheet": str(sheet.resolve())},
        "transcript": None,
    }

    if args.transcribe:
        wav = args.output_dir / "audio-16k.wav"
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise SystemExit("未安装 faster-whisper，无法转写；去掉 --transcribe 可继续画面复盘") from exc
        model = WhisperModel(args.model, device="cpu", compute_type="int8", local_files_only=True)
        segments, info = model.transcribe(str(wav), vad_filter=True, beam_size=5)
        transcript = [{"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()} for s in segments]
        transcript_path = args.output_dir / "transcript.json"
        transcript_path.write_text(json.dumps({"language": info.language, "segments": transcript}, ensure_ascii=False, indent=2), encoding="utf-8")
        result["transcript"] = str(transcript_path.resolve())

    review_path = args.output_dir / "review.json"
    review_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(review_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
