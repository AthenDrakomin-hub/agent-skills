# H5 / UniApp / WKWebView 源码静态审计清单

适用：UniApp/Vue/H5 打包进 iOS WKWebView 的套壳应用（如乐享 IM），以及纯 H5 在 iOS Safari/WebView 中的 UI 兼容。先跑 `source_scan.py`（H- 规则），再按本文件人工补查。

## 目录
1. RTL 文字方向与镜像（H-RTL-001）
2. viewport 与页面缩放（H-VIEWPORT-001）
3. 字体大小自动调整与输入框聚焦放大（H-TYPE-001 / H-INPUT-001）
4. 安全区适配（H-SAFE-001/002）
5. 100vh 失效、键盘与 fixed 定位（H-VH-001）
6. 玻璃模糊、滚动与其他 WKWebView 兼容点
7. 深色模式、触摸目标与无障碍
8. UniApp 专项（pages.json / tabBar / 配置）
9. 原生壳侧配置
10. 症状 → 根因速查表

## 0. 基线模板（新建页面直接抄）

```html
<!DOCTYPE html>
<html lang="zh-CN" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport"
        content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <style>
    :root {
      --sat: env(safe-area-inset-top);
      --sab: env(safe-area-inset-bottom);
      --sal: env(safe-area-inset-left);
      --sar: env(safe-area-inset-right);
    }
    html { -webkit-text-size-adjust: 100%; }
    body { margin: 0; min-height: 100dvh; }
    input, textarea, select { font-size: 16px; } /* 防止 iOS 聚焦自动缩放 */
    .fixed-bottom {
      position: fixed; left: 0; right: 0; bottom: 0;
      padding-bottom: calc(env(safe-area-inset-bottom) + 8px);
    }
    .scroll-area { overscroll-behavior: contain; touch-action: manipulation; }
    .glass { -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px); }
    @media (prefers-color-scheme: dark) { /* 深色变体 */ }
    @media (prefers-reduced-motion: reduce) { * { animation-duration: .01ms !important; } }
  </style>
</head>
```

## 1. RTL 文字方向与镜像（H-RTL-001）

- **症状**：tab 文字/图标水平镜像；tab 排列顺序整体反向；气泡尖头朝向错误。
- **机理**：阿语等 RTL 语言触发 `dir="rtl"`；中文页被 i18n 库/系统区域误触发即镜像；也可能是显式 `transform: scaleX(-1)` 误用。
- **检索**：`dir="rtl"`、`direction: rtl`、`unicode-bidi`、`scaleX(-1)`、`scale(-1, 1)`、`scaleX(-`；检查 i18n 初始化是否按 `navigator.language` 自动设 dir。
- **修复**：
  - 中文/英文页显式 `<html lang="zh-CN" dir="ltr">`；删除按系统语言动态改 direction 的逻辑，或仅对真正 RTL 语言（ar/he/fa/ur）设置。
  - 镜像图标（如返回箭头）在 RTL 下才翻转：`[dir="rtl"] .back { transform: scaleX(-1); }`，不要全局翻。
  - 原生壳可固定 WKWebView 的 `semanticContentAttribute = .forceLeftToRight` 作为兜底（但会牺牲真实阿语用户体验，只适用于明确不支持 RTL 的 App）。
- **验证**：系统语言切阿拉伯语 + 中文两种环境，tab 文字方向、顺序、选中态、气泡方向分别回归。

## 2. viewport 与页面缩放（H-VIEWPORT-001）

- **症状**：整体缩放错乱、两侧白边、页面比屏宽窄/宽。
- **检索**：确认每个 HTML 入口都有 viewport；UniApp 检查 `manifest.json → h5 → router/base/viewport` 与模板 `index.html`。
- **必须**：`width=device-width, initial-scale=1.0, viewport-fit=cover`。
- `maximum-scale=1.0, user-scalable=no` 会禁掉双指缩放——**无障碍倒退**（视力辅助用户依赖缩放），除非是真 WebView 受控环境并记录理由；WebView 内默认不影响原生缩放但仍不推荐。
- 注意：用了 `env(safe-area-inset-*)` 但缺 `viewport-fit=cover` 时变量恒为 0（H-SAFE-002，扫描器跨文件聚合检查）。

## 3. 字体大小自动调整与输入框聚焦放大

- **H-TYPE-001**：iOS 会自动放大小于默认正文尺寸的文字（横屏尤其明显），导致排版溢出。全局 `-webkit-text-size-adjust: 100%;`（不要用 `none`——新版 WKWebView 行为差异且完全无视用户字号偏好；100% 是稳妥值）。
- **H-INPUT-001**：输入框字号 <16px 时，聚焦瞬间 WKWebView 强制放大页面且不还原。所有 `input/textarea/select/[contenteditable]` 以及 UniApp 的 `.uni-input-wrapper`、`.u-input`（uView）、`.van-field` 等组件内 input 计算后字号必须 ≥16px（视觉需要小字可用 `transform: scale` 包裹视觉元素，但优先直接 16px）。
- 支持系统动态字号：用 `rem`/`em` 或监听 `fontSizeChanged`（UniApp `uni.onThemeChange`? 动态字体无标准事件，可用 CSS `font-size: -apple-system-body` 配合媒体查询），不要把容器高度写死。

