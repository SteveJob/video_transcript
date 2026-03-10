#!/usr/bin/env python3
import argparse
import asyncio
import os
import re
from pathlib import Path


def require_module(name):
    try:
        return __import__(name)
    except Exception as exc:
        raise SystemExit(
            f"Missing dependency: {name}. Install with: .venv/bin/python -m pip install openai-whisper edge-tts\n{exc}"
        )


def normalize_transcript(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(.)\1{5,}", r"\1\1", text)
    return text.strip()


def build_podcast_script_fallback(title, transcript):
    cleaned = normalize_transcript(transcript)
    preview = cleaned[:1200]
    return (
        f"欢迎收听本期内容精读。今天我们围绕《{title}》做一次快速梳理，"
        "目标是把原始文稿转成可直接吸收的行动版本。\n\n"
        "先说核心结论：这期内容可以浓缩成三件事，第一是先明确问题边界，"
        "第二是建立判断框架，第三是把观点转成可执行动作。\n\n"
        "结合文稿，主要信息如下：\n"
        f"{preview}\n\n"
        "为了便于落地，你可以直接按这个顺序做：\n"
        "第一，写下你当前最关键的问题和目标结果。\n"
        "第二，用三条标准评估可行方案，并选出优先级最高的一条。\n"
        "第三，把方案拆成今天能完成的第一步，并在当天复盘。\n\n"
        "最后总结：理解内容只是开始，真正产生价值的是把观点变成连续动作。"
    )


def write_text(path, content):
    path.write_text(content.strip() + "\n", encoding="utf-8")


def run_transcription(whisper_module, input_path, model_name, language):
    model = whisper_module.load_model(model_name)
    result = model.transcribe(str(input_path), language=language, fp16=False, verbose=False)
    text = (result.get("text") or "").strip()
    if not text:
        raise SystemExit("Transcription output is empty.")
    return text


async def synthesize(edge_tts_module, script_text, out_mp3, voice, rate):
    communicate = edge_tts_module.Communicate(script_text, voice=voice, rate=rate)
    await communicate.save(str(out_mp3))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate transcript txt + podcast script txt + podcast mp3 from video/audio."
    )
    parser.add_argument("--input", help="Video/audio path")
    parser.add_argument("--transcript-file", help="Use existing transcript txt and skip transcription")
    parser.add_argument("--output-dir", help="Output directory (default: same dir as input/transcript)")
    parser.add_argument("--model", default="base", help="Whisper model name (default: base)")
    parser.add_argument("--language", default="zh", help="Whisper language (default: zh)")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="Edge TTS voice")
    parser.add_argument("--rate", default="+0%", help="Edge TTS rate, default normal speed +0%%")
    parser.add_argument(
        "--podcast-script-file",
        help="Use external podcast script txt (recommended when used by Codex skill context)",
    )
    parser.add_argument(
        "--podcast-script-text",
        help="Use inline podcast script text directly",
    )
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Only generate transcript txt and exit",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.input and not args.transcript_file:
        raise SystemExit("Provide --input or --transcript-file")

    if args.transcript_file:
        transcript_path = Path(args.transcript_file).expanduser().resolve()
        if not transcript_path.exists():
            raise SystemExit(f"Transcript file not found: {transcript_path}")
        transcript = transcript_path.read_text(encoding="utf-8").strip()
        stem = transcript_path.stem
        source_dir = transcript_path.parent
    else:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            raise SystemExit(f"Input file not found: {input_path}")
        source_dir = input_path.parent
        stem = input_path.stem
        whisper_module = require_module("whisper")
        transcript = run_transcription(whisper_module, input_path, args.model, args.language)

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else source_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    transcript_out = output_dir / f"{stem}.txt"
    script_out = output_dir / f"{stem}_播客脚本.txt"
    audio_out = output_dir / f"{stem}_播客.mp3"

    write_text(transcript_out, transcript)
    if args.transcript_only:
        print(f"Transcript: {transcript_out}")
        return

    if args.podcast_script_text:
        podcast_script = args.podcast_script_text.strip()
    elif args.podcast_script_file:
        script_file = Path(args.podcast_script_file).expanduser().resolve()
        if not script_file.exists():
            raise SystemExit(f"Podcast script file not found: {script_file}")
        podcast_script = script_file.read_text(encoding="utf-8").strip()
    else:
        print("[WARN] No external podcast script provided, fallback summarizer used.")
        podcast_script = build_podcast_script_fallback(stem, transcript)

    if not podcast_script:
        raise SystemExit("Podcast script is empty.")
    write_text(script_out, podcast_script)

    edge_tts_module = require_module("edge_tts")
    asyncio.run(synthesize(edge_tts_module, podcast_script, audio_out, args.voice, args.rate))

    print(f"Transcript: {transcript_out}")
    print(f"Podcast script: {script_out}")
    print(f"Podcast audio: {audio_out}")


if __name__ == "__main__":
    main()
