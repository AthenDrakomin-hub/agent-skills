# IPA 静态产物审计手册

对最终交付的 `.ipa`（或已解包的 `.app`）做静态分析，回答"上架产物里是否携带 UI/UX 隐患与审核风险"。优先用脚本一键审计，深度项按本手册用命令人工复核。

> **平台能力边界**：Python 脚本（纯标准库）在 Windows/macOS/Linux 都能跑，覆盖 plist、结构、图标尺寸（PNG 头解析）、本地化、资源体积、Mach-O 架构、UIWebView/私有 API 字符串、签名目录结构。深度项（Assets.car 内容、otool/nm、codesign、provisioning 解码）必须在装有 Xcode 命令行工具的 macOS 上执行；Windows 上脚本会输出待人工执行的精确命令。

## 目录
1. 一键审计与产物解剖
2. Info.plist UI/UX 键审计
3. 图标与启动屏
4. Assets.car 资源目录审计
5. Mach-O 二进制分析（架构、UIWebView、私有 API、废弃符号）
6. 本地化覆盖
7. 资源体积与包体
8. 签名与描述文件
9. 上架 UI/UX 相关审核清单
10. 静态分析盲区与证据链
11. 附录：脚本规则编号索引

## 1. 一键审计与产物解剖

```bash
# 对 ipa 或 .app 目录
python scripts/ipa_audit.py ./LexiangIM.ipa --format md --out ipa-report.md
# JSON 给 CI
python scripts/ipa_audit.py ./LexiangIM.ipa --format json --out ipa-report.json
# 保留解包目录便于人工翻
python scripts/ipa_audit.py ./LexiangIM.ipa --keep --workdir ./ipa_work
```

IPA 本质是 zip，典型结构：

```
Payload/
└── LexiangIM.app/
    ├── LexiangIM                # 主二进制（Mach-O）
    ├── Info.plist               # 二进制 plist（plistlib 可解析）
    ├── Assets.car               # Asset Catalog 编译产物
    ├── LaunchScreen.storyboardc # 启动屏编译产物
    ├── Base.lproj/  zh-Hans.lproj/  ar.lproj/   # 本地化
    ├── Frameworks/*.framework/  # 内嵌动态库（逐个扫二进制）
    ├── PkgInfo                  # 无关注释
    ├── _CodeSignature/CodeResources
    └── embedded.mobileprovision # 描述文件（CMS 签名的 plist）
```

手动解包：`unzip -q App.ipa -d workdir`（Windows 用资源管理器或 Python zipfile）。主程序体即 `Payload/*.app`。

## 2. Info.plist 键审计（脚本 I-CONFIG/LAUNCH/ORIENT/ATS/PRIV 规则）

脚本自动判读以下键，人工复核以此表为准：

| 键 | 期望 / 风险 |
| --- | --- |
| `CFBundleShortVersionString` / `CFBundleVersion` | 必须有且语义正确（展示版本 + build 号） |
| `MinimumOSVersion` / `DTPlatformVersion`（实际取自二进制 LC_BUILD_VERSION 与 plist） | 过低的最低系统（<13）意味着无法用安全区/Dynamic Type API；用 iOS 26 SDK 编译才会获得液态玻璃 |
| `UIDeviceFamily` | `[1]` iPhone；含 2 则 iPad 义务随之而来（方向、多任务、图标） |
| `UILaunchStoryboardName` 或 `UILaunchScreen` | **必须至少一个**；缺失会在新机型黑屏/缩放运行（App 以兼容模式跑，不是全屏分辨率） |
| `UILaunchImages` / 根目录 `LaunchImage*.png` | 废弃静态启动图（I-LAUNCH-002），新机型黑边 |
| `UISupportedInterfaceOrientations` | iPhone 竖屏为主合理；游戏/视频可横屏；需与代码一致 |
| `UISupportedInterfaceOrientations~ipad` | iPad 必须支持多方向（官方要求支持竖放/横放两组共 4 方向，除非属于允许锁向的类别）；不足 + 无现代启动屏 = iPad 多任务被禁 |
| `UIRequiresFullScreen` | 应为 false（未填默认 false）；true 关闭 Slide Over/Split View（I-IPAD-001） |
| `NSAppTransportSecurity` | `NSAllowsArbitraryLoads=true` 为 I-ATS-001（P1）；WebView 类可用 `NSAllowsArbitraryLoadsInWebContent=true`（可接受，主程序 API 仍走 HTTPS） |
| `NSCameraUsageDescription` 等 `NS*UsageDescription` | 用哪个隐私 API 就必须有键且**非空**（空串调用即崩溃，I-PRIV-001）；建议随 `.lproj/InfoPlist.strings` 翻译 |
| `UIUserInterfaceStyle` | 不应为 `Light`（强制浅色） |
| `UIStatusBarHidden` / `UIViewControllerBasedStatusBarAppearance` | 除全屏媒体外不隐藏；状态栏样式推荐由 VC 控制 |
| `UIRequiredDeviceCapabilities` | 应含 `arm64` |
| `ITSAppUsesNonExemptEncryption` | 未填每次提审弹合规问卷；仅 HTTPS 的 App 设 false 减少摩擦（非 UI 项，列此备查） |
| `CFBundleIcons` / `CFBundleIconFiles` | 仅当未用 Asset Catalog 时依赖；见 §3 |

