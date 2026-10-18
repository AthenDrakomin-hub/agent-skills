---
name: iOS界面审计开发
label: iOS UI/UX 审计与开发助手
description: iOS App 界面 UI/UX 的多通道审计、排障与开发技能。支持四类证据输入：(1) 界面截图/录屏的视觉走查；(2) iOS 原生源码（Swift/Objective-C/UIKit/SwiftUI/Xib/Storyboard/Info.plist）静态审计；(3) H5 套壳源码（UniApp/Vue/H5/CSS 打包进 WKWebView）静态审计；(4) IPA 静态产物解包审计（Info.plist、Assets.car、Mach-O、图标启动屏、本地化、签名与上架风险）。覆盖安全区与设备适配（灵动岛/Home Indicator/尺寸类/旋转/iPad 多任务）、Auto Layout 隐患、 Dynamic Type 动态字体、深色模式与颜色对比度、44pt 触摸目标与无障碍、RTL 国际化、离屏渲染/约束性能、键盘遮挡、WKWebView 渲染故障（tab 文字镜像翻转、viewport 缩放、text-size-adjust 字体放大、safe-area 遮挡、100vh/键盘、transform 镜像）、iOS 26 Liquid Glass 液态玻璃新设计迁移。当用户要求对 iOS App（含乐享 IM 等 UniApp 套壳 App）做 UI/UX 体检、设计对标 HIG、审查界面源码、分析 IPA 包、贴截图排查界面 bug、给出像素级修复方案与审计评分报告时使用本技能。
---

# iOS UI/UX 审计与开发助手

把"界面有问题"变成"证据 → 根因 → 修复 → 回归"的闭环。**禁止只凭审美给空泛建议**：每个结论必须有证据（文件:行号 / plist 键 / 截图标注区域 / 工具输出），每条修复必须可落地（代码或配置），并给出验证方式。

## 1. 先盘点证据通道，再选工作流

先确认用户给了什么，按下表路由。证据通道越多，结论置信度越高；只有截图时根因必须标注置信度并写明"需查代码确认"。

| 用户提供的输入 | 走的通道 | 必读参考 | 必跑脚本 |
| --- | --- | --- | --- |
| 界面截图 / 录屏 | 视觉走查 | `references/audit-screenshots.md` | — |
| iOS 原生工程（.swift/.m/.xib/.storyboard/Info.plist） | 原生源码审计 | `references/audit-native-source.md` | `scripts/source_scan.py` |
| UniApp/Vue/H5 工程、WKWebView 套壳页 | H5 源码审计 | `references/audit-h5-source.md` | `scripts/source_scan.py` |
| `.ipa` 文件或 `.app` 目录 | 产物审计 | `references/audit-ipa.md` | `scripts/ipa_audit.py` |
| "iOS 界面该怎么设计" / HIG 对标 / 数值规范 | 设计规范 | `references/hig-design.md` | — |
| 乐享 IM tab 截图等实战排查 | 案例工作流 | `references/case-lexiang-tab-screenshot.md` | — |
| 出审计报告 / 评分 / 修复优先级 | 交付规范 | `references/rubric.md` | — |

多通道时全部加载对应参考；截图排查可先读案例文件中的五步工作流。

## 1.5 技能分工路由（与 uniapp-multi-platform-audit 的边界）

本技能与 `uniapp-multi-platform-audit` 都能审 UniApp 套壳 App 的 UI，按下表分流，避免重复劳动：

