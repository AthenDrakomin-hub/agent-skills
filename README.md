# agent-skills

A curated collection of 33 high-quality AI Agent Skills for development, DevOps, design, and content automation. Every skill ships with executable scripts or structured references — no pure prompt filler.

## Skills (33)

### Development & Engineering

| Skill | Description |
|---|---|
| [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) | Read-only codebase investigation with verifiable evidence. SCOPE→ROUTE→EFFECT→BREAK→SHIP methodology. Traces call chains, data flow, runtime wiring, and module responsibility. Every conclusion traces to literal path:symbol:line. |
| [code-to-prd](./skills/code-to-prd/SKILL.md) | Reverse-engineer any codebase into a complete PRD. Analyzes routes, components, state, APIs, and interactions to produce reconstruction-ready documentation. Supports React/Vue/Angular/Next.js/NestJS/Django/FastAPI. |
| [code-quality-review](./skills/code-quality-review/SKILL.md) | Read-only review of structural or abstraction changes for consequential maintainability risks. Flags architectural debt, over-abstraction, and hidden coupling in large diffs. |
| [context-mode](./skills/context-mode/SKILL.md) | MCP server that optimizes AI coding context windows. Sandbox execution + FTS5 indexing reduces context consumption by 98%. Session continuity across compaction. Think-in-code paradigm. |
| [conversational-ai-dev-workflow](./skills/conversational-ai-dev-workflow/SKILL.md) | 用豆包/Grok等对话式AI从零开发项目。5阶段：项目骨架→搭骨架代码→逐个模块开发→收尾验收→独立验收。每个阶段开新对话，手动本地验证循环。7个通用提示词技巧。 |
| [diagram-design](./skills/diagram-design/SKILL.md) | Editorial-grade diagram generation (52K stars). 42 diagram types: architecture, flowchart, sequence, ERD, timeline, swimlane, org chart. Self-contained HTML/SVG output, zero build step. Imports Mermaid/draw.io/Excalidraw. |
| [github-tech-optimizer](./skills/github-tech-optimizer/SKILL.md) | Scan project tech stack, research free/open-source alternatives, enforce visual demo walkthrough, output executable optimization plans with cleanup. |
| [git-safety-guard](./skills/git-safety-guard/SKILL.md) | Pre-commit secret scanning, .gitignore audit, and pull-modify-commit-push workflow enforcement. |
| [gsap-scroll-landing](./skills/gsap-scroll-landing/SKILL.md) | Cinematic scroll-driven landing pages with GSAP + ScrollTrigger. Product parallax, per-character text reveals, fluid loop effects. Single-file HTML output, no build step. |
| [perfection-loop](./skills/perfection-loop/SKILL.md) | Relentless verify-and-fix loop that proves work is actually finished. Sends adversarial judge sub-agents to inspect defects, fixes them, and repeats until zero issues remain. |
| [project-finishing-workflow](./skills/project-finishing-workflow/SKILL.md) | AI编程项目收尾工作流。5步闭环：盘点优先级→缺口清单（只找不改）→逐个修复（全绿才停）→独立验收→交付归档。防早停规则，禁止"应该可以了"，每个bug必须写复现测试。 |
| [rea-reverse-engineering](./skills/rea-reverse-engineering/SKILL.md) | AI-assisted reverse engineering via REA MCP Server (115K stars). Orchestrates Hopper/Ghidra/JADX/Binwalk for binaries, APKs, Electron apps, .NET assemblies, websites. Evidence-based analysis + functional-equivalent reimplementation. |
| [reverse-engineering-suite](./skills/reverse-engineering-suite/SKILL.md) | Unified reverse-engineering: source code→PRD, binary→analysis+reimplementation, website→behavior reconstruction. Auto-detects target type, no manual routing needed. |
| [skill-forge](./skills/skill-forge/SKILL.md) | 技能制作器：把反复出现的问题制作成可安装、可分级验证的单个 Skill，含需求分析与候选 Skill 检查测试。 |
| [skill-installer](./skills/skill-installer/SKILL.md) | 技能安装器：把单个或一批 Skill 安装到 Claude Code / Codex / Hermes / Kiro / Qwen Code / Cline 等 Agent。 |

### Creative & Media

