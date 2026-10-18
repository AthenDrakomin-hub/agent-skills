# 审计评分、报告与回归规范

所有审计结论按本规范分级、打分、出报告。脚本输出是底稿，最终报告由 agent 汇总三通道（截图/源码/IPA）证据。

## 目录
1. 严重级别定义（P0–P3）
2. 问题单字段（Finding schema）
3. 评分模型与等级
4. 修复优先级与批次建议
5. 回归验证矩阵
6. 运行时验证工具速查
7. 审计报告模板
8. 完成定义（DoD）

## 1. 严重级别定义

| 级别 | 定义 | 典型案例 |
| --- | --- | --- |
| **P0 阻断** | 崩溃、无法安装/全屏运行、App Store 拒审项、核心流程不可用、RTL 镜像影响全 App | UIWebView（I-WEB-001/N-WEB-001）、无 arm64、隐私键调用即崩、启动配置缺失导致非全屏、H5 全量镜像 |
| P1 严重 | 主流机型/模式下明显可见且影响使用：安全区遮挡、强制浅色、ATS 全局放行、ATS 废弃启动图、自绘双导航/双 tab、键盘遮输入框、AX5 动态字体下核心页不可读 | 安全区为零、overrideUserInterfaceStyle=.light、fixed 底栏无 safe-area、缺 launch storyboard |
| P2 一般 | 多状态/边缘条件下体验受损：硬编码 frame/机型分支、固定字号不跟随 Dynamic Type、硬编码颜色无深色变体、触摸热区 <44pt、RTL 残留、backdrop-filter 缺前缀、iPad 方向不全 | 系统字体 API 无 metrics、RGB 写死、按钮 36pt 高 |
| P3 建议 | 规范一致性、性能隐患提示、废弃 API、未使用资源、间距不成体系、缺深色提示、废弃 CSS 属性 | 100vh、`-webkit-overflow-scrolling`、statusBarFrame、大文件提示 |

## 2. 问题单字段（Finding schema）

每条问题（含脚本输出的每条）具备：

| 字段 | 内容 |
| --- | --- |
| id | 规则编号（N-/H-/I- + 域 + 序号）或人工编号（X-域-序号） |
| title | 一句话问题 |
| severity | P0/P1/P2/P3 |
| category | adapt/safearea/typography/darkmode/color/a11y/touch/interaction/performance/navigation/keyboard/i18n/webview/launch/config/icon/asset/sign/release |
| evidence | `相对路径:行号` 或 plist 键名或截图标注区域（A/B/C）或工具输出片段 |
| standard | HIG 章节 / iOS API 可用性版本 / WCAG 条款 / 审核指南条款 |
| impact | 用户可见后果 + 触发条件 |
| fix | 完整可落地代码/配置（不贴半截；改旧文件给完整修改后版本） |
| verify | 具体回归点（机型/模式/操作） |
| confidence | 高/中/低（截图-only 结论 ≤ 中，需代码印证；脚本命中通常高，但 N-COLOR/TYPE 类需人工确认是否已动态处理） |
| channel | screenshot/source/ipa/runtime |
| status | open/fixed/wontfix（wontfix 需产品确认并记录理由） |

## 3. 评分模型与等级

按隐患域给分（先扣到 0 为止），权重如下（纯 H5 套壳项目把"原生"相关域并入 H5，权重归一化）：

| 隐患域 | 权重 | 扣分规则 |
| --- | --- | --- |
| 安全区与多机型适配 | 18 | P0 扣 18；P1 每个 -6；P2 每个 -2；P3 每个 -0.5 |
| 导航与系统栏一致性（含 iOS 26 玻璃） | 10 | P1 -5；P2 -2；P3 -0.5 |
| 字体与 Dynamic Type | 12 | P1 -5；P2 -2；P3 -0.5 |
| 深色模式与颜色对比 | 12 | P1 -5；P2 -2；P3 -0.5 |
| 触摸目标与无障碍 | 14 | P0 视流程阻断扣 14；P1 -5；P2 -2；P3 -0.5 |
| 交互手势与反馈 | 8 | P1 -4；P2 -1.5；P3 -0.5 |
| 渲染性能与资源 | 10 | P1 -4；P2 -2；P3 -0.5 |
| 键盘与表单 | 6 | P1 -4；P2 -1.5；P3 -0.5 |
| 国际化与 RTL | 5 | P0 扣 5；P1 -2.5；P2 -1；P3 -0.3 |
| 启动屏/配置/上架合规（IPA） | 5 | P0 扣 5；P1 -2.5；P2 -1；P3 -0.3 |

单域扣完为止，不计负分；同一根因多处命中按 1 个问题计（在证据里列全部位置）。**任一 P0 存在时总分封顶 59。**

| 总分 | 等级 | 含义 |
| --- | --- | --- |
| 90–100 | S | 顶尖：全矩阵通过，只剩个别 P3 |
| 80–89 | A | 优秀：无 P1，P2 有计划修复 |
| 70–79 | B | 合格：主流路径可用，明确批次修复 |
| 60–69 | C | 及格线下：存在多个 P1，需发版前解决 |
| <60 | D | 不可发布/拒审风险 |

## 4. 修复批次建议

- **第一批（发版门槛）**：全部 P0 + 主流机型/核心页面 P1。
- **第二批（提审前）**：其余 P1 + 高频页面 P2（登录、会话列表、聊天、我的、设置）。
- **第三批（迭代）**：剩余 P2 + 影响评分的 P3。
- 修复顺序注意依赖：先定安全区责任约定（壳/H5 二选一）→ 再改布局 → 再改颜色字体 → 最后打磨动效，避免返工。

