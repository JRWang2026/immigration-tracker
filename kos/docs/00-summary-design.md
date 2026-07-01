# KOS — Knowledge Operating System 概要设计

> 版本: V0.3-p1-done | 日期: 2026-06-03 | 作者: 王工 + 小助
>
> **定位**: 面向申博的个人研究平台 — 数据可视化 · 在线编程(浏览器跑Python) · 3D展示 · 知识管理
>
> **P1 部署**: `https://4656ece7af8e4d1eae1575f6f13d43bb.app.codebuddy.work`  
> **路由**: `/` = 中文首页，`/en/index.html` = 英文首页（CloudStudio SPA fallback 需显式路径）
>
> **域名规划**: `kos.studio` / `kos.dev`（备选） ｜ 当前部署: CloudStudio

---

## 1. 项目背景

### 1.1 需求来源

- 展示企业专利竞争情报分析成果（已产出词云、合作网络、趋势图）
- 展示 Python 数据处理能力（党费分析、专利分析脚本在线运行）
- 构建申博 Portfolio（CV + Research Proposal + 学术成果）
- 建立可扩展的个人知识管理平台（与 Obsidian 双向同步）

### 1.2 红线约束

| # | 约束 | 来源 |
|---|------|------|
| R1 | 所有工具/库优先选国外/国际产品 | 用户长期原则 |
| R2 | 数据永不丢失，本地 Markdown 为主 | 用户红线 |
| R3 | 最高标准、最严要求 | 本次需求 |
| R4 | 逐步完善，每阶段独立可交付 | 用户需求 |
| R5 | 网页形式，永久在线，随时点击查看 | 上次确认 |
| R6 | 敏感信息保密（单位英文缩写、不展示党内身份） | 2026-06-03 确认 |
| R7 | 一次到位，优先最高标准方案 | 本次确认 |

### 1.3 目标用户

| 用户 | 场景 | 关注点 |
|------|------|--------|
| 德国高校教授 | 审核博士申请 | CV、Research Proposal、技术能力 |
| 高雄老师 | 指导学术方向 | AI 工具应用、竞争情报方法 |
| 王工本人 | 日常知识管理 | 快速查阅、笔记沉淀 |
| 潜在合作者 | 了解研究方向 | 可视化成果、代码能力 |

### 1.4 关键决策记录（V0.2 确认）

| 决策点 | 方案 | 日期 |
|--------|------|------|
| 平台名称 | **KOS** (Knowledge Operating System) | 2026-06-03 |
| 代码实验室 | **Pyodide + Sandpack，一次到位**（浏览器内跑 Python） | 2026-06-03 |
| 首页证书展示 | 6 卡片布局 + `public/certs/` 上传空间预留 | 2026-06-03 |
| 敏感信息 | 单位用 SLBY，不展示党内身份 | 2026-06-03 |
| 双语 | 中/英路由 `/zh/` `/en/` | 2026-06-03 |

---

## 2. 系统架构

```
┌─────────────────────────────────────────────┐
│              部署层: CloudStudio              │
│         静态站点 (Next.js static export)       │
├─────────────────────────────────────────────┤
│              渲染引擎层                        │
│  React 18 │ D3.js │ Three.js │ Excalidraw   │
├─────────────────────────────────────────────┤
│              应用模块层 (六大模块)              │
│  ┌──────┐ ┌──────┐ ┌──────┐                │
│  │专利  │ │代码  │ │ 3D  │                │
│  │分析  │ │实验  │ │展示  │                │
│  └──────┘ └──────┘ └──────┘                │
│  ┌──────┐ ┌──────┐ ┌──────┐                │
│  │研究  │ │知识  │ │绘图  │                │
│  │页面  │ │图谱  │ │画板  │                │
│  └──────┘ └──────┘ └──────┘                │
├─────────────────────────────────────────────┤
│              数据层: JSON / Markdown          │
│     专利数据 · 项目配置 · 研究笔记               │
│     ↔ Obsidian 知识库双向兼容                  │
└─────────────────────────────────────────────┘
```

---

## 3. 技术选型一览

