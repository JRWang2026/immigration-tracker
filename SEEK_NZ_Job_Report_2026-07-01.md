# SEEK NZ 岗位扫描报告 - 2026-07-01 (绿名单Tier1聚焦版 + 政策追踪)

> 📅 扫描时间：2026-07-01 09:00 | 📧 来源：QQ邮箱SEEK推送（6封ICT+Admin+NZ，6/30日）
> 🎯 策略：**绿名单Tier1 ICT岗** + **大学/研究机构研究岗** + **2026年NZ永居政策变化追踪**

---

## ❓ QQ邮箱连接器断连问题

**原因**：MCP连接器通过OAuth 2.0令牌认证，令牌有固定有效期（通常1-2小时）。以下情况均会导致断连：

| 场景 | 说明 |
|------|------|
| 令牌过期 | 访问令牌到期后如未自动刷新即断开 |
| 网络中断 | 任何网络波动可能打断连接握手 |
| 客户端重启 | 桌面应用重启后令牌缓存可能失效 |
| 服务端操作 | QQ邮箱服务器可能主动使令牌失效 |

**结论：不能永久保持连接**——这是 OAuth 安全机制的设计特性，不是 bug。任何基于 OAuth 的连接（GitHub、QQ 邮箱、微云等）都会周期性断开。工作台重启后需要手动恢复连接。

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | 6（ICT×3 + Admin×2 + NZ general×1） |
| 邮件日期范围 | 2026-06-30 |
| 去重岗位总数 | ~48（剔除行政/NZ general岗后ICT相关约28） |
| 过滤后相关岗位 | **2**（绿名单Tier1或近似匹配≥35分） |
| 🏆最佳匹配 | Database Administrator (BOEI SOLUTIONS LIMITED) **77分** |
| 🆕新发现 | Programmer / Junior Software Developer (Brand Developers) **可观望** |
| ⚠️近绿名单 | Senior Systems Analyst (DIA, $102-128K) — NZ政府高级岗，但 Systems Analyst≠Tier1 |

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 强移民路径

### 1. ⭐ Database Administrator | BOEI SOLUTIONS LIMITED
| 字段 | 详情 |
|------|------|
| **匹配度** | **77分** 🔥 |
| **地点** | Auckland CBD, Auckland |
| **薪资** | $69 – $72 per hour（约 $143,520 – $149,760/年） |
| **出现频次** | 连续出现在 6/27、6/28、6/29、6/30 共 6+ 封邮件中 |
| **首次出现** | 2026-06-27 |
| **已开放天数** | 4天+ |
| **匹配分析** | 绿名单Tier1: Database Administrator (ANZSCO 262111)；薪资远超中位数工资（$33.56/hr）门槛，达 2.1 倍 |
| **移民关联** | **Straight to Residence** — 有offer即可直申居留，无需等2年 |

---

## 🔵 近绿名单 / 可观望岗位

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 关联ANZSCO | 说明 |
|---|------|------|------|------|--------|-----------|------|
| 1 | **Programmer / Junior Software Developer** | Brand Developers Ltd | 未明确 | $70,000 – $80,000/yr | **48分** | 261313 (Software Engineer) | Junior级别，公司非科技公司，但可尝试映射为Software Engineer，需论证工作内容涉及软件开发 |
| 2 | **Senior Systems Analyst** | Department of Internal Affairs | Wellington | $102,846 – $128,009 | **42分** | ~262113 (Systems Admin) | NZ政府部门高级岗，薪资优越。注意：Systems Analyst ≠ Systems Administrator（后者才是Tier1），但可根据实际JD争取映射 |
| 3 | **Senior AI Engineer** | Tower Limited | Auckland CBD | Competitive Salary | **38分** | 261313 (Software Engineer) | AI工程师非绿名单，但如工作内容涉及软件开发可映射。保险公司AI岗 |

---

## 📉 已降级/过滤岗位（本轮新增）

| 职位 | 公司 | 降级原因 |
|------|------|---------|
| Founding Data Engineer | Awanui Group | Data Engineer 非绿名单，Tier2才有Data Scientist |
| Business Analyst | Ministry of Justice | BA非绿名单Tier1 |
| Product Analyst | MBIE | 非绿名单 |
| Programme Management Analyst | Unison Networks | 非绿名单 |
| Service and Data Analyst | University of Canterbury | 大学岗但非研究类，Data Analyst非绿名单 |
| Data and Insights Analyst | Department of Internal Affairs | $81K-101K，但Data Analyst非绿名单Tier1 |
| Delivery Lead | P&L Limited | 非绿名单 |
| Technical Business Analyst | Maori Television | BA非绿名单 |
| IT Support & AI Business Analyst | Miles Construction | BA/Support混合，非绿名单 |
| Operations Analyst | FirstCape | 非绿名单 |
| Research and Development Scientist | Sanitarium | 非ICT，食品行业 |
| All Admin/Office roles (>25) | 多家 | 行政岗，非移民路径 |

