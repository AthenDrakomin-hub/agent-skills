# 多端兼容性扫描规则

## 目录
- [版本适配层（必做）](#版本适配层必做)
- [平台判断与条件编译](#平台判断与条件编译)
- [iOS 端专项检查](#ios-端专项检查)
- [Android 端专项检查](#android-端专项检查)
- [H5 端专项检查](#h5-端专项检查)
- [通用 CSS 兼容性](#通用-css-兼容性)
- [API 兼容性高危清单](#api-兼容性高危清单)

---

## 版本适配层（必做）

### 为什么需要版本适配

uniapp 不同版本的 API 支持差异很大：
- 同一个 API 在旧版本可能有 bug，新版本修复了
- 有些 API 是新版本才新增的，旧版本根本没有
- uni-app x（蒸汽模式）和经典版 API 不通用
- 不同版本的平台支持矩阵不同

**不能凭印象判断 API 是否兼容，必须查版本发版说明验证。**

### 版本验证流程

**第一步：识别项目版本**
```bash
# 从 manifest.json 提取 uniapp 版本
grep -E "h5Version|app-plus|versionName" manifest.json

# 判断是经典版还是 uni-app x
grep -q "uni-app x" manifest.json && echo "uni-app x 蒸汽模式" || echo "经典 uniapp"
```

**第二步：批量提取项目中使用的 API**
```bash
# 提取所有 uni.* API 调用
grep -rohE "uni\.[a-zA-Z]+" pages/ components/ utils/ store/ | sort | uniq -c | sort -rn

# 提取 plus.* API（App 端专有）
grep -rohE "plus\.[a-zA-Z.]+ " pages/ components/ utils/ | sort | uniq -c | sort -rn
```

**第三步：调用 uniapp-release-notes 脚本验证**

脚本位于平行技能目录 `uniapp-release-notes/scripts/query_releasenotes.py`（与本技能同在 `.user_skills/` 下）。用绝对路径调用，例如：

```bash
python3 .user_skills/uniapp-release-notes/scripts/query_releasenotes.py search --keyword "API名称"
```

```bash
# 查询某 API 是否存在/何时新增
python3 query_releasenotes.py search --keyword "API名称" --type 新增

# 查询某 API 是否有已知 bug 修复
python3 query_releasenotes.py search --keyword "API名称" --type 修复

# 查询某 API 在特定平台的支持情况
python3 query_releasenotes.py search --keyword "API名称" --platform ios
python3 query_releasenotes.py search --keyword "API名称" --platform android
python3 query_releasenotes.py search --keyword "API名称" --platform web

# 区分经典版和 uni-app x
python3 query_releasenotes.py search --keyword "API名称" --module "uni-app"
python3 query_releasenotes.py search --keyword "API名称" --module "uni-app x"
```

### 版本判断规则

| 情况 | 严重程度 | 说明 |
|------|----------|------|
| API 在项目版本**之后**才新增 | 🔴 阻断级 | 当前版本根本没有这个 API，运行必报错 |
| API 在项目版本之后有**严重 bug 修复** | 🟠 严重级 | 当前版本有已知 bug，可能触发崩溃或异常 |
| API 在项目版本之后有**行为变更** | 🟡 一般级 | 行为不一致，可能有兼容性差异 |
| API 支持但**仅部分平台** | 🟡 一般级 | 需加条件编译或做降级处理 |
| API 在项目版本之后有**优化** | 🔵 优化建议 | 当前版本可用，但升级后体验更好 |

### 版本升级建议输出格式

```
API：uni.xxx
当前项目版本：5.10
发版说明显示：
- 5.15 版本新增（当前版本不支持）
- 5.20 版本修复了 Android 端崩溃问题
建议：升级到 5.20+，或降级使用旧版 API
```

---

## 平台判断与条件编译

### 正确用法
```vue
<!-- 条件编译注释 -->
<!-- #ifdef APP-PLUS -->
<view>仅 App 端显示</view>
<!-- #endif -->

<!-- #ifdef H5 -->
<view>仅 H5 端显示</view>
<!-- #endif -->

<!-- #ifdef MP-WEIXIN -->
<view>仅微信小程序显示</view>
<!-- #endif -->
```

### 常见问题扫描
- [ ] 搜索 `uni.getSystemInfoSync()` 使用，检查是否有硬编码平台判断
- [ ] 搜索 `#ifdef` / `#ifndef`，检查条件编译是否完整闭合（每个都要有对应 `#endif`）
- [ ] 搜索 `plus.` 开头的 API 使用，确认是否包在 `#ifdef APP-PLUS` 中
- [ ] 搜索 `window.` / `document.` 使用，确认是否包在 `#ifdef H5` 中
- [ ] 检查是否有混用 `uni.` API 和 `wx.` API 的情况

---

## iOS 端专项检查

### 安全区域与刘海屏
- [ ] 搜索 `safe-area-inset` 相关 CSS，检查是否适配
- [ ] 搜索 `padding-top: 44px` / `padding-bottom: 34px` 等硬编码安全区值
- [ ] 检查 iPhone X 及以上机型底部 Home 指示条是否被遮挡
- [ ] 检查顶部导航栏是否被刘海/灵动岛遮挡

**修复方案**：
```css
/* 底部安全区适配 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom); /* iOS < 11.2 */
  padding-bottom: env(safe-area-inset-bottom); /* iOS >= 11.2 */
}
```

### 滚动与橡皮筋效果
- [ ] 检查 H5 端是否禁用了 iOS 橡皮筋滚动（`bounce` 效果）
- [ ] 检查页面滚动是否有抖动
- [ ] 检查下拉刷新是否与页面滚动冲突

### 触摸与点击
- [ ] 搜索 `click` 事件使用，检查是否有 300ms 延迟问题
- [ ] 检查点击热区是否足够大（最小 44x44pt）
- [ ] 检查按钮触摸反馈是否正常
- [ ] 检查 `:active` 伪类在 iOS 上是否生效

### 字体与渲染
- [ ] 检查 `-webkit-font-smoothing` 字体渲染
- [ ] 检查 `1px` 边框在 Retina 屏上是否正常
- [ ] 检查 `backdrop-filter` 毛玻璃效果在 iOS 上的兼容性

---

## Android 端专项检查

### 物理返回键
- [ ] 搜索 `onBackPress` 生命周期使用
- [ ] 检查二级页面返回是否正确回到上一页
- [ ] 检查 tab 页按返回键是否退出应用
- [ ] 检查自定义导航栏返回按钮是否与物理返回键逻辑一致

**正确示例**：
```javascript
onBackPress(options) {
  // options.from = 'backbutton' 表示物理返回键
  if (this.showCustomPopup) {
    this.showCustomPopup = false
    return true // 阻止默认返回
  }
  // 其他情况默认返回
}
```

### 状态栏与沉浸效果
- [ ] 检查状态栏颜色与导航栏是否协调
- [ ] 检查状态栏文字颜色（深色/浅色）是否正确
- [ ] 沉浸式状态栏是否在不同 Android 版本上表现一致

### 屏幕适配
- [ ] 检查是否使用 `rpx` 单位（不要混用 px）
- [ ] 检查不同分辨率屏幕下布局是否错乱
- [ ] 检查折叠屏/平板适配情况
- [ ] 检查屏幕旋转时布局是否正常

### 权限处理
- [ ] 检查相机、相册、定位等权限申请时机
- [ ] 检查权限被拒绝后的引导逻辑
- [ ] 检查 Android 13+ 通知权限申请

---

## H5 端专项检查

### 路由与刷新
- [ ] 确认 `manifest.json` 中 H5 路由模式（hash / history）
- [ ] history 模式下部署是否配置了服务端重定向
- [ ] 刷新页面是否 404
- [ ] 浏览器前进/后退按钮是否正常

### 滚动与手势
- [ ] 检查是否禁用了 iOS 橡皮筋效果
- [ ] 检查下拉刷新在 H5 端是否正常
- [ ] 检查滚动穿透问题（弹窗打开时背景滚动）

### 性能与加载
- [ ] 检查首屏资源体积
- [ ] 检查是否做了路由懒加载
- [ ] 检查图片是否做了压缩和格式优化
- [ ] 检查是否有白屏加载时间过长问题

### 浏览器兼容
- [ ] 检查 `flex` 布局在旧版浏览器的兼容
- [ ] 检查 `css 变量` 兼容性
- [ ] 检查 `Promise` / `async/await` 语法兼容性
- [ ] 检查 `IntersectionObserver` 等 API 兼容性

---

## 通用 CSS 兼容性

### 高风险属性
| CSS 属性 | iOS 兼容 | Android 兼容 | H5 兼容 | 风险等级 |
|----------|----------|--------------|---------|----------|
| `backdrop-filter` | iOS 9+ 需前缀 | Android 12+ | Chrome 76+ | 中 |
| `position: sticky` | iOS 13+ | Android 9+ | Chrome 56+ | 低 |
| `gap` (flex) | iOS 14.5+ | Android 11+ | Chrome 84+ | 中 |
| `aspect-ratio` | iOS 15+ | Android 11+ | Chrome 88+ | 中 |
| `mask-image` | 需前缀 | 需前缀 | 需前缀 | 高 |
| `1px border` | Retina 需处理 | 正常 | 正常 | 高 |

### 扫描关键词
- 搜索 `backdrop-filter` — 检查是否做了降级
- 搜索 `position: sticky` — 检查是否有 fallback
- 搜索 `gap:` — 在 flex 布局中使用时注意兼容性
- 搜索 `aspect-ratio` — 注意低版本兼容
- 搜索 `box-shadow` — 检查是否过度使用导致性能问题

---

## API 兼容性高危清单

### 不跨端通用的 API
| API | App 支持 | H5 支持 | 风险 |
|-----|----------|---------|------|
| `plus.*` | ✅ | ❌ | 必须条件编译 |
| `uni.saveImageToPhotosAlbum` | ✅ | ⚠️ 部分支持 | 高 |
| `uni.scanCode` | ✅ | ⚠️ 需授权 | 高 |
| `uni.requestPayment` | ✅ | ⚠️ 不同平台不同 | 高 |
| `uni.getRecorderManager` | ✅ | ⚠️ 部分支持 | 高 |
| `uni.createInnerAudioContext` | ✅ | ✅ | 低 |
| `uni.vibrateLong` | ✅ | ❌ | 中 |

### 版本敏感 API（需查发版说明确认）

以下 API 在不同版本间有重大变更，**必须调用 uniapp-release-notes 脚本验证**：

| API 类别 | 常见问题 | 验证方法 |
|----------|----------|----------|
| `uni.request` / 网络请求 | 不同版本超时设置、错误码处理不同 | `search --keyword request --type 修复` |
| `uni.navigateTo` / 路由 | 不同版本路由参数传递、页面栈限制不同 | `search --keyword navigateTo` |
| `uni.getStorageSync` / 存储 | 不同版本存储大小限制、序列化方式不同 | `search --keyword storage` |
| `uni.onShow` / 生命周期 | 不同版本触发时机、参数不同 | `search --keyword onShow` |
| `uni.createVideoContext` / 媒体 | 不同版本 iOS/Android 表现差异大 | `search --keyword video --type 修复` |
| `uni.canvas` / 画布 | 不同版本渲染方式、API 变更 | `search --keyword canvas` |
| 暗黑模式 / 深色模式 | 不同版本支持程度不同 | `search --keyword 暗黑` |
| 安全区 / 刘海屏 | 不同版本适配方案不同 | `search --keyword 安全区` |

### 扫描方法
- 搜索 `plus.` — 确认是否都包在 App 条件编译中
- 搜索 `uni.scanCode` — 检查 H5 端降级方案
- 搜索 `uni.requestPayment` — 检查各端支付逻辑
- 搜索 `uni.saveImageToPhotosAlbum` — 检查权限处理
- 搜索 `uni.openLocation` — 检查地图 App 跳转
- **版本验证**：对所有提取出的 `uni.*` API，调用 query_releasenotes.py 查版本支持情况

---

## 问题严重程度定义

- 🔴 **阻断级**：导致白屏、崩溃、核心功能完全不可用
- 🟠 **严重级**：主要功能可用但体验明显受损，多数用户会遇到
- 🟡 **一般级**：边缘场景或小屏/低版本设备才会遇到
- 🔵 **优化建议**：锦上添花的体验提升
