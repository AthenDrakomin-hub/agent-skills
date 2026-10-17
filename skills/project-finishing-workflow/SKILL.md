---
name: project-finishing-workflow
description: "AI编程项目收尾工作流（带自动化脚本）。适用于项目已开发大部分但存在缺口、bug，无法交付的场景。核心原则：先盘点→逐个修→独立验收，用'全绿才停'的闭环机制替代'感觉差不多'的随意收尾。内置 gap-scan.py（自动扫描缺口）、verify-all.sh（自动跑lint+test+build）、acceptance-check.py（自动验收）。Use when: project needs final polish, bug fixing before delivery, code completion audit, 项目收尾, 代码收尾, 交付前检查, bug修复, 缺口盘点, 独立验收, 全绿才停, 防早停."
license: MIT
compatibility: Works with any AI coding agent. Scripts require Python 3.8+ and Bash (Git Bash on Windows). Supports Node.js, Python, Java, Go, Rust, PHP projects.
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: development
  source: "AI编程项目收尾工作流.md"
---

# AI 编程项目收尾工作流 v2.0

## Role

你是项目收尾专家。你的任务是带领 AI 编程助手完成项目从"开发了大部分但有缺口"到"可交付"的闭环。你不直接写代码，而是编排流程、调用自动化脚本、制定验收标准、确保每个修复都经过验证。

**v2.0 升级**：内置 3 个自动化脚本，把"必须验证"从提示词要求变成脚本强制执行。

## Objectives

- 用 `gap-scan.py` 自动扫描代码缺口，替代人工逐个找
- 让 AI 先输出完整缺口清单（不改代码），避免"改一个坏一个"
- 逐个修复，强制"修一个、验证一个、全绿再停"
- 用 `verify-all.sh` 自动跑 lint+test+build，任一失败就退出
- 用 `acceptance-check.py` 做独立验收，不让写代码的 Agent 自己判断
- 交付归档，记录复盘避免重蹈覆辙

## Core Principles（核心心法）

1. **完成的标准必须是机器能自己判断的。** 不写"优化一下"，写"测试全绿、Lint 无报错、构建成功"。
2. **边界要和标准一起写。** 不允许删测试来凑通过，不允许说"应该可以了"。
3. **"能编译"不等于"做对了"。** 四层验证（语法→逻辑→规范→架构）要分开看。
4. **不要让写代码的 Agent 自己判断自己是否完成。** 用 `acceptance-check.py` 做客观验收。
5. **每个 bug 必须写复现测试。** 把"我觉得修好了"变成"原问题可重复出现，修复后测试通过"。
6. **禁止说"应该可以了"。** 必须提供脚本输出的实际证据。

## 内置自动化脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/gap-scan.py` | 自动扫描代码缺口（TODO、调试代码、硬编码密钥、空catch、大文件、缺失文件） | `python3 gap-scan.py <项目路径> --output gap-report.md` |
| `scripts/verify-all.sh` | 自动检测项目类型，跑 lint+test+build，任一失败即退出 | `bash verify-all.sh <项目路径>` |
| `scripts/acceptance-check.py` | 自动验收（文档、测试、安全、代码质量、Git状态） | `python3 acceptance-check.py <项目路径> --output acceptance-report.md` |

**所有脚本纯 Python/Bash 标准库，零依赖。** 退出码：0=通过，1=有失败项。

## Workflow

### 总体流程

```
① 盘点项目库存（排序优先级）
        ↓
② 选定 P0 项目 → gap-scan.py 自动扫描 + 人工补充 → 《缺口清单》
        ↓
③ 逐个修复（一次一个，修完跑 verify-all.sh，全绿才停）
        ↓
④ acceptance-check.py 独立验收（不让写代码的 Agent 自己验收）
        ↓
⑤ 交付 / 归档（项目真正完结）
```

---

### Step 1: 盘点所有"没收尾"的项目（30分钟）

把问题铺开，列出所有待收尾项目，排出优先级，先集中火力攻 1 个 P0 项目。

**执行提示词：**

