# iOS 原生源码静态审计清单（Swift / Objective-C / UIKit / SwiftUI）

## 目录
1. 使用方法与规则编号
2. A 布局与多机型适配
3. B 安全区
4. C 字体与 Dynamic Type
5. D 深色模式与颜色
6. E 触摸目标与无障碍
7. F 交互与手势
8. G 渲染性能
9. H 导航栏与系统栏
10. I 键盘与表单
11. J 国际化与 RTL
12. K 启动屏与 plist 配置
13. L SwiftUI 专项
14. M WKWebView 壳工程专项
15. 人工/运行时补查项（脚本盲区）

## 1. 使用方法与规则编号

先跑扫描器拿底稿，再按本文件人工补查脚本查不到的项：

```bash
python scripts/source_scan.py <工程根目录> --format md --out source-report.md
```

规则编号约定：`N-域-序号`（Native），扫描器对每条给出 文件:行号、证据行、修复指向。H5 为 `H-` 开头，IPA 为 `I-`。

## 2. A 布局与多机型适配

| ID | 隐患 | 识别 | 后果 | 修复 |
| --- | --- | --- | --- | --- |
| N-ADAPT-001 | 按屏宽/机型写死分支（`UIScreen.main.bounds.width == 375`、`if iPhoneX`） | 同时出现 `mainScreen`/`UIScreen.main` 与 320/375/390/393/402/414/428/430/440 | 新机型直接错位；Display Zoom 失效 | 用**尺寸类** `traitCollection.horizontalSizeClass` 或 Auto Layout |
| N-ADAPT-002 | 大量 `CGRectMake`/`.frame=` 常量布局 | `CGRect(x:y:width:height:)`、`CGRectMake(` | 多机型/动态字体/旋转必错 | 改 Auto Layout（NSLayoutConstraint / Anchor） |
| — | 约束到具体设备名 | `if model == "iPhone17"` | 同 N-ADAPT-001 | 同上 |
| — | 旋转/分屏不重排 | 无 `viewWillTransition(to:with:)` / `traitCollectionDidChange` 处理或约束已覆盖 | iPad 分屏、横屏错乱 | 约束天然自适应；必要时在过渡回调里换常量 |
| N-DEPRECATED-002 | `UIScreen.main`（iOS 16 废弃）、`keyWindow`（iOS 13 废弃） | 对应符号 | 多场景（Stage Manager）下取错窗口 | `windowScene` 从视图所在 window 取；SwiftUI `@Environment(\.openWindow)` |
| N-DEPRECATED-001 | `UI_USER_INTERFACE_IDIOM()`（iOS 13 废弃） | 检索该宏 | 编译告警/未来失效 | `UIDevice.current.userInterfaceIdiom`（Swift）/ `UIDevice.currentDevice.userInterfaceIdiom`（ObjC） |

修复范式：

```swift
// 错误：写死尺寸
let w = UIScreen.main.bounds.width
frame = CGRect(x: 16, y: 100, width: w - 32, height: 44)

// 正确：约束 + 安全区 + 布局边距
NSLayoutConstraint.activate([
  card.leadingAnchor.constraint(equalTo: view.layoutMarginsGuide.leadingAnchor),
  card.trailingAnchor.constraint(equalTo: view.layoutMarginsGuide.trailingAnchor),
  card.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
  card.heightAnchor.constraint(greaterThanOrEqualToConstant: 44),
])
```

## 3. B 安全区

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-SAFE-001 | 用已废弃的 `topLayoutGuide`/`bottomLayoutGuide`（iOS 11 前） | 符号检索 | 换 `safeAreaLayoutGuide` |
| N-SAFE-002 | 滚动视图 `contentInsetAdjustmentBehavior = .never` 后未自行补偿 | 检索该赋值 | 非全屏场景用默认 `.automatic`；全屏自定义时手动加 `safeAreaInsets` |
| N-SAFE-003 | 依赖 `statusBarFrame` 算顶部 | `statusBarFrame` | 灵动岛/热点状态栏下错误，改安全区 |
| — | 约束挂到 `view.topAnchor/bottomAnchor` 承载内容（背景可以） | 审查顶部/底部固定控件 | 内容挂 `safeAreaLayoutGuide`；全屏背景仍可挂 view |
| — | 横屏忽略左右安全区 | 只处理了 top/bottom | 四向都取 inset；横屏左右约 48pt |
| — | iPad 忽略 `layoutFrame`（Stage Manager） | 固定宽高 | 以 window 的 safeArea 为准 |

