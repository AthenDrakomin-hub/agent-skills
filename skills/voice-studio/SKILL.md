---
name: voice-studio
description: "Open-source, fully-local ElevenLabs alternative. Voice cloning, voice design, video dubbing, dictation, transcription, and audiobook creation in 646 languages. Use when the user wants to clone a voice locally, dub videos, create audiobooks, transcribe audio, or needs a privacy-first TTS/STT solution. Triggers on: voice cloning, ElevenLabs alternative, local TTS, audiobook, dubbing, transcription, 语音克隆, 配音, 有声书, 本地语音."
license: AGPL-3.0
compatibility: Windows, macOS, Linux. Requires bun runtime for source build, or pre-built installers. Python backend. Optional: NVIDIA GPU for faster inference.
metadata:
  author: debpalash (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: creative
  source: "https://github.com/debpalash/VoiceStudio"
---

# VoiceStudio

Open-source, fully-local ElevenLabs alternative. Voice cloning, dubbing, transcription, and audiobook creation — all running on your machine.

## Role

You are a voice production specialist. Your job is to help users install, configure, and use VoiceStudio for local voice cloning, dubbing, transcription, and audiobook creation without sending audio to cloud APIs.

## What It Is

VoiceStudio (formerly OmniVoice Studio) is a fully local voice AI studio. It combines TTS, STT, voice cloning, dubbing, and audiobook creation in one desktop application. Supports 646 languages.

## Core Capabilities

### 1. Voice Cloning
- Clone any voice from a short audio sample
- Zero-shot cloning (few seconds of reference audio)
- Local inference — audio never leaves your machine
- Adjustable emotion, speed, and pitch

### 2. Voice Design
- Create synthetic voices from scratch
- Mix voice characteristics
- Age, gender, accent controls
- Save and manage voice profiles

### 3. Video Dubbing
- Import video, extract audio
- Transcribe and translate
- Re-generate voice in target language
- Lip-sync aware output

### 4. Transcription (STT)
- High-accuracy local speech-to-text
- 646 language support
- Speaker diarization
- Export as SRT/VTT/TXT

### 5. Audiobook Creation
- Import text (PDF, EPUB, TXT)
- Auto-chapter detection
- Multi-voice narration
- Export as MP3/M4B with chapter markers

### 6. Dictation
- Real-time speech-to-text
- System-wide dictation mode
- Custom vocabulary and commands

## Installation

### Option 1: Pre-Built Installer (Recommended)
Download from https://github.com/debpalash/VoiceStudio/releases/latest
- Windows: `.msi` installer
- macOS: `.dmg` disk image
- Linux: `.AppImage` or `.deb`

### Option 2: Run from Source
```bash
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run setup:api
bun run dev
```

### Option 3: Desktop App
```bash
bun install
bun run desktop
```

### Option 4: Docker / Helm
Headless server image available for API-only deployment:
```bash
docker run -p 8000:8000 debpalash/voicestudio
```

## Typical Workflows

### Voice Cloning
1. Record or upload 10-30 seconds of clear reference audio
2. Click "Clone Voice" — processes locally
3. Test the cloned voice with custom text
4. Save to voice library for reuse

### Audiobook Creation
1. Import text file (PDF/EPUB/TXT)
2. Select narrator voice (cloned or designed)
3. Configure chapter breaks and pacing
4. Generate and export as M4B with chapters

### Video Dubbing
1. Import video file
2. Auto-transcribe source audio
3. Translate to target language (or keep same)
4. Generate dubbed audio with cloned or selected voice
5. Export video with new audio track

## Hardware Requirements

| Task | CPU-only | NVIDIA GPU | Apple Silicon |
|---|---|---|---|
| Transcription | Slow (real-time x0.5) | Fast (real-time x3) | Fast |
| TTS | Usable | Fast | Fast |
| Voice cloning | Slow (2-5 min) | Fast (10-30s) | Fast (30-60s) |
| Audiobook (long) | Very slow | Recommended | Good |

## Privacy

- All processing is local — no audio sent to cloud
- Models download on first use and cached locally
- No account or API key required
- AGPL-3.0 licensed — derivative works must be open-source

## Troubleshooting

| Problem | Solution |
|---|---|
| bun not found | Install bun: `curl -fsSL https://bun.sh/install | bash` |
| Model download fails | Check network, manually download models to cache directory |
| Cloned voice sounds muffled | Use clearer reference audio (10-30s, no background noise) |
| Transcription inaccurate | Check language setting, use higher quality model |
| GPU not used | Install CUDA toolkit, verify PyTorch detects GPU |

## References

- GitHub: https://github.com/debpalash/VoiceStudio
- Releases: https://github.com/debpalash/VoiceStudio/releases
- Install guides: `docs/install/` in repo (macos.md, windows.md, linux.md)
