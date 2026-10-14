---
name: skills-cli
description: "Vercel Labs open-source CLI for the agent skills ecosystem. Install, discover, update, and share skills across 80+ AI coding agents including Claude Code, Cursor, Codex, Gemini CLI, VS Code Copilot. Use when the user wants to install skills from GitHub, search for skills, update installed skills, manage skill repositories, or publish their own skills. Triggers on: npx skills, skills add, skills find, skills update, agent skills, skill management, 技能管理."
license: MIT
compatibility: Requires Node.js >= 18 and npx. Works across 80+ AI coding agents. No other dependencies.
metadata:
  author: Vercel Labs (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: development
  source: "https://github.com/vercel-labs/agent-skills"
---

# Skills CLI

The open-source command-line tool for the agent skills ecosystem. Install, discover, update, and share skills across 80+ AI coding agents.

## Role

You are a skills management specialist. Your job is to help users use the `npx skills` CLI to find, install, update, and publish AI agent skills.

## What It Is

Skills CLI (vercel-labs/agent-skills) is the standard package manager for AI agent skills. It works with Claude Code, Cursor, Codex, Gemini CLI, VS Code Copilot, OpenCode, and 75+ other agents.

## Core Commands

### Install Skills

```bash
# Install all skills from a GitHub repo
npx skills add <owner>/<repo>

# Install from full GitHub URL
npx skills add https://github.com/<owner>/<repo>

# Install from local folder
npx skills add ./path/to/skills

# Install a specific skill from a multi-skill repo
npx skills add <owner>/<repo> --skill <skill-name>

# Install globally (all projects)
npx skills add <owner>/<repo> -g

# Install to a specific agent
npx skills add <owner>/<repo> -a claude-code
```

### Search & Discover

```bash
# Interactive search (as you type)
npx skills find <keyword>

# Non-interactive search (for scripts/automation)
npx skills find <keyword> --json

# List skills in a repo without installing
npx skills add <owner>/<repo> --list
```

### Update & Manage

```bash
# Update all installed skills
npx skills update

# Update a specific skill
npx skills update <skill-name>

# List installed skills
npx skills list

# Remove a skill
npx skills remove <skill-name>
```

### Publish Your Own

```bash
# Validate your skill structure
npx skills validate ./path/to/skill

# Test local skill before publishing
npx skills add ./my-skill --list
```

## Supported Agents

The CLI auto-detects installed agents and installs to the correct directory:

| Agent | Install path |
|---|---|
| Claude Code | `~/.claude/skills/` or `./.claude/skills/` |
| Cursor | `./.cursor/skills/` |
| Codex CLI | `~/.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| VS Code Copilot | `./.github/skills/` |
| OpenCode | `~/.config/opencode/skills/` |

Use `-a <agent>` to target a specific agent, or `-g` for global install.

## Skill Structure Standard

Every skill must follow:

```
my-skill/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: executable helpers
├── references/       # Optional: on-demand reference docs
└── assets/           # Optional: templates, static files
```

SKILL.md frontmatter requirements:
- `name`: lowercase-hyphen, must match folder name, max 64 chars
- `description`: what it does + when to use, max 1024 chars, include trigger keywords

## Typical Workflow

### 1. Find a skill
```bash
npx skills find "landing page"
# → interactive search results from skills.sh index
```

### 2. Install it
```bash
npx skills add cathrynlavery/diagram-design
# → auto-detects your agent, installs to correct directory
```

### 3. Use it
The skill becomes available immediately in your AI agent. Trigger it by describing the task.

### 4. Keep updated
```bash
npx skills update
# → checks all installed skills for updates
```

## Creating & Publishing Skills

### 1. Create the structure
```bash
mkdir my-skill
cd my-skill
# Create SKILL.md with frontmatter
```

### 2. Validate
```bash
npx skills validate .
```

### 3. Push to GitHub
```bash
git init
git add .
git commit -m "Initial skill release"
git remote add origin git@github.com:your-username/my-skill.git
git push -u origin main
```

### 4. Get indexed
Push to a public GitHub repo. skills.sh automatically indexes public repos within hours. Add topics like `agent-skill`, `claude-code`, `cursor` to improve discoverability.

## Troubleshooting

| Problem | Solution |
|---|---|
| `command not found: npx` | Install Node.js >= 18 |
| Skill not detected by agent | Check install path matches agent's expected directory; use `-a <agent>` |
| `npx skills find` returns nothing | Check internet connection; skills.sh index may be updating |
| Permission denied on install | Use `-g` for global or ensure write access to agent skills directory |
| SKILL.md not recognized | Verify filename is exactly `SKILL.md` (case-sensitive), name matches folder |

## Environment Variables

| Variable | Purpose |
|---|---|
| `SKILLS_AGENT` | Default target agent (overrides auto-detect) |
| `SKILLS_HOME` | Custom global skills directory |
| `SKILLS_REGISTRY` | Custom registry URL (default: skills.sh) |

## References

- Official docs: https://vercel-labs-skills.mintlify.app/
- GitHub: https://github.com/vercel-labs/agent-skills
- Registry: https://skills.sh
- Vercel KB: https://vercel.com/kb/guide/agent-skills
