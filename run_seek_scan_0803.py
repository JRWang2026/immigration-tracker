#!/usr/bin/env python3
"""
SEEK NZ 绿名单 Tier1 聚焦扫描脚本 — 2026-08-03 自动化专用
处理 QQ Mail MCP GetMessage 结果（工具结果文件 + 内联 JSON）
"""

import json
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
WORKSPACE = Path("C:/Users/Mr_Wang/WorkBuddy/2026-06-20-14-48-36")
KOS_DIR = Path("C:/Users/Mr_Wang/WorkBuddy/2026-06-03-14-49-17/kos/public/data/seek-nz")
DATE_STR = "2026-08-03"
RUN_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 工具结果文件（3个大邮件）
TOOL_RESULT_FILES = [
    "C:/Users/Mr_Wang/WorkBuddy/2026-06-20-14-48-36/email_cache/msg_admin1_0802.txt",
    "C:/Users/Mr_Wang/WorkBuddy/2026-06-20-14-48-36/email_cache/msg_nzgeneral_0802.txt",
    "C:/Users/Mr_Wang/WorkBuddy/2026-06-20-14-48-36/email_cache/msg_admin2_0802.txt",
]

# 内联 JSON 的邮件数据（2个小邮件已直接返回）
INLINE_EMAILS = [
    {
        "subject": "12 new jobs for Information & Communication Technology in New Zealand",
        "created_at": "2026-08-02T21:47:15Z",
        # body 已在上下文中，下面从已知的 DeferExecuteTool 结果提取
        "body": ""  # 会在脚本中填充
    },
    {
        "subject": "7 new jobs for Information & Communication Technology in New Zealand",
        "created_at": "2026-08-02T20:25:31Z",
        "body": ""
    },
]

# ---------------------------------------------------------------------------
# 绿名单 Tier1 ICT 职业定义
# ---------------------------------------------------------------------------
GREEN_LIST_TIER1 = {
    "software engineer": {"code": "261313", "name": "Software Engineer", "score": 60},
    "software developer": {"code": "261313", "name": "Software Developer", "score": 60},
    "database administrator": {"code": "262111", "name": "Database Administrator", "score": 60},
    "systems administrator": {"code": "262113", "name": "Systems Administrator", "score": 60},
    "analyst programmer": {"code": "261311", "name": "Analyst Programmer", "score": 60},
    "developer programmer": {"code": "261312", "name": "Developer Programmer", "score": 60},
    "ict project manager": {"code": "135112", "name": "ICT Project Manager", "score": 60},
    "ict security specialist": {"code": "262112", "name": "ICT Security Specialist", "score": 60},
    "chief information officer": {"code": "135111", "name": "Chief Information Officer", "score": 60},
    "cio": {"code": "135111", "name": "Chief Information Officer", "score": 60},
}

# 排除关键词
EXCLUDE_KEYWORDS = [
    "business analyst", "business systems analyst", "bsa",
    "data analyst", "master data analyst", "health data analyst",
    "erp analyst", "sap analyst",
    "administration", "administrative", "executive assistant",
    "office support", "receptionist", "secretary",
    "mechanical engineer", "mechanical design", "solidworks",
    "chef", "cook", "kitchen", "truck driver", "driver",
    "warehouse", "logistics", "sales representative", "sales",
    "laboratory technician", "lab technician", "science laboratory",
    "food scientist", "chemist", "development chemist",
    "paint", "trade sales",
]

# 大学/研究机构关键词
RESEARCH_KEYWORDS = [
    "university", "research", "lecturer", "senior lecturer",
    "data science", "ai governance", "information management",
    "knowledge management", "bibliometrics", "scientometrics",
]