| 层级 | 选择 | 版本 | 判定依据 |
|------|------|------|---------|
| 框架 | Next.js | 16.x (App Router) | 国际学术圈主流，静态导出原生支持 |
| 语言 | TypeScript | 5.x | 类型安全，工程底线 |
| 样式 | 纯 CSS（手写） | — | Tailwind 4 因 Turbopack PostCSS 沙箱兼容问题放弃 |
| 图表 | D3.js | 7.x | 全球顶级期刊标配，非 ECharts |
| 3D | Three.js | r170+ | WebGL 事实标准 |
| 在线代码 | Sandpack | 2.x | CodeSandbox 团队出品 |
| 绘图 | Excalidraw | npm 包 | 开源，数据本地 JSON |
| 部署 | CloudStudio | — | 墙内稳定，已跑通 |

---

## 4. 模块功能规格（概要）

### M1 — 首页 (Landing)

| 属性 | 说明 |
|------|------|
| 路径 | `/` 或 `/zh/`（中文），`/en/`（英文） |
| 内容 | 5 个区域：Hero 区 → 专利成果快照 → 能力证书 → 研究方向 → 项目展示 |
| 技术 | React Server Component + 静态渲染 + D3.js 雷达图 |
| 交互 | 打字机效果标题、证书图片上传空间（P1 占位/P2 启用）、成果卡片跳转 |

**证书展示区设计**：

| 卡片 | 内容 | 备注 |
|------|------|------|
| 教育背景 | 中国石油大学(华东) 学士 · 机械设计制造及自动化 / ISTIC 信息资源管理 硕士在读(均分86+) | 学位证图片预留 |
| 语言能力 | CET-4(66) / CET-6(66) / 雅思备考中 | 成绩单图片预留 |
| 专业资格 | 质量工程师(中级) / 制图员(中级) | 证书图片预留 |
| 技能证书 | 汽车修理(中级) / 驾驶证 A2 | 证书图片预留 |
| 荣誉奖项 | 石油大学三好学生 | 证书图片预留 |
| 其他能力 | 5 项专利 · Python 开发 · 竞争情报分析 | 专利证书图片预留 |

图片存放: `public/certs/` → P1 仅占位 UI，P2 实现上传功能。

### M2 — 专利分析 (Patent Lab)

| 属性 | 说明 |
|------|------|
| 路径 | `/patent` |
| 子页 | 词云 `/patent/wordcloud`、网络 `/patent/network`、趋势 `/patent/trend` |
| 数据 | `data/patents.json` (从万方 txt 解析) |
| 交互 | 悬停高亮、节点拖拽 (力导向图)、年份筛选 |
| 技术 | D3.js force simulation + wordcloud2.js |
| 证书展示 | 发明专利（2件）独占首行，实用新型（3件）第二行三等分，每行带类型标签 |

### M3 — 代码实验室 (Code Lab)

| 属性 | 说明 |
|------|------|
| 路径 | `/code` |
| 内容 | 党费分析脚本、专利分析脚本、浏览器内在线编辑+运行 |
| 技术 | Sandpack + Pyodide（Python 3.12 WASM 运行时，~3MB 预加载） |
| 交互 | Monaco Editor 代码编辑、一键 Run、输出面板、Loading 进度条 |
| 文件 | `data/code-samples/` 预置示例脚本 |

**一次到位方案**：跳过静态展示阶段，直接接入 Pyodide。
- 首次加载：显示「Loading Python Runtime...」进度条（~5s 3G）
- 后续页面切换：Service Worker 缓存 wasm，秒开

### M4 — 3D 展示 (3D Viewer) → 研究方向：学术可视化

| 属性 | 说明 |
|------|------|
| 路径 | `/3d` |
| 定位 | **学术研究可视化**（非 CAD 作品集），以数据驱动的 3D 图表展示研究能力 |
| 内容 | ① 专利聚类 3D 散点图（技术主题分布） ② 竞争情报时序曲面（技术路线演进） ③ 论文关键词共现 3D 网络 |
| 技术 | Three.js + OrbitControls + D3.js 数据绑定 → 3D 渲染 |
| 交互 | 旋转、缩放、悬停详情、时间轴拖拽、聚类切换 |
| 数据来源 | `data/patents.json` ← Python 解析脚本提取向量/关键词/年份 |

