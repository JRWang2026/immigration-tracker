# BOEI Database Administrator 岗位保姆级准备指南

> **岗位快照**：BOEI SOLUTIONS LIMITED · Auckland CBD, Auckland · $69 – $72/hr · 合同制/全职 · 可远程？（待确认）  
> **ANZSCO 代码**：262111 Database Administrator  
> **移民标签**：新西兰绿名单 Tier 1 · Straight to Residence  
> **适用签证**：Straight to Residence Visa（有 accredited employer 的 offer 即可直申永居）  
> **核心要求**：年龄 ≤55、雇主需为 accredited employer、薪资需 ≥ 中位数工资（2026 年为 NZD 33.56/小时，年薪约 NZD 69,805）、英语满足 INZ 要求（中国大陆申请人通常需雅思 6.5/PTE 58/托福 79）。

---

## 写在最前面：要不要冲这个岗？

**结论：可以冲，但只花 10% 精力，主线仍是德国岗位制博士。**

原因：
1. 这是近一周扫描中**唯一一个**达到 77 分的绿名单 Tier 1 ICT 岗位，稀缺。
2. DBA 的技能栈（SQL、数据建模、ERP 数据管理、Python ETL）和你在胜利泵业的项目经验**有 60% 重叠**，准备成本低。
3. 即便没拿到 offer，准备过程中练出的 SQL、数据库管理、英语面试能力，对申博、写论文、转数据方向都**零沉没成本**。
4. 该岗是合同时薪，不是永久职位，雇主 accreditation、offer 稳定性需重点验证。

---

## 阶段总览

| 阶段 | 时间 | 目标 | 产出物 |
|------|------|------|--------|
| 阶段一：自我评估与材料盘点 | 第 0-2 天 | 确认差距、锁定雇主资质 | 差距清单、雇主背调表 |
| 阶段二：SQL 与数据库管理突击 | 第 1-3 周 | 达到初级 DBA 面试水平 | LeetCode SQL 50 题完成、PostgreSQL 本地实验 |
| 阶段三：简历重构与作品集 | 第 2-3 周 | 把 ERP/质量背景包装成 DBA | 英文 CV、Cover Letter、GitHub Portfolio |
| 阶段四：投递与 networking | 第 3-4 周 | 把简历推到 decision maker | SEEK 申请、LinkedIn 内推、招聘代理 |
| 阶段五：面试备战 | 持续 | 能讲清每一个项目的技术细节 | 常见问题逐字稿、模拟面试 |
| 阶段六：入职 90 天预案 | 拿到 offer 后 | 快速站稳脚跟 | 30-60-90 天计划 |

---

## 阶段一：自我评估与材料盘点（第 0-2 天）

### 1.1 岗位拆解

打开该岗位的 SEEK 页面，把 JD 原文复制到一个文档，逐句标注：

| JD 关键词 | 你是否有直接经验 | 如何包装 |
|----------|------------------|----------|
| Database administration | 有（SAP/Oracle ERP 数据维护、追溯系统数据库） | 强调“企业级 ERP 数据库日常管理、权限控制、备份” |
| SQL / T-SQL / PL-SQL | 有（Python 数据分析时用过 SQL） | 列出具體查询、优化、存储过程经验 |
| Performance tuning / Index optimization | 弱 | 突击 2 周，LeetCode + EXPLAIN ANALYZE |
| Backup & recovery | 弱 | 本地 PostgreSQL 做 pg_dump/pg_restore 实验 |
| Cloud (AWS/Azure/GCP) | 弱 | 开 AWS Free Tier，跑 RDS PostgreSQL |
| ETL / Data integration | 有（电缆追溯系统数据采集） | 用“从 CSV/ERP 抽取 → 清洗 → 入库”描述 |
| Reporting / BI | 有（Power BI/Tableau） | 突出“从数据库到报表”的端到端经验 |
| New Zealand Privacy Act 2020 | 无 | 2 小时内速读 12 条隐私原则 |

### 1.2 雇主背调（必做）

