---
name: wechat-article-html
description: "Markdown 转微信公众号 HTML（带自动化转换脚本）。把 Markdown 文稿转换成符合微信公众号粘贴规范的行内样式 HTML，内置 15 种风格，所有样式直接写在每个元素上。md2wechat.py 一键转换，validate-html.py 自动验证粘贴规范。Use when: user asks to generate WeChat article HTML, format markdown for 公众号, create WeChat version of an article, 排版公众号文章, 微信公众号HTML, markdown to wechat, 公众号排版, 公众号转换."
license: MIT
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: content
---

# WeChat Article HTML Generator v2.0

## Role

你是微信公众号 HTML 生成工具。把用户给的 Markdown 文稿转换成可在浏览器打开、全选复制、粘贴到微信公众号后台并保持排版的 HTML。

**v2.0 升级**：内置 `md2wechat.py` 自动转换脚本和 `validate-html.py` 验证脚本，不再靠 AI 手动写 HTML。

## 核心能力

- 用 `md2wechat.py` 把 Markdown 一键转成公众号 HTML
- 15 种内置风格，支持单风格 / 6种推荐 / 全部15种
- 用 `validate-html.py` 自动验证是否符合粘贴规范
- 生成预览总览页，方便比较风格

## 内置脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/md2wechat.py` | Markdown 转公众号 HTML，15种风格，行内样式展开 | `python3 md2wechat.py 文章.md --style minimal` |
| `scripts/validate-html.py` | 验证 HTML 是否符合公众号粘贴规范（11项检查） | `python3 validate-html.py 输出.html` |

**纯 Python 标准库，零依赖。**

## 快速使用

### 1. 单风格转换

```bash
python3 scripts/md2wechat.py 文章.md --style minimal
```

输出到 `公众号HTML输出/文章_minimal_极简黑白_微信公众号版.html`

### 2. 6种推荐风格 + 总览页

```bash
python3 scripts/md2wechat.py 文章.md --preview
```

### 3. 全部15种风格 + 总览页

```bash
python3 scripts/md2wechat.py 文章.md --all
```

### 4. 验证生成的 HTML

```bash
python3 scripts/validate-html.py 公众号HTML输出/文章_minimal_极简黑白_微信公众号版.html
```

### 5. 列出所有风格

```bash
python3 scripts/md2wechat.py --list-styles
```

## 15 种风格

| style id | 风格 | 适合 |
|---|---|---|
| `minimal` ★ | 极简黑白 | 默认款、方法论、诊断报告 |
| `medium` ★ | Medium Essay | 长文观点、个人文章 |
| `wired` ★ | WIRED Feature | 科技观点、AI、产品发布 |
| `stripe` ★ | Stripe Docs | 工具说明、教程、产品文档 |
| `ft` ★ | FT Analysis | 商业分析、市场判断 |
| `course` ★ | 课程讲义 | 课程、教程、学习笔记 |
| `apple` | Apple Newsroom | 正式公告、品牌稿 |
| `linear` | Linear Changelog | 版本更新、changelog |
| `github` | GitHub README | 开源、安装说明 |
| `notion` | Notion Memo | 备忘录、内部总结 |
| `magazine` | Magazine Feature | 杂志、人物稿、品牌故事 |
| `editorial` | Editorial Column | 专栏、创作者随笔 |
| `newspaper` | Newspaper Report | 报道、调查、严肃分析 |
| `verge` | The Verge Briefing | 年轻、热点、资讯评论 |
| `event` | 活动公告 | 活动、招募、转化 |

★ = 推荐风格（--preview 生成这6种）

## 微信粘贴规范（脚本自动保证）

`md2wechat.py` 生成的 HTML 自动遵守以下规则：

1. **所有样式写在元素的 style 属性上** — 不使用 `<style>` 标签、class、id
2. **禁止伪元素** — :before/:after 不支持
3. **禁止外部资源** — 不加载外部 CSS/字体/图片/脚本
4. **扁平结构** — 正文元素直接在 `<body>` 下
5. **稳定 CSS 子集** — 只用 font-family/font-size/color/margin/padding/border 等
6. **消除双标题** — Markdown 第一个 `# 标题` 写入 `<title>`，不进入正文
7. **表格转列表** — 微信公众号 `<table>` 兼容性差，优先转列表
8. **图片保留占位** — 不内嵌图片，保留 `[图片：描述]` 占位

`validate-html.py` 会检查以上所有项，评分 100 分制，低于 100 会列出具体问题。

## Markdown 支持元素

| Markdown | HTML |
|---|---|
| 首个 `# 标题` | 写入 `<title>`，不进入正文 |
| 后续 `# 标题` | 降级为 `<h2>` |
| `## 标题` / `### 标题` | `<h2>` / `<h3>` |
| 普通段落 | `<p>`（自动去段末中文句号） |
| `> 引用` | `<blockquote>` |
| `- 列表` / `1. 列表` | `<ul><li>` / `<ol><li>` |
| `**粗体**` | `<strong>` |
| `` `代码` `` | `<code>` |
| ` ```代码块``` ` | `<pre><code>` |
| `---` | `<hr>` |
| `[链接](url)` | 保留链接文本（公众号不支持超链接） |

## 工作流

1. 用户给 Markdown 文件或文本
2. 如果用户没指定风格，问一句：单风格 / 6种推荐 / 全部15种 / 指定风格
3. 运行 `md2wechat.py` 生成 HTML
4. 运行 `validate-html.py` 验证，确保 100 分
5. 告诉用户：打开 HTML → Cmd+A 全选 → Cmd+C 复制 → 粘贴到公众号后台

## 用户使用提示

生成完成后告诉用户：

```text
已生成。

打开 HTML 后：
1. Cmd+A 全选
2. Cmd+C 复制
3. 粘贴到微信公众号后台编辑器
4. 用微信后台预览检查手机端效果
```

如果生成了多个风格，告诉用户先在总览页比较，选定后再复制对应 HTML。

## References

- `templates/styles.md` — 15 种风格的 CSS 权威来源（23KB）
- `scripts/md2wechat.py` — Markdown 转公众号 HTML 核心转换脚本
- `scripts/validate-html.py` — 公众号粘贴规范验证器（11项检查，100分制）
