# agent-skills

A collection of reusable AI Agent Skills for daily development, DevOps, and content automation.

## Skills (34)

### Development & Engineering

| Skill | Description |
|---|---|
| [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) | Read-only codebase investigation with verifiable evidence. SCOPE→ROUTE→EFFECT→BREAK→SHIP methodology. Traces call chains, data flow, runtime wiring, and module responsibility. Every conclusion traces to literal path:symbol:line. |
| [diagram-design](./skills/diagram-design/SKILL.md) | Editorial-grade diagram generation (52K stars). 42 diagram types: architecture, flowchart, sequence, ERD, timeline, swimlane, org chart. Self-contained HTML/SVG output, zero build step. Imports Mermaid/draw.io/Excalidraw. |
| [reverse-engineering-suite](./skills/reverse-engineering-suite/SKILL.md) | Unified reverse-engineering: source code→PRD, binary→analysis+reimplementation, website→behavior reconstruction. Auto-detects target type, no manual routing needed. |
| [code-to-prd](./skills/code-to-prd/SKILL.md) | Reverse-engineer any codebase into a complete PRD. Analyzes routes, components, state, APIs, and interactions to produce reconstruction-ready documentation. Supports React/Vue/Angular/Next.js/NestJS/Django/FastAPI. |
| [gsap-scroll-landing](./skills/gsap-scroll-landing/SKILL.md) | Cinematic scroll-driven landing pages with GSAP + ScrollTrigger. Product parallax, per-character text reveals, fluid loop effects. Single-file HTML output, no build step. |
| [github-tech-optimizer](./skills/github-tech-optimizer/SKILL.md) | Scan project tech stack, research free/open-source alternatives, enforce visual demo walkthrough, output executable optimization plans with cleanup. |
| [git-safety-guard](./skills/git-safety-guard/SKILL.md) | Pre-commit secret scanning, .gitignore audit, and pull-modify-commit-push workflow enforcement. |
| [rea-reverse-engineering](./skills/rea-reverse-engineering/SKILL.md) | AI-assisted reverse engineering via REA MCP Server (115K stars). Orchestrates Hopper/Ghidra/JADX/Binwalk for binaries, APKs, Electron apps, .NET assemblies, websites. Evidence-based analysis + functional-equivalent reimplementation. |
| [context-mode](./skills/context-mode/SKILL.md) | MCP server that optimizes AI coding context windows. Sandbox execution + FTS5 indexing reduces context consumption by 98%. Session continuity across compaction. Think-in-code paradigm. |
| [skills-cli](./skills/skills-cli/SKILL.md) | Vercel Labs open-source CLI for agent skills ecosystem. Install/discover/update/share skills across 80+ AI coding agents. `npx skills add/find/update/validate`. |
| [code-quality-review](./skills/code-quality-review/SKILL.md) | Read-only review of structural or abstraction changes for consequential maintainability risks. Flags architectural debt, over-abstraction, and hidden coupling in large diffs. |
| [perfection-loop](./skills/perfection-loop/SKILL.md) | Relentless verify-and-fix loop that proves work is actually finished. Sends adversarial judge sub-agents to inspect defects, fixes them, and repeats until zero issues remain. |
| [project-finishing-workflow](./skills/project-finishing-workflow/SKILL.md) | AI编程项目收尾工作流。5步闭环：盘点优先级→缺口清单（只找不改）→逐个修复（全绿才停）→独立验收→交付归档。防早停规则，禁止"应该可以了"，每个bug必须写复现测试。 |
| [conversational-ai-dev-workflow](./skills/conversational-ai-dev-workflow/SKILL.md) | 用豆包/Grok等对话式AI从零开发项目。5阶段：项目骨架→搭骨架代码→逐个模块开发→收尾验收→独立验收。每个阶段开新对话，手动本地验证循环。7个通用提示词技巧。 |
| [airllm](./skills/airllm/SKILL.md) | Run 70B+ LLMs on single 4GB GPU via layer-by-layer loading. No quantization, full precision. Drop-in transformers replacement. ~20s/token for 70B on 4GB. |
| [xtool](./skills/xtool/SKILL.md) | Cross-platform Xcode alternative. Build/test/deploy iOS apps from Linux/Windows/macOS via SwiftPM. No Mac required for compilation. CI/CD friendly. |
| [using-coze-cli](./skills/using-coze-cli/SKILL.md) | Coze CLI multi-module usage guide covering agent collaboration, code generation, file operations, and content creation workflows. |

### Creative & Media

| Skill | Description |
|---|---|
| [artcraft](./skills/artcraft/SKILL.md) | Open-source AI image/video creation IDE. Build 3D scenes, pose objects, light and photograph, feed renders back into generation. Consistent characters across angles. Local + browser. |
| [voice-studio](./skills/voice-studio/SKILL.md) | Open-source local ElevenLabs alternative. Voice cloning, dubbing, transcription, audiobook creation in 646 languages. Fully local, no cloud API, AGPL-3.0. |

### Visualization & Data

| Skill | Description |
|---|---|
| [gods-eye-view](./skills/gods-eye-view/SKILL.md) | Browser-based satellite imagery simulator with real public data. Weather, air traffic, maritime, seismic overlays. Surveillance-style UI. No install, runs in browser. |

### UI/UX & Mobile