| Skill | Description |
|---|---|
| [douyin-to-feishu-archiver](./skills/douyin-to-feishu-archiver/SKILL.md) | Parse Douyin video links into reusable AI prompts and archive them to a Feishu folder with category tags. |
| [image-to-code](./skills/image-to-code/SKILL.md) | 网站截图/设计图转代码（Codex 专用，image-to-code）。视觉重要任务先生成并深析设计图，再实现。核心 11 章保留主文件，细则 12–38 章见 references。 |
| [video-content-extraction](./skills/video-content-extraction/SKILL.md) | 视频内容提取：接收抖音/小红书/视频号等短视频链接或分享文案，查询作品/账号数据并提取语音文字稿，按作者和标题归档为 Markdown。 |

### UI/UX & Mobile

| Skill | Description |
|---|---|
| [design-taste-frontend](./skills/design-taste-frontend/SKILL.md) | Anti-slop frontend skill distilled from 247 curated gallery sites. Enforces a strict no-slop house style with real-browser inspector and look-and-fix loop on screenshots. For landing pages, marketing sites, portfolios, and public-facing web pages. |
| [ios-ui-ux-dev](./skills/ios-ui-ux-dev/SKILL.md) | Multi-channel iOS UI/UX audit: screenshot walkthrough, native source audit, H5/WKWebView audit, IPA unpacking. Covers safe-area, Auto Layout, Dynamic Type, WKWebView rendering bugs, iOS 26 Liquid Glass. |
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
| [ad-creative](./skills/ad-creative/SKILL.md) | Ad creative generation with headline variations, hook patterns, and platform-specific copy structures. |
| [ads](./skills/ads/SKILL.md) | Paid advertising campaign help for Google Ads, Meta, LinkedIn, Twitter/X and other platforms. Campaign strategy, audience targeting, bidding, ROAS/CPA optimization, ABM and retargeting, with 15 deep-dive references. |
| [ai-writing-detector](./skills/ai-writing-detector/SKILL.md) | Scan text for 22 AI writing patterns and produce per-location detection reports. Diagnosis-only by default, no rewriting. |
| [copywriting](./skills/copywriting/SKILL.md) | Product copywriting framework: positioning, value propositions, personas, feature-to-benefit conversion, and multi-length product descriptions. |
| [cro](./skills/cro/SKILL.md) | Conversion rate optimization: landing page structure, hero copy, pain points, social proof, pricing anchoring, and CTA design. |
| [social](./skills/social/SKILL.md) | Social media content package generation across platforms with post variations, hashtags, and engagement hooks. |
| [wechat-article-html](./skills/wechat-article-html/SKILL.md) | Convert Markdown into WeChat Official Account compatible inline-style HTML. 15 built-in themes, strict paste-compatibility rules (no style tags/classes, all styles inline). |

### Business Consulting

| Skill | Description |
|---|---|
| [business-toolbox](./skills/business-toolbox/SKILL.md) | dontbesilent 商业工具箱主入口，提供新手教程与单任务动态编排。 |

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
│   ├── code-to-prd/                 # Reverse-engineer codebase into PRD
│   ├── codebase-analyzer/           # Evidence-based codebase investigation
│   ├── design-taste-frontend/       # Anti-slop frontend art direction
│   ├── diagram-design/              # 42 diagram types generation
│   ├── douyin-to-feishu-archiver/   # Douyin video → Feishu archive
│   ├── gsap-scroll-landing/         # GSAP scroll-driven landing pages
│   ├── ios-ui-ux-dev/               # iOS multi-channel UI/UX audit
│   ├── project-finishing-workflow/  # Project delivery closure workflow
│   ├── rea-reverse-engineering/     # REA-based reverse engineering
│   ├── reverse-engineering-suite/   # Unified reverse-engineering suite
│   ├── site-launch-checklist/       # Pre-launch production checklist
│   └── ...                          # and 22 more
├── LICENSE
└── README.md
```

## Adding a New Skill

1. Create `skills/<your-skill-name>/SKILL.md`
2. Folder name must exactly match the `name` field in the YAML frontmatter
3. `SKILL.md` must be all-caps (not `skill.md` or `SKILL.MD`)
4. Keep the Markdown body under 500 lines; move detailed references to `references/`
5. Prefer executable scripts over pure prompts — S-grade skills must have `scripts/` or `references/`
6. Test locally: `npx skills add ./ --list`
7. Commit and push

## License

MIT
