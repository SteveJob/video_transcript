---
name: video-transcript
description: "Convert video/audio into transcript first, then have the current LLM directly read and understand the transcript to generate a podcast script, and finally synthesize podcast audio. Use when users want model-level understanding and summarization instead of programmatic summarization."
---

# Video Transcript

## Overview

This skill is a two-stage workflow:
1. Use local tools only for transcription and TTS.
2. Use the current chat model (LLM context) to read transcript text, understand it, summarize it, and write the podcast script.

Important constraints:
- Do not call OpenAI (or any LLM) API from local Python scripts.
- Do not rely on programmatic fallback summarization for final podcast script quality.
- The podcast script must be generated in the current LLM conversation after reading transcript content.

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

3. In LLM context, read the transcript file content and generate a high-quality podcast script based on understanding and summarization. Then save it to:
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
2. Read transcript text in the current conversation context.
3. Generate podcast script via current LLM understanding/summarization (not API call in script).
4. Save the generated script as `<basename>_播客脚本.txt`.
5. Synthesize podcast audio using `edge-tts` with default `--rate +0%`.

When transcript is very long:
- Split transcript into chunks and summarize each chunk in-context.
- Merge chunk summaries into one coherent podcast narrative.
- Keep voice/style consistent and avoid losing key arguments.

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
- The local script now enforces explicit podcast script input. If `--podcast-script-file` / `--podcast-script-text` is missing, it exits with an error to prevent accidental low-quality generation.
- Desired behavior: transcript understanding and podcast script writing happen in-chat, not via script-side model API calls.