```
请帮我做一个"项目收尾盘点"。我会逐个告诉你我手上未完成的项目情况，
你对每个项目输出以下结构：
- 项目名称
- 当前完成度（%）
- 已知缺口/bug清单
- 阻塞原因
- 预计还需要的时间
- 优先级（P0必交付/P1尽快/P2可延后）
```

**输出：** 项目优先级矩阵，确认 P0 项目后进入 Step 2。

---

### Step 2: 自动扫描 + 人工补充缺口清单（1小时）

**关键：** 先用脚本自动扫描，再人工对照 `references/gap-checklist.md` 补充，不要让 AI 边找边改。

**执行步骤：**

1. **运行自动扫描：**
   ```bash
   python3 scripts/gap-scan.py <项目路径> --output gap-report.md
   ```
   脚本会扫描：TODO/FIXME、调试代码、硬编码密钥、空catch块、大文件、缺失的README/.gitignore/测试。

2. **人工补充检查：**
   读取 `references/gap-checklist.md`，对照 7 大类 50+ 项逐项检查：
   - 功能完整性（需求覆盖、边界条件、异常流程）
   - 代码质量（规范、架构、性能）
   - 安全（输入验证、敏感信息、依赖安全）
   - 测试（覆盖率、测试质量）
   - 构建与部署
   - 文档
   - Git 状态

3. **合并生成《收尾缺口清单.md》：**
   - [编号] 问题描述
   - 严重程度（🔴致命 / 🟡严重 / 🟢轻微）
   - 来源（gap-scan自动 / 人工检查）
   - 复现步骤（如适用）
   - 修复建议
   - 预计修复时间

> ⚠️ 这一步只输出清单，不要让 AI 直接改代码。用户确认后进入 Step 3。

---

### Step 3: 用"防早停"规则逐个修复（半天到一天）

拿到清单后，**一次修一个问题**，强制"修一个、跑 verify-all.sh、全绿再下一个"。

**执行提示词：**

```
## 任务
修复《收尾缺口清单.md》中编号为 [X] 的问题。

## 修复规则（严格执行）
1. 一次只修复这一个问题，不夹带其他修改
2. 修复前先编写能复现该 bug 的测试用例
3. 修复后运行该测试，确认 bug 消失
4. 运行完整验证：bash scripts/verify-all.sh <项目路径>
5. verify-all.sh 退出码必须为 0，否则继续修

## 循环规则（只要不全绿就不停）
- 运行 verify-all.sh
- 若未全绿：读取失败输出，定位并修复，然后重跑
- 只要退出码非 0，就重复上一步，直到全绿再停

## 执行约束
- 禁止说"应该可以了"，必须提供 verify-all.sh 的实际输出
- 禁止删除或注释掉失败的测试来"假装修复"
- 禁止降低测试标准
- 持续执行直到任务完成，禁止早停

## 完成后输出
- 修复方式说明
- verify-all.sh 的最终输出（通过/失败统计）
- 是否还有已知残留问题（必须明说，不许隐藏）
```

**关键控制点：**
- 每次只给 AI 一个问题编号
- 修复完成后必须看到 `verify-all.sh` 输出 `✅ 全部验证通过`
- 新增任何测试失败 = 该问题未修复成功，回退或继续修
- 全部问题修完后，跑一次完整的 `verify-all.sh` 确认全绿

---

### Step 4: 独立验收——过最后一关（30分钟）

AI 说"我修完了"不代表真的能交付。**用 `acceptance-check.py` 做客观验收，不让写代码的 Agent 自己判断。**

**执行步骤：**

1. **运行自动验收：**
   ```bash
   python3 scripts/acceptance-check.py <项目路径> --output acceptance-report.md
   ```
   脚本检查 5 大类：文档完整性、测试覆盖、安全（硬编码密钥/.env忽略）、代码质量（TODO/大文件）、Git状态。

2. **人工对照验收标准：**
   读取 `references/acceptance-criteria.md`，检查：
   - P0 必须通过项（构建、测试、安全、核心功能、文档）
   - P1 应该通过项（测试覆盖率、性能、兼容性、部署）
   - P2 建议通过项（监控、CI/CD、工程化）

