---
name: conversational-ai-dev-workflow
description: "用豆包/Grok等通用对话式AI从零开发项目的完整工作流。适用于没有项目上下文记忆、不能直接读写本地文件、不能自动运行代码的对话式AI工具。5阶段闭环+5份可复制提示词模板+项目上下文摘要生成脚本。Use when: develop project with Doubao/Grok, conversational AI coding, 从零开发项目, 豆包写代码, Grok开发, 对话式AI编程, 无IDE开发, 手动验证循环."
license: MIT
compatibility: "Works with Doubao, Grok, ChatGPT, and any conversational AI without file system access. Python 3.8+ for the context summary script. No other external dependencies."
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: development
  source: "用豆包Grok从零开发项目完整工作流.md"
---

# 对话式 AI 从零开发项目工作流

## Role

你是对话式 AI 开发教练。指导用户使用豆包、Grok 等通用对话式 AI 从零开发完整项目。这类工具**无记忆、不能读写本地文件、不能运行代码**，用户充当"AI 和电脑之间的桥梁"。

## Core Difference

把对话式 AI 当成"能力很强但记性很差、手够不到你电脑的远程实习生"。你负责贴上下文和代码，它负责生成方案和代码，你负责本地验证和反馈。

| 特性 | 应对 |
|---|---|
| 无记忆 | 每次开新对话重新交代背景（用 `scripts/project-context-summary.py` 自动生成） |
| 不能运行代码 | 你复制到本地运行，报错贴回去让它修 |
| 不能读写文件 | 涉及具体代码时把文件内容贴给它 |
| 回复有长度上限 | 拆成模块，分多次写 |
| 对话式推进 | 设计分阶段对话脚本，一步一步走 |

## Workflow（5 阶段）

```
阶段0 项目骨架 → 阶段1 搭骨架代码 → 阶段2~N 逐个模块开发 → 阶段M 收尾验收 → 最终 独立验收
   (新对话)        (新对话)           (每模块新对话)          (新对话)          (换角色新对话)
```

每个阶段的详细提示词模板在 `references/` 中按需加载：

| 阶段 | 提示词文件 | 核心动作 | 通过标准 |
|---|---|---|---|
| 0. 项目骨架 | `references/stage-0-skeleton-prompt.md` | 贴想法→AI出需求清单+技术方案+目录结构 | 人审确认方案 |
| 1. 搭骨架 | `references/stage-1-scaffold-prompt.md` | 贴方案→AI出初始化代码 | 本地能跑起来 |
| 2~N. 模块开发 | `references/stage-2-module-prompt.md` | 贴背景+骨架→AI出模块代码 | 本地集成测试通过 |
| M. 收尾验收 | `references/stage-m-audit-prompt.md` | 贴完整项目→AI出缺口清单 | 逐项本地验证+逐个修复 |
| 最终. 独立验收 | `references/final-acceptance-prompt.md` | 换验收官角色逐条核对 | 验收官说"可以交付" |

## Scripts（自动化工具）

### project-context-summary.py

自动扫描项目，生成可直接粘贴到豆包/Grok 的上下文摘要，解决"每次开新对话都要重新交代背景"的痛点。

```bash
# 生成项目摘要（输出到终端，直接复制粘贴）
python scripts/project-context-summary.py /path/to/your-project

# 指定当前模块
python scripts/project-context-summary.py /path/to/your-project --module "用户登录模块"

# 输出到文件
python scripts/project-context-summary.py /path/to/your-project -o context.txt

# JSON 格式
python scripts/project-context-summary.py /path/to/your-project --format json
```

**输出内容**：项目名、技术栈（自动检测 package.json/requirements.txt/go.mod 等）、代码规模、目录结构、关键文件列表。

**纯 Python 标准库，无第三方依赖。**

## Universal Tips（7 个通用技巧）

1. **重新交代背景**：每次开新对话用 `project-context-summary.py` 生成摘要贴在开头
2. **少样本示例**：给一段你的代码风格示例，它会模仿
3. **输出启动**：提示词结尾加"以下是 Python 代码："，它会直接写代码
4. **函数级分解**：大任务拆成小函数，一个个要
5. **引用密集型启动**：用某个库前先把 API 文档喂给它
6. **安全导向写法**：用角色扮演"你是专注安全的资深开发者"
7. **代码解释**：要求"先解释逻辑再写代码"，既得代码又得文档

## Anti-Patterns

| 禁止行为 | 正确做法 |
|---|---|
| 一个对话塞完整项目 | 分阶段分模块，每个开新对话 |
| 新对话不交代背景 | 用脚本生成摘要贴在开头 |
| AI 说"应该可以了"就信 | 必须本地运行验证，报错贴回去 |
| 让写代码的 AI 自己验收 | 换新对话换角色做独立验收 |
| 一次让 AI 改多个 bug | 一次一个，修一个验一个 |
| 不贴代码就让 AI 改 | 把相关文件内容贴给它 |
| 跳过骨架直接写功能 | 先搭骨架跑通，再逐个加模块 |

## Example：用豆包做一个待办事项网页应用

1. **阶段0**：开新对话，用 stage-0 提示词 → 得到需求清单（增删改查/本地存储/过滤排序）+ 技术方案（纯前端 HTML+JS+localStorage）+ 目录结构
2. **阶段1**：开新对话，用 `project-context-summary.py` 生成摘要 + stage-1 提示词 → 得到 index.html + app.js 骨架，本地能打开
3. **阶段2**：每模块开新对话（贴摘要 + stage-2 提示词）→ 依次实现"添加/删除/编辑/过滤/本地存储"
4. **阶段M**：开新对话，贴完整项目 + stage-m 提示词 → 得到缺口清单，逐个开新对话修复
5. **最终**：开新对话换"验收官"角色 + final-acceptance 提示词 → 验收通过 → 交付

## Related Skills

| Skill | 关系 |
|---|---|
| `project-finishing-workflow` | 互补：本 Skill 从零开发，它是项目收尾补救 |
| `codebase-analyzer` | 配合：项目完成后做架构梳理 |
| `git-safety-guard` | 配合：提交代码前做安全扫描 |

## References Index

- `references/stage-0-skeleton-prompt.md` — 阶段0项目骨架提示词 + 产出物检查清单
- `references/stage-1-scaffold-prompt.md` — 阶段1搭骨架提示词 + 常见报错应对
- `references/stage-2-module-prompt.md` — 阶段2模块开发提示词 + 贴代码技巧 + 模块拆分建议
- `references/stage-m-audit-prompt.md` — 阶段M收尾验收提示词 + 单个bug修复提示词
- `references/final-acceptance-prompt.md` — 最终独立验收提示词 + 四层质量检查 + 边界场景清单
