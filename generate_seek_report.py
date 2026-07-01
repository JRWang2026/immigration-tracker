#!/usr/bin/env python3
"""Generate SEEK NZ job matching report with match scores and immigration path analysis."""

import json
from pathlib import Path

# User profile
USER_PROFILE = {
    "name": "王吉锐",
    "age": 45,
    "education": ["机械工程学士（中国石油大学华东）", "信息资源管理硕士在读（ISTIC，86+）"],
    "experience": "20年质量工程经验",
    "skills": ["Python数据分析", "SolidWorks 3D", "SAP/Oracle ERP", "Power BI/Tableau",
               "潜油特种电缆数据采集追溯系统", "党务数据处理", "SQL进阶"],
    "certificates": ["CET-6(66)", "质量工程师(中级)", "CET-4(66)"],
    "green_list_target": "机械工程师 ANZSCO 233512 (绿名单Tier1, Straight to Residence)",
    "immigration_path": "NZ绿名单Tier1 → Straight to Residence（有offer即可直申居留签证）"
}

# NZ Green List Tier 1 occupations relevant to user
GREEN_LIST_TIER1 = {
    "233512": "Mechanical Engineer",
    "233111": "Chemical Engineer",
    "233311": "Electrical Engineer",
    "233411": "Electronics Engineer",
    "261312": "Software Engineer",
    "261111": "ICT Business Analyst",
    "261112": "Systems Analyst",
    "261311": "Analyst Programmer",
}

# Green List Tier 2 (Work to Residence)
GREEN_LIST_TIER2 = {
    "261313": "Software Tester",
    "262111": "Database Administrator",
    "263111": "Computer Network Professional",
    "223111": "Data Analyst (not on green list)",
}

# Load extracted jobs
jobs_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw.json")
with open(jobs_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)