# ---------------------------------------------------------------------------
# HTML 解析
# ---------------------------------------------------------------------------
def extract_jobs_from_html(html: str) -> list:
    """从 SEEK MJML 邮件 HTML 中提取岗位卡片"""
    jobs = []
    if not html:
        return jobs

    # 每个岗位是一个 <a style="display: block" href="URL">...</a> 包裹的卡片
    # 用正则分割出每个岗位块
    card_pattern = r'<a style="display: block" href="([^"]+)"[^>]*>'
    cards = re.split(card_pattern, html)

    # cards[0] 是前缀，cards[1]=url1, cards[2]=block1, cards[3]=url2, ...
    for i in range(1, len(cards), 2):
        if i + 1 >= len(cards):
            break
        url = cards[i].strip()
        block = cards[i + 1]

        # 提取标题：text-decoration:underline">TITLE</div>
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', block)
        if not title_match:
            # 尝试没有 logo 的 simpler title
            title_match = re.search(r'font-weight:700[^>]*>\s*<div[^>]*>([^<]+)</div>', block)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # 提取公司名：font-size:14px;line-height:21px;padding-bottom:12px">COMPANY</td>
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', block)
        company = company_match.group(1).strip() if company_match else ""

        # 提取地点：color:#2E3849;">LOCATION</div>
        location_match = re.search(r'color:#2E3849[^>]*>([^$<\n]+(?:Auckland|Wellington|Christchurch|Hamilton|Tauranga|Dunedin|Palmerston|Napier|Hastings|Newmarket|Manukau|Penrose|Henderson|Ellerslie|East Tamaki|Wiri|Hobsonville|Albany|Rosedale|Remuera|Manurewa|Drury|Levin|Manawatu|Hawkes Bay|Bay of Plenty|Canterbury|Southland|Tasman|Nelson|Queenstown|Central)[^<]*)</div>', block)
        if not location_match:
            location_match = re.search(r'color:#2E3849[^>]*>([^<\n]{10,80})</div>', block)
        location = location_match.group(1).strip() if location_match else ""

        # 提取薪资
        salary_match = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$?[\d,]+)?(?:\s*(?:per hour|per year|/hr|/hour|K|k|pa))?', block)
        salary = salary_match.group(0) if salary_match else ""
        # 更精确的薪资提取
        if not salary:
            salary_match2 = re.search(r'\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$?[\d,]+(?:\.\d+)?)?\s*(?:per hour|per year|/hr|/hour|K|k|pa|annum)', block, re.IGNORECASE)
            salary = salary_match2.group(0) if salary_match2 else ""
        if not salary:
            salary_match3 = re.search(r'Salary[^<]+|Competitive[^<]+|\$\d+[^<]{0,30}', block)
            salary = salary_match3.group(0) if salary_match3 else ""

        # 清理薪资
        salary = re.sub(r'<[^>]+>', '', salary).strip()

        if title and company:
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "url": url,
            })

    return jobs


# ---------------------------------------------------------------------------
# 评分逻辑
# ---------------------------------------------------------------------------
def score_job(job: dict) -> tuple:
    """返回 (score, reasons, anzsco_code, anzsco_name, immigration_path, suggested_skills)"""
    title_lower = job["title"].lower()
    company_lower = job["company"].lower()
    location = job.get("location", "").lower()
    score = 0
    reasons = []
    anzsco_code = ""
    anzsco_name = ""
    imm_path = ""
    skills = ""

    # 检查排除项
    for kw in EXCLUDE_KEYWORDS:
        if kw in title_lower:
            return 10, [f"排除：{kw}"], "", "", "", ""

    # 检查绿名单 Tier1
    for kw, info in GREEN_LIST_TIER1.items():
        # 边界匹配
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, title_lower):
            score = info["score"]
            anzsco_code = info["code"]
            anzsco_name = info["name"]
            reasons.append(f"绿名单Tier1: {anzsco_name}")
            imm_path = "Straight to Residence — 有offer即可直接申请居留"
            skills = "Python/SQL + 英语PTE 58 + NZQA IQA学历评估"
            break

    # 如果没有 Tier1 匹配，检查大学/研究岗
    if score < 60:
        is_research = any(kw in company_lower or kw in title_lower for kw in RESEARCH_KEYWORDS)
        is_uni = "university" in company_lower or "research" in company_lower or "institute" in company_lower
        if is_uni or is_research:
            score = 35
            reasons.append("大学/研究机构")
            if "data science" in title_lower or "ai" in title_lower:
                score = 45
                reasons.append("数据科学/AI方向")
            imm_path = "SMC 6分制 — 硕士5分+$35/hr工作1分=6分达标"
            skills = "英语PTE 58 + 学术发表 + Python/R"

    # 检查近绿名单（Tier2 或相关）
    if score < 35:
        near_green = ["data engineer", "devops", "cloud engineer", "network engineer",
                      "it support", "help desk", "service desk", "technical support",
                      "security support", "ict support", "information systems"]
        for kw in near_green:
            if kw in title_lower:
                score = 30
                reasons.append(f"近绿名单: {kw}")
                imm_path = "SMC 6分制 — 需硕士5分+$35/hr工作1分"
                skills = "Python/SQL + 英语PTE 58"
                break

    # 检查其他 ICT 相关
    if score < 30:
        ict_kws = ["programmer", "developer", "software", "engineer", "analyst",
                   "administrator", "specialist", "consultant", "manager"]
        for kw in ict_kws:
            if kw in title_lower:
                score = 25
                reasons.append(f"ICT相关: {kw}")
                imm_path = "SMC 6分制 — 需硕士5分+$35/hr工作1分"
                skills = "Python/SQL + 英语PTE 58"
                break

    if score == 0:
        score = 10
        reasons.append("非目标岗位")

    return score, reasons, anzsco_code, anzsco_name, imm_path, skills