## 3. 图标与启动屏（I-ICON 系列）

现代 Xcode（14+）在 Asset Catalog 里提供一张 1024×1024 图标即可自动生成各尺寸；产物中图标编译进 `Assets.car`。脚本在无 macOS 时：

- 列举 .app 根目录 loose PNG（含旧法图标、LaunchImage），按 PNG chunk 解析真实像素，核对尺寸；
- 无 loose 图标且无 Assets.car → I-ICON-001（P1）；
- 有 Assets.car 但平台无 assetutil → 输出 macOS 复核命令。

各尺寸 slot（旧法/人工核对用，单位 px）：

| 用途 | 尺寸 @2x/@3x |
| --- | --- |
| iPhone 通知 20pt | 40 / 60 |
| iPhone 设置 29pt | 58 / 87 |
| iPhone Spotlight 40pt | 80 / 120 |
| iPhone App 60pt | 120 / 180 |
| iPad 通知 20pt | 20 / 40 |
| iPad 设置 29pt | 29 / 58 |
| iPad Spotlight 40pt | 40 / 80 |
| iPad App 76pt | 76 / 152 |
| iPad Pro App 83.5pt | 167 |
| App Store | 1024 × 1024 |

注意：iOS 26 图标有浅色/深色/着色三套外观与玻璃形状裁剪要求，核对 Asset Catalog AppIcon 配置（Universal → iOS 26+ 三个外观槽）。启动屏必须用 storyboard/`UILaunchScreen`，不能拿启动屏做广告页（审核风险），不能放动态文字（系统启动期静态快照）。

## 4. Assets.car 资源目录审计

```bash
# 列出全部资源条目（名称、尺寸、Scale、色域、编码）
xcrun --sdk iphoneos assetutil --info Payload/App.app/Assets.car > assets.json
# 只看 AppIcon
xcrun --sdk iphoneos assetutil --info Assets.car | grep -A8 -i appicon
```

审计点：

1. **Scale 完整性**：通用位图应有 @2x/@3x；只有 @2x 在 @3x 机型发糊，只有 @3x 在 @2x 下浪费内存（系统缩放，内存峰值高）。
2. **AppIcon 尺寸齐全**（见 §3 表）。
3. **内存体积**：单图解码后内存 = 宽×高×4 字节，与文件大小无关；找超大图（如 3000px 引导页）按显示尺寸出图。
4. **色域/位深**：照片类用 P3，UI 图标 sRGB 即可；Display P3 标记错误会色差。
5. **未使用资源**：car 内条目名与代码 `imageNamed:`/SwiftUI `Image("")` 交叉核对（脚本不做语义匹配，人工或用 LSUnusedResources 类工具）。
6. **深色变体**：支持深色模式的 logo/插画应有 Dark Appearance 条目。
7. **PDF/SVG 矢量**：单尺度矢量是否勾选 Preserve Vector Data。

## 5. Mach-O 二进制分析

脚本纯 Python 解析 fat/slice 头部与 LC_BUILD_VERSION，并对主二进制与 `Frameworks/*.framework` 逐个跑 ASCII strings。macOS 增强：