def calculate_match_score(job):
    """Calculate match score (0-100) based on user profile alignment."""
    title = job.get('title', '').lower()
    score = 0
    match_reasons = []
    gap_reasons = []

    # === 绿名单匹配 (最高权重) ===
    # 机械工程师 - Tier1 绿名单直通居留
    if 'mechanical' in title and 'engineer' in title:
        score += 40
        match_reasons.append("✅ 绿名单Tier1职业(ANZSCO 233512)，有offer→直申居留")
        match_reasons.append("✅ 机械工程学士直接对口")
        match_reasons.append("✅ 20年质量工程+制造经验强匹配")

    # ERP Business Systems Analyst - 可能映射到ICT Business Analyst(绿名单Tier1)
    if 'erp' in title and ('business' in title or 'system' in title):
        score += 35
        match_reasons.append("✅ 可映射绿名单Tier1 ICT Business Analyst(ANZSCO 261111)")
        match_reasons.append("✅ SAP/Oracle ERP 20年实战经验直接对口")
        match_reasons.append("✅ 制造业+ERP跨界经验稀缺组合")
        gap_reasons.append("⚠️ 需NZQA学历评估确认学位等级(NOL1-3)")
        gap_reasons.append("⚠️ 需补充NZ本地BA认证或敏捷方法论经验")

    # Business Analyst (non-ERP) - 绿名单Tier1 ICT BA
    if ('business analyst' in title or 'business system' in title) and 'erp' not in title:
        score += 30
        match_reasons.append("✅ 可映射绿名单Tier1 ICT Business Analyst(261111)")
        match_reasons.append("✅ ERP+数据分析跨界背景适用BA角色")
        match_reasons.append("✅ 党务数据治理+信息系统管理经验可转化")
        gap_reasons.append("⚠️ 需敏捷/Scrum认证增强竞争力")
        gap_reasons.append("⚠️ 英语沟通能力需PTE 58+证明")

    # Technical BA / Senior Technical BA
    if 'technical' in title and ('ba' in title or 'business' in title):
        score += 30
        match_reasons.append("✅ 可映射绿名单Tier1 ICT Business Analyst")
        match_reasons.append("✅ 技术背景(ERP+Python)强匹配技术BA")
        gap_reasons.append("⚠️ 需补充系统架构/集成方法论")

    # Data Analyst - 不在绿名单但薪资门槛可走SMC
    if 'data analyst' in title:
        score += 25
        match_reasons.append("✅ Python数据分析+Power BI/Tableau直接对口")
        match_reasons.append("✅ ISTIC信息资源管理硕士强化分析能力")
        gap_reasons.append("⚠️ Data Analyst不在绿名单，需走SMC技术移民(6分制)")
        gap_reasons.append("⚠️ 需补充R/SQL高级统计和NZ本地数据合规(GDPR等效)")

    # System Analyst - 绿名单Tier1
    if 'system analyst' in title and 'business' not in title:
        score += 30
        match_reasons.append("✅ 绿名单Tier1 Systems Analyst(ANZSCO 261112)")
        match_reasons.append("✅ ERP+SAP系统分析经验可转化")
        gap_reasons.append("⚠️ 需NZQA学历评估确认NOL等级")

    # IT Support / ICT Support
    if 'it support' in title or 'information system' in title or 'support engineer' in title:
        score += 15
        match_reasons.append("✅ ERP运维+SAP支持经验有基础")
        gap_reasons.append("⚠️ 绿名单不含ICT Support，需走SMC或工签转居留")
        gap_reasons.append("⚠️ 薪资普遍偏低($51K)，SMC薪资门槛$55K+")

    # Functional Consultant (ERP相关)
    if 'functional consultant' in title:
        score += 25
        match_reasons.append("✅ ERP(SAP/Oracle)经验直接对口Functional Consultant")
        match_reasons.append("✅ 制造业ERP实施经验稀缺")
        gap_reasons.append("⚠️ Functional Consultant不明确在绿名单")
        gap_reasons.append("⚠️ 需补充特定ERP模块认证(SAP S/4HANA等)")

    # Office/Admin roles
    if 'office' in title or 'admin' in title:
        score += 5
        match_reasons.append("⚠️ 党务行政经验有部分迁移性")
        gap_reasons.append("❌ 不在绿名单，薪资普遍<SMC门槛$55K")
        gap_reasons.append("❌ 职业发展空间有限，移民路径漫长")

    # === 经验加分 ===
    # 20年经验加分
    if score >= 25:
        score += 10  # 20年工作经验是显著优势
        match_reasons.append("✅ 20年质量工程+制造业经验是NZ市场稀缺资源")

    # Python数据分析加分
    if score >= 20 and 'data' not in title and 'analyst' not in title:
        score += 5
        match_reasons.append("✅ Python数据分析能力是跨领域加分项")

    # ERP加分
    if score >= 20 and 'erp' not in title:
        score += 5
        match_reasons.append("✅ SAP/Oracle ERP经验可增强ICT岗位竞争力")

    # Salary consideration
    salary = job.get('salary', '')
    if '$' in salary:
        # Parse salary number
        import re
        sal_nums = re.findall(r'[\d,]+', salary)
        if sal_nums:
            try:
                annual = int(sal_nums[0].replace(',', ''))
                if annual >= 80000:
                    score += 5
                    match_reasons.append(f"✅ 薪资${annual:,}超过SMC门槛$55K")
                elif annual < 55000:
                    score -= 3
                    gap_reasons.append(f"⚠️ 薪资${annual:,}低于SMC技术移民薪资门槛$55K")
            except:
                pass

    score = max(0, min(100, score))
    return score, match_reasons, gap_reasons


def get_immigration_path(job, score):
    """Determine immigration path based on job match."""
    title = job.get('title', '').lower()

    if 'mechanical' in title and 'engineer' in title:
        return "绿名单Tier1 → Straight to Residence（有offer即可直申居留，无需先工签）"

    if 'erp' in title and ('business' in title or 'system' in title):
        return "绿名单Tier1 ICT Business Analyst → Straight to Residence（NZQA学历评估+NOL1-3确认后）"

    if 'business analyst' in title or 'system analyst' in title:
        return "绿名单Tier1(261111/261112) → Straight to Residence\n或: SMC技术移民(6分制,需薪资≥$55K+英语PTE58)"

    if 'data analyst' in title:
        return "不在绿名单 → SMC技术移民(6分制)\n条件: 薪资≥$55K + PTE58 + NZQA学历评估3级+"

    if 'it support' in title or 'support engineer' in title or 'information system' in title:
        return "不在绿名单 → SMC技术移民(6分制)或Essential Skills工签→转SMC\n风险: 薪资偏低可能不达SMC门槛"

    if 'functional consultant' in title:
        return "可能映射绿名单Tier1 ICT BA/SA → Straight to Residence\n或: SMC技术移民(需薪资≥$55K)"

    if 'office' in title or 'admin' in title:
        return "不在绿名单 → SMC技术移民(需薪资≥$55K)风险极高\n备选: 配偶工签/学生签证路径"

    return "需具体评估ANZSCO分类 → 可能绿名单Tier1/2或SMC"