---

## 🔬 NZ永居政策追踪：2026年最新变化

### 核心政策参数（截至2026-07-01）

| 参数 | 当前值 | 变化 | 对王工的影响 |
|------|--------|------|-------------|
| **年龄上限** | ≤55岁 | 无变化 | ✅ 45岁，宽松 |
| **中位数工资** | **$33.56/hr** | ⬇ 从$35.00下调（2025.8.18生效） | ✅ 门槛降低，更容易达标 |
| **2倍中位数工资** | $67.12/hr | 豁免技能要求门槛 | BOEI DBA ($69-72/hr) 刚好超过 |
| **1.5倍中位数工资** | $50.34/hr | 5年AEWV最长停留 | — |
| **英语要求** | 雅思6.5或等效（如来自英语教育体系） | 无变化 | CET-6(66分)不一定被认可，需考雅思 |
| **NZQA IQA** | 必须（非NZ学历） | 无变化 | 必须做，4-8周，NZ$745 |
| **雇主认证** | 必须（Accredited Employer） | 无变化 | 需确认BOEI是否认证雇主 |
| **PR获取** | 持Residence Visa满2年 | 无变化 | — |
| **公民身份** | 持Residence满5年 | 无变化 | — |
| **绿名单Tier1 ICT** | 无增删 | 无变化 | Software Engineer/ DBA/ SysAdmin等8个ICT岗不变 |

### 2025.8.18 新增绿名单职业（仅Tier2，Work to Residence）

新增 8 个技工类职业（Metal Fabricator、Welder、Fitter等），**不涉及ICT领域**，对王工无影响。

### 趋势判断

| 维度 | 趋势 | 判断依据 |
|------|------|---------|
| ICT岗位政策 | **稳定** | 2025-2026 无ICT绿名单增删 |
| 工资门槛 | **轻微利好** | 中位数工资下调 $1.44/hr |
| 年龄政策 | **稳定** | 55岁上限未变 |
| 整体方向 | **门槛微降** | 工资下调 + 技工类扩容，反映劳动力短缺持续 |
| 风险点 | **认证雇主不确定性** | AEWV accreditation 要求可能趋严 |

### 自动化跟踪建议

为持续监控NZ永居政策变化，建议设置以下自动化跟踪：

1. **官方政策源**：https://www.immigration.govt.nz/ -> 每月检查 Green List 页面更新
2. **工资调整**：每年2-3月发布新的中位数工资，下次预期 **2027年2月**
3. **绿名单修订**：历史模式为每年8月更新，下次预期 **2026年8月**
4. **建议自动化**：每季度（3/6/9/12月）自动扫描INZ政策页面检查变化

---

## 🎯 BOEI Database Administrator 岗 — 详细准备策略

### 为什么这个岗值得认真对待

- **绿名单Tier1 Straight to Residence**：拿到offer即直申PR，最快6个月
- **薪资远超门槛**：$69-72/hr ≈ $145K/年，是NZ中位数工资的2.1倍
- **多轮曝光**：连续4天霸榜SEEK推送，说明招聘需求真实且可能未招到人
- **作为跳板**：NZ PR + 本地经验 → 后续申请澳洲/德国更有竞争力

### 分步准备计划

#### 第1步：简历重构（1周）

| 现有可包装经验 | 对应DBA JD要求 | 包装方式 |
|---------------|---------------|---------|
| SAP/Oracle ERP操作经验 | 企业级数据库管理 | "5+ years enterprise database operations (SAP/Oracle ERP)" |
| Python数据分析 | SQL查询优化/数据处理 | "Automated data pipelines with Python, SQL optimization" |
| 潜油特种电缆数据采集追溯系统 | 数据库设计/ETL | "Designed traceability database system for manufacturing" |
| 质量工程师经验 | 数据质量管理 | "Data quality management in ISO-certified environment" |
| ISTIC信息管理硕士在读 | 学术资质 | "Master's in Information Resource Management (GPA 86+)" |

**英文简历模板要点**：
- Objective: "Database Administrator with 5+ years enterprise data management experience in manufacturing, seeking Green List Tier1 DBA role in Auckland"
- Skills: SQL, Python, Oracle, SAP, Data Modeling, ETL, Dashboard (Power BI/Tableau)
- GitHub: 必须准备2-3个SQL/Python项目 repo（哪怕简单，也要有）

#### 第2步：技能补强（投简历前2-4周）

