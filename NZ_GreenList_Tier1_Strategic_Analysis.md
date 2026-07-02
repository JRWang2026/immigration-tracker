# 新西兰绿名单 Tier1 ICT 岗位：深度战略分析与行动方案

> 2026-07-02 | 基于官方 INZ Green List + 10 天 SEEK 扫描数据 + 用户背景匹配评估

---

## 一、核心发现：绿名单 ICT Tier1 完整清单（官方核实）

经过查证 INZ 官方资料及 jack-liu.com（引用 INZ 原始数据，更新至 2026-01），**绿名单 Tier1 ICT 完整清单如下**：

| # | ANZSCO | 职业名称 | 最低薪资门槛 | 合同制（离岸申请）额外要求 |
|---|--------|----------|-------------|---------------------------|
| 1 | 135111 | Chief Information Officer (CIO) | $69.80/hr（≈$145,184/yr） | $104.71/hr + 10年经验 |
| 2 | 135112 | ICT Project Manager | 中位数工资 $35/hr | 无额外 |
| 3 | 135199 | ICT Managers nec | 中位数工资 $35/hr | 无额外 |
| 4 | 261311 | Analyst Programmer | 中位数工资 $35/hr | 无额外 |
| 5 | 261312 | Developer Programmer | 中位数工资 $35/hr | 无额外 |
| 6 | 261313 | Software Engineer | 中位数工资 $35/hr | 无额外 |
| 7 | 261314 | Software Tester | 中位数工资 $35/hr | 无额外 |
| 8 | 262112 | ICT Security Specialist | 中位数工资 $35/hr | 无额外 |
| 9 | 261399 | Software and Applications Programmers nec | 中位数工资 $35/hr | 无额外 |
| 10 | **262111** | **Database Administrator** | **$67.12/hr（≈$139,610/yr）** | **$83.90/hr + 10年经验** |
| 11 | 262113 | Systems Administrator | 中位数工资 $35/hr | 无额外 |
| 12 | 261211 | Multimedia Specialist | $67.12/hr（≈$139,610/yr） | $83.90/hr + 10年经验 |

**关键纠正**：
- **Data Scientist 不在绿名单上**（部分非官方来源错误将其列为 Tier1）
- **DBA 确实是 Tier1**（部分来源错误将其列为 Tier2），但有 **$67.12/hr 的最低薪资门槛**，远高于中位数工资 $35/hr
- **Software Engineer / Analyst Programmer / Developer Programmer 均为 Tier1**，且只需要中位数工资 $35/hr
- Tier2 ICT 只有一个岗位：Telecommunications Technician (342414)

---

## 二、10 天 SEEK 扫描数据回顾（6/23 - 7/2）

| 日期 | Tier1 高匹配岗位 | 数量 |
|------|-----------------|------|
| 6/23 | ICT Business Analyst (映射261111) | 1-2 |
| 6/24 | Mechanical Engineer (Windcave, 95分) | 1 |
| 6/25-26 | 无 Tier1 ICT | 0 |
| 6/27-30 | **BOEI DBA ($69-72/hr)** | 1 |
| 7/1 | BOEI DBA 消失 | 0 |
| 7/2 | **Securitek Systems Admin ($40-48/hr)** | 1 |

**数据洞察**：
1. 10 天内仅出现 2 个真正的 Tier1 ICT 岗位（DBA + SysAdmin），平均每周不到 1.5 个
2. BOEI DBA 存活仅 4 天（6/27-6/30），说明合同制岗位流动性极高
3. 所有 Tier1 岗位都在 Auckland
4. Software Engineer / Analyst Programmer / Developer Programmer **从未在 SEEK 邮件推送中出现**

---

## 三、用户背景 vs 每个 Tier1 岗位的匹配评估

### 评分标准
- **直接经验**：有可验证的职业经历（20分）
- **可迁移技能**：有可包装的技能但不直接对口（10分）
- **薪资门槛**：岗位薪资达标（10分）
- **学历匹配**：学位方向对口（5分）
- **离岸可行性**：雇主是否可能从海外招聘（15分）

| Tier1 岗位 | 直接经验 | 可迁移技能 | 薪资门槛 | 学历匹配 | 离岸可行 | **总分** | **评估** |
|------------|---------|-----------|---------|---------|---------|---------|---------|
| DBA (262111) | 0 | 10 (SQL/ERP) | 5 ($67.12/hr门槛高) | 3 | 5 | **23/60** | ⚠️ 低 |
| Software Engineer (261313) | 0 | 12 (Python) | 8 ($35/hr门槛低) | 4 | 8 | **32/60** | 🟡 中 |
| Analyst Programmer (261311) | 0 | 12 (Python+SQL) | 8 | 4 | 8 | **32/60** | 🟡 中 |
| Developer Programmer (261312) | 0 | 12 (Python) | 8 | 4 | 8 | **32/60** | 🟡 中 |
| Systems Administrator (262113) | 0 | 5 (ERP用户) | 8 ($35/hr) | 2 | 5 | **20/60** | ⚠️ 低 |
| ICT Project Manager (135112) | 5 (党务项目) | 8 | 8 | 3 | 5 | **29/60** | 🟡 中低 |
| ICT Security Specialist (262112) | 0 | 2 | 8 | 2 | 3 | **15/60** | ❌ 极低 |
| CIO (135111) | 0 | 3 | 0 ($69.80/hr极高) | 2 | 2 | **7/60** | ❌ 不可行 |

