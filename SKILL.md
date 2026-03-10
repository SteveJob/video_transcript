---
name: video-transcript
description: Convert a video/audio file into three deliverables in one run: (1) full transcript TXT, (2) summarized podcast script TXT, and (3) podcast MP3 audio at normal speed. Use when a user asks to turn a recording into readable notes plus a listenable recap, especially for interview, course, meeting, or long-form commentary videos.
---

# Video Transcript

## Overview

Use LLM context to write the podcast script, then use the local script for transcription and audio synthesis.
No OpenAI API key is required by this skill.

## Quick Start

1. Prepare environment (once):
```bash
python3 -m venv .venv
.venv/bin/python -m pip install openai-whisper edge-tts
```

2. Generate transcript only:
```bash
.venv/bin/python video_transcript/scripts/video_transcript_podcast.py \
  --input "/abs/path/to/video.mp4" \
  --transcript-only
```

3. In LLM context, read the transcript and write a high-quality podcast script to:
`<basename>_播客脚本.txt`

4. Generate podcast audio from that script:
```bash
.venv/bin/python video_transcript/scripts/video_transcript_podcast.py \
  --transcript-file "/abs/path/to/<basename>.txt" \
  --podcast-script-file "/abs/path/to/<basename>_播客脚本.txt"
```

5. Outputs (same directory as input):
- `<basename>.txt`
- `<basename>_播客脚本.txt`
- `<basename>_播客.mp3`

## Workflow

1. Transcribe with `openai-whisper` (model default: `base`).
2. Generate podcast script via current LLM conversation/model context (not API call in script).
3. Synthesize podcast audio using `edge-tts` with default `--rate +0%`.

## Options

- `--output-dir DIR`: write the three outputs to a custom directory.
- `--model NAME`: whisper model (`tiny`, `base`, `small`, ...).
- `--voice VOICE`: default `zh-CN-XiaoxiaoNeural`.
- `--rate RATE`: default `+0%` (normal speed).
- `--language LANG`: default `zh`.
- `--transcript-file PATH`: skip transcription and use an existing transcript TXT as input.
- `--podcast-script-file PATH`: use external podcast script txt (recommended).
- `--podcast-script-text TEXT`: use inline podcast script text directly.
- `--transcript-only`: only generate transcript and exit.

## Notes

- This skill intentionally does not alter playback speed unless `--rate` is explicitly provided.
- For long videos, prefer `--model base` first, then upgrade model size only if quality is insufficient.
- If no podcast script is passed in, the script uses a basic fallback summarizer (lower quality than LLM-generated script).
