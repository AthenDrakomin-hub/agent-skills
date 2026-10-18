---
name: context-mode
description: "AI 编程上下文优化（带分析脚本）。context-analyzer.py 自动扫描项目上下文体积，估算 token 消耗，识别大文件，给出瘦身建议和 think-in-code 模式。配合 Context Mode MCP server 使用，可减少 98% 上下文消耗。Use when: context optimization, 上下文优化, save tokens, context window, think-in-code, session continuity, 省token, 上下文溢出, 大文件处理, AI编程效率."
license: MIT
compatibility: Scripts require Python 3.8+. MCP server requires Node.js >= 18. Works with Claude Code, Cursor, Codex CLI, Gemini CLI, VS Code Copilot, OpenCode.
metadata:
  author: mksglu (curated by AthenDrakomin-hub)
  version: "2.0.0"
  category: development
  source: "https://github.com/mksglu/context-mode"
---

# Context Mode v2.0

## Role

上下文优化专家。帮助 AI 编程助手避免上下文溢出，实践 "think-in-code" 模式，用脚本处理数据而不是 Read 整个文件。

**v2.0 升级**：内置 `context-analyzer.py` 自动分析项目上下文体积。

## 内置脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/context-analyzer.py` | 扫描项目上下文体积，估算 token，识别大文件，给出瘦身建议 | `python3 context-analyzer.py <项目路径>` |

**纯 Python 标准库，零依赖。**

## 快速使用

```bash
# 分析项目上下文
python3 scripts/context-analyzer.py ./my-project

# 显示最大的20个文件
python3 scripts/context-analyzer.py ./my-project --top 20

# 输出到文件
python3 scripts/context-analyzer.py ./my-project --output context-report.md

# JSON 格式（CI 集成）
python3 scripts/context-analyzer.py ./my-project --json
```

## 它解决什么问题

一个 Playwright 快照 56KB，20 个 GitHub issue 59KB，一条访问日志 45KB。30 分钟后 40% 上下文就没了。

Context Mode 坐在 AI Agent 和这些输出之间：315KB 变成 5.4KB（减少 98%）。

## context-analyzer.py 检测内容

| 检测项 | 说明 |
|---|---|
| 总 Token 估算 | 按 3 字符/token 估算全部代码文件的上下文消耗 |
| 风险等级 | low/medium/high/critical 四级评估 |
| 大文件识别 | >300 行标记警告，>800 行标记不应直接 Read |
| Top 文件排行 | 按 token 消耗排序，找出最占空间的文件 |
| 按类型统计 | 各扩展名的文件数、行数、token 占比 |
| 瘦身建议 | 针对项目情况给出具体的上下文优化建议 |

## 风险等级

| 等级 | 总 Token | 含义 |
|---|---|---|
| 🟢 LOW | <20K | 可以自由读取 |
| 🟡 MEDIUM | 20K-50K | 需要选择性读取 |
| 🟠 HIGH | 50K-100K | 上下文压力大，必须用脚本处理 |
| 🔴 CRITICAL | >100K | 单次 Read 全部会溢出，必须 think-in-code |

## Think-in-Code 模式

核心原则：**不 Read 原始数据，写小脚本执行，只返回精简结果。**

```bash
# ❌ 不要这样：Read 整个 500 行日志
# Read /var/log/app.log  → 50KB / 16K tokens

# ✅ 应该这样：用脚本定向提取
grep ERROR /var/log/app.log | tail -20  → 2KB / 600 tokens

# ❌ 不要这样：Read 整个配置
# Read config.yaml  → 10KB / 3K tokens

# ✅ 应该这样：提取需要的部分
grep -A5 'database:' config.yaml  → 500B / 150 tokens
```

## Context Mode MCP Server（可选增强）

如果需要更强大的上下文管理，可以安装 MCP server：

```bash
# npx 方式（最简单）
npx -y @mksglu/context-mode@latest

# Claude Code 配置
# 在 ~/.claude.json 的 mcpServers 中添加：
# "context-mode": {
#   "command": "npx",
#   "args": ["-y", "@mksglu/context-mode@latest"]
# }
```

### MCP 工具

| 工具 | 作用 |
|---|---|
| `ctx_execute` | 在沙箱中运行脚本，返回精简结果 |
| `ctx_index` | 将大输出索引到 FTS5 全文搜索 |
| `ctx_search` | 搜索索引内容，只返回匹配段落 |
| `ctx_snapshot` | 压缩前构建恢复快照 |
| `ctx_restore` | 压缩后恢复会话状态 |

## 最佳实践

1. **先用 context-analyzer.py 扫描**，了解项目上下文体积
2. **大文件用 grep/脚本定向读取**，不要 Read 整个文件
3. **数据探索用脚本**，把结果控制在 5KB 以内
4. **输出 >5KB 时先索引再搜索**，不要全部加载
5. **长操作前做快照**，防止上下文压缩后丢失状态
6. **保持脚本 <200 字节**，think-in-code 用小而精准的脚本

## 工作流

1. 新项目开始时运行 `context-analyzer.py`，了解上下文基线
2. 遇到大文件时，先 grep 定位，再 Read 特定行范围
3. 需要分析大量数据时，写脚本处理而不是 Read 全部
4. 定期重新扫描，监控上下文体积变化
5. 如果安装了 MCP server，用 `ctx_execute` 替代直接 Read

## References

- `scripts/context-analyzer.py` — 上下文体积分析器（token估算、大文件识别、瘦身建议）
- 官方 MCP: https://github.com/mksglu/context-mode
