# uniapp 三端 UI/UX 审计检查清单

## 目录
- [设计系统一致性](#设计系统一致性)
- [三端样式差异（重点）](#三端样式差异重点)
- [iOS 端专项 UI 问题](#ios-端专项-ui-问题)
- [Android 端专项 UI 问题](#android-端专项-ui-问题)
- [H5 端专项 UI 问题](#h5-端专项-ui-问题)
- [uniapp 特有 UI 坑点](#uniapp-特有-ui-坑点)
- [扫描关键词速查表](#扫描关键词速查表)

---

## 设计系统一致性

### 扫描命令
```bash
# 检查 uni.scss 有没有定义设计变量
ls uni.scss && grep -E "\$|--" uni.scss | head -20

# 统计硬编码颜色值数量
grep -rohE "#[0-9a-fA-F]{3,6}" pages/ components/ | sort | uniq -c | sort -rn | head -20

# 统计硬编码字号
grep -rohE "font-size:\s*[0-9]+rpx" pages/ components/ | sort | uniq -c | sort -rn | head -20

# 统计硬编码间距
grep -rohE "(padding|margin):\s*[0-9]+rpx" pages/ components/ | sort | uniq -c | sort -rn | head -20
```

### 检查项
- [ ] 颜色值有没有统一管理（uni.scss 变量）
- [ ] 常用字号有没有统一规范（标题/正文/辅助文字）
- [ ] 常用间距有没有统一规范（16/24/32rpx 等）
- [ ] 圆角有没有统一规范（卡片/按钮/输入框）
- [ ] 阴影有没有统一样式
- [ ] 按钮样式有没有统一组件
- [ ] 卡片样式有没有统一规范
- [ ] 图标尺寸有没有统一标准

---

## 三端样式差异（重点）

### 常见差异点
| 问题 | iOS 表现 | Android 表现 | H5 表现 | 严重程度 |
|------|----------|-------------|---------|----------|
| 安全区适配 | 有刘海/灵动岛 | 状态栏高度不同 | 无安全区概念 | 🔴 高 |
| 导航栏样式 | 大标题/毛玻璃 | 普通工具栏 | 浏览器自带 | 🟠 中 |
| 滚动橡皮筋 | 有回弹 | 无回弹 | 有/无取决于设置 | 🟡 低 |
| 触摸反馈 | 柔和渐变 | 明显波纹 | 无/淡灰 | 🟠 中 |
| 字体渲染 | 苹方字体 | 思源黑体/系统默认 | 浏览器字体 | 🟡 低 |
| 键盘弹起 | 页面整体上推 | adjustResize 压缩 | 页面上推 | 🔴 高 |
| 1px 边框 | Retina 屏偏粗 | 正常 | 正常 | 🟠 中 |
| 阴影效果 | 渲染较好 | 渲染偏硬 | 正常 | 🟡 低 |

### 检查项
- [ ] 搜索 `#ifdef APP-PLUS` 样式块，检查三端样式分支是否合理
- [ ] 搜索 `#ifdef H5` 样式块，检查 H5 特有样式
- [ ] 有没有同一个组件在不同平台表现不一致的情况
- [ ] 导航栏样式三端是否统一（颜色、高度、按钮位置）
- [ ] tabBar 样式三端是否一致
- [ ] 弹窗位置三端是否一致（底部弹窗高度、圆角）
- [ ] Toast/Loading 样式三端是否一致

---

## iOS 端专项 UI 问题

### 安全区域适配
> iOS WKWebView 侧根因级规则见 ios-ui-ux-dev `references/audit-h5-source.md` H-SAFE-001/002（`viewport-fit=cover` + `env(safe-area-inset-*)`）；本清单只做三端差异对比。
- [ ] 顶部导航栏有没有适配刘海屏/灵动岛
- [ ] 底部 tabBar 有没有适配 Home 指示条
- [ ] 底部弹窗/操作栏有没有适配底部安全区
- [ ] 页面内容有没有被刘海遮挡

**修复代码**：
```css
/* 顶部安全区 */
.safe-area-top {
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

/* 底部安全区 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}
```

### 键盘与输入
> iOS 输入框聚焦自动放大、键盘顶起布局错乱的根因级规则见 ios-ui-ux-dev `audit-h5-source.md` H-INPUT-001 / H-TYPE-001 / H-VH-001。
- [ ] 输入框字号是否 ≥16px（防止 iOS 自动放大）
- [ ] 键盘弹起时输入框是否被遮挡
- [ ] 键盘弹起时页面是否合理上推
- [ ] 确认/取消按钮位置是否符合 iOS 习惯

**pages.json 配置**：
```json
{
  "path": "pages/chat/chat",
  "style": {
    "app-plus": {
      "softinputMode": "adjustPan"
    }
  }
}
```

### 滚动与手势
- [ ] 下拉刷新与页面滚动是否冲突
- [ ] 左滑返回手势是否正常
- [ ] 滚动到底部回弹效果是否自然
- [ ] 橡皮筋效果是否符合预期

### 触摸体验
- [ ] 点击热区是否 ≥44x44pt
- [ ] `:active` 状态是否生效（iOS 默认可能不生效）
- [ ] 长按菜单是否正常
- [ ] 双击缩放是否禁用（如不需要）

**修复代码**：
```css
/* 修复 iOS :active 不生效 */
* {
  -webkit-tap-highlight-color: transparent;
}
button:active, .btn:active {
  opacity: 0.7;
}
```

---

## Android 端专项 UI 问题

### 状态栏与沉浸
- [ ] 状态栏颜色是否与导航栏协调
- [ ] 状态栏文字颜色是否正确（深色/浅色）
- [ ] 沉浸式状态栏在不同 Android 版本表现是否一致
- [ ] 底部三大金刚键是否适配

### 触摸反馈
- [ ] 点击波纹效果是否符合 Android 规范
- [ ] 长按反馈是否明显
- [ ] 滚动惯性是否自然

### 屏幕适配
- [ ] 不同分辨率屏幕布局是否错乱
- [ ] 折叠屏/平板是否适配
- [ ] 屏幕旋转时布局是否正常
- [ ] 字号大小是否合适（Android 默认字体比 iOS 大）

---

## H5 端专项 UI 问题

### 视口与适配
> viewport meta / 页面缩放 / `100vh` 地址栏失效的根因级规则见 ios-ui-ux-dev `audit-h5-source.md` H-VIEWPORT-001 / H-VH-001。
- [ ] viewport 设置是否正确（`viewport-fit=cover`）
- [ ] `100vh` 是否替换为 `100%`（地址栏问题）
- [ ] 不同浏览器表现是否一致（Chrome/Safari/微信）
- [ ] 横屏竖屏切换是否正常

### 滚动与手势
- [ ] 是否禁用了橡皮筋效果（如不需要）
- [ ] 滚动穿透问题（弹窗打开时背景滚动）
- [ ] 下拉刷新是否与浏览器默认行为冲突
- [ ] 页面滚动位置是否记住

**修复代码**：
```css
/* 禁用橡皮筋效果 */
html, body {
  overscroll-behavior: none;
  position: fixed;
  width: 100%;
  height: 100%;
}

/* 滚动穿透修复 */
.modal-open {
  overflow: hidden;
}
```

### 路由与导航
- [ ] 浏览器前进/后退按钮是否正常
- [ ] 刷新页面是否 404（history 模式）
- [ ] 地址栏是否正确反映当前页面
- [ ] 分享链接是否能正确打开对应页面

---

## uniapp 特有 UI 坑点

### rpx 单位
- [ ] 是否所有尺寸都用 rpx（不要混用 px）
- [ ] 字号是否用 rpx（防止不同屏幕字号差异过大）
- [ ] 边框是否用 px（1px 边框用 rpx 会有 Retina 问题）

**正确做法**：
```css
/* 尺寸用 rpx */
.container {
  padding: 32rpx;
}

/* 边框用 px 或 0.5px */
.border {
  border: 1px solid #eee;
}
```

### 1px 边框问题
- [ ] Retina 屏下 1px 边框是否偏粗
- [ ] 有没有用 transform 缩放方案解决

**修复代码**：
```css
/* 1px 边框解决方案 */
.hairline-border {
  position: relative;
}
.hairline-border::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: #eee;
  transform: scaleY(0.5);
}
```

### 滚动穿透
- [ ] 弹窗打开时背景是否还能滚动
- [ ] 遮罩层点击是否正常关闭弹窗

### 固定定位偏移
> iOS 键盘弹起时 fixed 定位偏移的根因级规则见 ios-ui-ux-dev `audit-h5-source.md` H-VH-001。
- [ ] `position: fixed` 元素在键盘弹起时位置是否偏移
- [ ] 底部固定按钮在键盘弹起时是否被遮挡

---

## 扫描关键词速查表

| 问题类型 | 搜索关键词 | 说明 |
|----------|-----------|------|
| 安全区 | `safe-area-inset` | 检查是否适配 |
| 硬编码颜色 | `#[0-9a-fA-F]{6}` | 统计数量，看有没有统一管理 |
| 硬编码字号 | `font-size: [0-9]` | 看有没有统一规范 |
| px 混用 | `padding: [0-9]px` | 检查是否混用 px 和 rpx |
| 100vh | `100vh` | H5 端地址栏问题 |
| 条件编译样式 | `#ifdef.*style` | 检查三端样式分支 |
| 固定定位 | `position: fixed` | 检查键盘弹起问题 |
| 输入框字号 | `input.*font-size` | 检查是否 <16px |
| 阴影 | `box-shadow` | 检查是否过度使用 |
| 圆角 | `border-radius` | 检查是否统一规范 |

---

## 问题严重程度定义

- 🔴 **阻断级**：导致布局错乱、元素被遮挡、核心功能无法使用
- 🟠 **严重级**：三端表现明显不一致，多数用户能感知到
- 🟡 **一般级**：小瑕疵，不影响核心使用
- 🔵 **优化建议**：锦上添花的体验提升
