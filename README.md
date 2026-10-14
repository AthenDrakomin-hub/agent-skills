# agent-skills

A collection of reusable AI Agent Skills for daily development, DevOps, and content automation.

## Skills (13)

### Development & Engineering

| Skill | Description |
|---|---|
| [reverse-engineering-suite](./skills/reverse-engineering-suite/SKILL.md) | Unified reverse-engineering: source code→PRD, binary→analysis+reimplementation, website→behavior reconstruction. Auto-detects target type, no manual routing needed. |
| [code-to-prd](./skills/code-to-prd/SKILL.md) | Reverse-engineer any codebase into a complete PRD. Analyzes routes, components, state, APIs, and interactions to produce reconstruction-ready documentation. Supports React/Vue/Angular/Next.js/NestJS/Django/FastAPI. |
| [gsap-scroll-landing](./skills/gsap-scroll-landing/SKILL.md) | Cinematic scroll-driven landing pages with GSAP + ScrollTrigger. Product parallax, per-character text reveals, fluid loop effects. Single-file HTML output, no build step. |
| [github-tech-optimizer](./skills/github-tech-optimizer/SKILL.md) | Scan project tech stack, research free/open-source alternatives, enforce visual demo walkthrough, output executable optimization plans with cleanup. |
| [git-safety-guard](./skills/git-safety-guard/SKILL.md) | Pre-commit secret scanning, .gitignore audit, and pull-modify-commit-push workflow enforcement. |
| [rea-reverse-engineering](./skills/rea-reverse-engineering/SKILL.md) | AI-assisted reverse engineering via REA toolchain. Analyze binaries, APKs, Electron apps, .NET assemblies, and websites to produce evidence-based analysis and functional-equivalent reimplementation. |

### UI/UX & Mobile

| Skill | Description |
|---|---|
| [ios-ui-ux-dev](./skills/ios-ui-ux-dev/SKILL.md) | Multi-channel iOS UI/UX audit: screenshot walkthrough, native source audit, H5/WKWebView audit, IPA unpacking. Covers safe-area, Auto Layout, Dynamic Type, WKWebView rendering bugs, iOS 26 Liquid Glass. |
| [uniapp-multi-platform-audit](./skills/uniapp-multi-platform-audit/SKILL.md) | uni-app iOS/Android/H5 three-platform UI/UX audit. Code-scan for layout issues, platform-specific styling, IM and game专项 checklists, with direct code fixes. |
| [uniapp-release-notes](./skills/uniapp-release-notes/SKILL.md) | Query HBuilder X / uni-app / uni-app x changelog for version selection, API compatibility, new features, and known-bug avoidance. Offline snapshot of 33 versions with Python query script. |

### DevOps

| Skill | Description |
|---|---|
| [boxim-release-assistant](./skills/boxim-release-assistant/SKILL.md) | Build, deploy, health-check, and roll back the boxim IM system across 3 frontends and 3 Java backend services. |

### Content & Automation

| Skill | Description |
|---|---|
| [wechat-article-html](./skills/wechat-article-html/SKILL.md) | Convert Markdown into WeChat Official Account compatible inline-style HTML. 15 built-in themes, strict paste-compatibility rules (no style tags/classes, all styles inline). |
| [ai-writing-detector](./skills/ai-writing-detector/SKILL.md) | Scan text for 22 AI writing patterns and produce per-location detection reports. Diagnosis-only by default, no rewriting. |
| [douyin-to-feishu-archiver](./skills/douyin-to-feishu-archiver/SKILL.md) | Parse Douyin video links into reusable AI prompts and archive them to a Feishu folder with category tags. |

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
