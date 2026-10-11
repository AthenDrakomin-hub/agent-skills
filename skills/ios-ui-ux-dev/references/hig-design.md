# Apple HIG 设计规范与 iOS 26 对标手册

## 目录
1. 设计原则与 iOS 26 Liquid Glass（液态玻璃）
2. 液态玻璃迁移要点（原生 / SwiftUI / H5 套壳）
3. 关键数值速查（触摸目标、栏高、间距、排印）
4. 机型分辨率与安全区参数表
5. 颜色、深色模式与材质
6. 字体排印与 Dynamic Type
7. 官方资源与 WWDC 路径
8. 技术框架与学习资源

## 1. 设计原则与 iOS 26 Liquid Glass

HIG 入口：https://developer.apple.com/design/human-interface-guidelines/

三大核心原则：**清晰 Clarity、顺从 Deference、层次 Hierarchy**。iOS 26 起设计基座升级为 **Liquid Glass（液态玻璃）**：控件与导航栏由半透明玻璃材质构成，实时折射下方内容，并随场景（滚动、聚焦、模式切换）动态形变。

对审计最重要的变化：

- **标签栏悬浮化**：iPhone 上 UITabBar 悬浮于内容之上，滚动时自动收缩为悬浮小条、上滑或点按时展开；iPad 上面向侧边栏形态。内容必须延伸到栏下方（edge-to-edge），再用安全区保证可见性。
- **导航栏/工具栏/标签栏统一玻璃材质**：系统栏会自动获得玻璃外观，自定义的纯色栏、自绘 tab 条会与系统割裂。
- **材质代替纯色遮罩**：浮层、面板、工具栏优先用系统材质（Material）而非自造半透明黑色蒙层；玻璃会自动适配明暗与对比度。
- **图标体系统一**：iOS 26 采用统一的玻璃质感 App 图标网格（支持浅色/深色/着色三种外观），SF Symbols 同步更新。
- **自动获得 vs 显式采用**：用 iOS 26 SDK 编译且使用系统容器（UITabBarController / UINavigationController / TabView / NavigationStack）的界面自动获得新外观；大量自定义栏、自绘控件、H5 套壳页不会自动获得。

审计含义：凡发现自绘底部 tab、纯色悬浮栏、自定义导航栏的项目，都要评估迁移成本（见 §2）；H5 套壳 App（如乐享 IM）的 H5 tab 栏属于"平台外 UI"，至少要保证安全区、滚动行为、视觉权重与系统标签栏一致，避免双层悬浮条（原生玻璃栏 + H5 固定 tab）并存。

## 2. 液态玻璃迁移要点

| 技术栈 | 正确做法 | 反模式 |
| --- | --- | --- |
| UIKit | 用 `UITabBarController` / `UINavigationController` / `UISplitViewController`，栏由系统管理；WWDC25《使用全新设计系统构建 UIKit App》（Session 284）给出迁移步骤 | 隐藏系统 tabBar 后自绘固定底栏；给系统栏 setBackgroundImage 纯色图 |
| SwiftUI | `TabView` / `NavigationStack`；iOS 26 可用 `Glass` 容器与 `.glassEffect()` 修饰符 | 用 ZStack 自造底部栏 + 固定安全区 padding |
| 材质 | UIKit `UIBlurEffect(style:)` 系列 / SwiftUI `.ultraThinMaterial` 等材质，iOS 26 起优先玻璃材质 API | `UIColor(white:0 alpha:0.3)` 自造蒙层；给 UIVisualEffectView 设 alpha<1（材质透明度必须走 contentView） |
| H5 套壳 | 不模仿玻璃；保持 H5 内容区干净，导航/tab 尽量交原生；必须自绘时遵循安全区与 49pt 左右栏高、滚动收缩可做可不做但不得遮挡内容 | H5 再画一条悬浮玻璃条 + 原生栏并存 |

## 3. 关键数值速查（pt）