## 4. 安全区适配（H-SAFE-001/002）

- **症状**：底部 tab/输入框被 Home Indicator 小黑条遮挡；底部异常留白；圆角/刘海处内容贴边；横屏左右贴圆角。
- **四向变量**：`env(safe-area-inset-top/bottom/left/right)`，底部固定栏 `padding-bottom: calc(env(safe-area-inset-bottom) + 原有间距)`。
- 老系统兜底：`constant()` 与 `env()` 双写（iOS <11.2 用 constant，当前最低系统若 ≥13 可只写 env）。
- UniApp：
  - 固定底栏优先用 `safe-area-inset-bottom: true`（组件属性，uView/u-input/自定义 tabbar 各有对应属性）；
  - 或 CSS `env()`；也可 JS 取 `uni.getSystemInfoSync().safeAreaInsets.bottom`，但 **CSS env 优先**（键盘弹起、屏幕旋转时 CSS 自动更新，JS 取值需自己监听）。
- 与原生壳的边界（避免双重安全区）：壳 `scrollView.contentInsetAdjustmentBehavior` 与 H5 `viewport-fit=cover` 只能一方补偿，约定见 §9。
- 顶部：沉浸式时 `--sat` 给导航栏；不要写死 44/47px。

## 5. 100vh、键盘与 fixed 定位（H-VH-001）

- **100vh 在 iOS 含工具栏/键盘时偏大**，底部内容被键盘或 Home Indicator 切掉；改用 `100dvh`（iOS 15.4+），或 `min-height: 100vh; min-height: 100dvh;` 双写；UniApp 可用 `calc(100vh - var(--window-bottom))` 或 flex 布局让内容区自适应。
- 键盘弹起常见故障：
  - `position: fixed` 底栏被键盘顶飞/留在视口外 → iOS 16+ WKWebView 视觉视口收缩时 fixed 行为已改善，但仍需真机验证；传统方案监听 `visualViewport.resize`，把底栏 transform 上移键盘高度，或交给原生 inputAccessoryView。
  - UniApp 的 `adjust-position`（默认 true）会自动推页面；自定义弹层内输入框要关 `adjust-position` 自己用 `keyboardHeightChange` 事件处理。
  - 输入框聚焦后页面滚不到位 → 不要在 focus 时同步 `scrollTop`，用 `scrollIntoView` 延迟或 `visualViewport` 的目标元素。
- 聊天页建议：消息区 `flex:1; overflow:auto`，输入区在文档流末尾（非 fixed），从根上避开键盘问题；fixed 底栏只用于无输入的 tab 栏。

## 6. 玻璃模糊、滚动与其他 WKWebView 兼容点

| ID | 隐患 | 修复 |
| --- | --- | --- |
| H-BLUR-001 | `backdrop-filter` 没写 `-webkit-` 前缀，WKWebView 不生效 | 两个都写（见 §0 模板） |
| H-OBSOLETE-001 | `-webkit-overflow-scrolling: touch` | iOS 13+ 已默认惯性滚动，删掉 |
| — | 弹层打开后背景仍可滚动穿透 | `.scroll-area{ overscroll-behavior: contain; }`；弹层打开时给 body 加 `position:fixed` 锁滚动并记录 scrollTop |
| — | 点击 300ms 延迟/点透 | `touch-action: manipulation`；UniApp 用 `@click` 即可（内置 fastclick 处理），不要再引 fastclick 库 |
| — | 灰色点击高亮遮不掉 | `-webkit-tap-highlight-color: transparent`（仅可点元素，不要 `*` 扩大化） |
| — | 1px 线在 Retina 上显粗 | `transform: scaleY(0.5)` 或 `0.5px`（WKWebView 支持） |
| — | 长列表卡顿（DOM 全量渲染） | 虚拟列表（recycle-list / 自研 IntersectionObserver 回收）；图片懒加载 |
| — | 图片在 @3x 屏糊或体积过大 | 按 `window.devicePixelRatio` 取 @2x/@3x；头像走 imageView 裁剪参数；WebP/AVIF |
| — | 日期 `new Date('2026-09-16 10:00')` iOS 解析 Invalid Date | 日期串改 `2026/09/16 10:00` 或 ISO `T` 格式；IM 时间戳高发 |
| — | `overflow:auto` 内 `-webkit-sticky` 失效 | sticky 父级不能有 overflow hidden；真机验证 |
| — | input 自动填充底色发黄 | `-webkit-box-shadow:0 0 0 1000px #fff inset;` 或深色模式对应色 |

## 7. 深色模式、触摸目标与无障碍

