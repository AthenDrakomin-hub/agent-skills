---
name: code-quality-review
description: "代码质量自动审查（带扫描脚本）。只读审查代码库中的可维护性风险：长函数、神级模块、重复代码、圈复杂度、硬编码密钥、空catch、TODO残留、调试代码。code-review.py 自动扫描并输出结构化报告，按 Critical/High/Medium/Low 分级，标记 must_fix 项。Use when: 代码质量审查, 架构审查, 可维护性, 代码评审, 结构变更审查, 抽象设计审查, code review, maintainability, technical debt, 代码扫描."
license: MIT
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: development
---

# Code Quality Review v2.0

## Role

只读审查重大结构或抽象变更中的可维护性风险。不适用于常规润色、二次正确性检查或周边代码清理。

**v2.0 升级**：内置 `code-review.py` 自动扫描脚本，量化检测 8 类可维护性问题。

## 核心原则

1. **只读**：不修改代码，不提交，不发布
2. **只报有实际影响的问题**：不报 nitpick、命名风格、纯美观建议
3. **must_fix 只用于真正阻塞的问题**：不变量违反、已验证的正确性/契约/测试可靠性风险
4. **无发现是正常的**：不为了凑数而报问题
5. **保留已接受的决策**：没有新证据不重开已 settled 的选择

## 内置脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/code-review.py` | 自动扫描代码质量问题，输出结构化报告 | `python3 code-review.py <项目路径>` |

**纯 Python 标准库，零依赖。** 支持 15 种语言（JS/TS/Python/Java/Go/Rust/PHP/C/C++/C#/Swift/Kotlin/Ruby）。

## 快速使用

```bash
# 扫描项目，输出 Markdown 报告
python3 scripts/code-review.py ./my-project

# 输出到文件
python3 scripts/code-review.py ./my-project --output review.md

# JSON 格式（便于 CI 集成）
python3 scripts/code-review.py ./my-project --json

# 只显示 High 及以上问题
python3 scripts/code-review.py ./my-project --threshold High
```

退出码：0=无 Critical 问题，1=有 Critical 或 must_fix 问题。

## 自动检测的 8 类问题

| 类别 | 检测内容 | 严重度 |
|---|---|---|
| 🔴 **Security** | 硬编码密钥（GitHub PAT/API Key/AWS Key/私钥/密码） | Critical |
| 🟠 **Long Function** | 函数超过 80 行（>200行 Critical，>120行 High） | High/Medium |
| 🟠 **God Module** | 文件超过 500 行（>1000行 Critical） | High/Medium |
| 🟠 **Error Handling** | 空 catch 块（异常被静默吞掉） | High |
| 🟡 **Complexity** | 圈复杂度过高（>30决策点） | Medium/High |
| 🟡 **Duplication** | 跨文件重复代码块（≥6行相同） | Medium |
| 🔵 **Technical Debt** | TODO/FIXME/HACK 残留 | Low |
| 🔵 **Debug Code** | console.log/print/debugger 残留 | Low |

## 审查流程

1. **运行自动扫描**：`code-review.py` 输出问题清单和统计
2. **人工补充审查**：脚本无法检测的架构问题（职责不清、抽象不当、耦合方向错误）
3. **过滤噪音**：去掉 nitpick、风格偏好、已接受的技术债
4. **分级输出**：每个问题包含 title/severity/location/issue/recommendation/must_fix
5. **给出结论**：`pass` / `needs_changes` / `blocked`

## 审查焦点

### 要报的问题

- **实质性重复**：同一逻辑在多处实现，修改一处会遗漏另一处
- **职责冲突**：一个模块承担了多个不相关的职责
- **可避免的耦合**：改动 A 必须同时改 B，但没有明确的契约
- **抽象增加维护成本**：为了"可能的复用"引入的过度抽象
- **契约/所有权/生命周期变更**：原语的 contract 变化但消费者未同步
- **不变量违反**：已验证的正确性、契约或测试可靠性风险

### 不要报的问题

- 命名/风格偏好（除非导致真实混淆）
- "可以更短"的等价实现
- 推测性的未来复用/扩展/风险
- 不相关的清理建议
- 已存在的技术债（不是本次变更新引入的）
- 纯美观简化

## 发现格式

每个发现必须包含：

```
**标题** [必须修复]
- 位置: 文件:行号
- 类别: 问题类别
- 问题: 具体描述（引用代码或行为）
- 建议: 可操作的修复方向
```

## 结论定义

| 结论 | 含义 |
|---|---|
| `pass` | 无阻塞性问题，可以合并 |
| `needs_changes` | 至少一个 must_fix 或 Critical 问题，修复后才能合并 |
| `blocked` | 关键覆盖不可用，无法完成审查 |

结论必须说明审查的版本和限制，不等于"完全正确"的批准。

## References

- `scripts/code-review.py` — 代码质量自动扫描工具（8类问题，15种语言，结构化报告）
