---
name: gsap-scroll-landing
description: "GSAP 滚动动画落地页生成器（带自动化脚本）。generate-landing.py 一键生成单文件 HTML 广告大片页面，5种配色模板，内置 Hero逐字入场+产品视差滚动+滚动淡入+移动端降级。validate-landing.py 验证技术约束。技术栈：Tailwind CSS CDN + GSAP 3.12.5 + ScrollTrigger，浏览器直接打开预览。Use when: ad landing page, 广告大片, brand landing page, scroll parallax, GSAP animation, VibeCoding, 视差落地页, 滚动动画, 产品宣传页, 网页动效, 落地页生成."
license: MIT
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: frontend
---

# GSAP Scroll Landing Page Generator v2.0

## Role

生成电影级滚动驱动的落地页，技术栈固定为 Tailwind CSS + GSAP + ScrollTrigger，单文件 HTML，浏览器直接打开预览。

**v2.0 升级**：内置 `generate-landing.py` 一键生成脚本和 `validate-landing.py` 验证脚本。

## 内置脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `scripts/generate-landing.py` | 一键生成完整落地页 HTML，5种配色模板 | `python3 generate-landing.py --title "产品名" --output landing.html` |
| `scripts/validate-landing.py` | 验证技术约束（GSAP引入、动画属性、移动端降级等） | `python3 validate-landing.py landing.html` |

**纯 Python 标准库，零依赖。**

## 快速使用

```bash
# 生成暗黑科技风格落地页
python3 scripts/generate-landing.py --title "我的产品" --subtitle "一句话描述" --template dark --output landing.html

# 生成活力渐变风格，自定义强调色
python3 scripts/generate-landing.py --title "我的产品" --template vibrant --accent "#ff6b6b" --output landing.html

# 自定义功能列表
python3 scripts/generate-landing.py --title "我的产品" --features "功能一" "功能二" "功能三" --output landing.html

# 验证生成的页面
python3 scripts/validate-landing.py landing.html

# 列出所有模板
python3 scripts/generate-landing.py --list-templates
```

## 5 种配色模板

| template | 名称 | 主色 | 适合 |
|---|---|---|---|
| `dark` | 暗黑科技 | #00ff88 | AI、科技产品、SaaS |
| `minimal` | 极简黑白 | #111111 | 方法论、咨询、高端品牌 |
| `vibrant` | 活力渐变 | #6366f1 | 消费产品、活动页 |
| `warm` | 温暖橙黄 | #f59e0b | 教育、生活方式 |
| `ocean` | 深海蓝 | #38bdf8 | 金融、企业服务 |

## 生成的页面包含

1. **Hero 首屏** — 逐字拆分入场动画（char split + stagger）
2. **产品展示层** — 多层视差滚动（不同 speed）
3. **功能特性** — 滚动淡入 + stagger 错位
4. **CTA 区域** — 滚动触发动画
5. **移动端降级** — `matchMedia` 自动降低动画强度

## 技术约束（脚本自动保证）

1. **技术栈固定**：HTML + Tailwind CSS + Vanilla JS + GSAP，不引入 Vue/React
2. **GSAP 版本**：3.12.5 CDN，必须引入 gsap.min.js + ScrollTrigger.min.js
3. **性能原则**：动画只操作 `transform` 和 `opacity`，禁止动画 `top/left/margin/padding`
4. **分层结构**：hero层、产品层、文字层、装饰层，分层做不同视差强度
5. **滚动动画**：全部基于 ScrollTrigger，平滑跟随用 `scrub: 1`
6. **单文件交付**：所有资源 CDN 引入，无本地依赖
7. **响应式**：`matchMedia` 做移动端降级

## validate-landing.py 检查项

| 检查项 | 严重度 |
|---|---|
| 引入 GSAP 库 | 必须 |
| 引入 ScrollTrigger 插件 | 必须 |
| 调用 registerPlugin | 必须 |
| 动画只操作 transform/opacity | 必须 |
| 有移动端降级（matchMedia） | 警告 |
| 无本地依赖（全CDN） | 警告 |
| 使用 ScrollTrigger 滚动动画 | 警告 |
| 有 DOCTYPE 声明 | 警告 |

## 工作流

1. 用户描述产品/页面需求
2. 运行 `generate-landing.py` 生成基础页面
3. 根据用户需求调整内容（文案、功能列表、配色）
4. 运行 `validate-landing.py` 验证技术约束
5. 浏览器打开预览，确认动画效果
6. 交付单文件 HTML

## References

- `scripts/generate-landing.py` — 落地页生成器（5种模板，Hero逐字+视差+滚动淡入+移动端降级）
- `scripts/validate-landing.py` — 技术约束验证器（9项检查，100分制）
