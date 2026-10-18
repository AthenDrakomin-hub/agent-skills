# [Quality] 中文命名技能被命名门禁结构性拦截 → PENDING.md 45 条积压无法自动消化

**Labels:** `quality` `naming-convention` `blocker` `chinese-locale`
**Milestone:** 技能库质量演进 · 门禁与本地内容解耦

---

## TL;DR

`daily-evolve.ps1` 与 CI `verify.yml` 共用同一条 ASCII-only 命名门禁
`^[a-z][a-z0-9-]*[a-z0-9]$`。而本仓库的内容垂直**强中文向**（小红书 / 公众号 /
抖音 / 豆包工作流），源技能目录里大量是中文名。结果：中文技能**在设计上永远进不了
main 分支**，只能无限沉淀在 `PENDING.md`——目前 45 条积压里 **41 条是中文名**。
这不是"个别技能没规范"，而是**门禁规则与项目内容语言之间的结构性死路**。

## 证据（可复现定位）

| # | 事实 | 定位 |
|---|------|------|
| 1 | 本地自动纳入脚本对中文名直接拒绝 | `scripts/daily-evolve.ps1:65` — `if ($name -notmatch $NamePattern) { return @{ Pass = $false; Reason = "Name '$name' not lowercase-hyphen format" } }` |
| 2 | 门禁正则是 ASCII-only | `scripts/daily-evolve.ps1:22` — `$NamePattern = '^[a-z][a-z0-9-]*[a-z0-9]$'` |
| 3 | CI 用**同一条**正则二次拦截 | `.github/workflows/verify.yml:37` — `grep -qE '^[a-z][a-z0-9-]*[a-z0-9]$'`，不匹配即 `FAIL=1` |
| 4 | 双门禁同规则 → 即便手工改脚本也过不了 CI | `verify.yml:32-40` + `daily-evolve.ps1:65` 均拒绝中文 `name` |
| 5 | 积压已堆积且大头是中文 | `PENDING.md` 共 **45** 条，其中**中文/含中文名 41 条**（如 `AI写作检测`、`小红书标题生成`、`公众号HTML转换`、`视频内容提取`…） |
| 6 | 作者其实想保留中文身份（先例已存在） | `skills/ios-ui-ux-dev/SKILL.md` frontmatter — `label: 'iOS UI/UX 审计与开发助手'` |

> 结论链：本地脚本按 `:22/:65` 拒中文 → 进不了 main → 落到 `PENDING.md`（证据 5）
> → 想手动补进会被 CI `verify.yml:37` 再拒（证据 4）→ **死路**，只能人工逐条手工规范，
> 而"手工规范"又必须改成 ASCII 名，导致中文身份丢失（与证据 6 的 `label` 意图冲突）。

## 影响

- **质量演进被卡死在单点**：门禁是唯一自动演进管线（`daily-evolve.ps1` 定时扫描纳入），
  它把 90%+ 的中文候选全部拒之门外，管线实际吞吐≈0。
- **积压不可自动清零**：`PENDING.md` 只能靠"人工逐条改名 + 改 SKILL.md"消化，无收敛趋势。
- **身份与兼容性的两难被误诊**：真正的约束其实是"各 Agent 的 skill identifier 必须
  小写连字符"，但当前实现把这条约束**错误地施加到了中文内容/标题上**，导致中文技能
  被当成"格式不合规"而非"需要一个 ASCII 别名 + 中文 label"。

## 根因

命名门禁 conflated 了两个本应分离的概念：

1. **filesystem / agent skill identifier**（`name`）—— 必须 ASCII 小写连字符，
   因为 Claude Code / Hermes / Coze 等 Agent 按此寻址。**这条约束是对的，保留。**
2. **人类可读的中文标题 / 触发语**（`label` / description 里的中文触发词）——
   完全可以且**应当**保留中文，用于内容识别与中文触发。**当前被 `name` 门禁误伤。**

`ios-ui-ux-dev` 已经自发用了 `label` 字段（证据 6），但 `label` 不是标准字段、未被门禁
放行、也未在 `daily-evolve.ps1` 的纳入/去重逻辑里被利用——所以它只是孤例，没形成机制。

## 建议解法（推荐 Option A，其余为备选）

### Option A（推荐）：解耦 identifier 与 label，门禁放行中文 `label`
- 标准 frontmatter 增补 `label`（可选，允许任意 Unicode 文本）作为中文/人类标题；
  `name` 维持 ASCII 小写连字符不变（保持全 Agent 兼容）。
- **`daily-evolve.ps1`**：对中文源目录不再直接拒绝，改为：
  - 由中文名生成 ASCII **slug**（如 `小红书标题生成` → `xiaohongshu-title-gen`，
    拼音或人工映射表）作为 `name`；
  - 把原中文名写入 `label`；
  - 用 `label`（而非被拒的 `name`）参与 `:101` 的 `$DuplicateBlacklist` 去重。
- **`verify.yml`**：`name` 仍校验 ASCII；**新增**"若存在 `label` 则不得为空/不得与 `name`
  重复"的轻量校验；不再因中文 `label` 判 FAIL。
- 收益：门禁吞吐恢复、积压获得可执行的 ASCII-slug + 中文-label 迁移路径、不牺牲
  任何 Agent 兼容性。

### Option B：门禁支持"双名"——ASCII `name` + 中文 `title`
- 比 A 更轻，但 `title` 语义偏展示、不进触发；适合只要"能进 main"、不要求中文触发命中。

### Option C（不推荐，列此供对照）：门禁直接放开 `name` 允许 Unicode
- 会破坏 Claude Code / Hermes 等按 identifier 寻址的兼容性，**否决**。

## 验收标准

- [ ] `name` 门禁保持 ASCII（`verify.yml:37` 语义不变）。
- [ ] `daily-evolve.ps1` 对含中文源名能产出 `ASCII slug(name) + 中文 label`，不再落到"拒收"。
- [ ] `PENDING.md` 每条中文积压给出映射示例：`原中文名 → name(slug) / label(原文)`。
- [ ] CI 对 `label` 存在性/合法性做校验，不因中文 `label` 判 FAIL。
- [ ] 用一条真实中文技能（如 `小红书标题生成`）跑通"脚本纳入 → CI 通过 → main 合并"全链路。

## 最小复现

```bash
# 本地管线对中文名的判定
$NamePattern = '^[a-z][a-z0-9-]*[a-z0-9]$'   # daily-evolve.ps1:22
"小红书标题生成" -notmatch $NamePattern       # → True：被拒（:65）

# CI 同规则
echo "小红书标题生成" | grep -qE '^[a-z][a-z0-9-]*[a-z0-9]$'   # → 1：FAIL（verify.yml:37）
```