| Skill | Description |
|---|---|
| [ios-ui-ux-dev](./skills/ios-ui-ux-dev/SKILL.md) | Multi-channel iOS UI/UX audit: screenshot walkthrough, native source audit, H5/WKWebView audit, IPA unpacking. Covers safe-area, Auto Layout, Dynamic Type, WKWebView rendering bugs, iOS 26 Liquid Glass. |
| [design-taste-frontend](./skills/design-taste-frontend/SKILL.md) | Anti-slop frontend skill distilled from 247 curated gallery sites. Enforces a strict no-slop house style with real-browser inspector and look-and-fix loop on screenshots. For landing pages, marketing sites, portfolios, and public-facing web pages. |
| [mobile-app-ui-design](./skills/mobile-app-ui-design/SKILL.md) | Design high-quality mobile app UI/UX screens, flows, and components. Covers app mockups, onboarding flows, mobile navigation, and React Native/Flutter/SwiftUI style visual prototypes. |
| [uniapp-multi-platform-audit](./skills/uniapp-multi-platform-audit/SKILL.md) | uni-app iOS/Android/H5 three-platform UI/UX audit. Code-scan for layout issues, platform-specific styling, IM and game专项 checklists, with direct code fixes. |
| [uniapp-release-notes](./skills/uniapp-release-notes/SKILL.md) | Query HBuilder X / uni-app / uni-app x changelog for version selection, API compatibility, new features, and known-bug avoidance. Offline snapshot of 33 versions with Python query script. |

### DevOps

| Skill | Description |
|---|---|
| [boxim-release-assistant](./skills/boxim-release-assistant/SKILL.md) | Build, deploy, health-check, and roll back the boxim IM system across 3 frontends and 3 Java backend services. |
| [site-launch-checklist](./skills/site-launch-checklist/SKILL.md) | Pre-launch checklist for shipping a new website or web app. Covers analytics, DNS, TLS, backups, legal/GDPR compliance, security headers, SEO/GEO, Lighthouse, Core Web Vitals, and WCAG quality gates. |

### Content & Marketing

| Skill | Description |
|---|---|
| [wechat-article-html](./skills/wechat-article-html/SKILL.md) | Convert Markdown into WeChat Official Account compatible inline-style HTML. 15 built-in themes, strict paste-compatibility rules (no style tags/classes, all styles inline). |
| [ai-writing-detector](./skills/ai-writing-detector/SKILL.md) | Scan text for 22 AI writing patterns and produce per-location detection reports. Diagnosis-only by default, no rewriting. |
| [douyin-to-feishu-archiver](./skills/douyin-to-feishu-archiver/SKILL.md) | Parse Douyin video links into reusable AI prompts and archive them to a Feishu folder with category tags. |
| [ad-creative](./skills/ad-creative/SKILL.md) | Ad creative generation with headline variations, hook patterns, and platform-specific copy structures. |
| [copywriting](./skills/copywriting/SKILL.md) | Product copywriting framework: positioning, value propositions, personas, feature-to-benefit conversion, and multi-length product descriptions. |
| [cro](./skills/cro/SKILL.md) | Conversion rate optimization: landing page structure, hero copy, pain points, social proof, pricing anchoring, and CTA design. |
| [social](./skills/social/SKILL.md) | Social media content package generation across platforms with post variations, hashtags, and engagement hooks. |

## Installation

### Search and install from this repository

```bash
# Search for available skills
npx skills find <keyword>

# Install all skills from this repo
npx skills add AthenDrakomin-hub/agent-skills

# Install a specific skill
npx skills add AthenDrakomin-hub/agent-skills --skill douyin-to-feishu-archiver

# Install globally
npx skills add AthenDrakomin-hub/agent-skills -g
```

### Install from local clone

```bash
git clone https://github.com/AthenDrakomin-hub/agent-skills.git
npx skills add ./agent-skills --list
npx skills add ./agent-skills --skill git-safety-guard
```

## Repository Structure

```
agent-skills/
├── skills/
│   ├── code-to-prd/              # Reverse-engineer codebase into PRD
│   │   ├── SKILL.md
│   │   ├── scripts/              # codebase_analyzer.py, prd_scaffolder.py
│   │   ├── references/           # framework patterns, quality checklist
│   │   ├── assets/               # sample analysis
│   │   └── expected_outputs/     # PRD output examples
│   ├── ios-ui-ux-dev/            # iOS multi-channel UI/UX audit
│   │   ├── SKILL.md
│   │   ├── scripts/              # source_scan.py, ipa_audit.py
│   │   └── references/           # 7 audit guides + rubric
│   ├── uniapp-multi-platform-audit/  # uni-app 3-platform UI audit
│   ├── github-tech-optimizer/    # Open-source tech research & optimization
│   ├── rea-reverse-engineering/  # REA-based reverse engineering
│   ├── git-safety-guard/         # Pre-commit secret scanning
│   ├── boxim-release-assistant/  # boxim deployment & rollback
│   ├── site-launch-checklist/    # Pre-launch production checklist
│   ├── code-quality-review/      # Structural change maintainability review
│   ├── perfection-loop/          # Verify-and-fix iteration loop
│   ├── design-taste-frontend/    # Anti-slop frontend art direction
│   └── mobile-app-ui-design/     # Mobile app UI/UX design standards
│   └── douyin-to-feishu-archiver/ # Douyin video → Feishu archive
├── LICENSE
└── README.md
```

## Adding a New Skill

1. Create `skills/<your-skill-name>/SKILL.md`
2. Folder name must exactly match the `name` field in the YAML frontmatter
3. `SKILL.md` must be all-caps (not `skill.md` or `SKILL.MD`)
4. Keep the Markdown body under 500 lines; move detailed references to `references/`
5. Test locally: `npx skills add ./ --list`
6. Commit and push

## License

MIT