```bash
lipo -info Payload/App.app/App                 # 架构
otool -l App | grep -A4 LC_BUILD_VERSION       # 最低系统/SDK
otool -L App                                   # 链接的系统库/私有库
nm App | grep -i UIWebView                     # 符号级 UIWebView
strings -a App | grep -E "UIWebView|_UIBackdropView|UICalloutBar" 
codesign -dvvv Payload/App.app                 # 签名与权限
```

审计点：

| ID | 检查 | 判定 |
| --- | --- | --- |
| I-WEB-001 | 任意 slice / 内嵌 framework 出现 `UIWebView` 符号或类名字符串 | **P0**：Apple 自 2020 年起拒审；改 WKWebView；三方 SDK 带的需升级 SDK |
| I-ARCH-001 | 无 arm64 device slice | P0，无法在真机/App Store 运行 |
| I-ARCH-002 | 含 x86_64/模拟器 slice 的设备包 | P1，打包流程错误（应只在 .xcframework 模拟器产物里） |
| I-OS-001 | `minos` 低于 iOS 13 | P3 提示：安全区/Dynamic Type/深色模式 API 都需条件化，审计成本高 |
| I-PRIVATE-001 | strings 命中私有类名（`_UIBackdropView`、`UICalloutBarButton`、`UITextEffectsWindow` 等） | P2 人工复核：可能是误报（系统框架字符串带入），也可能是私有 API 拒审 |
| I-DEPRECATED-001 | `UI_USER_INTERFACE_IDIOM()` 等废弃符号 | P3，换 `UIDevice.current.userInterfaceIdiom` |
| — | FairPlay 加密（App Store 分发版 __TEXT 加密） | strings 命中率下降；**审计用 Archive 导出的未加密 AdHoc/Development IPA**，脚本会提示是否加密（cryptid） |

## 6. 本地化覆盖（I-LOC）

- 列 `.lproj` 目录：`Base.lproj` + 各语言。只有一种语言而代码含多语言分支 → 资源缺失。
- 每个语言目录应有 `Localizable.strings`（或 `.stringsdict`）、`InfoPlist.strings`（权限文案翻译）、故事板字符串。
- 静态核对：`NSLocalizedString` key 与 strings 表交叉（源码审计阶段做）；IPA 侧看语言包是否真的被打进去（常见漏配 target membership）。
- RTL 语言（ar/he/fa/ur）存在时，必须验证镜像（见 H5/原生 RTL 章节），并检查启动屏/图标方向无关性。
- 伪语言验证在 Xcode scheme → App Language → Double-Length Pseudolanguage / Right-to-Left Pseudolanguage。

## 7. 资源体积与包体（I-SIZE）

- 脚本输出包体总大小与 Top 15 大文件；阈值：单资源未压缩 >10MB 提示；解包总体 >200MB 提示（蜂窝下载策略与首启解压峰值）。
- 视频/音频用 H.265/HEVC、AAC；引导视频放 On-Demand Resources 或云端。
- 重复分辨率：loose PNG 检查 @2x 无 @3x 配对（I-ASSET-001，P3）；@1x 在 iPhone 上基本无意义。
- 不应打入产物：`.xib` 源文件、`.h/.m` 源码、`.md`、测试数据、`.map`（I-RES-001）。
- 内嵌 framework：确认每个都实际使用且为 Embed & Sign；重复打包同一库不同版本会增大包体且潜伏类冲突。

## 8. 签名与描述文件

```bash
# macOS
security cms -D -i Payload/App.app/embedded.mobileprovision > provision.plist
plutil -p provision.plist | grep -E "ExpirationDate|TeamIdentifier|ProvisionedDevices|aps-environment"
codesign -d --entitlements :- Payload/App.app
```

- 无 `_CodeSignature` 目录 → I-SIGN-001（重签名/砸壳/打包异常的信号）。
- 描述文件过期、Bundle ID 不匹配、设备数不足（AdHoc）→ 安装失败或掉签。
- Entitlements 与功能不匹配（推送无 aps-environment）会影响功能完整性。
- Windows 下脚本只能确认 mobileprovision 是否存在与大小（CMS 无法纯 Python 解码），输出上述命令。

## 9. 上架审核中与 UI/UX 相关的高频拒审点

