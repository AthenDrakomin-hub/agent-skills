---
name: uniapp-release-notes
description: "Query HBuilder X / uni-app / uni-app x official changelog for version selection, API compatibility checks, new feature discovery, and known-bug avoidance. Uses bundled offline release notes (33 versions, 2024-03 to 2026-09) with a Python query script. Use when: starting a new uni-app project and unsure which version to use, checking if an API/component/CSS property is supported, looking for known bugs or breaking changes, comparing changes between versions, uni-app x steam mode compatibility, HarmonyOS support. Triggers: uni-app version, HBuilder X changelog, 发版说明, 版本选型, uni-app x, 蒸汽模式, 鸿蒙."
license: MIT
metadata:
  author: AthenDrakomin-hub
  version: "1.0.0"
  category: mobile-dev
---

# uni-app 发版说明查询

面向 **HBuilder X / uni-app / uni-app x 新项目开发**，用 bundled 的中文发版说明（33 个版本，4.06/2024-03 ~ 5.26/2026-09-17）回答"版本改了什么、当前支持什么、有什么坑"。

数据是一份离线快照，文件内最新版本为 **5.26.2026091702（2026-09-17）**。若用户问的是比这更新的改动，先说明"快照截至 2026-09-17，以下为快照内信息"。

## 核心原则

- **不要把整个 md 读进上下文**（约 500KB）。一律用 `scripts/query_releasenotes.py` 做过滤查询；只有当脚本结果不足时才对 `references/releasenotes_zh_CN.md` 做定向 grep。
- **先定位范围再输出**：根据用户项目判断（a）框架变体：`uni-app x`（蒸汽模式，5.26 起新建项目默认）还是经典 `uni-app`；（b）目标平台：Android / iOS / 鸿蒙 / Web / App / 小程序。判断不清时，用一句话追问，不要把全量结果甩给用户。
- **输出必须带版本号和出处链接**（issue / 文档），结论注明"来自 X 版本发版说明"。

## 快速命令

脚本路径（在 skill 目录内执行，或用绝对路径）：

```bash
python3 scripts/query_releasenotes.py <子命令> [过滤参数]
```

### 1. 版本选型 / 总览

新项目问"用哪个版本、最新版有什么大事"：

```bash
python3 scripts/query_releasenotes.py overview                 # 全部版本+计数
python3 scripts/query_releasenotes.py show --latest 1 --type 重要   # 最新版【重要】条目
python3 scripts/query_releasenotes.py show --latest 2 --module "uni-app x" --type 变更
```

回答时重点提炼：【重要】条目（如 5.26 起新建项目默认 uni-app x 蒸汽模式）、破坏性【变更】、当前版本针对目标平台的已知【修复】高发区。

### 2. 能力是否支持 / 某功能哪个版本引入

```bash
python3 scripts/query_releasenotes.py search --keyword list-view --module "uni-app x"
python3 scripts/query_releasenotes.py search --keyword backdrop-filter
python3 scripts/query_releasenotes.py search --keyword 鸿蒙 --type 新增 --limit 15
```

按版本从新到旧输出。"某能力从哪版开始"= 找到该关键词最早出现的【新增】条目；"当前是否支持"= 看最新版是否仍有对应【修复】/【变更】在改它。

### 3. 已知 bug / 避坑

新项目开工前查目标组件或 API 是否有未修复的坑：

```bash
python3 scripts/query_releasenotes.py search --keyword video --platform android --type 修复
python3 scripts/query_releasenotes.py search --keyword 白屏 --limit 20
```

注意：`--type 修复` 只表示某版本修了它，不代表所有版本都修。回答时给出版本号，提醒用户"需确认自己用的版本 ≥ 修复版本"。

### 4. 跨版本区间

```bash
python3 scripts/query_releasenotes.py range --from 5.14 --to 5.26 --module "uni-app" --type 新增
```

`--from`（新）/ `--to`（旧）顺序写反也会自动纠正；版本号可只写 `5.14` 前缀。

## 过滤参数速查

| 参数 | 取值（逗号分隔可多选） |
|---|---|
| `--module` | `HBuilder`、`uni-app x`、`uni-app`、`uts插件`、`uniCloud`、`App插件`、`miniprogram`（小程序SDK） |
| `--platform` | `android`、`ios`、`harmony`（鸿蒙）、`web`、`app`、`windows`、`macos`、`mp-weixin`、`mp-alipay`、`steam`（蒸汽模式） |
| `--type` | `新增`、`修复`、`优化`、`变更`、`重要`、`升级` |
| `--keyword` | 不区分大小写，匹配条目正文 |
| `--limit N` | 最多输出 N 条 |
| `--no-links` | 不输出链接 |

模块匹配是子串匹配：`--module "uni-app"` 会同时命中 `uni-app` 和 `uni-app x`（通常正是想要的）；只要经典版时靠上下文区分。

## 新项目开发典型应答套路

1. **"新项目用哪个版本？"** → `overview` + 最新版 `--type 重要`/`--type 变更`，给出最新稳定版本号、新建项目默认栈（uni-app x 蒸汽模式）、需注意的破坏性变更。
2. **"X 组件/API 现在支持吗？"** → `search --keyword X`，按版本从新到旧看：最新版有没有【新增】/【优化】/【修复】，判断成熟度与平台覆盖。
3. **"X 有没有坑？"** → `search --keyword X --type 修复`，列出最近修过的问题，提醒对照自己的版本。
4. **"X 和 Y 版之间改了什么？"** → `range --from X --to Y`，按模块汇总【新增】能力与【变更】/【重要】风险点。

## 注意事项

- 脚本退出码：0=有结果；1=用法错误；2=无匹配。无结果时换更短的关键词（如用 `canvas` 替代 `createCanvasContext`），或去掉平台/类型过滤重试。
- 发版说明只记录"改了什么"，不替代官方 API 文档；需要具体参数/用法时引导用户看条目中附带的 `[文档](...)` 链接。
- 平台标签 `App平台` 是泛指，`Android平台`/`iOS平台` 更具体；过滤时按用户实际目标平台选。

## Resources

- `references/releasenotes_zh_CN.md` — HBuilder X 官方中文发版说明全文（快照，约 500KB）。不要整读；脚本已解析。
- `scripts/query_releasenotes.py` — 解析与查询脚本（纯 Python 标准库，无第三方依赖）。