## 5. 回归验证矩阵

修复后逐项打勾，报告附结果（通过/失败/不涉及 + 证据截图或工具输出）：

| 维度 | 验证点 | 手段 |
| --- | --- | --- |
| 机型档 | SE（375）/ 主流（393–402）/ Pro Max（440）三档 | 模拟器/真机截图 |
| 设备特征 | 灵动岛不遮挡、Home Indicator 不遮挡、横屏左右安全区 | 真机或模拟器 |
| 深色模式 | 每个核心页切换无白底/不可见文字/资源缺失 | 模拟器 Ctrl+Cmd+D 或设置 |
| Dynamic Type | AX1、AX5 两档逐页；输入与聊天页必测 | 设置/Accessibility Inspector |
| 键盘 | 登录、聊天、资料编辑：键盘弹起输入框可见、可联动收回 | 真机（键盘行为以真机为准） |
| RTL | 阿语下镜像正确；中文下绝不误翻转 | Scheme App Language=Arabic；中文回归 |
| 方向/iPad | 声明支持的全部方向；iPad Split View 三档 | iPad 模拟器/真机 |
| 四态 | 空/加载/错误/无权限逐核心列表页 | 弱网工具（Network Link Conditioner） |
| 性能 | 会话/聊天长列表滚动无离屏黄区、混合红区收敛、60/120fps | Instruments Core Animation |
| 无障碍 | VoiceOver 核心流程走通；Audit 无 P1 项 | Accessibility Inspector |
| 启动 | 冷启动首帧无黑/白闪、全屏分辨率、启动屏不拉伸 | 真机录像 + IPA 复核 |
| H5 专项 | tab 方向/顺序/选中态、聚焦不缩放、100dvh、毛玻璃生效 | 真机 WKWebView + Safari Web Inspector |
| 上架 | 无 UIWebView、隐私文案、图标全、方向合规 | ipa_audit.py + macOS assetutil/codesign |

## 6. 运行时验证工具速查

| 工具 | 查什么 |
| --- | --- |
| Xcode View Debugger | 约束层级、Ambiguous Layout、safe-area、视图帧 |
| Accessibility Inspector → Audit | 对比度、触摸目标、标签、动态字体 |
| Instruments → Core Animation | 离屏渲染（黄）、混合层（红）、帧率 |
| Main Thread Checker | 主线程 UI/卡顿问题（默认开启） |
| Clang Static Analyzer / SwiftLint | 废弃 API、约束习惯、代码味道 |
| 模拟器 Debug 菜单 | Slow Animations、Dark Appearance、Rendering 调试 |
| `xcrun simctl io booted screenshot f.png` | 批量截图 |
| Safari Web Inspector | WKWebView 内 DOM/CSS/网络/控制台 |
| Network Link Conditioner | 弱网与四态 |
| Fastlane snapshot / Xcode UI Test 截图 | 截图矩阵自动化 |

## 7. 审计报告模板

```markdown
# iOS UI/UX 审计报告 · <App 名/版本/构建号>
日期：YYYY-MM-DD　审计人：…　证据通道：截图 ☑ 原生源码 ☑ H5 源码 ☐ IPA ☑ 运行时 ☐
审计环境：Xcode/SDK 版本、最低系统、机型矩阵

## 一、结论
- 总分：XX/100（等级 X）；P0 x、P1 x、P2 x、P3 x
- 发布建议：可发布 / 修复第一批后发布 / 不可发布
- 三句话总结最关键的问题与收益最大的修复

## 二、P0/P1 问题清单（按修复批次）
### 1. [P1][H-SAFE-001] 聊天页底部输入栏被 Home Indicator 遮挡
- 证据：chat.vue:128；截图区域 B（iPhone 17，@3x）
- 标准：HIG Layout/Safe areas；iOS 11+ env()
- 影响：竖屏竖持下发送按钮下半部不可点
- 修复：<完整代码>
- 验证：三档机型 + 键盘弹起回归
- 置信度：高（源码 + 截图双证据）

## 三、P2/P3 清单（表格）
| ID | 问题 | 证据 | 级别 | 修复要点 | 状态 |

## 四、分域得分
| 域 | 得分 | 说明 |

## 五、iOS 26 Liquid Glass 迁移评估
（系统栏使用情况、自绘栏清单、迁移工作量与建议顺序）

## 六、回归矩阵结果
（第 5 节表格逐项结果 + 截图存档位置）

## 七、未覆盖项与限制
（如：未拿到 IPA 无法核图标/签名；加密包 UIWebView 扫描受限；未连真机等）

## 八、附录：脚本原始输出
（source-report.md / ipa-report.md 路径或摘要）
```

## 8. 完成定义（DoD）

1. 可用通道全部执行：脚本跑过、清单逐项核对（含人工/运行时补查项），截图矩阵覆盖核心页面。
2. 每条问题证据齐全（位置可点开/区域可指认），无"感觉不美观"式结论。
3. 每条 P0/P1 有完整修复代码与版本可用性说明；P2/P3 有修复要点。
4. 回归矩阵逐项有结论；不能验证的项在"未覆盖项"声明原因与补验方法。
5. 评分可复算（问题数 × 扣分规则），同一根因合并计数。
6. 修复后重跑脚本与截图矩阵，确认问题关闭且无回归，才允许把状态改 fixed。