1. UIWebView（I-WEB-001）。
2. 权限用途描述缺失/空串/文案与功能不符（相机相册麦克风定位通讯录通知）。
3. iPad  App 不支持多任务/多方向、缺图标尺寸。
4. 启动屏缺失导致兼容模式运行、启动屏放广告/branding 超时。
5. 登录/账号类 App 未提供游客可用路径或隐私政策入口（非视觉但影响首屏流程）。
6. 纯 WebView 壳没有原生体验（HIG 4.2 Minimum Functionality）——乐享 IM 这类有原生导航/推送/相机的通常没问题，纯网页套壳高危；应对：原生导航栏、相册/相机/推送/分享能力、加载/错误/空态。
7. 付费/抽奖等需在审核备注说明；与 UI 无关不列。
8. 强制更新弹窗阻断、无关闭入口的弹窗。
9. Demo 账号缺失导致审核进不去主界面（提审信息页填写）。

## 10. 静态 IPA 分析盲区（必须用其他通道补）

IPA 是"死"产物，看不到：约束冲突、动态字体表现、深色模式实际配色、键盘联动、动画性能、RTL 实际布局、可访问性实际焦点、WebView 内 H5 行为。这些按 `audit-screenshots.md` 截图矩阵 + `rubric.md` 回归矩阵补；H5 资源若在 App 内置 bundle（`www/` 目录）则同时跑 `source_scan.py` 扫该目录，若 H5 在线部署则需拿到前端构建产物/源码。

## 11. 附录：脚本规则编号索引（I-*）

| ID | 级别 | 检查项 |
| --- | --- | --- |
| I-WEB-001 | P0 | 主二进制/内嵌框架含 UIWebView 字符串（拒审） |
| I-ARCH-001 | P0 | 缺 arm64 设备架构 / 找不到主二进制 |
| I-ARCH-002 | P1 | 设备包含 x86_64/模拟器 slice |
| I-LAUNCH-001 | P1 | 无任何启动屏配置（兼容分辨率运行） |
| I-LAUNCH-002 | P1 | 废弃 UILaunchImages/LaunchImage 静态启动图 |
| I-ATS-001 | P1 | NSAllowsArbitraryLoads 全局放行 HTTP |
| I-PRIV-001 | P1 | NS*UsageDescription 文案为空 |
| I-ICON-001 | P1 | 无 Assets.car / 无 AppIcon 资源 / 无图标声明 |
| I-ICON-002 | P1 | Assets.car 中无 AppIcon 条目（macOS assetutil） |
| I-SIGN-001 | P1 | 缺 _CodeSignature（未签名/砸壳） |
| I-ORIENT-001 | P2 | iPad 声明方向不足四个 |
| I-IPAD-001 | P2 | UIRequiresFullScreen 禁用 iPad 多任务 |
| I-DARK-001 | P2 | Info.plist 强制 Light 外观 |
| I-KEY-001 | P2 | 缺版本号/构建号 |
| I-ICON-003 | P2 | Assets.car AppIcon 尺寸不全（macOS assetutil） |
| I-PRIVATE-001 | P2 | 命中疑似私有 API 字符串（人工复核） |
| I-SIGN-002 | P2 | embedded.mobileprovision 已过期（macOS） |
| I-SIZE-001 | P2 | 解包总体积 >200MB |
| I-ATS-002 | P3 | NSAllowsArbitraryLoadsInWebContent（可接受，确认） |
| I-CAP-001 | P3 | UIRequiredDeviceCapabilities 未声明 arm64 |
| I-REL-001 | P3 | 未声明 ITSAppUsesNonExemptEncryption |
| I-OS-001 | P3 | MinimumOSVersion / minos < 13 |
| I-LOC-001 | P3 | 仅 0–1 个 .lproj 语言包 |
| I-SIZE-002 | P3 | 单资源 >10MB |
| I-SIZE-003 | P3 | Assets.car 含 ≥3000px 超大图（macOS） |
| I-ASSET-001 | P3 | loose PNG 有 @2x 无 @3x |
| I-RES-001 | P3 | 源码/开发文件（.h/.m/.xib/.md/.map）打入包体 |
| I-DEPRECATED-001 | P3 | UI_USER_INTERFACE_IDIOM 等废弃符号 |
