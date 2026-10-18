# agent-skills

A collection of reusable AI Agent Skills for daily development, DevOps, and content automation.

## Skills (67)

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
| [github-tech-advisor](./skills/github-tech-advisor/SKILL.md) | GitHub技术优化顾问：扫描项目技术栈与设计系统，基于开源生态调研最新高性价比方案，输出可执行优化 Plan 并落地清理。 |
| [project-rules-migration](./skills/project-rules-migration/SKILL.md) | 审计项目规则文件、识别真源、统一命名并生成桥接，把项目迁移成多端一致的 Agent 工作台（AGENTS.md / Claude Code / Codex / Grok）。 |
| [skill-forge](./skills/skill-forge/SKILL.md) | 技能制作器：把反复出现的问题制作成可安装、可分级验证的单个 Skill，含需求分析与候选 Skill 检查测试。 |
| [skill-installer](./skills/skill-installer/SKILL.md) | 技能安装器：把单个或一批 Skill 安装到 Claude Code / Codex / Hermes / Kiro / Qwen Code / Cline 等 Agent。 |

### Creative & Media

| Skill | Description |
|---|---|
| [artcraft](./skills/artcraft/SKILL.md) | Open-source AI image/video creation IDE. Build 3D scenes, pose objects, light and photograph, feed renders back into generation. Consistent characters across angles. Local + browser. |
| [voice-studio](./skills/voice-studio/SKILL.md) | Open-source local ElevenLabs alternative. Voice cloning, dubbing, transcription, audiobook creation in 646 languages. Fully local, no cloud API, AGPL-3.0. |
| [gsap-ad-replica](./skills/gsap-ad-replica/SKILL.md) | GSAP广告大片复刻：VibeCoding 风格网页广告大片复刻技能，GSAP + ScrollTrigger 生成滚动驱动动画落地页，产品视差、逐字入场、流体循环特效、分段叙事滚动。 |
| [video-content-extraction](./skills/video-content-extraction/SKILL.md) | 视频内容提取：接收抖音/小红书/视频号等短视频链接或分享文案，查询作品/账号数据并提取语音文字稿，按作者和标题归档为 Markdown。 |
| [short-video-hook-optimizer](./skills/short-video-hook-optimizer/SKILL.md) | 短视频开头优化：诊断短视频开头的问题并生成优化方案，提高开场吸引力或降低开头流失。 |
| [short-video-script-check](./skills/short-video-script-check/SKILL.md) | 短视频脚本检查：检查短视频逐字稿的段落衔接、信息密度和口播流畅度，定位观众可能划走的位置。 |

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
| [ios-ui-audit](./skills/ios-ui-audit/SKILL.md) | iOS界面审计开发：iOS App 界面 UI/UX 的多通道审计、排障与开发，支持截图视觉走查、原生源码静态审计、H5 套壳审计、IPA 解包审计四类证据输入。 |
| [uniapp-multi-audit](./skills/uniapp-multi-audit/SKILL.md) | uniapp多端体验审计：聚焦 iOS App / Android App / H5 三端的界面体验差异、交互流畅度、视觉一致性，代码扫描定位 UI 隐患并输出可落地优化方案。 |

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
| [ads](./skills/ads/SKILL.md) | Paid advertising campaign help for Google Ads, Meta, LinkedIn, Twitter/X and other platforms. Campaign strategy, audience targeting, bidding, ROAS/CPA optimization, ABM and retargeting, with 15 deep-dive references. |

### Business Consulting (dontbesilent)

The dontbesilent (dbs) business-diagnosis family. A diagnostic toolkit for business models, execution, content and knowledge work: entry routing, JTBD framing, diffusion/theory analysis, and multi-role chatrooms.

