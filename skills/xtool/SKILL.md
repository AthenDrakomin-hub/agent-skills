---
name: xtool
description: "Cross-platform Xcode alternative. Build, test, and deploy iOS apps from Linux, Windows, and macOS using SwiftPM. No macOS required for compilation. Use when the user wants to develop iOS apps on Linux/Windows, CI/CD iOS builds without Mac runners, or needs a SwiftPM-based iOS toolchain. Triggers on: Xcode alternative, Linux iOS build, Windows iOS development, SwiftPM iOS, cross-platform iOS, iOS CI without Mac, 跨平台iOS开发."
license: MIT
compatibility: macOS (brew), Linux (AppImage + Darwin Swift SDK), Windows (WSL2). Requires Swift toolchain and libimobiledevice for device deployment.
metadata:
  author: xtool-org (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: development
  source: "https://github.com/xtool-org/xtool"
---

# xtool

Cross-platform Xcode alternative. Build and deploy iOS apps from Linux, Windows, and macOS using Swift Package Manager — no Mac required for compilation.

## Role

You are an iOS build engineer. Your job is to help users install, configure, and use xtool to develop and deploy iOS applications on non-macOS platforms.

## What It Is

xtool allows building and deploying iOS applications from Linux, Windows (WSL2), and macOS using SwiftPM. It provides the Darwin Swift SDK and toolchain needed to compile iOS binaries without Xcode.

## Core Capabilities

### 1. Cross-Platform iOS Builds
- Compile iOS apps on Linux and Windows
- SwiftPM-based build system
- No macOS / Xcode required for compilation
- Support for iOS, simulator, and macOS targets

### 2. Device Deployment
- Deploy to physical iOS devices via libimobiledevice
- Wireless and USB deployment
- App installation and launch

### 3. SDK Management
- Download and manage Darwin Swift SDKs
- Multiple iOS SDK versions
- Automatic SDK detection and configuration

### 4. CI/CD Friendly
- Headless operation on Linux runners
- No macOS CI minutes needed
- Docker-compatible

## Installation

### macOS (Recommended)
```bash
brew install xtool-org/tap/xtool
```
Or download `xtool.app` from GitHub releases, move to `/Applications`, and run the PATH setup script.

### Linux
```bash
# Download AppImage
curl -fL "https://github.com/xtool-org/xtool/releases/latest/download/xtool-$(uname -m).AppImage" -o xtool
chmod +x xtool
sudo mv xtool /usr/local/bin/

# Install Darwin Swift SDK (required for iOS builds)
xtool sdk install
```

### Windows (WSL2)
```bash
# Inside WSL2 Ubuntu
# Follow Linux installation steps above
# Device deployment requires USB passthrough configuration
```

### From Source
```bash
git clone https://github.com/xtool-org/xtool.git
cd xtool
make install
```

Dependencies: SwiftPM, libimobiledevice, clang.

## Basic Usage

### Create a New iOS Project
```bash
xtool init MyApp --platform ios
cd MyApp
```

### Build
```bash
# Build for iOS device
xtool build --platform ios

# Build for simulator
xtool build --platform iphonesimulator

# Release build
xtool build --configuration release
```

### Run on Device
```bash
# List connected devices
xtool devices

# Deploy and launch on connected device
xtool run --device <device-id>

# Deploy to simulator
xtool run --simulator
```

### Archive and Export
```bash
# Create archive
xtool archive --output MyApp.xcarchive

# Export IPA (requires signing config)
xtool export --archive MyApp.xcarchive --output MyApp.ipa
```

### SDK Management
```bash
# List available SDKs
xtool sdk list

# Install specific iOS SDK
xtool sdk install --version 17.5

# Show current SDK configuration
xtool sdk show
```

## Project Structure

```
MyApp/
├── Package.swift          # SwiftPM manifest
├── Sources/
│   └── MyApp/
│       ├── App.swift
│       └── ContentView.swift
├── Resources/
│   ├── Assets.xcassets/
│   └── Info.plist
└── Tests/
    └── MyAppTests/
```

## Code Signing

xtool supports standard iOS code signing:
```bash
# Configure signing identity
xtool config set signing.team <team-id>
xtool config set signing.certificate <cert-name>

# Build with signing
xtool build --sign
```

For App Store distribution, you still need an Apple Developer account and proper provisioning profiles.

## CI/CD Example (GitHub Actions on Ubuntu)

```yaml
name: iOS Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install xtool
        run: |
          curl -fL "https://github.com/xtool-org/xtool/releases/latest/download/xtool-x86_64.AppImage" -o xtool
          chmod +x xtool && sudo mv xtool /usr/local/bin/
          xtool sdk install
      - name: Build
        run: xtool build --configuration release
```

## Limitations

| Feature | Status |
|---|---|
| SwiftUI / UIKit compilation | ✅ Supported |
| Interface Builder (.xib/.storyboard) | ⚠️ Limited |
| Metal shaders | ⚠️ May need precompilation |
| App Store submission | ✅ Possible with proper signing |
| In-app purchase / Apple services | ✅ Compiles, requires Apple config |
| Xcode-specific build phases | ⚠️ May need migration to SwiftPM |
| Live preview / canvas | ❌ Not available |
| Instruments / debugging | ⚠️ Limited (lldb works) |

## Troubleshooting

| Problem | Solution |
|---|---|
| SDK not found | Run `xtool sdk install` to download Darwin SDK |
| Build fails with clang errors | Verify Swift toolchain version matches SDK |
| Device not detected | Install libimobiledevice, trust device, check USB connection |
| WSL2 USB access | Configure USBIPD for Windows USB passthrough |
| Code signing fails | Verify team ID, certificate, and provisioning profile |
| Slow first build | Expected — SDK download and compilation cache building |

## References

- Official site: https://xtool.sh/
- GitHub: https://github.com/xtool-org/xtool
- Documentation: https://xtool.sh/documentation/
- Swift Package Index: https://swiftpackageindex.com/xtool-org/xtool
