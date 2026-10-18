# uniapp 游戏项目 UI 专项检查清单

## 目录
- [全屏沉浸与方向锁定](#全屏沉浸与方向锁定)
- [Canvas/WebGL 渲染](#canvaswebgl-渲染)
- [游戏 UI 布局适配](#游戏-ui-布局适配)
- [触摸与手势交互](#触摸与手势交互)
- [游戏页面类型检查](#游戏页面类型检查)
- [性能与帧率](#性能与帧率)

---

## 全屏沉浸与方向锁定

### 配置检查
```bash
# 检查 manifest.json 屏幕方向配置
grep -E "orientation|screenOrientation" manifest.json

# 检查游戏页是否隐藏导航栏
grep -E "titleNView|navigationStyle" pages.json
```

### 检查项
- [ ] 游戏主页面是否锁定横屏/竖屏
- [ ] 游戏页是否隐藏系统状态栏
- [ ] 游戏页是否隐藏底部导航栏（Android 三大金刚键）
- [ ] 游戏页是否隐藏顶部导航栏
- [ ] 屏幕旋转时游戏画面是否自动适配

### manifest.json 配置示例
```json
{
  "app-plus": {
    "screenOrientation": ["landscape-primary", "landscape-secondary"]
  }
}
```

### pages.json 配置示例
```json
{
  "path": "pages/game/main",
  "style": {
    "navigationStyle": "custom",
    "app-plus": {
      "titleNView": false,
      "fullscreen": true
    }
  }
}
```

---

## Canvas/WebGL 渲染

### 三端差异
| 问题 | iOS | Android | H5 |
|------|-----|---------|-----|
| Canvas 分辨率 | Retina 屏模糊 | 清晰 | 视口缩放 |
| 帧率 | 60fps 稳定 | 低端机掉帧 | 取决于浏览器 |
| 触摸事件延迟 | 低 | 中 | 高 |
| WebGL 支持 | Metal 加速 | OpenGL ES | WebGL 1/2 |

### 检查项
- [ ] Canvas 尺寸是否根据设备像素比（dpr）缩放
- [ ] Canvas 分辨率是否适配 Retina 屏
- [ ] 游戏元素是否在安全区域内显示
- [ ] 不同分辨率屏幕下游戏画面是否拉伸/变形
- [ ] 横竖屏切换时 Canvas 是否重新绘制

### 高清屏适配代码
```javascript
// 获取设备像素比
const dpr = uni.getSystemInfoSync().pixelRatio
// Canvas 宽度 = CSS 宽度 * dpr
canvas.width = canvasCssWidth * dpr
canvas.height = canvasCssHeight * dpr
ctx.scale(dpr, dpr)
```

---

## 游戏 UI 布局适配

### 安全区
- [ ] 游戏 UI 元素是否避开刘海屏/灵动岛
- [ ] 底部按钮是否避开 Home 指示条（iOS）
- [ ] 顶部 HUD（血条/分数）是否在安全区内
- [ ] 虚拟按键是否避开底部导航栏（Android）

### 不同分辨率适配
- [ ] 游戏 UI 是否使用百分比/弹性布局
- [ ] 不同比例屏幕（16:9 / 18:9 / 20:9）下 UI 是否正常
- [ ] 平板/折叠屏下游戏画面是否拉伸
- [ ] 宽屏手机两侧是否有黑边或元素溢出

### 设计稿适配
```bash
# 检查设计稿宽度
grep -E "designWidth|750" manifest.json

# 检查是否混用 px 和 rpx
grep -rohE "padding: [0-9]+px" pages/game/ | head -10
```

---

## 触摸与手势交互

### 触摸响应
- [ ] 虚拟按键触摸热区是否 ≥44x44pt
- [ ] 触摸事件是否有 300ms 延迟
- [ ] 多点触控是否支持（双指缩放/旋转）
- [ ] 快速点击是否有去抖
- [ ] 触摸结束后是否重置状态

### 手势操作
- [ ] 滑动手势灵敏度是否合适
- [ ] 捏合缩放是否流畅
- [ ] 长按是否有触发反馈
- [ ] 手势和页面滚动是否冲突

### 触摸事件对比
| 事件 | iOS | Android | H5 |
|------|-----|---------|-----|
| touchstart | 即时 | 即时 | 有延迟 |
| touchend | 即时 | 即时 | 有延迟 |
| click | 300ms | 300ms | 300ms |
| pointerdown | 支持 | 支持 | 支持 |

---

## 游戏页面类型检查

### 加载页
- [ ] 加载进度条样式
- [ ] 加载动画是否流畅
- [ ] 资源预加载是否完成
- [ ] 加载失败重试机制

### 主游戏页
- [ ] HUD 显示（分数/血量/时间）
- [ ] 暂停按钮位置
- [ ] 设置按钮位置
- [ ] 游戏开始/结束过渡

### 结算页
- [ ] 得分统计动画
- [ ] 重新开始按钮
- [ ] 返回主页按钮
- [ ] 分享/排行榜入口

### 设置页
- [ ] 音乐开关
- [ ] 音效开关
- [ ] 振动开关
- [ ] 账号/用户信息

---

## 性能与帧率

### 检查项
- [ ] 游戏主循环是否使用 `requestAnimationFrame`
- [ ] 是否避免在 `render` 里做大量计算
- [ ] 图片资源是否压缩到合理大小
- [ ] 内存泄漏（页面切换后游戏循环是否停止）
- [ ] 低端机是否有性能模式

### 常见性能坑
- [ ] 频繁操作 DOM 导致掉帧
- [ ] 图片资源太大导致内存过高
- [ ] 定时器未清除导致后台耗电
- [ ] Canvas 尺寸过大导致渲染慢

### 快速扫描
```bash
# 检查是否有游戏循环
grep -rn "requestAnimationFrame\|setInterval.*game" pages/game/ --include="*.vue"

# 检查定时器清理
grep -rn "setInterval\|setTimeout" pages/game/ --include="*.vue"

# 检查 Canvas 使用
grep -rn "canvas\|createCanvasContext" pages/game/ --include="*.vue" -l
```

---

## 游戏 UI 常见问题

### 横屏特有问题
- [ ] 横屏下状态栏是否隐藏
- [ ] 横屏下输入法是否正常弹出
- [ ] 横屏下安全区计算是否正确
- [ ] 横屏下返回键逻辑是否正常

### 虚拟按键
- [ ] 虚拟摇杆位置是否合适
- [ ] 虚拟按键是否可自定义位置
- [ ] 按键按下反馈是否明显
- [ ] 按键大小是否适合手指操作

### 弹窗样式
- [ ] 暂停弹窗位置是否居中
- [ ] 弹窗是否有半透明遮罩
- [ ] 弹窗按钮大小和位置
- [ ] 弹窗是否阻断游戏循环