> **2026-06-07 决策（最终）**：原 SW 实体模型方案取消。原因：(1) 练习级零件无法展示研究深度；(2) 学术可视化对申博说服力远超 CAD 作品集；(3) 纯数据驱动，无需依赖 SW 导出流程，开发更可控。

### M5 — 研究页面 (Research)

| 属性 | 说明 |
|------|------|
| 路径 | `/research` |
| 子页 | CV `/research/cv`、Proposal `/research/proposal`、论文 `/research/papers` |
| 内容 | 个人简历、博士研究计划、已发表/在写论文 |
| 技术 | Markdown 渲染 (react-markdown) |

### M6 — 知识图谱 (Knowledge Graph)

| 属性 | 说明 |
|------|------|
| 路径 | `/knowledge` |
| 内容 | AI 概念图谱、竞争情报方法图谱、专利-论文关联图 |
| 技术 | D3.js force graph + 节点过滤 |

### M7 — 绘图画板 (Draw)

| 属性 | 说明 |
|------|------|
| 路径 | `/draw` |
| 内容 | 自由绘图、流程图、架构图 |
| 技术 | Excalidraw 嵌入组件 |
| 数据 | 本地 JSON 存储 |

### M8 — AI 辅助设计探索 (AI Design Explorer) 🆕

| 属性 | 说明 |
|------|------|
| 路径 | `/design` |
| 定位 | 展示 AI + 机械工程交叉实战能力，独一无二的申博卖点 |
| 内容 | ① SW 2025 AI 生成式设计结果对比（原始 vs 优化）② 设计约束与迭代日志 ③ AI 工具在工程中的角色反思 |
| 技术 | Three.js 并排对比渲染 + 迭代参数折线图 (ECharts) |
| 交互 | 模型旋转缩放同步、迭代步骤滑块、设计约束切换 |
| 前提 | 需要用户用 SW 2025 AI 生成素材（模型 + 参数日志） |

### M9 — 互动研究提案 (Interactive Proposal) 🆕

| 属性 | 说明 |
|------|------|
| 路径 | `/research/proposal`（扩展） |
| 定位 | 替代静态 PDF，教授无需下载即可评估研究思路 |
| 内容 | 可折叠 IMRD 卡片（Introduction / Methods / Results / Discussion），每卡片一段英文 + 一张图 |
| 技术 | React 折叠面板 + 图表内嵌（ECharts / Mermaid） |
| 交互 | 点击展开/折叠、引用 DOI 跳转、图表悬停详情 |

### M10 — 专利技术路线图 (Tech Roadmap) 🆕

| 属性 | 说明 |
|------|------|
| 路径 | `/patent/roadmap` |
| 定位 | 展示技术演进脉络，证明你理解所在领域的发展方向 |
| 内容 | 桑基图（技术分类流向）+ 时间轴（专利 ↔ 论文时间对应） |
| 技术 | D3.js Sankey / ECharts Sankey |
| 数据 | `data/patents.json` IPC 分类字段 + 年份 |

---

## 5. 路由设计

```
/                          重定向到 /zh/
/zh/                       中文首页 Landing
/en/                       英文首页 Landing
├── /zh/patent             专利分析
│   ├── /zh/patent/wordcloud 交互词云
│   ├── /zh/patent/network   合作网络
│   ├── /zh/patent/trend     年度趋势
│   └── /zh/patent/roadmap   技术路线图 🆕
├── /zh/code               代码实验室
├── /zh/3d                 3D 学术可视化
├── /zh/design             AI 设计探索 🆕
├── /zh/research           研究页面
│   ├── /zh/research/cv    简历（打印友好）
│   └── /zh/research/proposal 互动研究提案 🆕
├── /zh/knowledge          知识图谱
└── /zh/draw               绘图画板
```

---

## 6. 数据流设计

```
/                          重定向到 /zh/
/zh/                       中文首页 Landing
/en/                       英文首页 Landing
├── /zh/patent             专利分析
│   ├── /zh/patent/wordcloud 交互词云
│   ├── /zh/patent/network   合作网络
│   └── /zh/patent/trend     年度趋势
├── /zh/code               代码实验室
├── /zh/3d                 3D 展示
├── /zh/research           研究页面
│   ├── /zh/research/cv    简历（打印友好）
│   └── /zh/research/proposal 研究计划
├── /zh/knowledge          知识图谱
└── /zh/draw               绘图画板
```

