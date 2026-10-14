---
name: marketing-suite
description: "Full-stack marketing copy generation suite. End-to-end workflow from codebase analysis → PRD → landing page → social media → ad creative. Use when: user wants to generate marketing copy from an existing codebase, build a landing page from product requirements, create social media content packages, produce ad headline variations, or run a complete marketing content sprint. Triggers: 'marketing suite', 'generate all marketing copy', 'code to marketing', 'product to landing page', 'content package', 'ad variants', 'solo marketing'."
version: 1.0.0
author: curated from coreyhaines31/marketingskills + alirezarezvani/claude-skills
---

# Marketing Suite — 全栈营销文案生成套件

一套从代码库到落地页、社媒、广告的完整营销文案流水线。

## 工作流总览

```
代码库 ──→ code-to-prd ──→ PRD 文档
                              │
                              ▼
                        copywriting ──→ 产品理解 + 文案初稿
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
            cro          social        ad-creative + ads
        (落地页文案)   (社媒内容包)    (广告标题+变体)
```

---

## 第一步：产品理解（code-to-prd + copywriting）

**触发条件**：用户说"从代码库生成文案"、"分析产品写文案"、"我有个项目帮我写营销稿"。

**执行流程**：
1. 调用 `code-to-prd` 技能，分析代码库生成完整 PRD
   - 输入：代码库路径
   - 输出：路由清单、页面列表、功能矩阵、API 端点、用户流程
2. 基于 PRD，调用 `copywriting` 技能生成：
   - 产品定位一句话（elevator pitch）
   - 核心价值主张（3 个版本）
   - 目标用户画像（2-3 个 persona）
   - 主要卖点清单（features → benefits 转化）
   - 产品简介（100字 / 300字 / 800字 三个版本）

**输出物**：`product-brief.md` — 产品理解文档，作为后续所有文案的基础。

---

## 第二步：落地页文案（cro）

**触发条件**：用户说"生成落地页"、"做一个 landing page 文案"、"首页文案"。

**前置条件**：必须先有 product-brief.md（第一步输出）。

**执行流程**：
1. 读取 product-brief.md，确认产品定位和目标用户
2. 调用 `cro` 技能，生成高转化落地页结构：
   - Hero 区：主标题 + 副标题 + CTA（3 个变体）
   - 痛点区：3-5 个用户痛点 + 对应解决方案
   - 功能区：核心功能的利益化表达
   - 社会证明区：客户证言 / 数据指标占位
   - 定价区：套餐命名 + 价值锚点
   - FAQ：5-8 个常见问题
   - 底部 CTA：最终转化引导
3. 每个区块提供 2 个文案变体供 A/B 测试

**输出物**：`landing-page-copy.md` — 完整落地页文案，可直接交给前端开发。

---

## 第三步：社交媒体内容包（social）

**触发条件**：用户说"社媒内容"、"社交媒体文案"、"发帖素材"、"内容包"。

**前置条件**：必须先有 product-brief.md。

**执行流程**：
1. 基于 product-brief.md，调用 `social` 技能生成：
   - **Twitter/X**：10 条推文（含 thread 系列 1 组）
   - **LinkedIn**：3 篇长文（产品发布 / 案例分析 / 行业观点）
   - **小红书/Instagram**：5 个帖子（含标题 + 正文 + 标签）
   - **微信朋友圈**：3 条短文案
2. 每条内容标注：
   - 目标漏斗阶段（认知 / 考虑 / 转化）
   - 核心钩子类型（痛点 / 利益 / 好奇 / 社会证明）
   - 建议发布时间窗

**输出物**：`social-content-package.md` — 全平台社媒内容包。

---

## 第四步：广告创意（ad-creative + ads）

**触发条件**：用户说"广告标题"、"ad copy"、"广告变体"、"广告文案迭代"。

**前置条件**：必须先有 product-brief.md。

**执行流程**：
1. 调用 `ad-creative` 技能，生成标题变体矩阵：
   - **3-5 个不同角度**：痛点型 / 结果型 / 好奇型 / 社会证明型 / 对比型
   - 每个角度生成 5-8 个标题
   - 总计 20-40 个标题变体
   - 标注每个标题的：钩子类型、目标情绪、字符长度
2. 调用 `ads` 技能，生成完整广告：
   - Google RSA：3 组完整响应式搜索广告（标题 + 描述）
   - Meta/Facebook：3 组广告（主文案 + 标题 + CTA）
   - LinkedIn：2 组 B2B 广告
3. 输出 A/B 测试建议：优先测试哪 3 组

**输出物**：`ad-creative-package.md` — 广告标题矩阵 + 完整广告组。

---

## 快速模式 vs 完整模式

### 快速模式（只出初稿）
用户说"快速出一版"时：
- 跳过 code-to-prd，直接问用户产品一句话描述
- 每步只出 1 个版本，不做变体
- 总输出：product-brief + landing + 5条社媒 + 10个广告标题

### 完整模式（全套交付）
用户说"完整生成"、"全套"时：
- 走完整四步流程
- 每步都出变体
- 输出 4 份独立文档 + 1 份总索引

---

## 子技能索引

| 阶段 | 技能名 | 作用 |
|------|--------|------|
| 产品分析 | `code-to-prd` | 从代码库逆向生成 PRD |
| 文案基础 | `copywriting` | 产品定位、价值主张、通用文案 |
| 落地页 | `cro` | 高转化页面结构 + 文案 |
| 社媒 | `social` | 全平台社交媒体内容 |
| 广告创意 | `ad-creative` | 标题变体、角度矩阵 |
| 广告投放 | `ads` | 平台规格广告组、投放策略 |

---

## 使用示例

**用户说**："我有个项目在 ./my-app，帮我从代码生成全套营销文案"

**Agent 执行**：
1. 读取 product-brief 需求 → 调用 code-to-prd 分析 ./my-app
2. 基于 PRD → 调用 copywriting 生成 product-brief.md
3. 基于 brief → 调用 cro 生成 landing-page-copy.md
4. 基于 brief → 调用 social 生成 social-content-package.md
5. 基于 brief → 调用 ad-creative + ads 生成 ad-creative-package.md
6. 汇总输出 4 份文档 + 索引

---

## 注意事项

- **不要跳过前置步骤**：后续所有文案都依赖 product-brief，没有 brief 就先做产品理解
- **每个变体都要有理由**：不只是换词，而是换角度、换情绪、换目标人群
- **平台规格要遵守**：广告标题必须符合各平台字符限制
- **诚实优先**：不夸大、不虚假承诺，所有卖点必须有产品功能支撑