- 上 [New Zealand Companies Office](https://companies-register.companiesoffice.govt.nz/) 查 BOEI SOLUTIONS LIMITED 注册信息、成立时间、股东、年报。
- 在 LinkedIn 搜索 "BOEI SOLUTIONS LIMITED"，看公司规模、员工、技术栈。
- **关键问题**：该公司是否为 INZ accredited employer？在 [INZ employer accreditation search](https://www.immigration.govt.nz/employ-migrants/accreditation-and-job-checks/accredited-employers-list) 中查。如果不是 accredited employer，该岗位**不能走 Straight to Residence**。
- 查 Glassdoor/Seek company reviews，看工作氛围、是否接受远程/支持签证。

### 1.3 英语考试自检

- 如果你已有雅思 6.5（单项 ≥6.0）或 PTE 58（communicative ≥50）：直接满足。
- 如果没有，**立刻报名** 最近一场雅思 General / PTE Academic。
- 建议优先 PTE：出分快（通常 48 小时内）、机考、可反复刷。目标 PTE 58（communicative ≥50）。

> 时间紧的话，先投递再考英语，但必须在面试前拿到成绩。

---

## 阶段二：SQL 与数据库管理突击（第 1-3 周）

### 2.1 SQL 能力：从“会写”到“能讲”

**推荐路径**：

1. **LeetCode Database 50 题**（免费，7 天刷完）：
   - 重点：JOIN、子查询、窗口函数、CTE、GROUP BY、HAVING、CASE WHEN。
   - 每题要求自己写出 SQL，并在 PostgreSQL 里跑一遍。
2. **SQLZoo**（免费）：巩固基础查询。
3. **Mode Analytics SQL Tutorial**（免费）：有真实数据集，练习商业分析 SQL。

**必须掌握的 8 类 SQL 面试题**：

| 类型 | 示例 | 关键函数/概念 |
|------|------|--------------|
| 多表 JOIN | 找出每个客户的最新订单 | LEFT JOIN, INNER JOIN, COALESCE |
| 窗口函数 | 计算销售额排名、同比 | ROW_NUMBER(), RANK(), LAG(), LEAD() |
| 聚合与筛选 | 按部门统计平均工资 | GROUP BY, HAVING, AVG() |
| 数据透视 | 把行转列 | CASE WHEN + SUM/COUNT |
| 重复数据 | 找出重复邮箱 | GROUP BY + HAVING COUNT(*) > 1 |
| 缺失值处理 | 填充缺失日期 | GENERATE_SERIES, CTE |
| 性能优化 | 为什么这条查询慢？ | INDEX, EXPLAIN ANALYZE |
| 事务与并发 | 转账场景如何保证一致？ | BEGIN, COMMIT, ROLLBACK, ACID |

### 2.2 数据库管理：从“用数据库”到“管数据库”

**安装本地实验环境**（30 分钟）：

```bash
# 用 Docker 启动 PostgreSQL（Windows 可用 Docker Desktop）
docker run --name pg-dba-lab -e POSTGRES_PASSWORD=pglab -p 5432:5432 -d postgres:16
```

**必做实验清单**：

| 实验 | 命令/工具 | 面试时可讲的故事 |
|------|-----------|------------------|
| 创建数据库、用户、角色 | `CREATE DATABASE`, `CREATE ROLE`, `GRANT` | “我建立了只读、读写、管理员三级权限模型” |
| 备份与恢复 | `pg_dump`, `pg_restore` | “我定期对追溯系统数据库做逻辑备份，并验证恢复流程” |
| 索引优化 | `CREATE INDEX`, `EXPLAIN ANALYZE` | “通过添加复合索引，把慢查询从 3 秒降到 100 毫秒” |
| 视图与物化视图 | `CREATE VIEW`, `CREATE MATERIALIZED VIEW` | “为报表层创建了物化视图，减少重复计算” |
| 监控表大小 | `pg_size_pretty`, `pg_stat_user_tables` | “我定期监控表膨胀和索引使用情况” |
| 导入 CSV | `COPY` / pandas + SQLAlchemy | “我写了 Python 脚本把 ERP 导出 CSV 自动导入 PostgreSQL” |

### 2.3 云服务：AWS Free Tier 实战

- 注册 AWS 免费账号（需信用卡，注意用量控制）。
- 创建 RDS PostgreSQL 实例（选 db.t3.micro，免费 12 个月）。
- 练习：本地 psql 连接 RDS、创建库、备份到 S3、从 S3 恢复。
- 面试价值：证明你接触过云数据库，不是纯本地玩家。

### 2.4 新西兰 Privacy Act 2020 速览

DBA 岗位常涉及个人数据，面试可能被问。核心掌握：

- **12 Information Privacy Principles**：
  1. 收集目的明确
  2. 直接从个人收集
  3. 收集时告知用途
  4. 以合法合理方式收集
  5. 保证数据安全存储
  6. 个人有权访问自己的数据
  7. 个人有权更正自己的数据
  8. 使用前确保数据准确、最新
  9. 保留时间不超过必要
  10. 使用目的不超出原定范围
  11. 限制披露
  12. 拥有唯一标识符管理
- 了解 **Privacy Commissioner** 角色。
- 面试话术：*"In my previous ERP data projects, I applied data minimization, role-based access, and audit logging to align with privacy principles similar to NZ Privacy Act 2020."*

---

## 阶段三：简历重构与作品集（第 2-3 周）

### 3.1 英文 CV 重写原则

**原则：不要“翻译中文简历”，而要“用北美/澳新 IT 岗位语言重新写”。**

**推荐模板**：

- 一页 A4（如果经验超过 15 年可两页，但尽量一页）。
- 顶部 Summary：3-4 行，点明 “Database & Data Operations Specialist with 10+ years in enterprise ERP systems, data traceability, and SQL-driven analytics.”
- 技术栈分栏：SQL, PostgreSQL, Oracle, Python, pandas, ETL, Power BI, SAP, AWS RDS。
- 工作经历用 STAR + 量化。
- 不要写“质量工程师”为标题，可以写 **“Senior Data & Systems Analyst | ERP Database Operations”**。

### 3.2 工作经历包装示例

**原写法**：
> 负责胜利泵业潜油特种电缆生产质量数据统计，编写 Python 程序处理数据。

**DBA 向写法**：
> **ERP Data & Traceability Specialist** — Shengli Pump Industry (Dongying, China)  
> - Managed and validated production data across SAP/Oracle ERP modules, ensuring data integrity for 10,000+ cable traceability records.  
> - Designed SQL-based reporting pipelines and Python ETL scripts to extract, transform, and load manufacturing data into analytical databases.  
> - Optimized slow-running ERP queries by introducing indexing and query refactoring, reducing report generation time by ~40%.  
> - Implemented role-based access controls and audit logging for sensitive production and payroll data sets.  
> - Built automated dashboards (Power BI/Tableau) consumed by production and Party-affairs management teams.

### 3.3 作品集：GitHub Portfolio

**项目名**：`manufacturing-erp-dba-portfolio` 或 `sql-dba-lab`。

**必须包含的内容**：

1. **README.md**：项目背景、技术栈、如何运行、成果截图。
2. **schema.sql**：一个制造追溯系统的数据库设计（产品、批次、原材料、质检记录、供应商）。
3. **queries.sql**：10-15 个复杂查询（多表 JOIN、窗口函数、CTE、聚合）。
4. **optimization.md**：索引优化案例、EXPLAIN ANALYZE 对比截图。
5. **etl_pipeline.py**：Python 脚本，从 CSV 读取、清洗、写入 PostgreSQL。
6. **backup_restore.md**：pg_dump/pg_restore 操作记录。

**示例项目结构**：

```text
sql-dba-lab/
├── README.md
├── schema/
│   └── manufacturing_traceability.sql
├── queries/
│   ├── 01_joins.sql
│   ├── 02_window_functions.sql
│   ├── 03_cte.sql
│   └── 04_optimization.sql
├── python/
│   └── csv_to_postgres.py
├── docs/
│   ├── backup_restore.md
│   └── privacy_notes.md
└── images/
    └── explain_analyze_before_after.png
```

### 3.4 Cover Letter 模板

```text
Dear Hiring Manager,

I am writing to express my strong interest in the Database Administrator position at BOEI SOLUTIONS LIMITED, as advertised on SEEK. With over a decade of experience managing ERP data operations, designing SQL-driven reporting pipelines, and ensuring data integrity in manufacturing environments, I am confident I can add immediate value to your team.

In my current role at Shengli Pump Industry, I have:
- Administered and maintained production data across SAP/Oracle ERP systems.
- Built Python ETL workflows and SQL queries to support traceability, quality control, and management reporting.
- Implemented access controls, audit logging, and backup procedures for business-critical databases.
- Optimized slow queries and improved report generation efficiency by approximately 40%.

I am particularly drawn to BOEI's work in [insert one sentence about the company from your research]. I am eager to bring my combination of database administration, data engineering, and enterprise systems experience to your Auckland team.

I would welcome the opportunity to discuss how my background aligns with your needs. Thank you for your time and consideration.

Sincerely,
Wang Jirui
```

---

## 阶段四：投递与 Networking（第 3-4 周）

### 4.1 SEEK 投递

- 直接点击岗位“Apply”，上传 CV + Cover Letter。
- 申请时勾选“允许雇主查看完整资料”。
- 记录投递时间、版本、反馈状态。

### 4.2 LinkedIn 内推（关键）

**步骤**：
1. 在 LinkedIn 搜索 "BOEI SOLUTIONS LIMITED"，找到公司员工。
2. 优先找：CTO、Head of Engineering、Database Manager、Technical Lead。
3. 发送连接请求，附言：

```text
Hi [Name], I noticed BOEI SOLUTIONS LIMITED is hiring a Database Administrator in Auckland. I have 10+ years of ERP data operations and SQL/ETL experience and am very interested in the role. Would you be open to a brief chat about the team and the position? Thank you, Jirui
```

4. 连接通过后，发送简短感谢 + 简历 PDF。

### 4.3 招聘代理

新西兰主要 IT 招聘公司：
- **Robert Walters** (Auckland)
- **Hays** (Auckland, Wellington)
- **Adecco** / **Modis**
- **Chandler Macleod**

在官网提交 CV，注明："Open to Database Administrator / Data Engineer / BI Developer roles in NZ, Green List eligible."

---

## 阶段五：面试备战（持续）

### 5.1 技术面常见问题

1. Walk me through your database design for the cable traceability system.
2. How do you optimize a slow SQL query?
3. What is the difference between INNER JOIN and LEFT JOIN? When would you use each?
4. Explain indexing. What are the trade-offs?
5. How do you handle database backups and disaster recovery?
6. What is normalization? When would you denormalize?
7. Describe a time you had to clean dirty data.
8. How do you ensure data security and privacy in a database?
9. What is a transaction? Explain ACID.
10. Experience with cloud databases? AWS RDS? Azure SQL?

### 5.2 行为面常见问题

1. Tell me about a time you had to learn a new technology quickly.
2. How do you handle conflicting requirements from business and technical teams?
3. Describe a data quality issue you identified and fixed.
4. Why do you want to move to New Zealand?
5. Why are you leaving your current role?

### 5.3 模拟面试建议

- 用 ChatGPT / Claude 做模拟面试官，输入 JD 让它提问。
- 对每个问题写出逐字稿，背到自然。
- 用手机录像自己的回答，检查语速、眼神、口头禅。

### 5.4 薪资谈判

- 该岗位标 $69-72/hr，按 40 小时/周、52 周 ≈ NZD 143,520-149,760/年，远高于中位数工资。
- 但合同制通常无年假、病假，需确认是否 PAYE、是否有福利、是否 remote。
- 底线：只要年薪 ≥ NZD 69,805（中位数工资）且雇主 accredited，即可满足 Straight to Residence。
- 如果雇主问期望，可以答："Based on the advertised range and my experience, I am targeting the middle-to-upper end of the range."

---

## 阶段六：入职 90 天预案（拿到 offer 后）

### 6.1 签证申请清单

1. 雇主提供 Job Offer + 证明 accredited employer。
2. 准备护照、学历学位、工作经验证明、无犯罪证明、体检（指定医院）。
3. 英语成绩（雅思/PTE）。
4. 在线提交 Straight to Residence Visa 申请。
5. 费用：主申请人约 NZD 4,290（2026 年参考），可能调整。

### 6.2 入职 30-60-90 天计划

| 阶段 | 目标 | 具体动作 |
|------|------|----------|
| 第 1-30 天 | 融入与审计 | 了解现有数据库架构、备份策略、权限模型；建立文档；修复明显风险 |
| 第 31-60 天 | 优化与标准化 | 梳理慢查询清单；优化索引；建立监控和告警；制定数据保留策略 |
| 第 61-90 天 | 自动化与价值输出 | 用 Python 脚本实现自动化备份检查；建立自助报表；提出云迁移或成本优化建议 |

---

## 附录：资源清单

| 资源 | 链接 | 用途 |
|------|------|------|
| LeetCode Database | https://leetcode.com/studyplan/top-sql-50 | SQL 刷题 |
| SQLZoo | https://sqlzoo.net | SQL 基础 |
| Mode SQL | https://mode.com/sql-tutorial | 商业分析 SQL |
| PostgreSQL 官方文档 | https://www.postgresql.org/docs/ | 实验参考 |
| AWS RDS 免费套餐 | https://aws.amazon.com/rds/free/ | 云数据库实践 |
| NZ Privacy Act | https://www.privacy.org.nz/privacy-act-2020/ | 隐私法速读 |
| INZ Straight to Residence | https://www.immigration.govt.nz/visas/straight-to-residence-visa/ | 签证官方要求 |
| INZ Accredited Employer List | https://www.immigration.govt.nz/employ-migrants/accreditation-and-job-checks/accredited-employers-list | 查雇主资质 |
| NZ Companies Office | https://companies-register.companiesoffice.govt.nz/ | 查公司注册 |
| SEEK NZ | https://www.seek.co.nz/ | 投递 |
| LinkedIn | https://www.linkedin.com/ | 内推 |

---

## 最后提醒

- **BOEI 这个岗是“机会”不是“救命稻草”**。投，但不要等。
- **英语考试先报名**。没有英语成绩，即使拿到 offer 也走不了签证。
- **先确认雇主是否 accredited**。如果否，直接放弃。
- **把简历里的“质量”二字换成“数据/数据库/系统”**。你不是在转行，你是在重新命名你的现有技能。
- **GitHub 作品集是最大的加分项**。新西兰雇主看 GitHub 的概率远高于国内。

祝好运，冲就完了。
