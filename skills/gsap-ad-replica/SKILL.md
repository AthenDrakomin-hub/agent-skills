---
name: gsap-ad-replica
label: GSAP广告大片复刻
description: "VibeCoding 风格网页广告大片复刻技能。使用 GSAP + ScrollTrigger 生成高级滚动驱动动画落地页，包含产品视差、逐字文字入场、流体循环特效、分段叙事滚动。适用于：广告大片复刻、品牌落地页、产品宣传页、滚动视差动画、VibeCoding 风格页面、网页动效开发、抖音视频转网页。当用户提到 VibeCoding、广告大片、GSAP 滚动动画、视差落地页、网页复刻、张鱼烧脑风格时触发。"
---

# VibeCoding GSAP 广告大片复刻

## 核心能力
生成单文件 HTML 广告大片页面，技术栈固定为 Tailwind CSS + GSAP + ScrollTrigger，所有资源 CDN 引入，浏览器直接打开即可预览。

## 技术约束（必须严格遵守）
1. **技术栈固定**：HTML + Tailwind CSS + Vanilla JS + GSAP，优先原生单文件页面，不引入 Vue/React/Next.js 等框架
2. **GSAP 引入**：必须引入 gsap.min.js 和 ScrollTrigger.min.js，版本使用 3.12.5 CDN
3. **性能原则**：动画只操作 `transform` 和 `opacity`，禁止动画 `top/left/margin/padding` 等触发重排的属性
4. **分层结构**：页面必须分层 —— hero 首屏层、产品层、文字层、装饰特效层，分层做不同视差强度
5. **文字动画**：默认采用逐字符拆分（char）+ stagger 错位入场，营造广告大片氛围感
6. **滚动动画**：全部基于 ScrollTrigger，平滑跟随滚动用 `scrub: 1`
7. **单文件交付**：输出完整单 HTML 文件，所有资源 CDN 引入，无本地依赖
8. **响应式**：移动端自动降低动画强度，`matchMedia` 做降级处理
9. **代码规范**：动画参数集中管理，附中文注释，方便微调

## CDN 引入模板（固定放在 head）
```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
```

## 内置动画模板库（按需选用）

### 模板1：产品滚动视差（广告大片核心）
产品元素随滚动产生位移和轻微旋转，营造景深效果。
```js
gsap.to(".product-item", {
  yPercent: -25,
  rotation: 3,
  ease: "none",
  scrollTrigger: {
    trigger: ".hero-wrap",
    start: "top top",
    end: "bottom top",
    scrub: 1
  }
});
```

### 模板2：逐字文字错位入场
将标题拆分为单个字符，逐个延迟入场。
```js
// 先拆分文字为 span.char
document.querySelectorAll(".ad-title").forEach(el => {
  el.innerHTML = el.textContent.split("").map(c => `<span class="char">${c}</span>`).join("");
});
// 再执行动画
gsap.from(".ad-title .char", {
  opacity: 0,
  y: 24,
  stagger: 0.06,
  duration: 0.9,
  ease: "power3.out",
  scrollTrigger: {
    trigger: ".ad-title",
    start: "top 80%"
  }
});
```

### 模板3：循环流体/气泡持续动画
装饰元素无限循环浮动，营造氛围。
```js
gsap.to(".liquid-effect", {
  xPercent: 12,
  duration: 2.2,
  repeat: -1,
  yoyo: true,
  ease: "sine.inOut"
});
```

### 模板4：分段内容渐显
滚动到视口时内容块淡入上浮。
```js
gsap.from(".section-block", {
  opacity: 0,
  y: 60,
  duration: 1,
  ease: "power2.out",
  scrollTrigger: {
    trigger: ".section-block",
    start: "top 75%"
  }
});
```

### 模板5：背景层慢速度视差（远景）
最底层背景滚动速度比内容慢，强化景深。
```js
gsap.to(".bg-layer", {
  yPercent: 15,
  ease: "none",
  scrollTrigger: {
    trigger: ".page-container",
    start: "top top",
    end: "bottom bottom",
    scrub: 0.5
  }
});
```

## 工作流程

### 步骤1：解析输入
根据用户提供的素材确定页面内容：
- **视频链接/截图**：提取画面结构、配色、产品形态、文字内容
- **文字描述**：提取产品类型、目标氛围、配色倾向
- **参考图**：识别构图、分层、主视觉元素

### 步骤2：规划页面结构
按广告大片叙事顺序规划分段：
1. Hero 首屏（大标题 + 产品主视觉 + 背景层）
2. 卖点分段（每段一个核心卖点 + 对应视觉）
3. 产品展示区（多角度/细节特写）
4. CTA 收尾段

### 步骤3：生成完整 HTML
直接输出完整单文件 HTML 代码，包含：
- head：CDN 引入 + 自定义 Tailwind 配置
- body：按分层结构编写 HTML
- script：GSAP 动画代码，注册 ScrollTrigger，执行各模板动画

### 步骤4：输出交付说明
代码输出后附简短说明：
1. 预览方式：浏览器直接打开
2. 可调整参数位置（视差强度、入场时长、缓动函数）
3. 移动端适配修改要点

## 移动端降级规则
使用 `gsap.matchMedia()` 或手动判断屏幕宽度：
- 屏幕宽度 < 768px 时，视差强度减半（yPercent 从 -25 改为 -12）
- 减少循环动画数量，只保留核心产品视差
- 文字 stagger 间隔缩小到 0.03，避免移动端卡顿

## 调优指南（附在输出末尾）
| 参数 | 位置 | 作用 |
|------|------|------|
| `yPercent` | gsap.to() 中 | 视差强度，数值越大移动越远 |
| `scrub` | scrollTrigger 中 | 滚动跟随平滑度，0 为立即跟随 |
| `stagger` | 文字动画中 | 字符入场间隔，单位秒 |
| `duration` | 动画参数中 | 单次动画时长，单位秒 |
| `ease` | 动画参数中 | 缓动函数，常用 power2.out / power3.out / sine.inOut |

## 参考资源
- `assets/beer-ad-demo.html`：啤酒广告大片完整示例，可直接打开预览效果，也可作为模板修改