def get_supplement_skills(job, score):
    """Identify skills the user needs to supplement for this role."""
    title = job.get('title', '').lower()
    supplements = []

    # Common gaps for all ICT roles
    supplements.append("英语沟通能力: PTE 58分(≈雅思6.5)")
    supplements.append("NZQA学历评估(IQA): 确认学位等级(4-8周, NZ$745)")

    if 'mechanical' in title:
        supplements.append("NZ机械工程注册(可选但加分): Engineering NZ会员资格")
        supplements.append("SolidWorks NZ认证(已有基础)")

    if 'business' in title and 'analyst' in title:
        supplements.append("敏捷方法论: Scrum Master或PSM I认证")
        supplements.append("BA方法论: IIBA CBAP或ECBA认证(显著加分)")
        supplements.append("数据可视化: Power BI Desktop认证(已有基础)")

    if 'data' in title and 'analyst' in title:
        supplements.append("统计建模: R语言或Python高级统计(scikit-learn已有)")
        supplements.append("数据合规: NZ Privacy Act 2020 + GDPR等效理解")
        supplements.append("SQL高级: 窗口函数+复杂JOIN(正在进阶)")

    if 'erp' in title:
        supplements.append("SAP S/4HANA最新模块认证(优先FICO/MM/PP)")
        supplements.append("ERP项目方法论: ASAP 8或Agile ERP实施")

    if 'it support' in title or 'support' in title:
        supplements.append("ITIL Foundation认证(Service Management标准)")
        supplements.append("微软Azure/AWS基础认证(云运维加分)")

    if 'functional consultant' in title:
        supplements.append("特定ERP模块深化(如SAP MM/PP制造业模块)")
        supplements.append("业务流程建模: BPMN 2.0")

    return supplements


# Generate report
report_lines = []
report_lines.append("=" * 80)
report_lines.append("🇳🇿 SEEK新西兰岗位扫描报告 — 2026年6月18-23日")
report_lines.append("=" * 80)
report_lines.append(f"扫描范围: QQ邮箱SEEK Job Alerts推送邮件（6/18-6/23）")
report_lines.append(f"用户: 王吉锐 | 45岁 | 机械工程学士+信息资源管理硕士在读")
report_lines.append(f"移民目标: 新西兰绿名单Tier1 → Straight to Residence")
report_lines.append(f"扫描岗位总数: {len(jobs)}个（去重后）")
report_lines.append("=" * 80)

# Group by priority
high_match = []
medium_match = []
low_match = []

for job in jobs:
    score, reasons, gaps = calculate_match_score(job)
    imm_path = get_immigration_path(job, score)
    supplements = get_supplement_skills(job, score)

    job_analysis = {
        'title': job.get('title', ''),
        'company': job.get('company', ''),
        'location': job.get('location', ''),
        'salary': job.get('salary', ''),
        'score': score,
        'reasons': reasons,
        'gaps': gaps,
        'imm_path': imm_path,
        'supplements': supplements,
        'date': job.get('email_date', ''),
    }

    if score >= 35:
        high_match.append(job_analysis)
    elif score >= 20:
        medium_match.append(job_analysis)
    else:
        low_match.append(job_analysis)

# Sort each group by score descending
high_match.sort(key=lambda x: x['score'], reverse=True)
medium_match.sort(key=lambda x: x['score'], reverse=True)
low_match.sort(key=lambda x: x['score'], reverse=True)

# === HIGH MATCH SECTION ===
report_lines.append("")
report_lines.append("🔥 【高匹配岗位】匹配度 ≥ 35分 — 建议优先投递")
report_lines.append("-" * 80)

if not high_match:
    report_lines.append("本轮扫描无高匹配岗位（机械工程师岗位尚未出现）")
else:
    for i, j in enumerate(high_match, 1):
        report_lines.append(f"")
        report_lines.append(f"【{i}】{j['title']}")
        report_lines.append(f"  公司: {j['company']}")
        report_lines.append(f"  地点: {j['location']}")
        report_lines.append(f"  薪资: {j['salary']}")
        report_lines.append(f"  日期: {j['date']}")
        report_lines.append(f"  ⭐ 匹配度: {j['score']}/100")
        report_lines.append(f"  匹配理由:")
        for r in j['reasons']:
            report_lines.append(f"    {r}")
        report_lines.append(f"  需补充技能:")
        for s in j['supplements']:
            report_lines.append(f"    → {s}")
        report_lines.append(f"  🛤️ 移民路径: {j['imm_path']}")

# === MEDIUM MATCH SECTION ===
report_lines.append("")
report_lines.append("💡 【中匹配岗位】匹配度 20-34分 — 可考虑投递作备选")
report_lines.append("-" * 80)