---

## 6. 数据流设计

```
万方导出 (.txt)
    │
    ▼
Python 解析脚本 (patent_parser.py)
    │
    ▼
data/patents.json ─────────────────┐
data/inventors.json                │
data/tech_keywords.json            │
    │                              │
    ▼                              ▼
React 组件 ←── D3.js ←── JSON ←── Markdown
    │
    ▼
Next.js static export
    │
    ▼
CloudStudio 部署

同步方向: Obsidian ←Git→ GitHub ←→ KOS 数据层
```

---

## 7. 目录结构

```
kos/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # 根布局 (侧边栏 + 顶部导航)
│   ├── page.tsx            # 首页
│   ├── patent/
│   │   ├── page.tsx
│   │   ├── wordcloud/page.tsx
│   │   ├── network/page.tsx
│   │   └── trend/page.tsx
│   ├── code/page.tsx
│   ├── 3d/page.tsx
│   ├── research/
│   │   ├── page.tsx
│   │   ├── cv/page.tsx
│   │   └── proposal/page.tsx
│   ├── knowledge/page.tsx
│   └── draw/page.tsx
├── components/             # 可复用组件
│   ├── layout/             # Sidebar, Navbar, Footer
│   ├── charts/             # D3.js 图表组件
│   ├── three/              # Three.js 3D 组件
│   └── ui/                 # 通用 UI 组件
├── data/                   # 静态数据
│   ├── patents.json
│   ├── profile.json        # 个人资料
│   └── research.json       # 研究成果
├── lib/                    # 工具函数
│   ├── patent-parser.ts    # 专利数据解析
│   └── types.ts            # TypeScript 类型定义
├── public/                 # 静态资源
│   └── images/
├── docs/                   # 设计文档
│   ├── 00-summary-design.md
│   └── 01-detailed-design.md
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 8. 开发环境

| 项目 | 值 |
|------|-----|
| Node.js | 22.12.0 (managed) |
| 包管理 | npm (使用工作区隔离路径) |
| IDE | VS Code / Codex |
| 版本控制 | Git + GitHub 私有仓库 |
| 部署 | CloudStudio (静态导出) |

---

## 9. 质量保证

### 代码规范
- ESLint + Prettier (Next.js 默认配置)
- TypeScript strict mode
- 组件命名: PascalCase, 文件命名: kebab-case

### 性能指标
- Lighthouse Performance ≥ 90
- 首屏加载 < 2s (3G)
- 所有图表组件支持懒加载

### 兼容性
- Chrome / Firefox / Safari 最新两个版本
- 响应式: Desktop 优先，Mobile 可用

---

## 10. 迭代计划摘要

| 阶段 | 版本 | 交付物 | 预计日期 |
|------|------|--------|---------|
| P1 | V0.1 | 项目骨架 + 首页（含证书区）+ 双语路由 + 部署 | ✅ 完成 2026-06-03 |
| P2 | V0.2 | 专利可视化交互（D3.js 词云+网络图+图表+明细表） | ✅ 完成 2026-06-03 |
| P3 | V0.3 | 研究页（CV+互动式Proposal）+ 3D 学术可视化（专利聚类/关键词共现）+ 知识图谱 + AI 设计探索 | 第三周 |
| P4 | V1.0 | 专利技术路线图 + 绘图画板 + 多语言完善 + 打印友善 CV + 正式版 | 第四周 |

---

## 11. 风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|------|------|------|
| Sandpack Pyodide 性能差 | 中 | 代码运行慢 | 预加载 + 降级为静态代码展示 |
| Three.js 3D 可视化开发 | 低 | P3 可交付 | 纯数据驱动，无需依赖外部 3D 模型，JS 直接生成几何体 |
| CloudStudio 构建超时 | 低 | 部署失败 | 本地 pre-build 验证 |
| 万方数据扩展后解析规则失效 | 中 | 数据错误 | 解析器加容错 + 单元测试 |