### 核心结论

**DBA 并非用户最佳 Tier1 目标。** 原因：

1. **薪资门槛最高之一**：$67.12/hr（≈$139,610/yr），BOEI 的 $69-72/hr 勉强达标，但绝大多数 DBA 岗位薪资在 $90,000-120,000 区间，达不到门槛
2. **合同制离岸申请要 $83.90/hr + 10年经验**：用户没有 10 年 DBA 经验，合同制路径直接堵死
3. **用户无直接 DBA 经验**：ERP 数据维护 ≠ 数据库管理，面试时会被拆穿
4. **岗位极度稀缺**：10 天只出现 1 个，存活 4 天

**Software Engineer / Analyst Programmer / Developer Programmer 才是更优目标。** 原因：

1. **薪资门槛仅 $35/hr**（中位数工资），大量岗位达标
2. **Python 技能可迁移**：用户的 Python 数据分析能力可以包装为编程能力
3. **GitHub 作品集可弥补经验缺口**：代码就是简历，新西兰雇主确实看 GitHub
4. **岗位数量远多于 DBA**：虽然 SEEK 邮件推送未捕获到，但 SEEK 网站上 Python/Software Developer 岗位长期大量存在（推送关键词未覆盖）
5. **不需要 10 年经验**：没有合同制的额外经验要求

---

## 四、策略重构：从"追单个岗位"到"能力建设+广撒网"

### 旧策略（已失效）
```
等 SEEK 邮件推送 → 发现 Tier1 岗位 → 突击准备 → 投递
```
**问题**：10 天只出 2 个岗位，等到时岗位已经关闭；即使出现也竞争不过本地候选人。

### 新策略：三层漏斗
```
第一层：能力建设（2-3周，一次性投入）
  → 英文 CV + GitHub Portfolio + PTE 58
第二层：主动搜索（持续，每天10分钟）
  → 直接在 SEEK 网站搜索 Software Engineer / Analyst Programmer
  → 不依赖邮件推送（推送关键词覆盖面太窄）
第三层：精准投递（岗位出现时）
  → 匹配度达标的岗位立即投，不再只等绿名单
```

---

## 五、行动方案（按优先级排序）

### P0：立刻做（本周内）

#### 1. 报名 PTE 考试
- 没有英语成绩 = 即使拿到 offer 也走不了签证
- PTE 出分快（48小时），可反复刷
- 目标：PTE 58（communicative ≥50），等同于雅思 6.5
- 报名费约 ¥1,800-2,000
- **这是所有 NZ 路径的前置条件，不考证一切免谈**

#### 2. 调整 SEEK 搜索关键词
当前推送只搜 "Information & Communication Technology"，覆盖面太窄。应该在 SEEK 上直接增加以下搜索：
- `Software Engineer` / `Python Developer` / `Analyst Programmer`
- `Developer Programmer` / `Software Developer` / `Backend Developer`
- `Data Engineer`（虽不在绿名单，但可走 SMC 6分制）
- **手动在 seek.co.nz 设置这些关键词的 Job Alert**，而不仅依赖 QQ 邮件推送

### P1：2-3 周内完成

#### 3. GitHub 作品集（以 Software Engineer 方向包装）
不是建一个"DBA 实验室"，而是建一个 **Python 项目集**，展示编程能力：

| 项目 | 技术栈 | 面试价值 |
|------|--------|---------|
| `seek-analyzer` | Python + pandas + JSON | 已有！就是你的 SEEK 扫描脚本，展示数据管道能力 |
| `etl-pipeline` | Python + SQLAlchemy + PostgreSQL | 展示数据工程能力 |
| `patent-analysis` | Python + NLP + scikit-learn | 与论文方向一致，展示研究编程能力 |
| `kos-website` | Next.js + TypeScript | 已有！展示全栈开发能力 |

**关键**：给每个项目写好 README，加部署链接。你的 KOS 网站本身就是最好的作品——它能在线访问。

#### 4. 英文 CV 重构
**目标职位**：不再只写 "Database Administrator"，而是写 **"Software & Data Engineer"** 或 **"Analyst Programmer"**

CV 核心叙事重构：
```
Wang Jirui — Software & Data Engineer
  ├── 10+ years enterprise data systems experience (SAP/Oracle ERP)
  ├── Python developer: ETL pipelines, data analysis, web applications
  ├── ISTIC Master's candidate (Information Resource Management, 86+ GPA)
  └── GitHub: github.com/JRWang2026 — SEEK scanner, ETL pipeline, KOS website
```

**不要用的标题**："Quality Engineer" — 质量工程师在 NZ 不在绿名单
**应该用的标题**："Data & Systems Engineer" — 数据与系统工程师，可映射到多个 Tier1 岗位

### P2：持续做（每周）

