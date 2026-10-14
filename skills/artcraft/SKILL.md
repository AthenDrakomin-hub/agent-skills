---
name: artcraft
description: "Open-source AI image and video creation IDE for artists. Build 3D scenes, pose objects, light and photograph them, then feed renders back into image generation. Use when the user wants to create AI art with scene control, generate consistent characters across angles, turn images into video, or needs a local AI image/video studio. Triggers on: AI art IDE, image generation, video generation, 3D scene, consistent character, 图生视频, AI绘画, 场景控制."
license: MIT
compatibility: Windows (.exe/.msi), macOS Apple Silicon (.dmg), Linux (build from source). NVIDIA RTX 3060+ (8GB+ VRAM) or Apple Silicon M1+ (16GB+ RAM). Also runs in browser at app.getartcraft.com.
metadata:
  author: storytold (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: creative
  source: "https://github.com/storytold/artcraft"
---

# ArtCraft

Open-source AI image and video creation IDE. Build scenes like a game, then render them consistently across angles and takes.

## Role

You are an AI art production specialist. Your job is to help users install, configure, and use ArtCraft to create controlled AI images and videos with scene-level precision.

## What It Is

ArtCraft is a controllable AI creation IDE. Unlike text-to-image generators, it lets you build 3D scenes, pose objects, set lighting, and photograph the scene — then feed the renders back into image generation for consistent output.

## Core Capabilities

### 1. 3D Scene Editor
- Pose and compose objects in 3D space
- Set up cameras, lighting, and environments
- Render scenes from any angle
- Feed renders back into image generation for style transfer

### 2. Image Generation
- Text-to-image with scene control
- Image-to-image with composition lock
- Consistent character generation across angles
- Photorealistic output with reference inputs

### 3. Image-to-Video
- Turn a single image into a cinematic clip
- Controllable motion and style
- Short video generation from scene renders

### 4. Multi-Model Support
- Works with multiple AI models
- Local and cloud inference options
- No subscription required for core features

## Installation

### Option 1: Stable Release (Recommended)
Download from https://getartcraft.com/
- Windows: `.exe` or `.msi` installer
- macOS Apple Silicon: `.dmg` disk image

### Option 2: Bleeding-Edge Builds
Download from https://github.com/storytold/artcraft/releases

### Option 3: Browser (No Install)
Open https://app.getartcraft.com/ — runs entirely in browser.

### Option 4: Build from Source (Linux)
```bash
git clone https://github.com/storytold/artcraft.git
cd artcraft
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
# Follow platform-specific build instructions in README
```

## Hardware Requirements

| Platform | Minimum | Recommended |
|---|---|---|
| NVIDIA GPU | RTX 3060 (8GB VRAM) | RTX 4070+ (12GB+ VRAM) |
| Apple Silicon | M1 (16GB RAM) | M2/M3/M4 Pro (32GB+ RAM) |
| CPU-only | Not recommended | — |

## Typical Workflow

### 1. Create a Scene
1. Open the 3D editor
2. Add objects, characters, and environment elements
3. Position camera and set lighting
4. Render the scene from desired angle

### 2. Generate Image
1. Feed the render into image generation
2. Add style prompts and references
3. Generate variations while keeping composition
4. Refine with inpainting and edits

### 3. Generate Video (Optional)
1. Select a generated image
2. Define motion parameters
3. Generate short cinematic clip
4. Export in desired format

## Key Concepts

- **Scene Control**: Build the composition in 3D first, then apply AI style — avoids random layouts
- **Consistency**: Same scene rendered from different angles gives consistent characters and environments
- **Render-Feedback Loop**: AI output can be turned back into 3D objects for further scene building
- **Local First**: Models run locally when hardware allows; cloud fallback for lighter tasks

## Troubleshooting

| Problem | Solution |
|---|---|
| Out of VRAM | Reduce resolution, use cloud mode, or close other GPU apps |
| Slow generation | Check GPU is being used (not CPU fallback), update drivers |
| 3D viewport blank | Update graphics drivers, ensure WebGL support |
| Installation fails on Linux | Check Python version (3.10+), install build-essential |
| Browser version limited | Browser version has fewer features; use desktop app for full capability |

## References

- Official site: https://getartcraft.com/
- Browser app: https://app.getartcraft.com/
- GitHub: https://github.com/storytold/artcraft
- FAQ: https://getartcraft.com/faq