| 项目 | 规范值 | 说明 |
| --- | --- | --- |
| 可点控件最小触摸目标 | **44 × 44 pt** | HIG 最低要求；视觉上可更小，但命中热区必须 ≥44pt（WCAG 2.2 AAA 同为 44 CSS px） |
| 导航栏 | 44pt 高 + 状态栏 | iOS 26 玻璃导航栏悬浮于内容；大标题（Large Title）默认 96pt 左右总高 |
| 标签栏 | 约 49pt 内容高 + 安全区底部 34pt | iOS 26 为悬浮玻璃条，视觉高度变小但热区不变 |
| 工具栏 | 44pt | |
| 标准左右边距 | 16–20pt | 跟随 readable/content margins，不要写死 16；用 layoutMargins / readableContentGuide |
| 列表行高 | ≥44pt | 常规列表 44–48pt，聊天会话行常见 56–76pt |
| 圆角 | 连续圆角（continuous） | 卡片 12–20pt；用 `cornerCurve = .continuous` / SwiftUI `.continuous`，不要用普通圆角 |
| 间距网格 | 8pt 基准 | 4/8/12/16/24 序列，禁止 3、5、7、13 这类随意值成体系出现 |
| 状态栏（非全面屏） | 20pt | 仅 SE 等老机型；全面屏由安全区取代，不要硬编码 |
| Home Indicator 底部安全区 | 34pt（竖屏） | 横屏约 21pt；必须取 `safeAreaInsets`，禁止写死 |
| 灵动岛/刘海顶部安全区 | 47–59pt | 因机型而异（见 §4），禁止写死 |
| 最小文字 | 11pt（Caption 2） | 正文 Body 17pt；IM 气泡内文不建议小于 15pt |
| 对比度 | 4.5:1（AA 正文） | 大文本 3:1；图标/控件 3:1；玻璃材质下方内容仍需满足 |

## 4. 机型分辨率与安全区参数表

审计与截图矩阵以"最小 + 主流 + 最大"三档覆盖即可，iPad 单列。数值单位 pt（@2x/@3x 为像素倍率）。

| 机型（代表档） | 逻辑分辨率 (pt) | 倍率 | 像素 | 顶部安全区(约) | 底部安全区 |
| --- | --- | --- | --- | --- | --- |
| iPhone SE（第 3 代）·最小档 | 375 × 667 | @2x | 750 × 1334 | 20（状态栏） | 0（有 Home 键） |
| iPhone 15/16 ·主流档 | 393 × 852 | @3x | 1179 × 2556 | 47–49 | 34 |
| iPhone 17 / 17 Pro | 402 × 874 | @3x | 1206 × 2622 | 47–50 | 34 |
| iPhone Air | 420 × 912 | @3x | 1260 × 2736 | 约 50–54 | 34 |
| iPhone 16/17 Pro Max ·最大档 | 440 × 956 | @3x | 1320 × 2868 | 47–51 | 34 |
| iPhone 16 Plus / 15 Pro Max（存量） | 428–430 × 926–932 | @3x | 1284×2778 等 | 47 | 34 |
| iPad（11"/13"） | 约 820×1180 / 1024×1366 起 | @2x | — | 24 状态栏 | 0 |

注意：

- 安全区数值随系统版本和形态（横屏、灵动岛、个人热点状态栏、导航/标签栏）变化，**表中值只用于设计估算，代码必须运行时取 `safeAreaInsets` / `env(safe-area-inset-*)`**。
- 横屏全面屏左右两侧也有安全区（约 48pt 给灵动岛/圆角），底部横屏约 21pt。
- Display Zoom（显示缩放）会改变 point 尺寸；用尺寸类（size class）而非机型做布局判断。
- 完整官方设备表：HIG → Layout → Resources（每年 9 月随新机更新）。

## 5. 颜色、深色模式与材质