| Skill | Description |
|---|---|
| [business-toolbox](./skills/business-toolbox/SKILL.md) | dontbesilent 商业工具箱主入口，提供新手教程与单任务动态编排。 |
| [auto-triage](./skills/auto-triage/SKILL.md) | 自动识别用户是在解决具体商业问题还是希望全面检查商业模式，并进入对应诊断流程（问诊/体检）。 |
| [expert-chatroom](./skills/expert-chatroom/SKILL.md) | 专家聊天室：根据话题推荐或接受指定专家，模拟多角色对话并总结分歧。 |
| [austrian-economics-chatroom](./skills/austrian-economics-chatroom/SKILL.md) | 奥派经济学聊天室：哈耶克、米塞斯与 Claude 从奥派经济学视角展开多角色讨论。 |
| [benchmark-screening](./skills/benchmark-screening/SKILL.md) | 对标筛选：用五重过滤法寻找值得模仿的对标，排除主体差异噪音。 |
| [business-problem-breakdown](./skills/business-problem-breakdown/SKILL.md) | 商业问题拆解：用维特根斯坦与奥派经济学方法拆解模糊的商业概念。 |
| [content-diagnosis](./skills/content-diagnosis/SKILL.md) | 内容诊断：诊断如何把已确定的选题做成好内容，检查文案与改善表达。 |
| [content-resonance-analysis](./skills/content-resonance-analysis/SKILL.md) | 内容共鸣分析：用传播学与社会心理学理论诊断共鸣机制、问题位置和修改方向。 |
| [content-risk-check](./skills/content-risk-check/SKILL.md) | 内容风险检查：逐句检查标题/正文/字幕/口播/画面等平台违规风险，给出最小修改动作。 |
| [diffusion-analysis](./skills/diffusion-analysis/SKILL.md) | 传播效果分析：解码内容共鸣机制、受众情绪、有效立场与传播动机。 |
| [execution-blockage-diagnosis](./skills/execution-blockage-diagnosis/SKILL.md) | 执行阻滞诊断：用阿德勒心理学框架诊断"知道却不做"的拖延与行动中断路径。 |
| [goal-probing](./skills/goal-probing/SKILL.md) | 目标追问：只追问影响执行/验收的信息，把模糊愿望整理成可行动、可检查的交付物。 |
| [jtbd-task-model](./skills/jtbd-task-model/SKILL.md) | JTBD任务模型：用 Jobs to Be Done 识别用户想推进的进展与切换方案的力量，优化产品/内容/提示词。 |
| [knowledge-base-builder](./skills/knowledge-base-builder/SKILL.md) | 知识库构建：把本地文件夹建成 Agent 可稳定查找/收录/维护的知识库，含 SOT 分层治理。 |
| [long-term-decision-tracker](./skills/long-term-decision-tracker/SKILL.md) | 长期决策跟踪：把长期问题建成决策知识工程，支持立案、回填、状态画像与复盘。 |
| [question-rewriting](./skills/question-rewriting/SKILL.md) | 问题改写优化：把模糊问题改写成 Agent 可推理/可批评/可验证的问题说明书。 |
| [standard-answer-gen](./skills/standard-answer-gen/SKILL.md) | 标准答案生成：挖掘行业/学科/理论 + 历史成败反例比较，提炼带条件的标准答案。 |
| [study-article-splitter](./skills/study-article-splitter/SKILL.md) | 学习文章拆分：把课题拆成连续学习文章，按反馈调整深度、角度和节奏。 |
| [theory-support-analysis](./skills/theory-support-analysis/SKILL.md) | 理论支撑分析：审查经验判断，匹配并核实可信理论，用该理论重释案例并标明边界。 |
| [diagnosis-report-gen](./skills/diagnosis-report-gen/SKILL.md) | 诊断报告生成：把多次 dbs-save 存档合并成可交付的 Markdown 报告。 |
| [diagnosis-state-save](./skills/diagnosis-state-save/SKILL.md) | 诊断状态保存：把当前诊断关键状态存到本地，支持跨会话续接与存档位置管理。 |
| [diagnosis-state-restore](./skills/diagnosis-state-restore/SKILL.md) | 诊断状态恢复：恢复由 dbs-save 保存的最近诊断状态，接着上次结论继续。 |

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
