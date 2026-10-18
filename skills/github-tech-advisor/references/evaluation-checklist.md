# 评估检查清单与参考模板

## 目录
- [技术栈扫描检查清单](#技术栈扫描检查清单)
- [开源方案评估评分表](#开源方案评估评分表)
- [GitHub 搜索关键词模板](#github-搜索关键词模板)
- [方案对比报告模板](#方案对比报告模板)

---

## 技术栈扫描检查清单

### 前端项目
- [ ] 包管理器：npm / pnpm / yarn / bun
- [ ] 框架版本：React 18+ / Vue 3 / Svelte / Angular
- [ ] 构建工具：Vite / Webpack / Rollup / Turbopack
- [ ] 路由：React Router / Vue Router / Next.js App Router
- [ ] 状态管理：Redux Toolkit / Pinia / Zustand / Jotai / MobX
- [ ] 数据请求：Axios / Fetch / SWR / React Query / tRPC
- [ ] UI 组件库：Ant Design / Element Plus / shadcn/ui / Naive UI / MUI
- [ ] 样式方案：Tailwind CSS / CSS Modules / Styled Components / Sass
- [ ] 类型检查：TypeScript 配置严格程度
- [ ] 测试框架：Vitest / Jest / Playwright / Cypress
- [ ] 代码规范：ESLint / Prettier 配置

### 后端项目
- [ ] 语言版本：Node.js / Python / Go / Java / Rust
- [ ] Web 框架：Express / Fastify / Koa / Django / FastAPI / Gin / Spring Boot
- [ ] 数据库：PostgreSQL / MySQL / MongoDB / Redis / SQLite
- [ ] ORM：Prisma / TypeORM / Sequelize / SQLAlchemy / GORM
- [ ] 认证：JWT / Session / OAuth / Passport
- [ ] 部署方式：Docker / Vercel / Netlify / 自托管

---

## 开源方案评估评分表

总分 100 分，60 分以下不推荐。

> 说明：**「视觉完成度」仅对 UI/设计类方案（组件库、设计系统、主题、模板）评分**；非 UI 类方案（纯工具库、状态管理、构建工具）不评视觉，其 25% 权重按比例并入维护度与兼容性。

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **视觉完成度**（UI 类必填） | 25% | - demo 界面成体系、默认主题开箱即好看、暗色模式完整：25分<br>- 默认主题尚可，少量定制即可用：18分<br>- 默认主题平庸，需 3-5 天主题定制：10分<br>- demo 界面混乱/无设计体系：0分 |
| **维护度** | 20% | - 最近 3 个月有提交：20分<br>- 最近 6 个月有提交：15分<br>- 最近 12 个月有提交：8分<br>- 超过 12 个月未更新：0分（直接排除） |
| **社区活跃度** | 15% | - Star > 10k 且周下载 > 10w：15分<br>- Star 5k-10k 且周下载 5w-10w：11分<br>- Star 1k-5k 且周下载 1w-5w：7分<br>- Star < 1k：3分 |
| **文档完善度** | 15% | - 官方文档齐全 + 示例丰富 + 中文文档：15分<br>- 官方文档齐全 + 有示例：11分<br>- 只有 README + 简单示例：6分<br>- 文档混乱/缺失：3分 |
| **兼容性** | 15% | - 完全兼容现有技术栈版本：15分<br>- 主要兼容，需少量适配：10分<br>- 有 breaking changes，需大量改造：5分<br>- 完全不兼容：0分 |
| **用户口碑** | 5% | - 主流技术博客/大V推荐：5分<br>- GitHub 评价整体正面：3分<br>- 褒贬不一：2分<br>- 负面评价较多：1分 |
| **安全性** | 5% | - 无已知安全 issue + 有安全审计：5分<br>- 无已知严重 issue：3分<br>- 有未修复的高危 issue：0分（直接排除） |

### UI 方案视觉走查清单（评分前逐项过）

- [ ] 打开在线 demo / Storybook / live preview，而非只看 README 截图
- [ ] 主色是否成体系（主/辅/中性色阶），有无品牌感
- [ ] 字阶是否有层级（标题/正文/辅助字重字号分明）
- [ ] 间距是否遵循 4/8px 栅格，留白是否统一
- [ ] 组件圆角/边框/阴影是否克制统一
- [ ] 暗色模式是否原生支持
- [ ] 默认主题开箱是否好看；若一般，估算主题定制工时（按 0.5/1/3/5 天档）
- [ ] 记录 demo 链接，写进对比表，禁止只给 GitHub 仓库

### 升级决策规则
- 总分 ≥ 85 且明显优于现有方案 → **强烈推荐**
- 总分 70-84 且有明确优势 → **可考虑升级**
- 总分 60-69 且优势不明显 → **不推荐**
- 总分 < 60 → **直接排除**
- 现有方案评分已 ≥ 80 → **原则上不建议更换**

---

## GitHub 搜索关键词模板

### 通用搜索语法
```
[关键词] stars:>1000 pushed:>2024-01-01 language:JavaScript
```

### 按技术栈分类搜索模板

**React 生态**
```
React component library stars:>5000 pushed:>2024-01-01
React state management 2025 stars:>1000
React UI framework stars:>10000
```

**Vue 生态**
```
Vue 3 component library stars:>3000 pushed:>2024-01-01
Vue UI framework stars:>5000
Vue 3 composable stars:>500
```

**构建工具**
```
JavaScript bundler stars:>2000 pushed:>2024-06-01
Frontend build tool comparison
```

**设计系统 / UI**
```
design system open source stars:>5000
Tailwind component library stars:>2000
shadcn/ui alternatives
```

### 热门榜单参考
- GitHub Trending: https://github.com/trending
- Awesome 列表: GitHub 搜索 `awesome-[topic]`
- npm Trends: https://npmtrends.com/

---

## 方案对比报告模板

```markdown
## 技术栈现状

| 类别 | 现有方案 | 版本 |
|------|----------|------|
| 框架 | | |
| UI 库 | | |
| 构建工具 | | |
| 状态管理 | | |

## 调研发现

### 候选方案 1：[名称]
- 地址：GitHub 链接
- **在线 demo / Storybook：链接**（UI 类必填）
- Star 数：XXk
- 最近更新：YYYY-MM-DD
- 周下载量：XXw
- 评分：XX/100
- **视觉走查**：主色/字阶/间距/组件质感/暗色模式/默认主题成熟度一句话结论
- **主题定制成本**：0 / 0.5 / 1 / 3 / 5 天
- 核心优势：
- 主要劣势：
- 迁移成本：人天估算

### 候选方案 2：[名称]
...

## 结论与建议

[推荐/不推荐升级的明确结论]
[理由：对比现有方案的量化优势]
[执行步骤清单]
[清理清单]
```