| 技能 | 紧迫度 | 学习资源 | 预计时间 |
|------|--------|---------|---------|
| SQL高级查询 | 🔴高 | LeetCode SQL 50题 | 2周 |
| Database Administration基础 | 🔴高 | PostgreSQL/MySQL官方文档 + 动手实践 | 3周 |
| Cloud DB (AWS RDS/Azure) | 🟡中 | AWS Free Tier | 2周 |
| Linux基础命令 | 🟡中 | Linux Journey | 1周 |
| NZ就业市场面试 | 🟡中 | Seek NZ面试经验 | 1周 |

#### 第3步：投递策略

| 时间节点 | 行动 |
|---------|------|
| 本周 | 准备英文简历 (CV + Cover Letter) |
| 下周 | 完成SQL刷题 + LeetCode |
| 第3周 | 投递BOEI岗位 + 同时搜索LinkedIn上BOEI员工内推 |
| 第4周 | 如无回复，主动联系BOEI HR (LinkedIn/公司网站) |

#### 第4步：面试准备

- **技术面试**：SQL查询、数据库设计、索引优化、备份恢复
- **行为面试**：STAR法则准备3-5个案例
- **NZ本地化**：了解NZ Privacy Act 2020、NZ数据保护法规
- **薪资谈判**：$69-72/hr是公布范围，可争取上限

### 风险对冲

- **不要等这个岗**：继续主线德国博士申请
- **不要把希望押在一次投递上**：同时关注LinkedIn/SEEK上的DBA/Software Engineer岗
- **NZQA IQA可以提前做**：$745 + 4-8周，学历评估结果5年有效

### 主线提醒

> 德国岗位制博士仍然是 **90%精力投入** 的主线。BOEI DBA只是"撞大运"的机会——拿到了可以转换人生轨迹，拿不到不损失任何东西（简历和技能准备对申博也有用）。

---

## 📈 持续开放岗位跟踪

| 职位 | 公司 | 首次出现 | 已开放天数 | 本轮匹配度 | 状态 | ANZSCO |
|------|------|----------|-----------|-----------|------|--------|
| Database Administrator | BOEI Solutions Ltd | 6/27 | 4天+ | **77** | 🔥绿名单Tier1 | 262111 |
| Senior Systems Analyst | DIA | 6/30 | 1天 | 42 | ⚠️近绿名单 | ~262113 |
| Programmer/Software Dev | Brand Developers | 6/30 | 1天 | 48 | 🆕近绿名单 | 261313 |

---

## 🎯 行动建议（优先级排序）

| 优先级 | 行动项 | 截止日期 | 精力占比 |
|--------|--------|---------|---------|
| P0 | 继续德国博士申请（EURAXESS+academics.de日常扫描） | 持续 | 90% |
| P1 | 准备英文简历（通用版+ DBA版） | 本周 | 5% |
| P2 | BOEI DBA岗投递 | 下周 | 3% |
| P3 | NZQA IQA学历评估（可选，5年有效） | 2个月内 | 1% |
| P4 | NZ永居政策季度跟踪 | 每季度 | 1% |

---

## 📋 绿名单移民路径对照表

| 职业 | ANZSCO | 绿名单层级 | 移民路径 | 薪资门槛 | 王工匹配度 |
|------|--------|-----------|---------|---------|----------|
| Software Engineer | 261313 | **Tier1** ⭐ | Straight to Residence | ≥$33.56/hr | 低-中 |
| **Database Administrator** | **262111** | **Tier1** ⭐ | **Straight to Residence** | **≥$33.56/hr** | **中高** |
| Systems Administrator | 262113 | Tier1 ⭐ | Straight to Residence | ≥$33.56/hr | 低-中 |
| Analyst Programmer | 261311 | Tier1 ⭐ | Straight to Residence | ≥$33.56/hr | 低 |
| Developer Programmer | 261312 | Tier1 ⭐ | Straight to Residence | ≥$33.56/hr | 低 |
| ICT Project Manager | 135112 | Tier1 ⭐ | Straight to Residence | ≥$33.56/hr | 极低 |
| ICT Security Specialist | 262112 | Tier1 ⭐ | Straight to Residence | ≥$33.56/hr | 极低 |
| Data Scientist | - | Tier2 | Work 2年→Residence | ≥$33.56/hr | 中 |
| ICT Support Engineer | - | Tier2 | Work 2年→Residence | ≥$33.56/hr | 中 |

> ⭐ Tier1 = Straight to Residence（有offer即直申居留）
> Tier2 = Work to Residence（认证雇主工作2年后可申）
> 所有绿名单路径必须：**NZQA IQA学历评估** + 薪资达标 + 雇主认证 + 年龄≤55

---

*报告由SEEK NZ自动化扫描 + 绿名单政策追踪生成 | 下次扫描：2026-07-02*