```objc
// ObjC 正确范式
self.tableView.contentInsetAdjustmentBehavior = UIScrollViewContentInsetAdjustmentAutomatic;
[NSLayoutConstraint activateConstraints:@[
  [self.submitBtn.bottomAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.bottomAnchor constant:-16],
  [self.submitBtn.leadingAnchor constraintEqualToAnchor:self.view.layoutMarginsGuide.leadingAnchor],
]];
```

## 4. C 字体与 Dynamic Type

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-TYPE-001 | `systemFont(ofSize:)`/`boldSystemFont`/`systemFontOfSize:` 固定字号且无缩放 | 检索固定字号 API | 改文本样式或 UIFontMetrics |
| N-TYPE-002 | SwiftUI `.font(.system(size:))` 固定字号 | 同模式 | `.font(.body)` 等样式；自定义字体 `@ScaledMetric` |
| — | Label 行数写死 1 且容器固定高 | `numberOfLines = 1` + 固定高约束 | `numberOfLines = 0`，行高 `greaterThanOrEqualTo`，cell 用 automaticDimension |
| — | cell 高度写死 | `heightForRowAt` 返回常量 | `rowHeight = UITableView.automaticDimension` + 合理 `estimatedRowHeight` |
| — | `adjustsFontSizeToFitWidth` 用来扛长文案 | 检索 | 它与 Dynamic Type 哲学冲突，只允许用于不可换行的数字徽标 |

```swift
// 自定义字体支持动态字体
let base = UIFont(name: "PingFangSC-Medium", size: 17)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: base)
label.adjustsFontForContentSizeCategory = true
label.numberOfLines = 0
```

## 5. D 深色模式与颜色

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-DARK-001 | `overrideUserInterfaceStyle = .light` 强制浅色/深色 | 检索 | 删除，跟随系统；仅单个特殊页面可局部覆盖并说明理由 |
| N-COLOR-001 | `UIColor(red:green:blue:)` / `colorWithRed:` / `#colorLiteral` / SwiftUI `Color(red:green:blue:)` 写死颜色且无动态提供者 | 检索 | 系统色；或 Asset Catalog 配明暗两套；或 `init(dynamicProvider:)` |
| — | `UIColor.white/black` 直接做文字/背景 | 审查 | `.systemBackground` / `.label` 等语义色 |
| — | 硬编码状态栏样式不随模式切换 | `preferredStatusBarStyle` 固定 `.default` | `.darkContent`/`.lightContent` 按背景明暗返回，或 `.default` 自动 |
| — | 图片资源无深色版本（logo/插画） | Asset Catalog 检查 | 配 Dark Appearance 变体 |

```swift
let brand = UIColor { tc in
    tc.userInterfaceStyle == .dark ? UIColor(red: 0.45, green: 0.7, blue: 1, alpha: 1)
                                  : UIColor(red: 0.0, green: 0.48, blue: 1, alpha: 1)
}
```

## 6. E 触摸目标与无障碍

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-TOUCH-001 | 按钮/图标热区 <44pt（常与"视觉图标 24pt"一起出现） | 扫描按钮相关 `equalToConstant: 20–43`；人工核对 | 视觉小、热区大：用 `contentEdgeInsets` 或透明热区容器 ≥44pt |
| N-A11Y-001 | 纯图标按钮缺 `accessibilityLabel`（扫描器做文件级聚合提示） | 文件内有按钮但无 accessibilityLabel | 补标签、traits（.button）、必要时 `accessibilityValue` |
| — | 自定义 cell 不暴露无障碍元素 | 重写 view 的页面 | `isAccessibilityElement` 或 `accessibilityElements`，气泡按条合并朗读 |
| — | 仅靠颜色表达状态（红点/红字报错） | 人工 | 颜色 + 图标/文字双通道 |
| — | 对比度不足（灰字灰底、玻璃下文字） | Accessibility Inspector Audit | 正文 4.5:1、大字/图标 3:1 |
| — | 不支持"降低透明度/减弱动态效果/加粗文本" | 人工 | `UIAccessibility.isReduceMotionEnabled` 等分支；动画提供降级 |
| — | 命中区互相重叠或贴屏幕边缘 <8pt | 人工 | 边缘留 ≥8pt 间隙 |

