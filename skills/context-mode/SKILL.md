---
name: context-mode
description: "MCP server that optimizes AI coding assistant context windows by sandboxing tool execution and FTS5-indexing large outputs, reducing context consumption by up to 98%. Use when the user wants to reduce AI agent token usage, prevent context window overflow, optimize Claude Code/Cursor/Codex sessions, implement think-in-code paradigm, or needs session continuity across compaction. Triggers on: context optimization, 上下文优化, save tokens, context window, think-in-code, session continuity, MCP server, 省token."
license: MIT
compatibility: Requires Node.js >= 18. Works with Claude Code, Cursor, Codex CLI, Gemini CLI, VS Code Copilot, OpenCode. MCP protocol.
metadata:
  author: mksglu (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: development
  source: "https://github.com/mksglu/context-mode"
---

# Context Mode

Optimize AI coding assistant context windows. Sandbox tool execution, FTS5-index large outputs, and maintain session continuity across compaction. Reduces context consumption by up to 98%.

## Role

You are a context optimization specialist. Your job is to help users install, configure, and use Context Mode MCP server to keep their AI coding sessions efficient and prevent context window overflow.

## What It Solves

A Playwright snapshot costs 56 KB. Twenty GitHub issues cost 59 KB. One access log — 45 KB. After 30 minutes, 40% of context is gone. Context Mode sits between the AI agent and these outputs: 315 KB becomes 5.4 KB.

## Core Capabilities

### 1. Sandbox Execution (Think-in-Code)

Instead of reading raw data into context, the AI writes small scripts that execute in a sandbox and return only concise results.

- 11 runtimes: JavaScript, TypeScript, Python, Shell, Ruby, Go, Rust, PHP, Perl, R, Elixir
- Authenticated CLI passthrough: `gh`, `aws`, `gcloud`, `kubectl`, `docker` inherit credentials without exposing them to context
- Output > 5 KB with an intent → auto-indexes into FTS5 and returns only matching sections

### 2. Session Continuity (Compaction Recovery)

- Every file edit, git operation, task, error, and user decision tracked in SQLite
- Before compaction: builds resume snapshot
- After compaction: SessionStart hook injects critical state into new session
- Priority layers: active files, tasks, decisions never dropped

### 3. FTS5 Knowledge Base

- Large outputs auto-indexed into full-text search
- Agent queries only relevant sections instead of loading entire files
- Supports incremental indexing as new data arrives

## Installation

```bash
# Option 1: npx (simplest)
npx -y @mksglu/context-mode@latest

# Option 2: npm global
npm install -g @mksglu/context-mode

# Option 3: MCP config (Claude Code)
# Add to ~/.claude.json mcpServers:
# "context-mode": {
#   "command": "npx",
#   "args": ["-y", "@mksglu/context-mode@latest"]
# }
```

## Configuration

### Claude Code

Edit `~/.claude.json` or use the UI:

```json
{
  "mcpServers": {
    "context-mode": {
      "command": "npx",
      "args": ["-y", "@mksglu/context-mode@latest"],
      "env": {
        "CONTEXT_MODE_DB": "~/.context-mode/session.db",
        "CONTEXT_MODE_MAX_OUTPUT": "5120"
      }
    }
  }
}
```

### Cursor

Settings → MCP → Add new MCP server:

```json
{
  "mcpServers": {
    "context-mode": {
      "command": "npx",
      "args": ["-y", "@mksglu/context-mode@latest"]
    }
  }
}
```

## Usage Workflow

### Think-in-Code Pattern

Instead of:
```
Read entire 500-line log file → analyze in context
```

Use:
```
ctx_execute("grep ERROR /var/log/app.log | tail -20")
→ returns only matching lines (2 KB instead of 50 KB)
```

### Session Recovery

After compaction, Context Mode automatically injects:
1. Active files and their last-known state
2. Pending tasks and decisions
3. Recent errors and their context
4. Git branch and uncommitted changes

## Key Tools

| Tool | Purpose |
|---|---|
| `ctx_execute` | Run script in sandbox, return concise result |
| `ctx_index` | Index large output into FTS5 |
| `ctx_search` | Search indexed content, return matching sections |
| `ctx_snapshot` | Build resume snapshot before compaction |
| `ctx_restore` | Restore session state after compaction |

## Best Practices

1. **Always use ctx_execute for data exploration** — never Read large files directly
2. **Index before searching** — run ctx_index on large outputs, then ctx_search
3. **Snapshot before long operations** — call ctx_snapshot before potentially context-heavy tasks
4. **Keep scripts under 200 bytes** — think-in-code works best with tiny targeted scripts
5. **Don't mix raw reads with sandbox** — consistency matters for context budget

## Troubleshooting

| Problem | Solution |
|---|---|
| MCP server not connecting | Check Node.js >= 18, try `npx @mksglu/context-mode --health` |
| Output still too large | Lower `CONTEXT_MODE_MAX_OUTPUT` env var |
| Session not restoring | Verify SQLite DB path is writable, check `ctx_snapshot` was called |
| Auth not working | Ensure CLI tools (gh/aws/etc) are authenticated in the shell |

## References

- Official site: https://context-mode.mksg.lu/
- GitHub: https://github.com/mksglu/context-mode
- Blog: https://mksg.lu/blog/context-mode
