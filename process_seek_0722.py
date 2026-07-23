#!/usr/bin/env python3
"""
SEEK NZ 岗位扫描处理器 — 2026-07-22
处理 QQ Mail connector 拉取的邮件，生成绿名单 Tier1 聚焦报告 + KOS JSON。
"""

import json
import re
import html
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
WORKSPACE = Path("C:/Users/Mr_Wang/WorkBuddy/2026-06-20-14-48-36")
KOS_DIR = Path("C:/Users/Mr_Wang/WorkBuddy/2026-06-03-14-49-17/kos/public/data/seek-nz")
REPORTS_DIR = WORKSPACE / "local_agent_output"
DATA_DIR = WORKSPACE / "data"

# 工具结果文件目录（包含被截断保存的大邮件）
TOOL_RESULTS_DIR = Path("C:/Users/Mr_Wang/.workbuddy/projects/c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36/0e4d80f6-58cf-4e94-b7b5-b9755877c49f/tool-results")

# ---------------------------------------------------------------------------
# HTML 解析器（兼容 MJML 模板）
# ---------------------------------------------------------------------------
def _strip_mso_comments(body: str) -> str:
    return re.sub(r'<!--\[if mso \| IE\]>.*?<!\[endif\]-->', '', body, flags=re.DOTALL)