热区修复：

```swift
// 视觉 28pt 的关闭按钮，热区扩到 44pt
closeButton.contentEdgeInsets = UIEdgeInsets(top: 8, left: 8, bottom: 8, right: 8)
closeButton.accessibilityLabel = "关闭"
closeButton.accessibilityTraits = .button
```

## 7. F 交互与手势

| 隐患 | 识别 | 修复 |
| --- | --- | --- |
| 给 UILabel/UIImageView 加点击手势却没开 `isUserInteractionEnabled`（N-GESTURE-001 聚合提示） | 同文件有 Tap 手势与 Label/ImageView 但无该属性 | 显式置 true；优先用 UIButton |
| 手势与滚动/侧滑返回冲突 | 人工审查 | `shouldRecognizeSimultaneouslyWith` / `require(toFail:)` 明确关系 |
| 无按压反馈（自绘按钮点击无任何状态变化） | 人工 | `isHighlighted` 态调透明度/缩放；列表用 cellSelected 态 |
| 长按无菜单（IM 消息不能复制/引用/撤回） | 人工 | `UIContextMenuInteraction`（iOS 13+），不要自己写矩形判定 |
| 缺必要的 Haptics | 人工 | `UIImpactFeedbackGenerator` 轻量反馈，勿滥用 |
| 自定义返回手势失效（全屏 pop 被自己的手势吃掉） | 人工 | 保留 `interactivePopGestureRecognizer` |

## 8. G 渲染性能

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-PERF-001 | `cornerRadius` + `masksToBounds/clipsToBounds` 触发离屏渲染（尤其头像列表每帧） | 文件同时出现二者 | 图片圆角优先 `UIImage` 绘制时裁剪 / `UIGraphicsImageRenderer` 预裁剪；UIKit 16+ 用 `maskedCorners`+`cornerCurve=.continuous`（不再强制离屏）；避免对滚动内容根层 masks |
| N-PERF-002 | `shouldRasterize=true` 不配 `rasterizationScale`（默认 1x，Retina 糊） | 同文件有光栅化无 scale | `layer.rasterizationScale = UIScreen.main.scale`；且只用于静态内容，动态内容光栅化反而掉帧 |
| N-PERF-003 | 阴影无 `shadowPath`（每帧离屏求 alpha） | 有 shadowOpacity 无 shadowPath | 设 `layer.shadowPath = CGPath(roundedRect:...`，或改预渲染阴影图 |
| — | cell 内 `layoutIfNeeded` / 同步圆角裁剪放在 `cellForRowAt` | 人工 | 异步预排版（缓存高度）+ 预裁剪图 |
| — | `cellForRowAt` 里 `dequeue` 失败后每次 alloc new cell（拼写错误的复用标识） | 人工 | 固定 reuseIdentifier，注册类/nib |
| — | 大图不按显示尺寸解码（聊天原图直接上屏） | 人工 | 后台 downsample 到显示 pt×scale（ImageIO 缩略图 API） |
| — | `draw(_:)` 里做重绘或 `setNeedsDisplay` 滥用 | 人工 | 拆分图层，仅失效区域重绘 |
| — | 透明度堆叠：多层 alpha<1、effect 视图嵌套 | Core Animation 工具 Color Blended Layers | 合并层、给 opaque 视图正确背景色 |

验证：Instruments → Core Animation 勾选 Color Off-Screen Rendered（黄色即命中）、Color Blended Layers（红色即命中），滚动列表帧率 60/120fps（ProMotion）。

## 9. H 导航栏与系统栏

