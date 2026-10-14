# 各技术栈实现模式

## 目录
- [HTML + TailwindCSS](#html--tailwindcss)
- [Vue2 / Vue3](#vue2--vue3)
- [React](#react)
- [UniApp / UniApp X](#uniapp--uniapp-x)
- [小程序原生](#小程序原生)
- [Electron](#electron)

---

## HTML + TailwindCSS

### 设计变量配置（tailwind.config.js）
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',  // 主色
          600: '#2563eb',  // hover
          700: '#1d4ed8',  // active
        },
        gray: { /* 9级色阶 */ },
        danger: '#ef4444',
        success: '#10b981',
        warning: '#f59e0b',
      },
      spacing: {
        // 8px栅格体系（Tailwind默认已基于4px，可直接用）
        18: '4.5rem',  // 72px 特殊需求
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        full: '9999px',
      },
      fontSize: {
        h1: ['24px', { lineHeight: '32px', fontWeight: '600' }],
        h2: ['20px', { lineHeight: '28px', fontWeight: '600' }],
        h3: ['16px', { lineHeight: '24px', fontWeight: '500' }],
        body: ['14px', { lineHeight: '22px' }],
        caption: ['12px', { lineHeight: '18px' }],
      },
      boxShadow: {
        sm: '0 1px 3px rgba(0,0,0,0.08)',
        md: '0 4px 12px rgba(0,0,0,0.12)',
        lg: '0 8px 24px rgba(0,0,0,0.16)',
      },
    },
  },
}
```

### 组件示例：按钮
```html
<button class="px-4 h-10 rounded-md bg-primary-500 text-white text-body
               hover:bg-primary-600 active:bg-primary-700
               disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed
               transition-all duration-200">
  按钮文字
</button>
```

---

## Vue2 / Vue3

### 设计变量（CSS Variables）
```css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-active: #1d4ed8;
  --color-gray-50: #f9fafb;
  --color-gray-900: #111827;
  --space-4: 16px;
  --radius-md: 8px;
}
```

### Vue3 <script setup> 组件示例
```vue
<template>
  <button
    class="ui-btn"
    :class="[`ui-btn--${type}`, { 'is-disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <span v-if="loading" class="ui-btn__spinner" />
    <slot />
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'primary' }, // primary / secondary / text
  disabled: Boolean,
  loading: Boolean,
})
const emit = defineEmits(['click'])
const handleClick = (e) => {
  if (!props.disabled) emit('click', e)
}
</script>

<style scoped>
.ui-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
.ui-btn--primary {
  background: var(--color-primary);
  color: #fff;
}
.ui-btn--primary:hover { background: var(--color-primary-hover); }
.ui-btn--primary:active { background: var(--color-primary-active); }
.ui-btn.is-disabled {
  background: var(--color-gray-200);
  color: var(--color-gray-400);
  cursor: not-allowed;
}
</style>
```

---

## React

### 设计变量（与Vue共用CSS Variables）
```tsx
// Button.tsx
import React from 'react'
import './Button.css'

type ButtonProps = {
  type?: 'primary' | 'secondary' | 'text'
  disabled?: boolean
  loading?: boolean
  onClick?: (e: React.MouseEvent) => void
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  type = 'primary',
  disabled = false,
  loading = false,
  onClick,
  children,
}) => {
  return (
    <button
      className={`ui-btn ui-btn--${type} ${disabled ? 'is-disabled' : ''}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && <span className="ui-btn__spinner" />}
      {children}
    </button>
  )
}
```

---

## UniApp / UniApp X

### 适配要点
- 尺寸单位统一使用 `rpx`（750rpx = 屏幕宽度）
- 设计稿 375px 宽度时：1px = 2rpx
- 安全区适配：底部 `padding-bottom: env(safe-area-inset-bottom)`
- 可点击区域在 rpx 下约 96rpx（=48px @375屏宽）

### 设计变量（uni.scss）
```scss
$ui-color-primary: #3b82f6;
$ui-color-primary-hover: #2563eb;
$ui-color-danger: #ef4444;
$ui-color-success: #10b981;

$ui-space-xs: 8rpx;
$ui-space-sm: 16rpx;
$ui-space-md: 24rpx;
$ui-space-lg: 32rpx;
$ui-space-xl: 48rpx;

$ui-radius-sm: 8rpx;
$ui-radius-md: 16rpx;
$ui-radius-lg: 24rpx;
```

### 按钮组件示例（Vue3 + UniApp）
```vue
<template>
  <view class="ui-btn" :class="[`ui-btn--${type}`, { disabled }]" @tap="handleTap">
    <text>{{ text }}</text>
  </view>
</template>

<script setup>
defineProps({
  text: String,
  type: { type: String, default: 'primary' },
  disabled: Boolean,
})
const emit = defineEmits(['click'])
const handleTap = () => {
  if (!props.disabled) emit('click')
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.ui-btn {
  height: 88rpx; /* 44px @375 */
  padding: 0 $ui-space-lg;
  border-radius: $ui-radius-md;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 200ms;
}
.ui-btn--primary {
  background: $ui-color-primary;
  color: #fff;
}
.ui-btn--primary:active {
  opacity: 0.85;
}
.ui-btn.disabled {
  background: #f3f4f6;
  color: #9ca3af;
}
</style>
```

---

## 小程序原生

### 设计要点
- 尺寸单位：rpx（同UniApp）
- 样式写在 `.wxss` 文件中，支持 CSS 变量
- 组件使用自定义组件（Component构造器）
- 注意小程序不支持部分CSS选择器，避免嵌套过深

### app.wxss 全局变量
```css
page {
  --color-primary: #3b82f6;
  --color-gray-50: #f9fafb;
  --color-gray-900: #111827;
  --radius-md: 8px;
}
```

---

## Electron

### 设计要点
- 桌面端尺寸用 px，不用 rpx/vw 自适应
- 窗口最小宽度通常 800px，侧边栏可折叠
-  hover 状态必须有（鼠标精确操作）
- 滚动条样式自定义（美化系统默认滚动条）
- 支持窗口缩放响应式

### 桌面端特有规范
- 按钮高度：32px（紧凑工具栏）/ 36~40px（表单区）
- 表格行高：36~40px
- 侧边栏宽度：200~240px
- 右键菜单：必须支持，样式统一