#### 5. 主动搜索 + 投递
- 每天花 10 分钟在 seek.co.nz 搜索上述关键词
- 同时关注 LinkedIn NZ 的 Software Engineer / Python Developer 岗位
- 投递时不局限于"绿名单标注"的岗位——任何薪资 ≥$35/hr 的 ICT 岗位都可以走 SMC 6 分制
- **关键认知**：用户有硕士学位（ISTIC 在读），在 SMC 6 分制下硕士=5分，只需 1 分（来自收入或 NZ 工作经验），比绿名单更灵活

#### 6. SMC 6 分制作为备选路径
即使不在绿名单上，用户也可以通过 SMC 6 分制移民：
- 硕士学位：5 分
- 收入达到 1.5 倍中位数工资（$52.50/hr）：3 分 → 总 8 分（超过 6 分线）
- 或收入达到 1 倍中位数工资（$35/hr）：1 分 → 总 6 分（刚好达标）
- **结论**：只要找到任何 $35/hr 以上的 ICT 岗位，SMC 路径就可行**

---

## 六、NZ 路径 vs 德国博士路径对比

| 维度 | NZ 绿名单/SMC | 德国岗位制博士 |
|------|--------------|--------------|
| **时间到永居** | 有 offer 即可申请（理论 0-6 月） | 3-4 年（§18d 签证 + 4 年工作） |
| **前置投入** | PTE + CV + GitHub（2-3 周） | 硕士毕业 + 论文 + 陶瓷（6-18 月） |
| **经济成本** | ¥2,000（PTE）+ ¥0（投递） | ¥0（带薪博士，月 €2,000-2,800） |
| **成功率** | **低**（离岸找工作极难，10 天仅 2 岗） | **中**（取决于陶瓷质量和论文） |
| **年龄限制** | ≤55 岁 | 无限制 |
| **语言要求** | 英语 PTE 58 / 雅思 6.5 | 德语 B1（永居时），英语可做科研 |
| **职业天花板** | IT 运维/开发岗 | 学术界 + 产业界双通道 |
| **风险** | 雇主不 accredited / 岗位消失 / 签证被拒 | 博士位置难找 / 导师不匹配 |

### 建议精力分配

```
德国博士（主线，80%）
  ├── ISTIC 硕士论文（当前最重要）
  ├── 专利竞争情报论文（CSSCI 首投）
  ├── 目标导师陶瓷（TU Darmstadt / Fraunhofer ISI / GESIS）
  └── scan_german_phd.py 每日扫描

NZ 副线（20%）
  ├── P0：PTE 报名 + 考试（本周）
  ├── P1：GitHub Portfolio 整理 + CV 重构（2-3 周）
  ├── P2：seek.co.nz 主动搜索（每周 3 次，每次 10 分钟）
  └── SEEK 自动化扫描继续运行（已有，零成本）
```

---

## 七、为什么 DBA 准备指南仍然有用

之前写的 `BOEI_DBA_Prep_Guide.md` 不是白写——里面的 SQL 刷题、PostgreSQL 实验、英文 CV 重构、面试逐字稿等内容，**同样适用于 Software Engineer / Analyst Programmer 岗位准备**。具体来说：

| 准备内容 | 对 DBA 的价值 | 对 Software Engineer 的价值 |
|----------|-------------|---------------------------|
| LeetCode SQL 50 题 | ✅ 核心 | ✅ 数据工程方向加分 |
| PostgreSQL 本地实验 | ✅ 核心 | ✅ 全栈开发需要 |
| Python ETL 脚本 | ✅ 加分 | ✅ 核心 |
| GitHub 作品集 | ✅ 加分 | ✅ **核心** |
| 英文 CV | ✅ 必需 | ✅ 必需 |
| PTE 58 | ✅ 必需 | ✅ 必需 |
| NZ Privacy Act 速览 | ✅ 面试可能问 | 🟡 轻微相关 |

**结论：准备过程零沉没成本。** 无论最终目标是 DBA 还是 Software Engineer，投入的精力都能复用。

---

## 八、最终建议

1. **不要为单个岗位焦虑**。BOEI DBA 消失了，但 Software Engineer 岗位在 SEEK 上长期存在。关键是改变搜索策略——从被动等邮件推送，到主动搜索 seek.co.nz。

2. **PTE 是所有路径的通行证**。本周就报名，不要拖。没有英语成绩，NZ 路径是空中楼阁。

3. **GitHub 是你最大的差异化优势**。你已经有了实际运行的项目（SEEK 扫描器、KOS 网站、git_pusher），这些比刷题更能证明编程能力。整理好 README，让雇主能看到在线 demo。

4. **SMC 6 分制是隐藏的 Plan B**。即使绿名单岗位不出现，任何 $35/hr 以上的 ICT 岗位 + 硕士学位 = SMC 6 分达标。这比死等绿名单灵活得多。

5. **主线不动摇**。德国博士仍然是最优路径——带薪、零学费、学术天花板高、无年龄焦虑。NZ 只是备选出境通道，不是终点。

---

*本文档基于 INZ 官方 Green List 数据（2026-01 更新）+ 10 天 SEEK NZ 自动化扫描数据 + 用户背景分析生成。*