- 优先用**系统动态色**：`UIColor.label / .secondaryLabel / .systemBackground / .systemGroupedBackground / .separator / .systemBlue` 等；SwiftUI 对应 `.primary / .secondary / Color(.systemBackground)`。它们自动适配深色模式与高对比。
- 自定义品牌色放入 Asset Catalog 并提供 **Any（浅色）/ Dark（深色）两套值**，或用 `init(dynamicProvider:)` 按 trait 提供。
- 深色模式不是简单反色：背景抬升到近黑而非纯黑（系统 grouped 背景 #1C1C1E 层级），文字用 off-white；纯黑纯白大面积相邻会刺眼。
- 广色域：资源用 sRGB/P3 标注，避免跨设备色差；对比度过玻璃材质后要复测。
- 禁止强制浅色：`overrideUserInterfaceStyle = .light` 是 P1 级体验倒退（代码扫描规则 N-DARK-001）。
- 对比度自检：Accessibility Inspector → Audit → Color Contrast；目标 AA（正文 4.5:1，大字 3:1）。

## 6. 字体排印与 Dynamic Type

- 用**文本样式（Text Styles）**而非固定字号：Large Title 34 / Title 1 28 / Title 2 22 / Title 3 20 / Headline 17(SB) / Body 17 / Callout 16 / Subhead 15 / Footnote 13 / Caption 1 12 / Caption 2 11。
- UIKit：`UIFont.preferredFont(forTextStyle:)`；自定义字体必须经 `UIFontMetrics(forTextStyle:).scaledFont(for:)`，并打开 `adjustsFontForContentSizeCategory = true`。
- SwiftUI：`.font(.title)` 等样式自动支持 Dynamic Type；自定义字号用 `@ScaledMetric`。
- 标签 `numberOfLines = 0` + 自适应行高（`automaticDimension` / SwiftUI 原生），禁止固定行高容纳文字。
- 必测：系统设置里把字号拉到最大档（AX5），界面允许纵向生长/堆叠，不得截断、重叠、溢出。
- H5 侧对应：不得全局 `-webkit-text-size-adjust:none` 后对用户字号偏好完全无感（权衡见 H5 审计文档）。

## 7. 官方资源与 WWDC 路径

- HIG：https://developer.apple.com/design/human-interface-guidelines/ （重点章节：Layout、Navigation、Typography、Color、Materials、Icons、Accessibility、Right to left）
- Apple Design Resources：https://developer.apple.com/design/resources/ （iOS 26 Figma/Sketch 组件库、SF Symbols、图标模板）
- SF Symbols：5000+ 系统图标，按字重/层级渲染，支持单色/双色/分层/渲染模式；自绘图标要对齐其视觉权重与留白。
- WWDC25：Session 284《使用全新设计系统构建 UIKit App》、《Get to know the new design system》、SwiftUI 液态玻璃相关 Session；WKWebView 适配看历年《WKWebView enhancements》。
- Device Hub：Xcode 内多设备/尺寸类/动态字体截图核验（HIG Layout 推荐）。

## 8. 技术框架与学习资源

- **UIKit**：Auto Layout + Safe Area + 尺寸类是必守基线；`translatesAutoresizingMaskIntoConstraints = false`；约束冲突/歧义会在控制台输出（运行时必查日志）。
- **SwiftUI**：iOS 13+，iOS 15/16/26 分别补齐大量 API；可与 UIKit 混编（`UIHostingController` / `UIViewRepresentable`）。
- 书：《iOS 人机界面指南》中文译本、《Auto Layout 实战》、《移动 UI 设计模式》（IM/会话列表/标签栏/个人中心模式）。
- IM 类界面专项：会话列表（头像圆角、未读红点、时间右对齐、置顶/免打扰语义）、聊天气泡（最大宽度 70–75%、连续气泡合并、长按菜单、引用回复缩进）、输入框（键盘联动、语音/加号热区 ≥44pt、安全区）——这些模式的具体隐患排查见 `audit-native-source.md` 与 `audit-screenshots.md`。
