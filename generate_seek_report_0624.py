#!/usr/bin/env python3
"""Generate SEEK NZ Job Report for 6/24 scan - with matching analysis."""
import json
from pathlib import Path

# All extracted jobs from this scan (6/18-6/24 emails, comprehensive)
all_jobs = [
    # === 6/23 NEW EMAILS (this scan's focus) ===
    # ICT 6/23 21:47 - new jobs not in previous scan
    {"title": "Senior Business Analyst", "company": "Absolute IT Limited", "location": "Auckland CBD, Auckland", "salary": "Up to $125 per hour", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Senior Technical Business Analyst", "company": "Techspace Consulting Limited", "location": "Te Puke, Bay of Plenty", "salary": "$125,000-$145,000", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Business and Technology Systems Analyst", "company": "Recruitnet Consulting Group Ltd", "location": "Te Rapa, Waikato", "salary": "$90,000 - $110,000", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Analyst - Planning, Funding and Outcomes", "company": "Health New Zealand - Te Whatu Ora", "location": "Auckland CBD, Auckland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Application Analyst", "company": "Potentia", "location": "Dunedin Central, Otago", "salary": "Salary + Kiwisaver + Benefits", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Application Analyst", "company": "Potentia", "location": "Christchurch, Canterbury", "salary": "Salary + Kiwisaver + Benefits", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "IS Senior Systems Analyst", "company": "Vitaco Health Group", "location": "Manukau & East Auckland, Auckland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Enterprise Portfolio Analyst", "company": "Stats NZ", "location": "Wellington Central, Wellington", "salary": "$77,259 - $90,893 + kiwisaver", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    
    # ICT 6/23 20:25 - additional new jobs
    {"title": "Lead Intelligence Analyst", "company": "Department of Internal Affairs", "location": "Wellington", "salary": "$115,425 - $143,640", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Systems & AI Administrator", "company": "McCulloch and Partners", "location": "Invercargill Central, Southland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Senior Data Analyst/Kaitātari Hoahoa Matua", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Senior Data Analyst/Kaitātari Hoahoa Matua", "company": "Stats NZ", "location": "Wellington Central, Wellington", "salary": "", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Senior Data & Platform Engineer", "company": "WineWorks", "location": "Auckland CBD, Auckland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Senior Systems Engineer", "company": "New Zealand Defence Force", "location": "Whenuapai, Auckland", "salary": "$88,217 - $101,930", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    {"title": "Practice Lead, Analysis and Design", "company": "Ministry of Social Development", "location": "Wellington Central, Wellington", "salary": "$138,125 - $171,889", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    
    # Admin 6/23 23:58 - ⭐ KEY FINDING: Mechanical Engineer!
    {"title": "Mechanical Engineer", "company": "Windcave Limited", "location": "Ellerslie, Auckland", "salary": "", "category": "Admin", "first_seen": "2026-06-23T23:58", "green_list": "Tier1"},
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Henderson, Auckland", "salary": "$51,000 per year", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "IT Support Engineer", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Operations & Administration Manager", "company": "The Life Centre", "location": "Ponsonby, Auckland", "salary": "$75,000 – $80,000 per year", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Office Co-Ordinator", "company": "Flo & Frankie", "location": "Parnell, Auckland", "salary": "Competitive pay and great perks", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Executive Assistant", "company": "Enviro NZ", "location": "Ellerslie, Auckland", "salary": "Competitive salary & free carpark", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Office Manager", "company": "323 Recruitment Limited", "location": "Auckland CBD, Auckland", "salary": "NZD 70k - 80k per year", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Office Manager/Team Leader", "company": "Archway Recruitment", "location": "Wellington Central, Wellington", "salary": "$115,000-120,000 per annum", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Office Manager", "company": "Empower Electrical", "location": "Port Whangarei, Northland", "salary": "$30 – $40 per hour", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Executive Group Assistant", "company": "NZ Police Association", "location": "Wellington Central, Wellington", "salary": "$80,000 – $90,000 per year", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "Administration Coordinator", "company": "Graeme Dingle Foundation Auckland", "location": "Mount Wellington, Auckland", "salary": "$30 – $32 per hour", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    {"title": "IT Operations & Support Engineer", "company": "Traffic Safe New Zealand Ltd", "location": "Takanini, Auckland", "salary": "$50,000 – $58,000 per year", "category": "Admin", "first_seen": "2026-06-23T23:58"},
    
    # ICT overlap from 6/23 (already in snippets)
    {"title": "Business Analyst (6M Contract)", "company": "Sourced | IT Recruitment Specialists", "location": "Auckland CBD, Auckland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Business Operations Analyst", "company": "Cultivate", "location": "Auckland CBD, Auckland", "salary": "Base + Bonus + insurances + more", "category": "ICT", "first_seen": "2026-06-23T21:47"},
    {"title": "Project Business Analyst", "company": "PowerNet", "location": "Invercargill Central, Southland", "salary": "", "category": "ICT", "first_seen": "2026-06-23T20:25"},
    
    # === Previously seen jobs (6/18-6/22) still active ===
    {"title": "Business Systems Analyst - ERP", "company": "Windsor Engineering Group Ltd", "location": "Mount Wellington, Auckland", "salary": "Competitive annual salary + employee benefits", "category": "ICT", "first_seen": "2026-06-19"},
    {"title": "Senior Technical Business Analyst", "company": "New Zealand Customs Service", "location": "Wellington Central, Wellington", "salary": "Competitive salary + gym", "category": "ICT", "first_seen": "2026-06-21"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Wellington Central, Wellington", "salary": "", "category": "ICT", "first_seen": "2026-06-22"},
    {"title": "Business Analyst", "company": "New Plymouth District Council", "location": "New Plymouth Central, Taranaki", "salary": "", "category": "ICT", "first_seen": "2026-06-21"},
    {"title": "Graduate Functional Consultant", "company": "Credisense Limited", "location": "Auckland CBD, Auckland", "salary": "", "category": "ICT", "first_seen": "2026-06-21"},
    {"title": "Data Analyst", "company": "Frog Recruitment - Auckland", "location": "Auckland CBD, Auckland", "salary": "$40 per hour", "category": "ICT", "first_seen": "2026-06-21"},
    {"title": "IT Support & AI Business Analyst", "company": "Miles Construction Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "category": "ICT", "first_seen": "2026-06-18"},
    {"title": "System Analyst", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "category": "ICT", "first_seen": "2026-06-19"},
    {"title": "Technical BA", "company": "Techspace Consulting Limited", "location": "", "salary": "$40 per hour", "category": "ICT", "first_seen": "2026-06-18"},
    {"title": "Information Systems & Technology Support Analyst", "company": "Craigmore Corporate", "location": "Christchurch Central, Canterbury", "salary": "", "category": "Admin", "first_seen": "2026-06-21"},
    {"title": "Office Administrator / Manager", "company": "Simtec Therapeutic Limited", "location": "Onehunga, Auckland", "salary": "$65,000 – $85,000 per year", "category": "Admin", "first_seen": "2026-06-21"},
    {"title": "Office Manager", "company": "Finelawn Limited", "location": "Matangi, Waikato", "salary": "$75,000 – $90,000 per year + Bonus", "category": "Admin", "first_seen": "2026-06-21"},
]

# Deduplicate
seen = set()
unique = []
for j in all_jobs:
    key = f"{j['title']}|{j['company']}|{j['location']}"
    if key not in seen:
        seen.add(key)
        unique.append(j)

# User profile for matching
USER_PROFILE = {
    "age": 45,
    "degree_bachelor": "机械设计制造及其自动化 (中国石油大学)",
    "degree_master": "信息资源管理 (ISTIC, 在读, 86+)",
    "experience": "20年质量工程经验",
    "skills": ["Python数据分析", "SolidWorks", "SAP/Oracle ERP", "Power BI/Tableau", "党务数据处理"],
    "project": "潜油特种电缆数据采集追溯系统",
    "cert": "质量工程师(中级)",
    "green_list_target": "机械工程师 ANZSCO 233512 (Tier1, Straight to Residence)",
}

# Matching analysis function
def match_score(job):
    """Calculate match score (0-100) and generate analysis."""
    title = job['title'].lower()
    company = job['company'].lower()
    score = 0
    match_reasons = []
    missing_skills = []
    immigration_path = ""
    
    # === Green List Tier 1: Mechanical Engineer ===
    if 'mechanical engineer' in title:
        score = 95
        match_reasons = [
            "✅ 绿名单Tier1职业，有offer即可直申居留",
            "✅ 机械工程学士直接对口",
            "✅ 20年质量工程经验高度匹配",
            "✅ SolidWorks/3D设计能力加分",
        ]
        missing_skills = [
            "需NZQA IQA学历评估（前置条件，4-8周）",
            "需PTE 58+或同等英语证明（绿名单不硬性要求但雇主可能要求）",
            "了解NZ机械工程行业标准(AS/NZS)",
        ]
        immigration_path = "绿名单Tier1 → Straight to Residence → 拿offer即申居留签证"
        return score, match_reasons, missing_skills, immigration_path
    
    # === Business Systems Analyst - ERP ===
    if 'erp' in title and ('business system' in title or 'analyst' in title):
        score = 80
        match_reasons = [
            "✅ SAP/Oracle ERP经验直接对口",
            "✅ 质量工程+数据系统经验叠加",
            "✅ 制造业ERP场景熟悉",
            "⚠️ 需证明BA方法论能力",
        ]
        missing_skills = [
            "BA方法论(敏捷/瀑布)证书可加分",
            "NZ本地ERP市场经验(需快速适应)",
            "英语商务沟通能力",
        ]
        immigration_path = "ANZSCO 261111 Business Analyst → 可能符合绿名单Tier2(需薪资≥$55/h或年薪≥$95K)"
    
    # === Senior Technical Business Analyst ===
    if 'senior technical business' in title:
        score = 75
        match_reasons = [
            "✅ 技术背景+业务分析双重匹配",
            "✅ 20年工程经验体现senior级别",
            "✅ 数据分析能力加分",
        ]
        missing_skills = [
            "BA方法论和UML/BPMN",
            "英语商务沟通",
            "NZ政府项目经验(Customs是政府机构)",
        ]
        immigration_path = "绿名单Tier2 → Work to Residence (需2年工作后转居留)"
    
    # === Business Analyst (generic) ===
    if 'business analyst' in title and 'senior' not in title and 'technical' not in title:
        score = 60
        match_reasons = [
            "✅ 数据分析+系统经验部分匹配",
            "⚠️ 纯BA角色需方法论补充",
            "⚠️ 合同岗位(6M)移民价值有限",
        ]
        missing_skills = [
            "BA方法论证书(IIBA CBAP/ECBA)",
            "英语商务沟通",
            "NZ本地市场了解",
        ]
        immigration_path = "绿名单Tier2 → Work to Residence (薪资门槛$95K+)"
    
    # === Business and Technology Systems Analyst ===
    if 'technology system' in title or 'business and technology' in title:
        score = 70
        match_reasons = [
            "✅ 技术+业务双轨匹配用户背景",
            "✅ 薪资范围合理($90-110K)",
            "✅ Waikato地区生活成本较低",
        ]
        missing_skills = [
            "系统分析方法论",
            "英语商务沟通",
            "NZ技术标准",
        ]
        immigration_path = "绿名单Tier2 → Work to Residence (薪资需≥$95K, 此岗$90-110K可能达标)"
    
    # === Data Analyst ===
    if 'data analyst' in title and 'senior' not in title:
        score = 55
        match_reasons = [
            "✅ Python数据分析能力直接匹配",
            "✅ 统计/Power BI/Tableau加分",
            "⚠️ 数据分析师不在绿名单",
        ]
        missing_skills = [
            "SQL/数据库高级查询",
            "数据可视化工具(Power BI/Tableau深化)",
            "NZ统计方法/政府数据标准(Stats NZ特需)",
        ]
        immigration_path = "非绿名单 → 需Essential Skills工签 → 2-3年后转SMC(Skilled Migrant Category)"
    
    # === Senior Data Analyst ===
    if 'senior data analyst' in title:
        score = 65
        match_reasons = [
            "✅ Python+数据分析匹配",
            "✅ 20年经验体现senior级别",
            "⚠️ 不在绿名单",
        ]
        missing_skills = [
            "高级统计建模",
            "SQL/数据库",
            "NZ政府数据标准",
        ]
        immigration_path = "非绿名单 → Essential Skills工签 → SMC路径"
    
    # === System Analyst ===
    if 'system analyst' in title and 'senior' not in title:
        score = 50
        match_reasons = [
            "✅ 系统分析经验部分匹配",
            "⚠️ 需深化IT系统知识",
        ]
        missing_skills = [
            "IT系统架构知识",
            "英语技术沟通",
        ]
        immigration_path = "非绿名单 → Essential Skills工签"
    
    # === IS Senior Systems Analyst ===
    if 'is senior system' in title or 'senior system' in title:
        score = 55
        match_reasons = [
            "✅ 信息系统+管理经验部分匹配",
            "⚠️ 需IT系统深化知识",
        ]
        missing_skills = [
            "IT基础设施知识",
            "英语技术沟通",
        ]
        immigration_path = "非绿名单 → Essential Skills工签"
    
    # === Application Analyst ===
    if 'application analyst' in title:
        score = 45
        match_reasons = [
            "✅ 应用系统经验部分匹配",
            "⚠️ 偏临床/医疗应用可能不对口",
        ]
        missing_skills = [
            "医疗/临床应用知识(Potentia是医疗行业)",
            "英语",
        ]
        immigration_path = "非绿名单 → Essential Skills工签"
    
    # === Lead Intelligence Analyst ===
    if 'intelligence analyst' in title:
        score = 40
        match_reasons = [
            "⚠️ 竞争情报方向匹配学术背景",
            "⚠️ 需安全/情报领域经验",
            "⚠️ 政府岗位可能需公民身份",
        ]
        missing_skills = [
            "情报分析方法论",
            "安全审查(政府岗位)",
            "可能需NZ公民/永居身份",
        ]
        immigration_path = "⚠️ 政府情报岗位可能不开放给非公民"
    
    # === Practice Lead ===
    if 'practice lead' in title:
        score = 35
        match_reasons = [
            "⚠️ 管理层级高，需丰富NZ本地经验",
            "⚠️ 薪资高但对口性低",
        ]
        missing_skills = [
            "NZ政府项目经验",
            "高级管理证书",
            "英语商务沟通高级",
        ]
        immigration_path = "非绿名单 → 需SMC路径"
    
    # === IT Support ===
    if 'it support' in title or 'support engineer' in title:
        score = 40
        match_reasons = [
            "⚠️ 入门级IT支持，薪资偏低",
            "✅ 有一定技术背景",
        ]
        missing_skills = [
            "IT支持证书(Microsoft/Cisco)",
            "英语客户服务",
        ]
        immigration_path = "非绿名单 → 薪资低难以满足工签门槛"
    
    # === Operations & Admin Manager ===
    if 'operations' in title and 'admin' in title:
        score = 45
        match_reasons = [
            "✅ 党务管理+运营经验部分匹配",
            "⚠️ 偏行政而非技术",
        ]
        missing_skills = [
            "NZ行政管理标准",
            "英语",
        ]
        immigration_path = "非绿名单 → Essential Skills工签"
    
    # === Admin/Office ===
    if 'office' in title or 'admin' in title:
        score = 25
        match_reasons = [
            "⚠️ 基础行政岗位，薪资低",
            "⚠️ 移民价值极低",
        ]
        missing_skills = ["英语", "NZ办公软件"]
        immigration_path = "❌ 薪资远低于工签门槛，移民价值极低"
    
    # === Systems & AI Administrator ===
    if 'systems & ai' in title:
        score = 55
        match_reasons = [
            "✅ AI+系统管理匹配学术方向",
            "✅ Python+数据分析加分",
            "⚠️ 偏小型公司/地区",
        ]
        missing_skills = [
            "AI系统运维经验",
            "英语",
        ]
        immigration_path = "非绿名单 → Essential Skills工签(薪资不确定)"
    
    # === Functional Consultant ===
    if 'functional consultant' in title:
        score = 55
        match_reasons = [
            "✅ ERP/系统经验可能匹配",
            "⚠️ Graduate级可能太初级",
        ]
        missing_skills = [
            "特定ERP产品深化知识",
            "英语商务沟通",
        ]
        immigration_path = "非绿名单 → 初级岗位移民路径长"
    
    # === Enterprise Portfolio Analyst ===
    if 'portfolio analyst' in title or 'enterprise' in title and 'analyst' in title:
        score = 50
        match_reasons = [
            "✅ 数据分析+管理经验部分匹配",
            "✅ Stats NZ政府机构稳定",
            "⚠️ 偏项目管理/投资组合",
        ]
        missing_skills = [
            "项目组合管理方法论",
            "NZ政府工作流程",
        ]
        immigration_path = "非绿名单 → Stats NZ政府岗位可能需NZ身份背景"
    
    # Default
    if score == 0:
        score = 20
        match_reasons = ["⚠️ 匹配度低"]
        missing_skills = ["英语", "NZ本地经验"]
        immigration_path = "非绿名单 → 移民路径长"
    
    return score, match_reasons, missing_skills, immigration_path

# Generate report
report_lines = []
report_lines.append("# SEEK新西兰岗位扫描报告 2026-06-24")
report_lines.append("")
report_lines.append("> 扫描时间：2026-06-24 08:00 | 邮件来源：QQ邮箱SEEK推送(6/18-6/23)")
report_lines.append("> 扫描范围：ICT + Administration & Office Support 两大类")
report_lines.append("")
report_lines.append("## 🚨 关键发现")
report_lines.append("")
report_lines.append("**机械工程师岗位首次出现！** 这是新西兰绿名单Tier1职业(ANZSCO 233512)，")
report_lines.append("有offer即可直申居留签证(Straight to Residence)，是移民最优路径。")
report_lines.append("")
report_lines.append("| 项目 | 详情 |")
report_lines.append("|------|------|")
report_lines.append("| 岗位 | Mechanical Engineer @ Windcave Limited |")
report_lines.append("| 地点 | Ellerslie, Auckland |")
report_lines.append("| 绿名单 | ✅ Tier1 (Straight to Residence) |")
report_lines.append("| 用户匹配 | 机械工程学士 + 20年质量工程经验 |")
report_lines.append("| 行动建议 | 立即查看SEEK详情页 + 启动NZQA学历评估 |")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 本轮新增岗位（6/23，对比6/22扫描）")
report_lines.append("")

new_since_last = [j for j in unique if j.get('first_seen', '').startswith('2026-06-23')]
report_lines.append(f"本轮新增 **{len(new_since_last)}** 个岗位（不含6/18-6/22重复岗位）")
report_lines.append("")
report_lines.append("### 新增ICT岗位")
ict_new = [j for j in new_since_last if j['category'] == 'ICT']
for j in ict_new:
    s, r, m, p = match_score(j)
    report_lines.append(f"- **{j['title']}** | {j['company']} | {j['location']} | {j['salary']}")
    report_lines.append(f"  - 匹配度：{s}/100 | 移民路径：{p}")
    report_lines.append(f"  - 匹配理由：{r[0]}")
report_lines.append("")
report_lines.append("### 新增Admin岗位（含机械工程师）")
admin_new = [j for j in new_since_last if j['category'] == 'Admin']
for j in admin_new:
    s, r, m, p = match_score(j)
    gl = " ⭐绿名单Tier1" if j.get('green_list') else ""
    report_lines.append(f"- **{j['title']}** | {j['company']} | {j['location']} | {j['salary']}{gl}")
    report_lines.append(f"  - 匹配度：{s}/100 | 移民路径：{p}")

report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 全量岗位匹配分析（按匹配度排序）")
report_lines.append("")
report_lines.append("| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 绿名单 | 移民路径 |")
report_lines.append("|---|------|------|------|------|--------|--------|----------|")

# Sort by match score
scored_jobs = []
for j in unique:
    s, r, m, p = match_score(j)
    scored_jobs.append((s, j, r, m, p))

scored_jobs.sort(key=lambda x: -x[0])

for i, (s, j, r, m, p) in enumerate(scored_jobs, 1):
    gl_mark = "✅Tier1" if j.get('green_list') else ("⚠️Tier2" if s >= 70 and 'analyst' in j['title'].lower() else "")
    # Truncate immigration path for table
    p_short = p.split('→')[0] if '→' in p else p[:40]
    report_lines.append(f"| {i} | {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {s}/100 | {gl_mark} | {p_short} |")

report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 重点岗位详细分析")
report_lines.append("")

# Top 5 jobs detailed analysis
for i, (s, j, r, m, p) in enumerate(scored_jobs[:8], 1):
    report_lines.append(f"### {i}. {j['title']} — {j['company']} (匹配度 {s}/100)")
    report_lines.append("")
    report_lines.append(f"- **地点**：{j['location']}")
    report_lines.append(f"- **薪资**：{j['salary']}")
    report_lines.append(f"- **首次发现**：{j.get('first_seen', 'N/A')}")
    report_lines.append(f"- **移民路径**：{p}")
    report_lines.append(f"- **匹配理由**：")
    for reason in r:
        report_lines.append(f"  {reason}")
    report_lines.append(f"- **需补充技能**：")
    for skill in m:
        report_lines.append(f"  - {skill}")
    report_lines.append("")

report_lines.append("---")
report_lines.append("")
report_lines.append("## 移民路径对照")
report_lines.append("")
report_lines.append("| 路径 | 适用岗位 | 条件 | 时限 |")
report_lines.append("|------|----------|------|------|")
report_lines.append("| 绿名单Tier1(Straight to Residence) | 机械工程师 | 有offer + NZQA学历评估 | 即时 |")
report_lines.append("| 绿名单Tier2(Work to Residence) | Business Analyst(薪资≥$95K) | 工签2年后转居留 | 2年 |")
report_lines.append("| SMC(Skilled Migrant Category) | Data Analyst等非绿名单 | 积分制(160分+) | 2-3年 |")
report_lines.append("| Essential Skills工签 | 其他ICT岗位 | 雇主担保+薪资门槛 | 1-3年续签 |")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 行动建议")
report_lines.append("")
report_lines.append("### 🔴 最高优先级（本周必须执行）")
report_lines.append("1. **立即查看Windcave Mechanical Engineer岗位详情页** — 这是绿名单Tier1，移民最优路径首次出现")
report_lines.append("2. **启动NZQA IQA学历评估** — 机械工程学士评估是绿名单前置条件（4-8周，NZ$745）")
report_lines.append("3. **准备PTE考试** — 目标58+（对标雅思6.5），绿名单不硬性要求但雇主会看")
report_lines.append("")
report_lines.append("### 🟡 中优先级（2周内）")
report_lines.append("4. ** Windsor Engineering BSA-ERP** — 如果机械工程师岗位关闭，这是第二选择（ERP经验直接对口）")
report_lines.append("5. **NZ Customs Senior Technical BA** — 政府岗位稳定，但需NZ本地经验")
report_lines.append("6. **Techspace Consulting Senior Technical BA** — 薪资$125-145K，达到绿名单Tier2门槛")
report_lines.append("")
report_lines.append("### 🟢 低优先级（持续关注）")
report_lines.append("7. Stats NZ系列岗位（Data Analyst/Enterprise Portfolio）— 政府稳定但匹配度中等")
report_lines.append("8. Recruitnet Business & Technology Systems Analyst — 薪资$90-110K，Waikato地区")
report_lines.append("9. 行政类岗位不建议主动追求（移民价值极低）")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 岗位统计")
report_lines.append("")
ict_count = len([j for j in unique if j['category'] == 'ICT'])
admin_count = len([j for j in unique if j['category'] == 'Admin'])
high_match = len([s for s, j, r, m, p in scored_jobs if s >= 70])
mid_match = len([s for s, j, r, m, p in scored_jobs if 50 <= s < 70])
low_match = len([s for s, j, r, m, p in scored_jobs if s < 50])
green_list = len([j for j in unique if j.get('green_list')])

report_lines.append(f"- 总岗位数：{len(unique)}（ICT {ict_count} + Admin {admin_count}）")
report_lines.append(f"- 高匹配(≥70分)：{high_match} | 中匹配(50-69分)：{mid_match} | 低匹配(<50分)：{low_match}")
report_lines.append(f"- 绿名单Tier1岗位：{green_list}个（机械工程师）")
report_lines.append(f"- 本轮新增（6/23）：{len(new_since_last)}个")
report_lines.append("")
report_lines.append("---")
report_lines.append(f"*报告生成时间：2026-06-24 08:00 | 下次扫描：2026-06-25 08:00*")

report_content = '\n'.join(report_lines)

# Fix variable name bug
report_content = report_content.replace('{green_match}', f'{green_list}')

# Save report
report_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\SEEK_NZ_Job_Report_2026-06-24.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

# Also save raw JSON
json_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw_0624.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"Report saved: {report_path}")
print(f"JSON saved: {json_path}")
print(f"\n=== SUMMARY ===")
print(f"Total unique jobs: {len(unique)}")
print(f"New since 6/23: {len(new_since_last)}")
print(f"Green List Tier1: {green_list} (Mechanical Engineer!)")
print(f"High match (≥70): {high_match}")
print(f"Mid match (50-69): {mid_match}")
print(f"Low match (<50): {low_match}")
print(f"\n🏆 TOP 5 MATCHES:")
for s, j, r, m, p in scored_jobs[:5]:
    print(f"  {s}/100 - {j['title']} @ {j['company']} | {j['location']} | {j['salary']}")
    print(f"    Immigration: {p}")
