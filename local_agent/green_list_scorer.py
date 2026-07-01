"""
新西兰绿名单 Tier1 ICT 岗位评分器。
严格限定：只给绿名单 Tier1 ICT + 大学/研究机构研究岗高分；
BSA / Data Analyst / 行政 / 机械 一律低分或忽略。
"""

from typing import List, Tuple


GREEN_LIST_TIER1 = {
    "261313": "Software Engineer / Software Developer",
    "262111": "Database Administrator",
    "262113": "Systems Administrator",
    "261311": "Analyst Programmer",
    "261312": "Developer Programmer",
    "261211": "Multimedia Specialist",
    "135112": "ICT Project Manager",
    "262112": "ICT Security Specialist",
    "135111": "Chief Information Officer",
}


def is_research_org(company: str) -> bool:
    keywords = [
        "university", "research institute", "research centre", "research center",
        "crown research", "gns science", "callaghan innovation", "crl",
        "agresearch", "plant & food", "scion", "landcare", "niwa", "branz", "esr",
    ]
    c = company.lower()
    return any(k in c for k in keywords)


def score_job(job: dict) -> Tuple[int, List[str]]:
    title = job["title"].lower()
    company = job["company"].lower()
    location = job["location"].lower()
    score = 0
    reasons = []

    # 1. 角色匹配（0-60）
    if any(k in title for k in ["software engineer", "software developer", "full stack developer", "backend developer", "frontend developer"]):
        score += 55
        reasons.append("绿名单Tier1: Software Engineer (261313)")
    elif "database administrator" in title or "dba" in title:
        score += 55
        reasons.append("绿名单Tier1: Database Administrator (262111)")
    elif "systems administrator" in title or "system administrator" in title:
        score += 55
        reasons.append("绿名单Tier1: Systems Administrator (262113)")
    elif any(k in title for k in ["analyst programmer", "programmer analyst"]):
        score += 55
        reasons.append("绿名单Tier1: Analyst Programmer (261311)")
    elif any(k in title for k in ["developer programmer", "application developer", "software and applications programmer"]):
        score += 55
        reasons.append("绿名单Tier1: Developer Programmer (261312)")
    elif "multimedia specialist" in title:
        score += 55
        reasons.append("绿名单Tier1: Multimedia Specialist (261211)")
    elif "ict project manager" in title or "it project manager" in title:
        score += 55
        reasons.append("绿名单Tier1: ICT Project Manager (135112)")
    elif any(k in title for k in ["ict security", "cyber security", "information security"]):
        score += 55
        reasons.append("绿名单Tier1/Tier2: ICT Security Specialist (262112)")
    elif "chief information officer" in title or "chief digital officer" in title:
        score += 55
        reasons.append("绿名单Tier1: CIO/CDO (135111)")
    elif is_research_org(company) and any(k in title for k in ["research fellow", "postdoctoral", "postdoc", "doctoral candidate", "phd candidate", "research scientist", "research analyst"]):
        score += 50
        reasons.append("大学/研究机构研究岗")
    elif is_research_org(company) and "data scientist" in title:
        score += 48
        reasons.append("大学研究型 Data Scientist")
    elif is_research_org(company) and any(k in title for k in ["information management", "knowledge management", "research information"]):
        score += 45
        reasons.append("大学信息管理研究岗")
    elif "data scientist" in title or "machine learning engineer" in title:
        score += 35
        reasons.append("绿名单Tier2: Data Scientist (Work to Residence)")
    elif "ict support" in title or "network administrator" in title or ("systems analyst" in title and "business systems" not in title):
        score += 30
        reasons.append("绿名单Tier2: ICT Support/Network/Systems Analyst")
    elif any(k in title for k in ["business systems analyst", "business analyst", "erp analyst"]):
        score += 8
        reasons.append("非绿名单:BSA/ERP(已降级)")
    elif any(k in title for k in ["data analyst", "service and data analyst", "reporting analyst"]):
        score += 8
        reasons.append("非绿名单:Data Analyst(已降级)")
    elif any(k in title for k in ["office manager", "administrator", "admin support", "reception", "executive assistant", "coordinator"]):
        score += 2
        reasons.append("行政岗:忽略")
    else:
        score += 5
        reasons.append("非目标岗位")

    # 2. 领域加分（0-15）
    if is_research_org(company):
        score += 15
        reasons.append("大学/研究机构")
    elif any(k in company + " " + title for k in ["government", "ministry", "council", "education review"]):
        score += 10
        reasons.append("政府/公共部门")
    elif any(k in company + " " + title for k in ["ict", "technology", "software", "data", "digital", "cloud", "cyber"]):
        score += 12
        reasons.append("ICT/科技公司")
    elif any(k in company + " " + title for k in ["engineering", "manufacturing", "industrial", "cable", "pump"]):
        score += 5
        reasons.append("工程制造背景(已降级)")

    # 3. 技能关键词加分（0-15）
    if any(k in title for k in ["python", "java", "javascript", "c#", "sql", "cloud", "aws", "azure"]):
        score += 10
        reasons.append("编程/云计算技能")
    if any(k in title for k in ["security", "cyber", "network", "database", "system admin"]):
        score += 10
        reasons.append("ICT基础设施技能")
    if "data" in title and any(k in title for k in ["scientist", "engineer", "machine learning", "ml"]):
        score += 8
        reasons.append("高级数据技能")
    if "sharepoint" in title or "information management" in title:
        score += 5
        reasons.append("Sharepoint/IM(非绿名单降权)")

    # 4. 地点加分（0-8）
    non_akl = ["canterbury", "christchurch", "waikato", "hamilton", "dunedin", "bay of plenty", "whakatane", "hawkes bay", "napier", "hastings", "palmerston north", "manawatu", "marlborough", "otago"]
    if any((", " + k in location or location.endswith(", " + k) or location == k) for k in non_akl):
        score += 8
        reasons.append("非奥克兰地区加分")
    elif location.endswith(", wellington") or location == "wellington":
        score += 5
        reasons.append("惠灵顿地区")

    # 5. 惩罚
    if "part-time" in title or "part time" in title:
        score -= 10
        reasons.append("兼职降分")
    if any(k in title for k in ["junior", "graduate", "entry"]):
        score -= 10
        reasons.append("初级岗降分")
    if "executive assistant" in title:
        score -= 8
        reasons.append("高管助理专业性强")

    return max(0, min(100, score)), reasons