| 场景特征 | 走本技能（ios-ui-ux-dev） | 走 uniapp-multi-platform-audit |
| --- | --- | --- |
| 给了 `.ipa` / `.app` 产物，要查上架风险、签名、Assets.car、Mach-O | ✅ 主通道（`scripts/ipa_audit.py`） | — |
| iOS 原生工程（.swift/.m/.xib/.storyboard/Info.plist）、Auto Layout、HIG 对标、iOS 26 Liquid Glass 迁移 | ✅ 主通道 | — |
| 纯 H5/UniApp 套壳页的 WKWebView 渲染故障（tab 镜像、viewport 缩放、text-size-adjust、safe-area 遮挡、100vh/键盘、transform 镜像）的**根因级**排查 | ✅ 主通道（`references/audit-h5-source.md`，规则号 H-*） | — |
| 要对比 iOS / Android / H5 **三端**同一页面的体验差异、Android 状态栏/物理返回键/折叠屏 | 辅助（仅 iOS 侧结论） | ✅ 主通道 |
| IM 聊天页 / 游戏 Canvas 等业务**专项**清单（气泡、输入栏、通话全屏、横竖屏） | 不覆盖 | ✅ 主通道 |
| uniapp `#ifdef` 条件样式、rpx 混用、`uni.*`/`plus.*` API 兼容性与版本核验 | 不覆盖 | ✅ 主通道（再联动 uniapp-release-notes） |

协作方式：跨端项目先由 uniapp-multi-platform-audit 出三端差异清单，其中**iOS 侧的 WKWebView 深度问题**回本技能按 H-* 规则与 `source_scan.py` 复核；涉及 API 版本/已知 bug 时，由 uniapp-multi-platform-audit 联动 uniapp-release-notes 查询。本技能不输出三端对比矩阵，也不做 `uni.*` API 版本判断。

## 2. 审计总流程（六步）

1. **取证盘点**：列出用户提供的全部输入与缺失项。关键输入缺失会显著影响覆盖度（如只有截图无法确认暗色模式、动态字体行为），一次性向用户说明缺什么、怎么补（截图矩阵见 `audit-screenshots.md` 第 1 节）。
2. **自动扫描**：对源码目录跑 `source_scan.py`，对 IPA 跑 `ipa_audit.py`（命令见第 4 节），拿到 P0–P3 问题清单作为底稿。脚本是底线覆盖，不替代人工审计。
3. **分通道人工审计**：按对应 reference 的检查清单逐项核对。脚本查不出的（约束歧义、运行时布局、对比度、状态完整性、手势冲突、动效卡顿）必须人工补查。
4. **交叉印证**：同一隐患尽量用两个通道互证（如源码缺 safe-area 约束 + 截图底部被 Home Indicator 遮挡 + IPA 无 launch screen）。截图只证明症状，源码/产物证明根因。
5. **给修复**：按 `audit-native-source.md` / `audit-h5-source.md` 中的修复范式输出完整可落地代码（不贴片段化 diff；修改旧文件给完整修改后代码），并标注 iOS 版本可用性。
6. **回归与评分**：按 `rubric.md` 的回归矩阵在真机/模拟器验证，输出评分与审计报告（模板在 `rubric.md`）。

## 3. 覆盖矩阵（隐患域 × 有效通道）

●=直接发现　◐=辅助发现　○=基本无效（需换通道或上运行时工具）

| 隐患域 | 截图 | 原生源码 | H5 源码 | IPA |
| --- | --- | --- | --- | --- |
| 安全区/灵动岛/底部遮挡 | ● | ● | ● | ◐（启动屏配置） |
| 多机型/尺寸类/旋转/iPad 适配 | ● | ● | ● | ◐（设备族/方向配置） |
| Auto Layout 约束冲突/硬编码 frame | ◐ | ● | ○ | ◐（nib 计数） |
| Dynamic Type 动态字体/文本截断 | ● | ● | ● | ○ |
| 深色模式/颜色/对比度 | ● | ● | ● | ◐（Assets.car） |
| 触摸目标/无障碍（VoiceOver 等） | ◐ | ● | ● | ○ |
| RTL/国际化/镜像 | ● | ● | ● | ◐（.lproj） |
| 离屏渲染/滚动性能/图片资源体积 | ◐ | ● | ◐ | ●（资源体积/架构） |
| 键盘遮挡/表单体验 | ● | ● | ● | ○ |
| WKWebView 渲染故障 | ● | ◐（壳配置） | ● | ◐（UIWebView 残留） |
| 图标/启动屏/配置类上架风险 | ◐ | ◐（plist 源） | ○ | ● |
| iOS 26 Liquid Glass 迁移 | ● | ● | ● | ◐（SDK/符号） |

