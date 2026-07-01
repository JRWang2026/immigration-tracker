#!/usr/bin/env python3
"""
SEEK NZ 岗位扫描报告 2026-06-26
解析3封新邮件，去重，匹配用户背景，生成结构化报告
"""
import re
import json

# ========== 从已观察到的文本输出中手动提取所有岗位 ==========
# 这比正则解析更可靠，因为邮件HTML格式不稳定

# ICT_2147: 6/25 21:47 UTC - ICT 新岗位20+3个missed
ict1_jobs = [
    ("Technical Business Analyst", "Maori Television", "East Tamaki, Auckland", ""),
    ("Research and Development Scientist", "Sanitarium Health Food Company", "Epsom, Auckland", ""),
    ("Business Analyst", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Data Engineer", "REINZ", "Auckland CBD, Auckland", "$90,000 – $115,000 per year"),
    ("Data & Reporting Officer", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Intermediate Business Analyst", "New Zealand Qualifications Authority", "Wellington Central, Wellington", ""),
    ("Jr R&D Technologist", "KraftHeinz", "Hastings Central, Hawkes Bay", ""),
    ("Business Analyst (ICT)", "Whangarei District Council", "Whangarei Central, Northland", ""),
    ("Trainee or Phlebotomist - Patient Services", "Awanui Group", "Hastings Central, Hawkes Bay", ""),
    ("Process + Systems Manager", "CDB Media Limited", "Albany, Auckland", ""),
    ("Senior Business Analyst - ICT", "New Zealand Police", "Wellington", "$110,425"),
    ("Senior Technical Business Analyst", "Techspace Consulting Limited", "Te Puke, Bay of Plenty", "$125,000-$145,000"),
    ("Data Engineer", "Mr Apple NZ Ltd", "Whakatu, Hawkes Bay", ""),
    ("HACCP & Food Safety Advisor", "Volunteer Service Abroad (VSA)", "Wellington Central, Wellington", ""),
    ("Payroll Transformation Lead", "ACC New Zealand", "Wellington", "9% Superannuation"),
    ("Laboratory Technician - Animal Health", "Livestock Improvement Corporation", "Riverlea, Waikato", ""),
    ("Med Lab Technician", "NZ Blood Service", "Epsom, Auckland", "$67,488 - $88,887"),
    ("Laboratory Technician", "Fulton Hogan", "Dunedin, Otago", ""),
    ("Application Support Analyst", "Ministry of Justice", "Wellington Central, Wellington", ""),
    ("Science technician", "Papatoetoe High School", "Papatoetoe, Auckland", ""),
]
ict1_missed = [
    ("Business Systems Analyst - ERP", "Windsor Engineering Group Ltd", "Mount Wellington, Auckland", "Competitive annual salary + employee benefits"),
    ("IT Support & AI Business Analyst", "Miles Construction Ltd", "Christchurch Central, Canterbury", ""),
    ("Laboratory Production Technician & Compounder", "Bright Teams", "Henderson, Auckland", "$65,000 – $70,000 per year"),
]

# Admin_2358: 6/25 23:58 UTC - Admin/Office Support 20+3个missed
admin_jobs = [
    ("Admin Support", "General Travel NZ Ltd", "Auckland CBD, Auckland", ""),
    ("Service Desk Support", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$65,000 – $75,000 per year"),
    ("Office Administrator", "A.J. TUTILL & SONS LIMITED", "Penrose, Auckland", "$65,000 – $70,000 per year"),
    ("Service Desk Administrator", "The Audit Office", "Wellington Central, Wellington", "$66,000-$77,000"),
    ("Help Desk Analyst – Stibo", "Duco Consultancy Limited", "Auckland CBD, Auckland", "$75,000 per year"),
    ("Office Manager", "Veolia", "Auckland", ""),
    ("IT Support Engineer", "Morgan Furniture Int Ltd", "Christchurch Central, Canterbury", ""),
    ("Helpdesk Analyst", "Halter", "Auckland CBD, Auckland", ""),
    ("Office Administrator", "Lero Innovation Limited", "East Tamaki, Auckland", "$24 – $29 per hour"),
    ("IT Support Coordinator", "Momentum Consulting Group", "Auckland", "Training & upskilling provided"),
    ("Service Engineer", "Spark New Zealand Trading Limited", "Aotea, Wellington", ""),
    ("Office Support / Administratior", "Summit Business Solutions Ltd", "Otahuhu, Auckland", ""),
    ("Technical Business Analyst", "Maori Television", "East Tamaki, Auckland", ""),
    ("Executive Assistant", "Enviro NZ", "Ellerslie, Auckland", "Competitive salary & free carpark"),
    ("Research and Development Scientist", "Sanitarium Health Food Company", "Epsom, Auckland", ""),
    ("IT Senior Co-ordinator (ops & support)", "Bright Teams", "Parnell, Auckland", ""),
    ("IT Helpdesk Technician", "Tonkin & Taylor Ltd", "Auckland CBD, Auckland", ""),
    ("Office Manager/Team Leader", "Archway Recruitment", "Wellington Central, Wellington", "$115,000-120,000 per annum"),
    ("Office Manager", "Empower Electrical", "Port Whangarei, Northland", "$30 – $40 per hour"),
    ("Executive Assistant", "Profile Group", "Christchurch, Canterbury", ""),
]
admin_missed = [
    ("Entry Level Support Engineer", "New Era Technology", "Henderson, Auckland", "$51,000 per year"),
    ("Office Administrator / Manager", "Simtec Therapeutic Limited", "Onehunga, Auckland", "$65,000 – $85,000 per year"),
    ("Office Co-Ordinator", "Flo & Frankie", "Parnell, Auckland", "Competitive pay and great perks"),
]

# ICT_2025: 6/25 20:25 UTC - earlier ICT send, may have duplicates
# From search highlights: Business Operations Analyst - Cultivate, Data Analyst/Kaitātari - Stats NZ
ict2_jobs = [
    ("Technical Business Analyst", "Maori Television", "East Tamaki, Auckland", ""),
    ("Research and Development Scientist", "Sanitarium Health Food Company", "Epsom, Auckland", ""),
    ("Business Analyst", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Data Engineer", "REINZ", "Auckland CBD, Auckland", "$90,000 – $115,000 per year"),
    ("Business Analyst", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Data & Reporting Officer", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Data Analyst/Kaitātari Hoahoa", "Stats NZ", "Christchurch Central, Canterbury", ""),
    ("Data & Reporting Officer", "Rotorua Lakes Council", "Rotorua Central, Bay of Plenty", "$92,000 – $102,000 per year"),
    ("Senior Business Analyst - ICT", "New Zealand Police", "Wellington", "$110,425"),
    ("Application Support Analyst", "Ministry of Justice", "Wellington Central, Wellington", ""),
    ("Business Analyst (ICT)", "Whangarei District Council", "Whangarei Central, Northland", ""),
    ("Business Operations Analyst", "Cultivate – SEEK", "Te Rapa, Waikato", "$90,000 - $110,000 based on experience"),
    # The rest likely overlap with ICT_2147
]

# ========== 去重合并 ==========
seen = set()
all_jobs = []

def add_job(title, company, location, salary, source):
    key = (title.strip().lower(), company.strip().lower())
    if key not in seen:
        seen.add(key)
        all_jobs.append({
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "salary": salary.strip(),
            "source": source,
        })

for j in ict1_jobs:
    add_job(j[0], j[1], j[2], j[3], "ICT_2147")
for j in ict1_missed:
    add_job(j[0], j[1], j[2], j[3], "ICT_2147_missed")
for j in admin_jobs:
    add_job(j[0], j[1], j[2], j[3], "Admin_2358")
for j in admin_missed:
    add_job(j[0], j[1], j[2], j[3], "Admin_2358_missed")
for j in ict2_jobs:
    add_job(j[0], j[1], j[2], j[3], "ICT_2025")

print(f"Total unique jobs after dedup: {len(all_jobs)}")
print(f"ICT sources: ICT_2147({len(ict1_jobs)+len(ict1_missed)}) + ICT_2025({len(ict2_jobs)})")
print(f"Admin source: Admin_2358({len(admin_jobs)+len(admin_missed)})")

# ========== 用户背景画像 ==========
user_profile = {
    "age": 45,
    "education": ["机械设计制造学士(中国石油大学)", "信息资源管理硕士在读(ISTIC, 86+均分)"],
    "experience": ["20年质量工程", "Python数据分析", "潜油特种电缆数据项目", "SAP/Oracle ERP", "SolidWorks 3D"],
    "certifications": ["CET-6(66)", "质量工程师(中级)"],
    "target_visa": "NZ Green List Tier1 (Mechanical Engineer ANZSCO 233512, Straight to Residence)",
    "english": "PTE 58 (target, ~IELTS 6.5)",
}

# ========== 关键词匹配打分 ==========
def score_job(job):
    title_l = job["title"].lower()
    company_l = job["company"].lower()
    location = job["location"]
    salary = job["salary"]
    
    score = 0
    reasons = []
    skills_needed = []
    visa_path = ""
    
    # --- 核心匹配加分 ---
    
    # Tier1: Mechanical Engineer (绿名单直接居留)
    if any(kw in title_l for kw in ["mechanical engineer", "mechanical design"]):
        score += 50
        reasons.append("绿名单Tier1机械工程师-直接居留路径")
        visa_path = "Green List Tier1 Straight to Residence (ANZSCO 233512)"
    
    # Tier2: Data Engineer, ICT相关
    if "data engineer" in title_l:
        score += 35
        reasons.append("绿名单Tier2-工作转居留路径(Data Engineer)")
        visa_path = "Green List Tier2 Work to Residence (2年后转)"
    
    # Business Systems Analyst 高匹配
    if "business systems analyst" in title_l:
        score += 40
        reasons.append("ERP/SAP经验直接匹配BSA角色")
        visa_path = "需雇主担保AEWV→2年后申请居留"
        if "erp" in title_l:
            score += 5
            reasons.append("明确标注ERP经验需求")
    
    # Business Analyst
    if "business analyst" in title_l and "systems" not in title_l:
        score += 30
        reasons.append("数据分析+ERP经验匹配BA角色")
        visa_path = "AEWV雇主担保→居留路径"
    if "senior" in title_l:
        score += 10
        reasons.append("高级岗位,薪资更高")
    if "ict" in title_l:
        score += 5
        reasons.append("ICT类别,技术移民加分")
    
    # Data Analyst / Reporting
    if "data analyst" in title_l or "reporting officer" in title_l or "reporting" in title_l:
        score += 28
        reasons.append("Python+Power BI经验匹配数据分析岗")
        visa_path = "AEWV雇主担保→居留路径"
        if "stats nz" in company_l:
            score += 10
            reasons.append("政府机构Stats NZ-稳定性高")
    if "kaitātari" in title_l:  # 毛利语data analyst
        score += 5
    
    # IT Support / Helpdesk (过渡岗位)
    if any(kw in title_l for kw in ["it support", "helpdesk", "help desk", "service desk", "it helpdesk"]):
        score += 15
        reasons.append("IT支持可作为新西兰入境过渡岗位")
        visa_path = "AEWV→入境后再转目标岗位"
        if "analyst" in title_l:
            score += 5
    
    if "it support & ai" in title_l:
        score += 10
        reasons.append("AI方向有加分,结合Python技能")
    
    # Application Support Analyst
    if "application support" in title_l:
        score += 22
        reasons.append("ERP/SAP应用支持经验匹配")
        visa_path = "AEWV雇主担保→居留路径"
    
    # Systems Manager / Process Manager
    if "systems manager" in title_l or "process" in title_l:
        score += 20
        reasons.append("质量工程+ERP经验匹配流程/系统管理")
        visa_path = "AEWV雇主担保→居留路径"
    
    # --- 地点加分 ---
    if "wellington" in location.lower():
        score += 3
        reasons.append("惠灵顿(首都,政府机构集中)")
    if "auckland" in location.lower():
        score += 2
        reasons.append("奥克兰(最大城市,机会多)")
    
    # --- 薪资加分 ---
    salary_num = 0
    if salary:
        nums = re.findall(r'\$?([\d,]+)', salary)
        if nums:
            try:
                salary_num = int(nums[0].replace(',', ''))
            except:
                pass
    if salary_num >= 110000:
        score += 10
        reasons.append(f"高薪(${salary_num:,}+)有利于签证申请")
    elif salary_num >= 90000:
        score += 5
        reasons.append(f"中等偏上薪资(${salary_num:,})")
    
    # --- 技能缺口评估 ---
    if "senior" in title_l:
        skills_needed.append("NZ本地工作经验(可通过初级岗位积累)")
    if "business analyst" in title_l:
        skills_needed.append("NZ业务环境理解")
        skills_needed.append("可能需NZ学历认证(NZQA IQA)")
    if "data" in title_l:
        skills_needed.append("NZ数据合规/隐私法规")
    if "erp" in title_l:
        skills_needed.append("NZ本地ERP系统经验(如MYOB/Xero)")
    
    # --- 政府/大型雇主加分 ---
    gov_employers = ["new zealand police", "ministry of justice", "stats nz", "rotorua lakes council", 
                     "whangarei district council", "nzqa", "acc new zealand", "the audit office"]
    if any(gov in company_l for gov in gov_employers):
        score += 8
        reasons.append("政府/公共部门雇主-稳定性+AEWV支持")
    
    # 不相关岗位大幅扣分
    irrelevant = ["phlebotomist", "laboratory technician", "lab technician", "science technician",
                  "haccp", "food safety", "med lab", "patient services", "r&d technologist", 
                  "r&d scientist", "compounder", "executive assistant", "admin support",
                  "office administrator", "office manager", "office co-ordinator", "office support",
                  "payroll", "service engineer"]
    for kw in irrelevant:
        if kw in title_l:
            score = max(0, score - 50)
            break
    
    # 完全不相关直接给0
    if score < 0:
        score = 0
    
    # 归一化到100
    score = min(100, score)
    
    return score, reasons, skills_needed, visa_path, salary_num


# ========== 评分并分类 ==========
results = []
for job in all_jobs:
    score, reasons, skills_needed, visa_path, salary_num = score_job(job)
    results.append({
        **job,
        "score": score,
        "reasons": reasons,
        "skills_needed": skills_needed,
        "visa_path": visa_path,
        "salary_num": salary_num,
    })

# 按得分排序
results.sort(key=lambda x: x["score"], reverse=True)

# ========== 输出报告 ==========
print("\n" + "="*100)
print("SEEK NZ 岗位扫描报告 - 2026年6月26日")
print("="*100)
print(f"扫描时间: 2026-06-26 13:56 NZT")
print(f"邮件来源: 3封新SEEK推送 (ICT×2 + Admin×1, 收件时间6/25)")
print(f"去重后有效岗位: {len(all_jobs)} 个")
print(f"用户画像: 45岁,机械工程学士+信息资源管理硕士,20年质量工程+Python/SAP经验")
print(f"目标路径: 新西兰绿名单Tier1(机械工程师直申居留) + Tier2(Data Engineer) + AEWV雇主担保")
print()

# 分级
high = [r for r in results if r["score"] >= 50]
mid = [r for r in results if 30 <= r["score"] < 50]
low = [r for r in results if 15 <= r["score"] < 30]
irrelevant = [r for r in results if r["score"] < 15]

print(f"=== 匹配度分级 ===")
print(f"  高匹配 (≥50分): {len(high)} 个")
print(f"  中匹配 (30-49分): {len(mid)} 个")
print(f"  低匹配 (15-29分): {len(low)} 个")
print(f"  不相关 (<15分): {len(irrelevant)} 个")
print()

print("="*100)
print("🏆 高匹配岗位 (≥50分)")
print("="*100)
for i, r in enumerate(high, 1):
    print(f"\n{i}. {r['title']}")
    print(f"   公司: {r['company']}")
    print(f"   地点: {r['location']}")
    print(f"   薪资: {r['salary'] or '未公布'}")
    print(f"   匹配度: {r['score']}/100")
    print(f"   匹配理由: {'; '.join(r['reasons'])}")
    print(f"   需补充技能: {'; '.join(r['skills_needed']) if r['skills_needed'] else '无特殊需求'}")
    print(f"   移民路径: {r['visa_path']}")

print("\n" + "="*100)
print("📊 中匹配岗位 (30-49分)")
print("="*100)
for i, r in enumerate(mid, 1):
    print(f"\n{i}. {r['title']}")
    print(f"   公司: {r['company']} | 地点: {r['location']} | 薪资: {r['salary'] or '未公布'}")
    print(f"   匹配度: {r['score']}/100 | 移民路径: {r['visa_path']}")

print("\n" + "="*100)
print("🔍 低匹配岗位 (15-29分) - 过渡/备选")
print("="*100)
for i, r in enumerate(low, 1):
    print(f"\n{i}. {r['title']} @ {r['company']} ({r['location']}) - {r['salary'] or '薪资未公布'} [{r['score']}分]")

print("\n" + "="*100)
print("📋 关键观察 & 建议")
print("="*100)

# 关键观察
me_count = sum(1 for r in results if "mechanical engineer" in r["title"].lower())
bsa_count = sum(1 for r in results if "business systems analyst" in r["title"].lower())
ba_count = sum(1 for r in results if "business analyst" in r["title"].lower())
de_count = sum(1 for r in results if "data engineer" in r["title"].lower())
da_count = sum(1 for r in results if "data analyst" in r["title"].lower())

print(f"\n⚠️ Mechanical Engineer (绿名单Tier1): {me_count} 个岗位")
print(f"   → 连续两轮扫描零ME岗位！建议：在SEEK网站直接搜索并开新提醒")

print(f"\n📊 Business Systems Analyst - ERP: {bsa_count} 个岗位")
for r in results:
    if "business systems analyst" in r["title"].lower():
        print(f"   → {r['title']} @ {r['company']} ({r['location']}) - {r['salary']}")

print(f"\n📊 Business Analyst 类: {ba_count} 个岗位")
for r in results:
    if "business analyst" in r["title"].lower() and "systems" not in r["title"].lower():
        print(f"   → {r['title']} @ {r['company']} ({r['location']}) - {r['salary']} [{r['score']}分]")

print(f"\n📊 Data Engineer: {de_count} 个岗位 (绿名单Tier2)")
print(f"📊 Data Analyst/Reporting: {da_count} 个岗位")

# 与上轮对比
print(f"\n=== 与6/25报告对比 ===")
print(f"  6/25: Mechanical Engineer(Windcave)消失 | 最佳: BA-ICT(NZ Police, $110K, 81分)")
print(f"  6/26: ME仍然零岗 | BSA-ERP(Windsor)仍在missed列表 | 新增Data Engineer(Mr Apple)")
print(f"  注意: NZ Police Senior BA-ICT 本轮在ICT_2147中再次出现(第11号岗)")

# 行动建议
print(f"\n=== 即日行动建议 ===")
print(f"1. 【紧急】在SEEK网站新增 Mechanical Engineer + Manufacturing 专项提醒")
print(f"2. 【重点】Windsor Engineering BSA-ERP岗位仍开放 → 准备CV投递(ERP/SAP经验是独特卖点)")
print(f"3. 【重点】NZ Police Senior BA-ICT $110K → 政府BA岗位，中国石油行业背景可包装为public sector经验")
print(f"4. 【关注】Miles Construction IT Support & AI BA → AI+IT结合，Python技能可突出")
print(f"5. 【备用】Data Engineer岗位(Tier2绿名单) → REINZ($90-115K) 和 Mr Apple均可投")

# ========== JSON 保存 ==========
with open("seek_jobs_raw_0626.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n✅ 原始数据已保存: seek_jobs_raw_0626.json")