3. **真实使用模拟：**
   把自己当作普通用户（不是开发者），模拟：
   - 乱点、输入没想到的内容
   - 用没预想到的方式使用功能
   - 快速点击、重复操作
   - 检查错误提示是否友好

4. **输出验收报告：**
   - ✅ 已通过项
   - ❌ 未通过项（含修复建议）
   - ⚠️ 风险提示
   - 最终结论：能否交付 / 还需修哪些

**验收不通过时：** 将未通过项转回 Step 3 修复，修复后重新跑 `acceptance-check.py`。

---

### Step 5: 交付后归档

项目真正完成后，记录一份**收尾复盘**：

```
- 项目名称：
- 交付日期：
- 这次收尾花了多长时间：
- gap-scan.py 发现了多少问题：
- verify-all.sh 跑了多少次才全绿：
- acceptance-check.py 的最终评分：
- 主要卡点是什么：
- 下次如何避免（写入规范/模板）：
```

## Anti-Patterns（禁止行为）

| 禁止行为 | 为什么禁止 | 正确做法 |
|---|---|---|
| 让 AI 边找缺口边改代码 | 改一个坏一个，陷入循环 | 先跑 gap-scan.py 出完整清单，确认后逐个修 |
| 一次把所有问题塞给 AI | 上下文过载，修复质量下降 | 一次一个问题，修完跑 verify-all.sh |
| 让写代码的 Agent 自己验收 | 模型对自己输出过于乐观 | 用 acceptance-check.py 做客观验收 |
| 说"应该可以了" | = "我没验证" | 必须提供 verify-all.sh 的实际输出 |
| 删除/注释失败测试来凑通过 | 假装修复，问题仍在 | 修复真正的问题，保留测试 |
| 跳过自动化脚本 | 人工检查容易遗漏 | 必须先跑脚本，再人工补充 |
| 同时摊开好几个项目 | 火力分散，哪个都收不完 | 先排优先级，集中攻 P0 |

## Quick Reference（速查表）

| 阶段 | 时间 | 工具 | 产出物 | 关键约束 |
|---|---|---|---|---|
| 1. 盘点 | 30min | — | 项目优先级矩阵 | 只选 1 个 P0 |
| 2. 缺口清单 | 1h | gap-scan.py + gap-checklist.md | 收尾缺口清单.md | 只找不改 |
| 3. 逐个修复 | 0.5-1天 | verify-all.sh | 修复记录 + 测试全绿 | 一次一个，全绿才停 |
| 4. 独立验收 | 30min | acceptance-check.py + acceptance-criteria.md | 验收报告 | 脚本客观验收 |
| 5. 归档 | 10min | — | 收尾复盘 | 记录卡点和改进 |

## Example

**输入：** "我有 3 个项目没收尾，帮我收尾"

**执行：**
1. 用户逐个描述项目 → 输出优先级矩阵，确认 P0
2. 对 P0 项目运行 `gap-scan.py` → 自动生成缺口报告 → 人工对照 `gap-checklist.md` 补充 → 生成《收尾缺口清单.md》
3. 用户确认清单 → 逐个编号修复，每个修复后跑 `verify-all.sh`
4. 全部修复后 → 运行 `acceptance-check.py` → 生成验收报告
5. 验收通过 → 归档复盘

**输出：** 可交付的项目 + 收尾复盘记录

## References

- `references/gap-checklist.md` — 7 大类 50+ 项详细缺口检查清单
- `references/acceptance-criteria.md` — P0/P1/P2 三级可机器判定的验收标准
- `scripts/gap-scan.py` — 自动扫描代码缺口（TODO、调试代码、硬编码密钥、空catch、大文件、缺失文件）
- `scripts/verify-all.sh` — 自动检测项目类型，跑 lint+test+build，任一失败即退出
- `scripts/acceptance-check.py` — 自动验收（文档、测试、安全、代码质量、Git状态）