def get_anzsco(title: str) -> Tuple[str, str]:
    """返回 (anzsco_code, occupation_name) 或 ('', '')。"""
    t = title.lower()
    if "software engineer" in t or "software developer" in t or "full stack" in t or "backend" in t or "frontend" in t:
        return "261313", "Software Engineer"
    elif "database administrator" in t or "dba" in t:
        return "262111", "Database Administrator"
    elif "systems administrator" in t or "system administrator" in t:
        return "262113", "Systems Administrator"
    elif "analyst programmer" in t:
        return "261311", "Analyst Programmer"
    elif "developer programmer" in t or "application developer" in t:
        return "261312", "Developer Programmer"
    elif "multimedia specialist" in t:
        return "261211", "Multimedia Specialist"
    elif "ict project manager" in t or "it project manager" in t:
        return "135112", "ICT Project Manager"
    elif any(k in t for k in ["ict security", "cyber security", "information security"]):
        return "262112", "ICT Security Specialist"
    elif "chief information officer" in t or "chief digital officer" in t:
        return "135111", "Chief Information Officer"
    return "", ""


def immigration_path(job: dict) -> str:
    title = job["title"].lower()
    company = job["company"].lower()
    code, name = get_anzsco(title)
    if code in GREEN_LIST_TIER1:
        return f"绿名单Tier1 Straight to Residence | {code} {name} — 有offer即可直申居留"
    elif "data scientist" in title or "ict support" in title or "network administrator" in title or ("systems analyst" in title and "business systems" not in title):
        return "绿名单Tier2 Work to Residence — 需工作2年转居留"
    elif is_research_org(company):
        return "大学/研究机构岗位 — 通常可雇主担保 Accredited Employer Work Visa"
    else:
        return "非绿名单，移民路径弱，建议忽略"


def suggest_skills(job: dict) -> str:
    title = job["title"].lower()
    code, _ = get_anzsco(title)
    if code in GREEN_LIST_TIER1:
        return "1)英文简历突出具体技术栈(Python/SQL/Cloud/Security)；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估"
    elif is_research_org(job["company"]):
        return "1)突出研究经历和论文；2)准备Research Statement；3)联系相关导师"
    elif "data scientist" in title or "machine learning" in title:
        return "1)Python/R + ML项目作品集；2)Kaggle/GitHub展示；3)统计学基础补强"
    else:
        return "非目标岗位，不建议投入精力"