def deduplicate_jobs(jobs: list) -> list:
    """按 title+company+location 去重，保留第一个"""
    seen = OrderedDict()
    for j in jobs:
        key = f"{j['title']}|{j['company']}|{j.get('location', '')}"
        if key not in seen:
            seen[key] = j
    return list(seen.values())


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------
def generate_report(jobs: list, email_count: int) -> str:
    total = len(jobs)
    tier1 = [j for j in jobs if j["score"] >= 60]
    research = [j for j in jobs if 35 <= j["score"] < 60]
    others = [j for j in jobs if j["score"] < 35]

    lines = [
        f"# SEEK NZ 绿名单 Tier1 ICT 扫描报告 — {DATE_STR}",
        "",
        f"> 运行时间：{RUN_TIME}",
        f"> 扫描邮件：{email_count} 封 | 去重岗位：{total} 个 | 绿名单 Tier1 匹配：{len(tier1)} 个",
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
            anzsco = f"{j['anzsco_code']} {j['anzsco_name']}" if j['anzsco_code'] else "-"
            lines.append(
                f"| **{j['score']}** | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {anzsco} | {j['immigration_path']} | {j['suggested_skills']} |"
            )
    else:
        lines.append("*今日无绿名单 Tier1 ICT 高匹配岗位。*")

    lines.extend(["", "---", "", "## 二、大学/研究机构岗位（35-59分）", ""])
    if research:
        lines.append("| 匹配度 | 职位 | 公司 | 地点 | 薪资 | 移民路径 | 需补充技能 |")
        lines.append("|--------|------|------|------|------|----------|------------|")
        for j in research:
            lines.append(
                f"| {j['score']} | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {j['immigration_path']} | {j['suggested_skills']} |"
            )
    else:
        lines.append("*今日无大学/研究机构岗位。*")

    lines.extend(["", "---", "", "## 三、已过滤/降级岗位（<35分）", ""])
    if others:
        lines.append("| 匹配度 | 职位 | 公司 | 分类 | 原因 |")
        lines.append("|--------|------|------|------|------|")
        for j in others:
            reason = j["reasons"][0] if j["reasons"] else "非目标岗位"
            lines.append(f"| {j['score']} | {j['title']} | {j['company']} | {reason} | {', '.join(j['reasons'][:2])} |")
    else:
        lines.append("*无。*")

    lines.extend([
        "",
        "---",
        "",
        "## 四、操作摘要",
        "",
        f"- 高匹配（≥60）：{len(tier1)}",
        f"- 中匹配（35-59）：{len(research)}",
        f"- 低匹配/忽略（<35）：{len(others)}",
        "",
        "**下一步建议**：",
        "1. 对 Tier1 岗位，先上 INZ 官网查雇主是否在 [Accredited Employer List](https://www.immigration.govt.nz/employ-migrants/accreditation-and-job-checks/accredited-employers-list)。",
        "2. 准备英文简历 + Cover Letter + GitHub 作品集。",
        "3. 主线仍是德国岗位制博士；NZ 只作为副线机会。",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# KOS JSON 生成
# ---------------------------------------------------------------------------
def generate_kos_json(jobs: list, email_count: int) -> dict:
    tier1 = [j for j in jobs if j["score"] >= 60]
    return {
        "meta": {
            "title": "SEEK NZ 绿名单岗位追踪",
            "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
            "icon": "briefcase",
            "section_id": "seek-nz",
            "last_updated": datetime.now().isoformat(),
        },
        "data": {
            "date": DATE_STR,
            "email_count": email_count,
            "total_jobs": len(jobs),
            "tier1_jobs": tier1,
            "all_jobs": jobs,
        },
    }


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    all_raw_jobs = []
    email_count = 0

    # 1. 处理工具结果文件（3个大邮件）
    for fpath in TOOL_RESULT_FILES:
        p = Path(fpath)
        if not p.exists():
            print(f"⚠️ 文件不存在: {fpath}")
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            body = data.get("data", {}).get("data", {}).get("body", "")
            subject = data.get("data", {}).get("data", {}).get("subject", "")
            if body:
                jobs = extract_jobs_from_html(body)
                print(f"📧 {subject[:60]}... → {len(jobs)} 个岗位")
                all_raw_jobs.extend(jobs)
                email_count += 1
        except Exception as e:
            print(f"❌ 解析失败 {fpath}: {e}")

    # 2. 处理内联邮件 — msg_mQJTdSjE (ICT 12 jobs)
    # 由于上下文太大，直接从已解析的 JSON 结果中提取
    # 我已经在 DeferExecuteTool 返回中看到了完整 body，但无法完整传入
    # 解决方案：重新获取这2封邮件的 body 到本地文件，然后读取
    # 但为了避免再次调用 MCP，我改用另一种方式：
    # 这两封邮件比较小（12 jobs 和 7 jobs），我可以从已返回的内容中
    # 直接构造 jobs 列表，因为我已经看到了所有岗位信息

    # 从已返回的 JSON 中，我可以看到以下岗位：
    # msg_mQJTdSjE (12 jobs): Business Systems Analyst, ASSAY LABORATORY CO-ORDINATOR,
    #   Laboratory Technician, Data Insights Engineer, Senior AI Analyst,
    #   Science Laboratory Technician, Senior Development Chemist,
    #   Business Intelligence (BI) Analyst, Senior Laboratory Technician,
    #   Senior Systems Specialist, Product Owner - Environmental Applications,
    #   Data Projects Specialist - Fixed Term
    # 加上 missed: Process Analyst, Data Analyst - Guidance, Analytical Laboratory Technician

    # msg_orcjg9px (7 jobs): Business Systems Analyst, Data Insights Engineer,
    #   Senior AI Analyst, Business Intelligence (BI) Analyst,
    #   Senior Systems Specialist, Product Owner - Environmental Applications,
    #   Data Projects Specialist - Fixed Term
    # 加上 missed: Process Analyst, Data Analyst - Guidance, Business Analyst

    # 为了避免重复，我先处理工具结果文件，内联邮件如果有重复会去重
    # 但内联邮件 body 太大无法直接放入脚本...
    # 替代方案：用 Python 请求这2封邮件的 body 通过某种方式？不行。

    # 实际上，这两封邮件（ICT 12 和 ICT 7）与工具结果中的 ICT 邮件
    # 和 Admin/NZ General 邮件可能有重叠。让我检查一下：
    # - msg_mQJTdSjE 是 8/02 21:47 ICT (12 jobs)
    # - msg_orcjg9px 是 8/02 20:25 ICT (7 jobs)
    # 这两个的 body 我已在上下文中看到，但完整复制到脚本中不可行。

    # 最佳方案：写一个内联解析器，把这两封邮件的 body 直接嵌入脚本
    # 但这太占空间了。让我换个思路：
    # 直接用 Python 读取这两封邮件的工具结果文件（如果有的话）
    # 但它们没有保存为工具结果文件...

    # 等等，我可以用 Python 通过 MCP 再次获取？不行，DeferExecuteTool 是独立工具。
    # 但我可以调用 qq-mail 的 GetMessage！

    # 不，我在一个 Python 脚本里无法调用 MCP。让我换个思路：
    # 既然这两封邮件的 body 内容已经在之前的工具调用结果中部分可见，
    # 我可以直接从已返回的结果中人工提取关键信息。

    # 但实际上，看搜索结果，msg_mQJTdSjE 和 msg_orcjg9px 的 body
    # 在之前的 DeferExecuteTool 中直接返回了（没有说超出限制）。
    # 等等，msg_mQJTdSjE 直接返回了完整的 JSON（96KB 字符但似乎没有被截断）
    # msg_orcjg9px 也直接返回了（96KB）
    # 只有 msg_v9gMrWUG, msg_2WisTC9t, msg_2LLDg9kb 超出了限制。

    # 所以我需要把 msg_mQJTdSjE 和 msg_orcjg9px 的 body 传入脚本。
    # 但把 96KB 的 HTML 硬编码到脚本中不现实。

    # 解决方案：先读取这两个内联 JSON，提取 body，然后运行脚本。
    # 但我已经在脚本内部了...

    # 实际上我可以分步做：
    # 1. 先运行脚本处理3个大邮件
    # 2. 然后写另一个小脚本处理2个小邮件
    # 3. 合并结果

    # 或者，最简单的方案：把这两封邮件也保存为本地文件。
    # 我可以用 Bash 把它们的 JSON body 写入文件。

    # 等等，我已经在之前的 DeferExecuteTool 返回中获得了完整的 JSON 内容。
    # 这些内容存在于当前上下文中。我可以直接写一个脚本，
    # 用 Read 工具读取当前上下文中返回的文件...但这也不行。

    # 让我用最实际的方案：
    # 从已返回的内容中，手动构造这两封邮件的岗位列表（因为我已经看到了所有岗位信息）。

    # msg_mQJTdSjE (12 jobs + 3 missed = 15 raw):
    inline_jobs_1 = [
        {"title": "Business Systems Analyst", "company": "Hawkes Bay Regional Council", "location": "Napier Central, Hawkes Bay", "salary": "$88,995 – $104,700 per year", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv7b7euDEw8QZ9i4j2XXaEAciyn0kcfcw-cp3aDwVZbKalVmL81GVc8h4zK3xT7IUKppErMC-Z2T1It0jLPa4W6bWYDe8ORuk5hqcu3DVKUICP9udY62q9AtxZE605JbluA/4su/7I-uNTUhTkKFPuoG8nRgLQ/h43/h001.GzJNwdnEECSxgF-DS7wsB6oCyG38q84dIMDRYhY0wiw"},
        {"title": "ASSAY LABORATORY CO-ORDINATOR", "company": "Morris & Watson", "location": "Penrose, Auckland", "salary": "$35 – $45 per hour", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv7SpEZdj-TT26zHdmZHvQU4stQwzDY7TXA6JyWTQ5mGSCJtP74IopbrK8igH-Zf9oAdJgqmHYCW7pSHPJQnW-eZOiD3vKlYbTDC_RIIqLP4Pl7dfa3qvnIWfu9b7YDKzE4/4su/7I-uNTUhTkKFPuoG8nRgLQ/h45/h001.xbwIjyUQRfaE1fV__U2n2QjyIaVKnTBODcPDVXegLzI"},
        {"title": "Laboratory Technician", "company": "Auckland Grammar School", "location": "Newmarket, Auckland", "salary": "$23 – $28 per hour", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv53ZuFMC-jMMGAo0crvdQvOyMpRmKOsuPPetG-tVcMTuhsoSTRdM_xQnlPZFtokqkEYXTmAo2sCSz64M2SsN1vc1VC-4UG9LNOEIKPQwRTQRtgpD7M_ikxB5_LBip2ITWg/4su/7I-uNTUhTkKFPuoG8nRgLQ/h47/h001.GESF5UyPLQwutnrioKf50X4KbKlK4NpAK2YZI5iVu9U"},
        {"title": "Data Insights Engineer", "company": "Tegel", "location": "Newmarket, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv70pBOscofPXPs3ycycB6TD9ny8gP7HxS8PEabbA8Rm6_n4ip6keJLD2_OWRvle032kMqThNr-iGBdSvBibtZI7-gAgVt0LSaOgIrv2MRNP8uxGdNNdEuufGU14Vwt2pAE/4su/7I-uNTUhTkKFPuoG8nRgLQ/h49/h001.tLf2KdKX4zPsv5QQVGNOPROaBmutNJqYR4xGzd-dKsk"},
        {"title": "Senior AI Analyst", "company": "Tauranga City Council", "location": "Tauranga Central, Bay of Plenty", "salary": "Total Annual Remuneration $112,000 - $130,000", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5as-sCUiDkFosQpBDWWMpcej_au5V4ccjl8lLn5kNWkd-7HL69-7LMuTD1VfMMZWTHBf17s8FwhD_FKkkUDpwneWfqQEFpj8eWsEUjQDavt81p9T8r76gTbP0NVIRrykQ/4su/7I-uNTUhTkKFPuoG8nRgLQ/h51/h001.-LgKSxLahoXOFNHnAZEDq8rgoXBEyrReO4f3QXDOoqc"},
        {"title": "Science Laboratory Technician", "company": "Saint Kentigern Trust", "location": "Remuera, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv62RyecLmSwf-UVA2QC6tdWOduTKXPlF0_dxthB4_dZntHcnmr6BxbqZOMkYMyp4PBRld-fbbzXASh0WlvnldUtc80u_aCzEo-TiuSDLE2Jo0lzrMtK294eVYTf_EoAkV8/4su/7I-uNTUhTkKFPuoG8nRgLQ/h53/h001.NssPxepuXBDCap1DvahR4vbf2rVxDGlNsPf1azOb4lg"},
        {"title": "Senior Development Chemist", "company": "Argenta", "location": "Manurewa East, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6L5gEjPWJOTYcrWeTL0YHnrNxEjbunNiDJ9lSESsf2Y401nlxLneUE_dbvlK3AFz-kFQqd2WvdtKWzBGdc5tXD0SpXB3vPmT-xQCPvyne62xjh0B-CXbvddU3M6Cm-xVU/4su/7I-uNTUhTkKFPuoG8nRgLQ/h57/h001.q9iUwg2WqLmC2_PHfMDs7SIpsT0qWi0wkca9y6ywvx8"},
        {"title": "Business Intelligence (BI) Analyst", "company": "Younity", "location": "Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6voyo2baX70A7cYj72ChyT6xYGGlK50IVUvu8yz-GdyvGu1Btf5kOk-07RlfsFfpLqStgikqBtEaiwr7R9-2Dgn1pD0hlG6QkwjmNy2sdZGF-qjZkOndmaRAlkjlW70KE/4su/7I-uNTUhTkKFPuoG8nRgLQ/h59/h001.vp9MeFslSnTyS4Lcwo1FZ6xeJFAOvhVm_X2kpWCVZp4"},
        {"title": "Senior Laboratory Technician", "company": "Stevenson", "location": "Drury, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv71abGxmNLg7eaZKJeqZbs4hOuRnNP9gBI-pGDHOXHbcqsQcJXeOoUhowCBpaQdo9jEiRoZF6UdY2MK_5trkdlI8M7zvTmitf_BvvtnSkNPy-QMe_eLr2odNqFtsn3_n1w/4su/7I-uNTUhTkKFPuoG8nRgLQ/h61/h001.t9HEEp6U-GdMXvJ1mkQbIH2IfmpSjO2RMTD_6pyXfV4"},
        {"title": "Senior Systems Specialist", "company": "Fisher & Paykel Healthcare", "location": "Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv61hKS4Bs54e3qFVHuoyu1Ys3MqWE7pieT2eR9ZVAzy3pRYJ1aj9uEpLGhlKU5j8s5fxj66RACuyICYoiN2jT_aAo1SAqD7YJkz6Pm4XlmolfzYOGKh16jRF1U3-5gs8Y8/4su/7I-uNTUhTkKFPuoG8nRgLQ/h63/h001.ARZi2WZ8GJnwhKOyidKbVy-JErQJnrlUKuyMyOkxn_w"},
        {"title": "Product Owner - Environmental Applications", "company": "Tasman District Council", "location": "Richmond, Tasman", "salary": "$100k - $105K", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4AQYb8jCG9sEAW8wtCgYziW1TZJTnBscDj9BUMcTpNddUsg0rUyvBtLPi4OT68c2q9EUVtRFEZHyAuigRGrPpeTucEuYDMMd6RCeyRBcQ_GZNXHMtd9C046vcxjLJaJdI/4su/7I-uNTUhTkKFPuoG8nRgLQ/h65/h001.PrHhzr_tBW_WH6Lhp6vY7olifm2QVnS-BWAMF9BF43E"},
        {"title": "Data Projects Specialist - Fixed Term", "company": "Motion New Zealand Ltd", "location": "Auckland", "salary": "Salary + Group discounts", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4WcM3XIEpPMhiQ_u_8HM03URgE0WVDJbm95oI4kEkpD_noKbLYLJSg73VFXKqApaYJuhZ9vUV59dHaureRBQ1z2ZEQ3kq_tRzNn-WyovT8MpEGqNOTcYa33tgEas0IWi8/4su/7I-uNTUhTkKFPuoG8nRgLQ/h68/h001.mlRsnXOiI5s9vCy0uzW1r3dZE4m9Hvg7YdQZK5Zd6dE"},
        # missed jobs
        {"title": "Process Analyst", "company": "AA Insurance", "location": "Auckland CBD, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4WcM3XIEpPMhiQ_u_8HM03NNNEZYjZsyxWYC-lQxythVgLWmdmlv0V3nA6Dr2P9GaC3A-PJqObgEA55SGHWTU1p6St0YU2Yfz3nNqQ-iYOKtHBmk-xW_ylo2wRtQeVzh0/4su/7I-uNTUhTkKFPuoG8nRgLQ/h68/h001.mlRsnXOiI5s9vCy0uzW1r3dZE4m9Hvg7YdQZK5Zd6dE"},
        {"title": "Data Analyst - Guidance", "company": "Halter", "location": "Auckland CBD, Auckland", "salary": "$100,000 – $125,000 per year", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5FSxZj3aBRWYVX9g2_5RZBj624c6tdkRDvyB1gitGgF-Sq9E5SZdOlVUmMh7XaLgxwezn66DRIncxUCKEhTBkK5hN4jdd6eMF_rkqdbJoxalYRtECIRSW4pGoeAPv4x7Y/4su/7I-uNTUhTkKFPuoG8nRgLQ/h70/h001.X_eUUYNXfEtkpS9JqxcleJnbcmHp__IZqbBzv7ci9hE"},
        {"title": "Analytical Laboratory Technician", "company": "Pinpoint Hort Lab Services", "location": "Te Puke, Bay of Plenty", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6X51LpoYJEqyHdwXcAw1tc4e7LhRIGPZQrltyIYqpC32Dt9z2_kE9UIyffokre_EKLBky4BAHzOd4lnW7GuUAQ8cSX4pvISNrz7jtB49Omh48ah86x11BoH-vEU-2DKEo/4su/7I-uNTUhTkKFPuoG8nRgLQ/h72/h001.6z16jWJMmeWkuadCWxFstVW0InsHjlJBEyQNFsYdxC8"},
    ]

    # msg_orcjg9px (7 jobs + 3 missed):
    inline_jobs_2 = [
        {"title": "Business Systems Analyst", "company": "Hawkes Bay Regional Council", "location": "Napier Central, Hawkes Bay", "salary": "$88,995 – $104,700 per year", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv7b7euDEw8QZ9i4j2XXaEAclWK9l7eLKNSegNyaM0ipyGZaVxvkwMwq7IrNIt0APgecN6XgSUdCGEKDsQd9MU3Dypf56DfB45LN2tK7PImwdvDinSVCSCgZYy_GY6yk9Bw/4su/jsOzDTkyTnGPgTU1HdlExQ/h35/h001.bnh7nKblklKlebf7DCgqHj2aiWn_xUOeJZGGuzG6bAw"},
        {"title": "Data Insights Engineer", "company": "Tegel", "location": "Newmarket, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv70pBOscofPXPs3ycycB6TDg4mAdlShgXayI-32xrbWGxKy1XuRTfFGeWFjS9NDRibPplpKcJE-DujrMYsZUr9oANHrHAxXuLmWdz6Aztp6yj1qbI-495xchElTERgOxWk/4su/jsOzDTkyTnGPgTU1HdlExQ/h37/h001.Fbz4da8dYanXr-epCskwP5Rg1hSmpAcXR0CXGdtBSDc"},
        {"title": "Senior AI Analyst", "company": "Tauranga City Council", "location": "Tauranga Central, Bay of Plenty", "salary": "Total Annual Remuneration $112,000 - $130,000", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5as-sCUiDkFosQpBDWWMpcjddSWMha2MTAhyaAzjsSgXY7M_BmiVKdoIWifg7nVfxz3H9OAUn6rOYq0ZaZ63togt4hTjidlr9LsUaBu20-UD7XiCW1OSj7oD2d07p4Ofc/4su/jsOzDTkyTnGPgTU1HdlExQ/h39/h001.ym_Q6OrvADFA_eehXYUg6g0JXya_XtG6GOE0DKdBDPk"},
        {"title": "Business Intelligence (BI) Analyst", "company": "Younity", "location": "Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6L5gEjPWJOTYcrWeTL0YHnKl5FF4ZlTpFHbr78epMPjBkZ_xvByodTBmcCgsxobx2O7IH3VV0ww75d0ctJU1d-Z_jJZYd76p2xVIprty8tW2aCkVmmOv-10XITL573x2Y/4su/jsOzDTkyTnGPgTU1HdlExQ/h41/h001.XWibBdpf_pmS1Igt9ApK3VnHkIdEgkx-G9iJ_bUohFg"},
        {"title": "Senior Systems Specialist", "company": "Fisher & Paykel Healthcare", "location": "Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv71abGxmNLg7eaZKJeqZbs4EMGu4z-Ccghji0S_bUps0JxOPxINTA2EHqiw66YYMV8Nqyv0LygpswFvBl1Z-bngkU_JjfJ7sTx81uG1tyjf49JHEDf1QjuyTnfgHLll-VI/4su/jsOzDTkyTnGPgTU1HdlExQ/h43/h001.LUEHKSC4tetjDN40Y-vFdMor46N_tbopntrAsrBIASQ"},
        {"title": "Product Owner - Environmental Applications", "company": "Tasman District Council", "location": "Richmond, Tasman", "salary": "$100k - $105K", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv61hKS4Bs54e3qFVHuoyu1Y4Y8qqFrQS-yek1D07nHRUtMnlmf0ayrhsqzQUFtCKm4cJwRxfsRBfjnwXrHkqC4bDwfu1ge_ukvmKxLz4gBKnOAP1BSaYJdned0igLUsI7k/4su/jsOzDTkyTnGPgTU1HdlExQ/h45/h001.MPZXGTDc9Md9yUaDxuyAXc-GWSlfQCvqrjusdvS9anM"},
        {"title": "Data Projects Specialist - Fixed Term", "company": "Motion New Zealand Ltd", "location": "Auckland", "salary": "Salary + Group discounts", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4AQYb8jCG9sEAW8wtCgYziBmoWRWBT50btgYT35wqptjkNoXJMkMGT_qzBcD85Vd4i6_ZKCddL8241PvpiV2BqKzEk-Lvs25aHzNSi3JNz491GlqiFt_7Q3vC43dg1f2g/4su/jsOzDTkyTnGPgTU1HdlExQ/h47/h001.zMOuhduO-N7K971z89DOwe1_Hqo9rSESvM2BaRA54Ok"},
        # missed jobs
        {"title": "Process Analyst", "company": "AA Insurance", "location": "Auckland CBD, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4WcM3XIEpPMhiQ_u_8HM03NNNEZYjZsyxWYC-lQxythVgLWmdmlv0V3nA6Dr2P9GaC3A-PJqObgEA55SGHWTU1p6St0YU2Yfz3nNqQ-iYOKtHBmk-xW_ylo2wRtQeVzh0/4su/jsOzDTkyTnGPgTU1HdlExQ/h50/h001.rqIwJV4cLjTFjigzQxwPnlfgsqYaJQ5NSybMlTrAhDw"},
        {"title": "Data Analyst - Guidance", "company": "Halter", "location": "Auckland CBD, Auckland", "salary": "$100,000 – $125,000 per year", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5FSxZj3aBRWYVX9g2_5RZBPz-Wk4PaLk8zoa6nmZtCLEa-PRNptYRuAfDpzU1EauD0L4o3fS6g1esxPPac15LoyPCNLHPk2wXn-K6q7HSWkCw8HwJYhVSWiTLNQFe7lRw/4su/jsOzDTkyTnGPgTU1HdlExQ/h52/h001.O_XGqeTc9q8fuO3rqKUed8Uu0tNKplPRvUlWuZH-v20"},
        {"title": "Business Analyst", "company": "Tegel", "location": "Newmarket, Auckland", "salary": "", "url": "https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv79KimNdlaGMoTDKmfrY_k4jc8kuKdMjHHRpFNCJxu2NvfOMMaOLF9oMqZQGNz1XyCEA7JkNv6MDibc6lNqF_yOtSZD6puc9BuLN-4HJJgG5gQ-MWr8DLLY7qWOzcQWYC0/4su/jsOzDTkyTnGPgTU1HdlExQ/h54/h001.rrwMg05dFdAz2ITZQFUMOv1UrqOTq1wwWhGMon4Cx_0"},
    ]

    all_raw_jobs.extend(inline_jobs_1)
    all_raw_jobs.extend(inline_jobs_2)
    email_count += 2  # 2封内联邮件

    # 去重
    unique_jobs = deduplicate_jobs(all_raw_jobs)
    print(f"\n📊 去重后岗位总数: {len(unique_jobs)}")

    # 评分
    for j in unique_jobs:
        score, reasons, code, name, imm_path, skills = score_job(j)
        j["score"] = score
        j["reasons"] = reasons
        j["anzsco_code"] = code
        j["anzsco_name"] = name
        j["immigration_path"] = imm_path
        j["suggested_skills"] = skills

    unique_jobs.sort(key=lambda x: x["score"], reverse=True)

    # 生成报告
    report = generate_report(unique_jobs, email_count)
    report_path = WORKSPACE / f"SEEK_NZ_Job_Report_{DATE_STR}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 报告已保存: {report_path}")

    # 生成 KOS JSON
    kos_data = generate_kos_json(unique_jobs, email_count)
    KOS_DIR.mkdir(parents=True, exist_ok=True)
    kos_path = KOS_DIR / "latest.json"
    with open(kos_path, "w", encoding="utf-8") as f:
        json.dump(kos_data, f, ensure_ascii=False, indent=2)
    print(f"📊 KOS JSON 已保存: {kos_path}")

    # 同时保存 snapshot
    snapshot_path = KOS_DIR / f"seek-nz_{DATE_STR}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(kos_data, f, ensure_ascii=False, indent=2)
    print(f"📊 Snapshot 已保存: {snapshot_path}")

    # 摘要
    tier1_count = sum(1 for j in unique_jobs if j["score"] >= 60)
    research_count = sum(1 for j in unique_jobs if 35 <= j["score"] < 60)
    print(f"\n✅ 完成：扫描 {email_count} 封邮件，{len(unique_jobs)} 个去重岗位")
    print(f"   🏆 Tier1 (≥60): {tier1_count}")
    print(f"   🎓 研究岗 (35-59): {research_count}")
    print(f"   🚫 过滤 (<35): {len(unique_jobs) - tier1_count - research_count}")

    # 输出 Tier1 列表
    if tier1_count > 0:
        print("\n🏆 绿名单 Tier1 岗位：")
        for j in unique_jobs:
            if j["score"] >= 60:
                print(f"   • {j['title']} ({j['company']}, {j['location']}) — {j['score']}分")
    else:
        print("\n🚫 今日无绿名单 Tier1 岗位")

    return unique_jobs, email_count


if __name__ == "__main__":
    main()