def extract_jobs_from_html(body: str) -> List[Dict[str, str]]:
    jobs = []
    cleaned = _strip_mso_comments(body)
    card_pattern = '<a style="display: block"'
    cards = cleaned.split(card_pattern)

    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(
            r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card
        )
        loc_matches = re.findall(
            r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>',
            card,
        )
        salary_match = re.search(r'>\$[^<]+</div>', card)
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        url_match = re.search(r'href="([^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue

        location = "Unknown"
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm
                break
            elif lm and lm not in [title, company] and location == "Unknown":
                location = lm

        salary = ""
        if salary_match:
            raw = salary_match.group(0)
            m = re.search(r'\$[^<]+', raw)
            if m:
                salary = m.group(0).strip()
        else:
            for lm in loc_matches:
                lm = lm.strip()
                if lm.startswith('$') or '$' in lm:
                    salary = lm
                    if location == salary:
                        location = "Unknown"
                    break

        if salary and location == salary:
            for lm in loc_matches:
                lm = lm.strip()
                if lm != salary and lm not in [title, company]:
                    location = lm
                    break

        posted_date = date_match.group(1) if date_match else ""
        url = url_match.group(1) if url_match else ""

        jobs.append({
            "title": html.unescape(title),
            "company": html.unescape(company),
            "location": html.unescape(location),
            "salary": html.unescape(salary),
            "posted_date": posted_date,
            "url": url,
            "source": "SEEK NZ email",
        })

    return jobs

def deduplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for j in jobs:
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique

# ---------------------------------------------------------------------------
# 评分器
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 读取工具结果文件中的邮件正文
# ---------------------------------------------------------------------------
def extract_body_from_tool_result(filepath: Path) -> str:
    """从 QQ Mail connector 工具结果文件中提取 body HTML。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 工具结果文件是 JSON 格式，但可能被截断
    # 尝试提取 body 字段
    # 格式通常是 JSON 嵌套在文本中
    
    # 方法1: 尝试找 body 字段
    body_match = re.search(r'"body"\s*:\s*"(.+?)"\s*,\s*"body_format"', content, re.DOTALL)
    if body_match:
        body = body_match.group(1)
        # 处理转义字符
        body = body.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        return body
    
    # 方法2: 如果文件被截断，尝试提取所有 <a style="display: block"> 附近的内容
    # 直接返回整个内容，让解析器尝试
    return content

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    date_str = "2026-07-22"
    run_time = datetime.now()
    
    all_raw_jobs = []
    email_count = 0
    
    # 1. 读取工具结果文件中的大邮件
    if TOOL_RESULTS_DIR.exists():
        for f in TOOL_RESULTS_DIR.glob("mcp-connector-proxy-qq-mail_GetMessage-*.txt"):
            body = extract_body_from_tool_result(f)
            if len(body) > 500:
                jobs = extract_jobs_from_html(body)
                if jobs:
                    all_raw_jobs.extend(jobs)
                    email_count += 1
                    print(f"  文件 {f.name}: 提取 {len(jobs)} 个岗位")
                else:
                    print(f"  文件 {f.name}: 0 个岗位（HTML解析可能失败）")
    
    print(f"\n总计：{email_count} 封邮件，{len(all_raw_jobs)} 个原始岗位")
    
    # 2. 去重
    unique_jobs = deduplicate_jobs(all_raw_jobs)
    print(f"去重后：{len(unique_jobs)} 个岗位")
    
    # 3. 评分
    for j in unique_jobs:
        score, reasons = score_job(j)
        j["score"] = score
        j["reasons"] = reasons
        j["immigration_path"] = immigration_path(j)
        j["suggested_skills"] = suggest_skills(j)
        code, name = get_anzsco(j["title"])
        j["anzsco_code"] = code
        j["anzsco_name"] = name
    
    unique_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. 分类统计
    tier1 = [j for j in unique_jobs if j["score"] >= 60]
    research = [j for j in unique_jobs if 40 <= j["score"] < 60]
    others = [j for j in unique_jobs if j["score"] < 40]
    
    print(f"\n分类统计：")
    print(f"  Tier1 (≥60): {len(tier1)}")
    print(f"  研究岗 (40-59): {len(research)}")
    print(f"  其他 (<40): {len(others)}")
    
    # 5. 生成 Markdown 报告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = REPORTS_DIR / f"SEEK_NZ_Job_Report_{date_str}.md"
    
    lines = [
        f"# SEEK NZ 绿名单 Tier1 ICT 扫描报告 — {date_str}",
        "",
        f"> 运行时间：{run_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 扫描邮件：{email_count} 封 | 去重岗位：{len(unique_jobs)} 个 | 绿名单 Tier1 匹配：{len(tier1)} 个",
        "",
        "---",
        "",
        "## 一、绿名单 Tier1 ICT 高匹配岗位（≥60分）",
        "",
    ]
    
    if tier1:
        lines.append("| 匹配度 | 职位 | 公司 | 地点 | 薪资 | ANZSCO | 移民路径 | 需补充技能 |")
        lines.append("|--------|------|------|------|------|--------|----------|------------|")
        for j in tier1:
            code, name = get_anzsco(j["title"])
            anzsco = f"{code} {name}" if code else "-"
            lines.append(
                f"| **{j['score']}** | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {anzsco} | {j['immigration_path']} | {j['suggested_skills']} |"
            )
    else:
        lines.append("*今日无绿名单 Tier1 ICT 高匹配岗位。*")
    
    lines.extend(["", "---", "", "## 二、大学/研究机构岗位（40-59分）", ""])
    if research:
        lines.append("| 匹配度 | 职位 | 公司 | 地点 | 薪资 | 移民路径 | 需补充技能 |")
        lines.append("|--------|------|------|------|------|----------|------------|")
        for j in research:
            lines.append(
                f"| {j['score']} | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {j['immigration_path']} | {j['suggested_skills']} |"
            )
    else:
        lines.append("*今日无大学/研究机构岗位。*")
    
    lines.extend(["", "---", "", "## 三、已过滤/降级岗位（<40分）", ""])
    if others:
        lines.append("| 匹配度 | 职位 | 公司 | 分类 | 原因 |")
        lines.append("|--------|------|------|------|------|")
        for j in others[:30]:  # 只显示前30个
            reason = j["reasons"][0] if j["reasons"] else "非目标岗位"
            lines.append(f"| {j['score']} | {j['title']} | {j['company']} | {reason} | {', '.join(j['reasons'][:2])} |")
        if len(others) > 30:
            lines.append(f"| ... | ... | ... | ... | 共 {len(others)} 个，其余省略 |")
    else:
        lines.append("*无。*")
    
    lines.extend([
        "",
        "---",
        "",
        "## 四、操作摘要",
        "",
        f"- 高匹配（≥60）：{len(tier1)}",
        f"- 中匹配（40-59）：{len(research)}",
        f"- 低匹配/忽略（<40）：{len(others)}",
        "",
        "**下一步建议**：",
        "1. 对 Tier1 岗位，先上 INZ 官网查雇主是否在 [Accredited Employer List](https://www.immigration.govt.nz/employ-migrants/accreditation-and-job-checks/accredited-employers-list)。",
        "2. 准备英文简历 + Cover Letter + GitHub 作品集。",
        "3. 主线仍是德国岗位制博士；NZ 只作为副线机会。",
        "",
    ])
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n📄 Markdown 报告已保存：{md_path}")
    
    # 6. 保存 JSON
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / f"seek_nz_{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "email_count": email_count,
            "total_jobs": len(unique_jobs),
            "jobs": unique_jobs,
        }, f, ensure_ascii=False, indent=2)
    print(f"📊 JSON 数据已保存：{json_path}")
    
    # 7. KOS JSON feed
    KOS_DIR.mkdir(parents=True, exist_ok=True)
    kos_path = KOS_DIR / "latest.json"
    
    feed = {
        "meta": {
            "title": "SEEK NZ 绿名单岗位追踪",
            "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
            "icon": "briefcase",
            "section_id": "seek-nz",
            "last_updated": run_time.isoformat(),
        },
        "data": {
            "date": date_str,
            "email_count": email_count,
            "total_jobs": len(unique_jobs),
            "tier1_jobs": [{
                "title": j["title"],
                "company": j["company"],
                "location": j["location"],
                "salary": j["salary"],
                "url": j["url"],
                "score": j["score"],
                "reasons": j["reasons"],
                "immigration_path": j["immigration_path"],
                "suggested_skills": j["suggested_skills"],
                "anzsco_code": j["anzsco_code"],
                "anzsco_name": j["anzsco_name"],
            } for j in tier1],
            "all_jobs": [{
                "title": j["title"],
                "company": j["company"],
                "location": j["location"],
                "salary": j["salary"],
                "url": j["url"],
                "score": j["score"],
                "reasons": j["reasons"],
                "immigration_path": j["immigration_path"],
                "suggested_skills": j["suggested_skills"],
                "anzsco_code": j["anzsco_code"],
                "anzsco_name": j["anzsco_name"],
            } for j in unique_jobs],
        },
    }
    
    with open(kos_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
    print(f"🌐 KOS feed 已保存：{kos_path}")
    
    # 同时保存历史快照
    snapshot_path = KOS_DIR / f"seek-nz_{date_str}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
    print(f"🌐 KOS 快照已保存：{snapshot_path}")
    
    # 8. 控制台摘要
    print(f"\n{'='*60}")
    print(f"✅ 完成：扫描 {email_count} 封邮件，{len(unique_jobs)} 个去重岗位")
    print(f"   绿名单Tier1: {len(tier1)} | 研究岗: {len(research)} | 其他: {len(others)}")
    print(f"{'='*60}")
    
    # 打印 TOP 10
    print(f"\n🏆 TOP 10 岗位：")
    for i, j in enumerate(unique_jobs[:10], 1):
        tier_marker = "🥇" if j["score"] >= 60 else "🥈" if j["score"] >= 40 else ""
        print(f"  {i}. {tier_marker} [{j['score']}分] {j['title']} @ {j['company']} ({j['location']}) {j['salary']}")

if __name__ == "__main__":
    main()