- 深色模式：`@media (prefers-color-scheme: dark)` 全局变量切换；UniApp 配置 `darkmode:true` + `theme.json`，或 uni 级 CSS 变量；meta 可设 `color-scheme: light dark`，让滚动条/表单原生控件同步。**检测项目里 0 处 prefers-color-scheme 时扫描器给 H-DARK-001 提示**（若产品明确不支持深色，需壳侧锁定并记录）。
- 触摸热区：可点元素 CSS 命中盒 ≥44×44px（H-TOUCH-001 扫描 btn/tab/icon 类名下 20–43px 固定高）；图标按钮用 padding 撑热区而非放大图标。
- 无障碍：
  - 不要全局 `user-select:none`（H-A11Y-001），消息文本应允许选择复制；
  - 图标按钮加 `role="button"` + `aria-label`；图片 `alt`；
  - 动效尊重 `prefers-reduced-motion`（扫描器 H-A11Y-002 聚合提示）；
  - 颜色不是唯一状态通道（未读红点 + 数字/加粗）；
  - 表单 `inputmode="numeric/tel/email"`、`enterkeyhint`、`autocomplete` 提升键盘体验。
- 对比度同原生标准（正文 4.5:1）。

## 8. UniApp 专项（pages.json / tabBar / 配置）

| ID | 检查点 | 说明 |
| --- | --- | --- |
| H-UNI-001 | `pages.json` 配置原生 tabBar 还是自定义 tabBar | 原生 tabBar 由壳渲染、安全区自动；**自定义/H5 tabBar 无法获得 iOS 26 悬浮液态玻璃栏**，需自证安全区、键盘、滚动行为（乐享 IM tab 翻转即发生在 H5 自绘 tab） |
| — | `manifest.json → h5 → titleNView` | 自绘导航与壳导航重复时会出现双导航栏；二选一 |
| — | `safearea` 配置 | `background`/`bottom` 配置与 CSS env 不要重复补偿 |
| — | rpx 基准 | rpx 以 750 设计稿宽度换算，在 iPad/大屏上元素过大；大屏用媒体查询或 px + 尺寸类思路 |
| — | nvue/uvue 页面 | nvue 原生渲染不支持全部 CSS（不支持 * 选择器、部分 flex 语法），样式问题与 vue 页面分开排查 |
| — | 条件编译 | `#ifdef H5` 与 `APP-PLUS` 分支的样式差异要双端回归 |
| — | 状态栏占位 | `navigationStyle: custom` 时必须自行处理 `--sat`，否则内容钻到灵动岛下 |

## 9. 原生壳侧配置（WKWebView）

- **UIWebView 零容忍**：壳工程与三方 SDK 不得出现 UIWebView（IPA 扫描 I-WEB-001 为 P0）。
- 安全区责任约定（二选一，全 App 统一）：
  - 方案 A（推荐给全屏 H5）：壳 `webView.scrollView.contentInsetAdjustmentBehavior = .never` + H5 `viewport-fit=cover` + env()；
  - 方案 B：壳默认 `.automatic`，H5 不用 cover、不写 env 底部；
  - 两套同时生效 = 底部双倍留白。
- 暗色闪白：`webView.isOpaque = false; webView.backgroundColor = .clear;` 与 H5 body 背景一致。
- 字体：不设置 `minimumFontSize` 之类强制缩放；尊重 H5 的 text-size-adjust。
- 方向：`semanticContentAttribute` 与 H5 `dir` 保持一致策略，不要一方强制 LTR 一方 RTL。
- 缓存/路由：SPA 切路由时滚动位置、输入态由 H5 管；WKUIDelegate 三个 JS 面板必须实现，否则 alert/confirm 无响应。
- 真机调试：iPhone 设置 → Safari → 高级 → Web 检查器；Mac Safari 开发菜单连真机 WebView。

## 10. 症状 → 根因速查表

| 症状 | 第一嫌疑 | 章节 |
| --- | --- | --- |
| tab/文字水平镜像、顺序反向 | RTL 误触发 / scaleX(-1) | §1 |
| 布局整体缩放错乱、白边 | viewport meta | §2 |
| 字体被放大、横屏字号跳变 | text-size-adjust | §3 |
| 点输入框页面放大、不回缩 | 输入框字号 <16px | §3 |
| 底部被小黑条遮挡/底部留白 | safe-area / 双重补偿 | §4、§9 |
| 100vh 底部被切、键盘遮挡 | vh/dvh、fixed、键盘 | §5 |
| 毛玻璃没效果 | 缺 -webkit- 前缀 | §6 |
| 弹层背景滚动穿透 | overscroll/锁滚动 | §6 |
| 日期 NaN/Invalid Date | 日期串格式 | §6 |
| 深色下白底刺眼/控件还是白的 | prefers-color-scheme 缺失 | §7 |
| 图标按钮 VoiceOver 读不出 | aria-label 缺失 | §7 |
| H5 tab 与系统标签栏观感割裂 | 自绘 tab / 双栏并存 | §8、hig §2 |

## 参考资料来源

- Apple HIG：Layout / Right to left / Typography / Materials（https://developer.apple.com/design/human-interface-guidelines/）
- WWDC：WKWebView enhancements 系列；Safe Area & Layout margins
- WebKit 博客：visualViewport、dynamic viewport units（dvh）、`color-scheme`
- 移动端 H5 在 iOS WKWebView 兼容实践（viewport、safe-area、键盘、fixed）