- 优先 `UINavigationController` / `UITabBarController`，iOS 26 SDK 编译自动获得液态玻璃悬浮栏；不要隐藏后自绘（丢失滚动收缩、大标题、返回手势、状态适配）。
- 大标题：`navigationBar.prefersLargeTitles = true`，二级页关闭；搜索用 `UISearchController` 挂 `navigationItem.searchController`，勿自画搜索框。
- iOS 26 标签栏支持栏上方补充视图（随收缩下移），播放器/排序条用该能力而非另起悬浮条。
- 全屏内容页可隐藏栏，但必须提供替代退出路径且避开灵动岛；状态栏样式随背景明暗。
- 自绘 tab 扫描要点：`tabBar.isHidden = true` / `window.addSubview(自定义底栏)` → P1 平台一致性问题。

## 10. I 键盘与表单

| 隐患 | 识别 | 修复 |
| --- | --- | --- |
| 键盘弹起遮挡输入框 | 无键盘监听/约束 | iOS 15+ 直接约束到 `view.keyboardLayoutGuide.snapshot(top:)`（`keyboardLayoutGuide`）；低版本监听 keyboard 通知改 `contentInset` |
| 无点击空白收起键盘 | 人工 | `view.endEditing(true)`  tap 手势或 `scrollView.keyboardDismissMode = .interactive` |
| 未声明键盘类型 | 人工 | `keyboardType = .phonePad/.numberPad/.emailAddress/.asciiCapableNumberPad`；`textContentType`（oneTimeCode 自动短信验证码） |
| 大小写/纠错没关 | 人工 | 账号/邮箱字段 `autocapitalizationType = .none`、`autocorrectionType = .no` |
| 输入栏无 inputAccessoryView（IM 输入框不能跟随键盘悬浮） | 人工 | `inputAccessoryView` 或 `keyboardLayoutGuide` 约束，安全区底部联动 |
| 密码框没用安全文本/密码自动填充 | 人工 | `isSecureTextEntry` + `textContentType = .password/.newPassword` |

## 11. J 国际化与 RTL

| ID | 隐患 | 识别 | 修复 |
| --- | --- | --- | --- |
| N-I18N-001 | 界面文案直接写中文字面量（`label.text = "发送"`、`setTitle:@"发送"`） | 扫描赋值语句中的中文 | `NSLocalizedString` / `String(localized:)` + Localizable.strings |
| N-I18N-002 | 日期格式串用大写 `YYYY`（ISO 周年日，跨年周会错一年，IM 时间戳高发） | `"YYYY-MM-dd"` 等 | 用 `"yyyy-MM-dd"`；且 `locale`/`timeZone` 显式设置 |
| N-I18N-003 | 写死 `.left/.right` 对齐与 leading 约束 | `NSTextAlignmentLeft`、`leftAnchor` 承载语义内容 | 文本用 `.natural`；约束用 `leadingAnchor/trailingAnchor` |
| — | 图片/渐变带方向性（返回箭头、气泡尖角、进度条） | 人工 | 用 `imageWithHorizontallyFlippedOrientation()` 或 asset 配 RTL 变体；`semanticContentAttribute` |
| — | 数字/货币/复数没走本地化 | 人工 | `NumberFormatter` / `stringsdict` 复数规则 |
| — | App 没做 Auto-layout 英文/阿语压力测试 | 人工 | Xcode scheme → App Language: Double-Length Pseudolanguage / Arabic（RTL） |

```swift
// 日期范式（IM 会话列表时间）
let f = DateFormatter()
f.locale = Locale.current
f.timeZone = .current
f.dateFormat = "yyyy-MM-dd HH:mm"   // 绝不用 YYYY
```

## 12. K 启动屏与 plist 配置

源码工程里审 `Info.plist`（或 Build Settings 生成项），IPA 侧复核见 `audit-ipa.md`。

| ID | 键 | 风险 |
| --- | --- | --- |
| N-LAUNCH-001 | `UILaunchImages` 静态启动图 | 已废弃，新机型/旋转/多任务黑屏或上下黑边；改 LaunchScreen.storyboard 或 `UILaunchScreen` 字典 |
| N-CONFIG-001 | `NSAppTransportSecurity → NSAllowsArbitraryLoads=true` | 全局 HTTP 降级，审核风险；只对必要域名开 Exception Domains，WebView 场景用 `NSAllowsArbitraryLoadsInWebContent` |
| N-CONFIG-002 | `NS*UsageDescription` 空串 | 调用相机/相册/麦克风/定位/通知时直接崩溃或拒审；写用途文案并做多语言 |
| N-CONFIG-003 | `UIRequiresFullScreen=true` | 关闭 iPad Slide Over/Split View；除非有硬理由 |
| N-CONFIG-004 | `UIUserInterfaceStyle=Light` | 全 App 禁用深色模式（同 N-DARK-001） |
| N-CONFIG-005 | iPad 设备族但 `UISupportedInterfaceOrientations~ipad` 不足四个方向 | iPad 多任务被禁、审核风险；至少支持两横两竖 |
| — | `UIRequiredDeviceCapabilities` 缺 arm64、缺 `CFBundleShortVersionString` | 安装/展示异常 |
| — | 状态栏 `UIStatusBarHidden` 全局隐藏 | 除全屏媒体外一律不要隐藏 |