IPA/静态分析的共同盲区：运行时才出现的布局、约束歧义、深色模式与动态字体实际表现、动画卡顿。盲区必须用截图矩阵或第 5 节运行时工具补齐，并在报告中如实标注未覆盖项。

## 4. 脚本速查（Python 3.8+，纯标准库，Windows/macOS/Linux 可跑）

```bash
# 源码静态审计（原生 + H5 + plist 自动识别），输出 markdown 报告
python scripts/source_scan.py <工程目录> --format md --out uiux-source-report.md
# 只看 P0/P1
python scripts/source_scan.py <工程目录> --min-severity P1

# IPA 静态产物审计（也可直接传 .app 目录）
python scripts/ipa_audit.py <App.ipa> --format md --out uiux-ipa-report.md
```

- 脚本自动跳过 node_modules/Pods/dist/build/unpackage/.git 等目录。
- 发现 P0/P1 时退出码为 1，可接入 CI；规则编号（N-/H-/I-）与各 reference 文档一一对应。
- **macOS + Xcode 增强项**（Windows 上会降级为"给出命令人工执行"）：`xcrun assetutil --info Assets.car`（资源/图标明细）、`otool`/`nm`（Mach-O 架构与符号）、`codesign`/`security cms`（签名与描述文件）。详见 `audit-ipa.md`。

## 5. 运行时工具（静态通道之外的专业手段，按需建议用户执行）

- Xcode View Debugger：看约束、层级、Ambiguous Layout、safe-area 线。
- Accessibility Inspector → Audit：对比度、触摸目标、无障碍标签一键扫描。
- Instruments → Core Animation：Color Off-Screen Rendered（黄底=离屏渲染）、Color Blended Layers（红底=混合过度）。
- Main Thread Checker / Clang Static Analyzer / SwiftLint；模拟器切换 Dark Appearance、Dynamic Type 最大档、RTL 伪语言（Xcode → App Language → Double-Length/Pseudolanguage、`-AppleLocale ar`）。
- H5：Safari → 开发 → 模拟器/真机 Web Inspector；真机 WKWebView 回归（模拟器不能代表真机渲染）。
- 截图矩阵与回归清单见 `references/audit-screenshots.md` 与 `references/rubric.md`。

## 6. 关键症状速查（先给方向，再进文档核实）

- tab/文字镜像翻转 → H5 先查 `dir="rtl"` / `direction:rtl` / `scaleX(-1)`（`audit-h5-source.md` §1）；原生查 `semanticContentAttribute`。
- 底部被小黑条遮挡/底部留白/圆角异常 → safe-area：H5 查 `viewport-fit=cover` + `env(safe-area-inset-bottom)`；原生查 safeAreaLayoutGuide。
- 布局整体缩放错乱/输入框聚焦页面放大 → viewport meta / 输入框字号 <16px。
- 字体被系统自动放大或放大后截断溢出 → `-webkit-text-size-adjust` / Dynamic Type 适配。
- 自定义 tab 栏在 iOS 26 上与系统悬浮液态标签栏不一致 → 改用 UITabBarController/TabView，见 `hig-design.md` §2。
- 代码里出现 UIWebView → P0，App Store 拒审，立即换 WKWebView。

## 7. 输出要求

- 设计规范类回答：附具体数值与出处（HIG 章节、pt 值、iOS 版本），不空谈审美。
- 排障类回答：症状 → 根因（置信度）→ 修复代码 → 真机验证方式，四要素齐全。
- 审计类交付：使用 `rubric.md` 的问题单与报告模板，含评分、P0–P3 分级、修复优先级、回归矩阵、未覆盖项声明。
- 涉及乐享 IM 或同类 UniApp 套壳 App，优先复用 `references/case-lexiang-tab-screenshot.md` 的已知背景。