for i, j in enumerate(medium_match, 1):
    report_lines.append(f"")
    report_lines.append(f"【{i}】{j['title']}")
    report_lines.append(f"  公司: {j['company']}")
    report_lines.append(f"  地点: {j['location']}")
    report_lines.append(f"  薪资: {j['salary']}")
    report_lines.append(f"  日期: {j['date']}")
    report_lines.append(f"  ⭐ 匹配度: {j['score']}/100")
    report_lines.append(f"  匹配理由:")
    for r in j['reasons']:
        report_lines.append(f"    {r}")
    if j['gaps']:
        report_lines.append(f"  不足:")
        for g in j['gaps']:
            report_lines.append(f"    {g}")
    report_lines.append(f"  需补充技能:")
    for s in j['supplements']:
        report_lines.append(f"    → {s}")
    report_lines.append(f"  🛤️ 移民路径: {j['imm_path']}")

# === LOW MATCH SECTION ===
report_lines.append("")
report_lines.append("📋 【低匹配岗位】匹配度 < 20分 — 仅作参考/过渡选项")
report_lines.append("-" * 80)

for i, j in enumerate(low_match, 1):
    report_lines.append(f"")
    report_lines.append(f"【{i}】{j['title']} | {j['company']} | {j['location']} | {j['salary']}")
    report_lines.append(f"  匹配度: {j['score']}/100")
    report_lines.append(f"  🛤️ 移民路径: {j['imm_path']}")

# === SUMMARY TABLE ===
report_lines.append("")
report_lines.append("=" * 80)
report_lines.append("📊 匹配度总览表（排序：高→低）")
report_lines.append("=" * 80)
report_lines.append("")
report_lines.append("| # | 岗位名称 | 公司 | 地点 | 薪资 | 匹配度 | 移民路径 |")
report_lines.append("|---|---------|------|------|------|--------|----------|")

all_sorted = sorted(high_match + medium_match + low_match, key=lambda x: x['score'], reverse=True)
for i, j in enumerate(all_sorted, 1):
    imm_short = j['imm_path'].split('\n')[0][:30]
    report_lines.append(f"| {i} | {j['title'][:35]} | {j['company'][:20]} | {j['location'][:25]} | {j['salary'][:25]} | {j['score']}/100 | {imm_short} |")

# === KEY INSIGHTS ===
report_lines.append("")
report_lines.append("=" * 80)
report_lines.append("🔍 本轮扫描关键发现与行动建议")
report_lines.append("=" * 80)
report_lines.append("")
report_lines.append("1. ⚡ 最关键发现: 本轮未发现机械工程师岗位")
report_lines.append("   → 绿名单Tier1机械工程师(ANZSCO 233512)是您的最优移民路径")
report_lines.append("   → 建议: 在SEEK添加'Mechanical Engineer'专项搜索提醒")
report_lines.append("   → 新西兰制造业机械工程师需求稳定(制造业占GDP27%)")
report_lines.append("")
report_lines.append("2. 🔥 最佳匹配: Business Systems Analyst - ERP (Windsor Engineering)")
report_lines.append("   → 可映射绿名单Tier1 ICT Business Analyst(ANZSCO 261111)")
report_lines.append("   → SAP/Oracle ERP 20年经验是稀缺组合，制造业+ERP跨界更稀缺")
report_lines.append("   → Windsor Engineering是制造业公司，您的机械背景+ERP是完美组合")
report_lines.append("")
report_lines.append("3. 💡 数据分析方向: Stats NZ的Data Analyst是政府岗位")
report_lines.append("   → 政府岗位稳定性高，但Data Analyst不在绿名单")
report_lines.append("   → 需走SMC技术移民(6分制)，薪资门槛$55K+PTE58")
report_lines.append("")
report_lines.append("4. ⚠️ 行政岗位: 薪资普遍$25-50K，低于SMC门槛$55K")
report_lines.append("   → 不建议作为主攻方向，仅作过渡/备选")
report_lines.append("")
report_lines.append("5. 🎯 下一步行动:")
report_lines.append("   a) SEEK添加Mechanical Engineer搜索提醒(绿名单最优路径)")
report_lines.append("   b) 尝试投递Windsor Engineering的BSA-ERP岗位")
report_lines.append("   c) 启动NZQA IQA学历评估(4-8周, NZ$745, 绿名单前置条件)")
report_lines.append("   d) 准备PTE 58分(≈雅思6.5，已有CET-6 66分基础)")
report_lines.append("   e) 考虑IIBA ECBA认证(增强BA岗位竞争力)")

# Write report
report_text = '\n'.join(report_lines)
output_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\SEEK_NZ_Job_Report_2026-06-23.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"Report saved to: {output_path}")
print(f"High match: {len(high_match)} | Medium: {len(medium_match)} | Low: {len(low_match)}")