## 13. L SwiftUI 专项

- 用 `safeAreaInset(edge:)` 挂底部输入栏/工具栏，自动跟安全区与键盘；`ignoresSafeArea(.keyboard)` 只用于背景。
- `Text` 天然支持 Dynamic Type 与多行；给 Text 固定 `.frame(height:)` 是 N-TYPE 类隐患；长文案用 `.lineLimit(nil)`、`.fixedSize(horizontal:false, vertical:true)` 审查。
- `ScrollView` 优先 `LazyVStack`/`List`；长列表用 `List`/`LazyVStack` 防一次性布局。
- 导航用 `NavigationStack`（iOS 16+），弃用 `NavigationView`。
- 颜色用语义色或 asset catalog；`.foregroundStyle(.primary)`。
- iOS 26 玻璃：`Glass` 容器、`.glassEffect()`；不要用 `.background(.ultraThinMaterial)` 堆叠模仿新栏。
- `GeometryReader` 内做机型分支判断 = SwiftUI 版 N-ADAPT-001；尺寸类用 `@Environment(\.horizontalSizeClass)`。

## 14. M WKWebView 壳工程专项

原生壳侧（H5 侧见 `audit-h5-source.md`）：

| ID | 隐患 | 修复 |
| --- | --- | --- |
| N-WEB-001 | 仍在用 **UIWebView**（`UIWebView` 类、`@"UIWebView"`、xib 对象） | **P0 拒审项**，全面换 WKWebView |
| — | 没设 `scrollView.contentInsetAdjustmentBehavior` 且 H5 用了 `viewport-fit=cover`，双重安全区导致底部大留白 | 壳与 H5 约定一方处理：壳 `.never` + H5 env()，或壳 automatic + H5 不 cover，二选一 |
| — | WebView 不透明 + 暗色闪白屏 | `webView.isOpaque = false; backgroundColor = .clear`，H5 body 背景同步 |
| — | 键盘内联媒体播放/预览手势异常 | `allowsInlineMediaPlayback`、`allowsBackForwardNavigationGestures` 按产品配 |
| — | Cookie/滚动位置在导航跳转丢失 | 用 `WKWebsiteDataStore.default()`，必要时 snapshot |
| — | 自定义 User-Agent 后未包含系统信息导致 H5 适配分支误判 | UA 追加在默认 UA 之后，不覆盖 |
| — | 未处理 `window.alert/confirm/open` 的 WKUIDelegate | 实现三个面板回调，否则按钮无响应 |
| — | 消息通道 `WKScriptMessageHandler` 循环引用 | weak 代理或显式 removeScriptMessageHandler |

## 15. 人工/运行时补查项（脚本盲区，必须在报告中覆盖或声明）

1. **约束歧义/冲突**：跑起来看控制台 `Will attempt to recover by breaking constraint`；View Debugger 看红线。
2. **真实动态字体表现**：AX5 档逐页截图。
3. **深色模式实际效果**：模拟器切换 + 玻璃材质下对比度。
4. **真机渲染性能**：Core Animation Instruments（模拟器测不出真实离屏成本）。
5. **VoiceOver 全流程**：开机按流程划一遍，朗读顺序、标签、转子。
6. **弱网/空态/错误态/加载态**：源码静态看不到数据驱动状态，逐页确认四态齐全。
7. **首屏启动时长与启动屏**：静态度量需真机 Instruments App Launch。
8. **iPad 分屏 Stage Manager、外接屏、CarPlay/Widget 等扩展形态**（如适用）。
