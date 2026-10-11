# agent-skills

A collection of reusable AI Agent Skills for daily development, DevOps, and content automation.

## Skills

| Skill | Description |
|---|---|
| [douyin-to-feishu-archiver](./skills/douyin-to-feishu-archiver/SKILL.md) | Parse Douyin video links into reusable AI prompts and archive them to a Feishu folder with category tags |
| [boxim-release-assistant](./skills/boxim-release-assistant/SKILL.md) | Build, deploy, health-check, and roll back the boxim IM system across 3 frontends and 3 Java backend services |
| [git-safety-guard](./skills/git-safety-guard/SKILL.md) | Pre-commit secret scanning, .gitignore audit, and pull-modify-commit-push workflow enforcement |

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
│   ├── douyin-to-feishu-archiver/
│   │   ├── SKILL.md          # Entry point (required)
│   │   ├── scripts/          # Executable helpers
│   │   ├── references/       # On-demand reference docs
│   │   └── assets/           # Templates & static resources
│   ├── boxim-release-assistant/
│   │   └── SKILL.md
│   └── git-safety-guard/
│       └── SKILL.md
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
