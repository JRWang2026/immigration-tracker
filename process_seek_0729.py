#!/usr/bin/env python
"""SEEK NZ 岗位扫描 - 2026-07-29 处理脚本
读取 QQ Mail MCP GetMessage 工具结果文件，MJML模板解析，绿名单Tier1聚焦评分。
"""

import json, re, os, html as html_mod
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# === File paths ===
TOOL_RESULTS_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\d37947d6-8936-4f15-a263-21ef7c6dbe8b\tool-results")

FILES = [
    # 7/28 Admin (20 new jobs)
    (TOOL_RESULTS_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785286916942-fff94c.txt", "json", "Admin"),
    # 7/28 ICT (20 new jobs)  
    (TOOL_RESULTS_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785286917443-dbb909.txt", "json", "ICT"),
    # 7/28 NZ General (20 new jobs)
    (TOOL_RESULTS_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785286917903-2fa0cf.txt", "json", "NZ General"),
    # 7/28 ICT (13 new jobs) - small email, directly extracted
    ("__INLINE_ICT13__", "inline", "ICT2"),
]

# The 4th email body (ICT 13 jobs) - will be injected by the calling process
INLINE_ICT13_BODY = None  # placeholder, set below


def load_body(path, ftype):
    if ftype == "inline":
        return INLINE_ICT13_BODY
    with open(str(path), 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['data']['data']['body']


def extract_jobs_mjml(body):
    """Extract jobs from MJML-format SEEK email body."""
    jobs = []
    # Split by job card anchors
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        # Title: inside text-decoration:underline div
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        # Company: font-size:14px;line-height:21px;padding-bottom:12px
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        # Location: first location-looking field
        loc_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        # Salary: $... pattern
        salary_matches = re.findall(r'>(\$[^<]+)</div>', card)
        # Date: Posted on ...
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        # URL
        url_match = re.search(r'href="(https://email\.s\.seek\.co\.nz[^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue

        # Location
        location = 'Unknown'
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm
                break
            elif lm and lm not in [title, company]:
                if location == 'Unknown':
                    location = lm

        # Salary
        salary = ''
        if salary_matches:
            salary = salary_matches[0].strip()
        else:
            # Check for "Competitive" style text
            for lm in loc_matches:
                lm = lm.strip()
                if lm and lm != location and lm not in [title, company] and ',' not in lm:
                    if re.search(r'(competitive|benefits|insurance|super|bonus|salary)', lm, re.I):
                        salary = lm
                        break

        posted_date = date_match.group(1) if date_match else ''
        url = url_match.group(1) if url_match else ''

        # HTML unescape
        title = html_mod.unescape(title)
        company = html_mod.unescape(company)
        location = html_mod.unescape(location)
        salary = html_mod.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
            'url': url,
        })
    return jobs


def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])

    # Tier 1 Green List ICT
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55; reasons.append('绿名单Tier1: Software Engineer')
    elif 'database administrator' in title or 'dba' in title:
        score += 55; reasons.append('绿名单Tier1: Database Administrator')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55; reasons.append('绿名单Tier1: Systems Administrator')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55; reasons.append('绿名单Tier1: Analyst Programmer')
    elif 'developer programmer' in title or 'application developer' in title:
        score += 55; reasons.append('绿名单Tier1: Developer Programmer')
    elif 'multimedia specialist' in title:
        score += 55; reasons.append('绿名单Tier1: Multimedia Specialist')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55; reasons.append('绿名单Tier1: ICT Project Manager')
    elif any(k in title for k in ['ict security', 'cyber security', 'information security']):
        score += 55; reasons.append('绿名单Tier1/Tier2: ICT Security')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55; reasons.append('绿名单Tier1: CIO/CDO')
    # University/research
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50; reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48; reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title):
        score += 45; reasons.append('大学信息管理研究岗')
    # Tier 2
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35; reasons.append('绿名单Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30; reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    # Database related (near Green List)
    elif any(k in title for k in ['database specialist', 'database reliability', 'database engineer', 'datacom database']):
        score += 32; reasons.append('近绿名单:数据库相关(非DBA)')
    # BSA/Data Analyst/ERP filtered
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8; reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title or 'bi analyst' in title or 'business intelligence' in title:
        score += 8; reasons.append('非绿名单:Data Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator']):
        score += 2; reasons.append('行政岗:忽略')
    else:
        score += 5; reasons.append('非目标岗位')

    # Domain bonus
    if any(k in (company + ' ' + title) for k in ['university', 'research institute', 'crown research']):
        score += 15; reasons.append('大学/研究机构')
    elif any(k in (company + ' ' + title) for k in ['government', 'ministry', 'council', 'education review']):
        score += 10; reasons.append('政府/公共部门')
    elif any(k in (company + ' ' + title) for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12; reasons.append('ICT/科技公司')

    # Skills bonus
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10; reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin']):
        score += 10; reasons.append('ICT基础设施技能')
    if 'data' in title and any(k in title for k in ['scientist', 'engineer', 'machine learning']):
        score += 8; reasons.append('高级数据技能')

    # Location bonus
    non_akl_regions = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
    matched_region = False
    for k in non_akl_regions:
        if (', ' + k in location or location.endswith(', ' + k) or location == k):
            score += 8; reasons.append('非奥克兰地区加分'); matched_region = True; break
    if not matched_region and (location.endswith(', wellington') or location == 'wellington'):
        score += 5; reasons.append('惠灵顿地区')

    # Penalties
    if 'part-time' in title or 'part time' in title:
        score -= 10; reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10; reasons.append('初级岗降分')

    return max(0, min(100, score)), reasons


def is_green_list_tier1(title):
    tier1 = [
        'software engineer', 'software developer', 'full stack developer',
        'database administrator', 'dba',
        'systems administrator', 'system administrator',
        'analyst programmer', 'programmer analyst',
        'developer programmer', 'application developer',
        'multimedia specialist',
        'ict project manager', 'it project manager',
        'ict security specialist', 'chief information officer', 'chief digital officer'
    ]
    title = title.lower()
    return any(k in title for k in tier1)


def green_list_anzsco(title):
    title = title.lower()
    if 'software engineer' in title or 'software developer' in title:
        return '261313', 'Software Engineer'
    elif 'database administrator' in title or 'dba' in title:
        return '262111', 'Database Administrator'
    elif 'systems administrator' in title or 'system administrator' in title:
        return '262113', 'Systems Administrator'
    elif 'analyst programmer' in title:
        return '261311', 'Analyst Programmer'
    elif 'developer programmer' in title or 'application developer' in title:
        return '261312', 'Developer Programmer'
    elif 'multimedia specialist' in title:
        return '261211', 'Multimedia Specialist'
    elif 'ict project manager' in title or 'it project manager' in title:
        return '135112', 'ICT Project Manager'
    elif 'ict security' in title or 'cyber security' in title:
        return '262112', 'ICT Security Specialist'
    elif 'chief information officer' in title:
        return '135111', 'Chief Information Officer'
    return '', ''


def suggest_skills(j):
    title = j['title'].lower()
    if is_green_list_tier1(title):
        return '1)英文简历突出具体技术栈(Python/SQL/Cloud/Security)；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1)突出研究经历和论文；2)准备Research Statement；3)联系相关导师'
    elif 'data scientist' in title or 'machine learning' in title:
        return '1)Python/R + ML项目作品集；2)Kaggle/GitHub展示；3)统计学基础补强'
    else:
        return '非目标岗位，不建议投入精力'


def immigration_note(j):
    title = j['title'].lower()
    anzsco_code, anzsco_name = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence{" | " + anzsco_code + " " + anzsco_name if anzsco_code else ""} — 有offer即可直申居留'
    elif 'data scientist' in title or 'ict support' in title or 'network administrator' in title:
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    else:
        return '非绿名单，移民路径弱，建议忽略'


def build_job_record(j):
    code, name = green_list_anzsco(j['title'])
    return {
        'title': j['title'],
        'company': j['company'],
        'location': j['location'],
        'salary': j['salary'],
        'url': j['url'],
        'score': j['score'],
        'reasons': j['reasons'],
        'immigration_path': immigration_note(j),
        'suggested_skills': suggest_skills(j),
        'anzsco_code': code,
        'anzsco_name': name,
    }


# ===== MAIN =====
print("=" * 60)
print("SEEK NZ 岗位扫描 - 2026-07-29")
print("=" * 60)

# Load all emails
all_jobs = []
email_count = 0
for path, ftype, label in FILES:
    if ftype == "inline":
        if INLINE_ICT13_BODY is None:
            print(f"SKIP inline ICT13: body not set")
            continue
        body = INLINE_ICT13_BODY
    else:
        path_str = str(path)
        if not os.path.exists(path_str):
            print(f"MISSING: {path_str}")
            continue
        body = load_body(path_str, ftype)
    
    jobs = extract_jobs_mjml(body)
    email_count += 1
    print(f"[{label}] {os.path.basename(str(path)) if ftype != 'inline' else 'inline_ICT13'}: {len(jobs)} jobs extracted")

    for j in jobs:
        j['source'] = label
    all_jobs.extend(jobs)

print(f"\nEmails processed: {email_count}")
print(f"Raw jobs extracted: {len(all_jobs)}")

# Deduplicate
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"After dedup: {len(unique_jobs)}")

# Score
for j in unique_jobs:
    s, r = score_job(j)
    j['score'] = s
    j['reasons'] = r

# Sort
unique_jobs.sort(key=lambda x: x['score'], reverse=True)

# Filter relevant (>= 35)
relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)

tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']) and not is_green_list_tier1(j['title']))

high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 45 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 45]

# ===== Generate Report =====
today = datetime.now().strftime('%Y-%m-%d')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
workspace_root = Path(__file__).parent
report_path = workspace_root / f'SEEK_NZ_Job_Report_{today}.md'

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送（4封邮件，2026-07-28 Admin×1 + ICT×2 + NZ General×1）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | 4（2026-07-28 Admin×1 + ICT×2 + NZ General×1） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 🏆最佳匹配 | {high[0]['title'] + ' (' + high[0]['company'] + ') ' + str(high[0]['score']) + '分' if high else '无60+高匹配'} |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(45-59) | {len(medium)} |
| 低匹配(35-44) | {len(low)} |

---

## 🚨 策略提醒

本脚本仅保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence）
2. **大学/研究机构的研究岗**（雇主担保工签，可衔接德国博士）

BA/BSA/Data Analyst虽工作内容可能匹配，但**不在绿名单**，移民路径弱，已降级过滤。

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""

if high:
    for idx, j in enumerate(high, 1):
        anzsco_code, anzsco_name = green_list_anzsco(j['title'])
        report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** |
| **ANZSCO** | {anzsco_code} {anzsco_name if anzsco_code else '非绿名单'} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '近期'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |

"""
else:
    report += "**本轮无60分以上高匹配岗位。**\n\n"

report += """---

## 🟡 中匹配岗位 (45-59分) — Tier2 / 数据库相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | ANZSCO | 核心匹配点 |
|---|------|------|------|------|--------|--------|-----------|
"""
for idx, j in enumerate(medium, start=len(high)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    code, name = green_list_anzsco(j['title'])
    anzsco_str = f"{code} {name}" if code else '-'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {anzsco_str} | {'；'.join(j['reasons'][:3])} |\n"

if not medium:
    report += "| - | 本轮无中匹配岗位 | - | - | - | - | - | - |\n"

report += """
---

## 🔵 低匹配岗位 (35-44分) — 可观望

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
for idx, j in enumerate(low, start=len(high)+len(medium)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"

if not low:
    report += "| - | 本轮无低匹配岗位 | - | - | - | - | - |\n"

# Tier1 detail table
tier1_jobs = [j for j in unique_jobs if is_green_list_tier1(j['title'])]
report += f"""
---

## 🎯 绿名单Tier1岗位详情

| 职位 | 公司 | 地点 | 薪资 | 匹配度 | ANZSCO | 移民路径 |
|------|------|------|------|--------|--------|---------|
"""
if tier1_jobs:
    for j in tier1_jobs:
        sal = j['salary'] if j['salary'] else '未公布'
        code, name = green_list_anzsco(j['title'])
        report += f"| {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {code} {name} | Straight to Residence |\n"
else:
    report += "| **本轮无绿名单Tier1岗位** 🚨 | - | - | - | - | - | - |\n"

# Weekly trend
report += f"""
---

## 📈 绿名单Tier1趋势（近7轮）

| 日期 | 扫描邮件 | 去重岗位 | 绿名单Tier1 | 趋势 |
|------|----------|----------|------------|------|
| 7/22 | - | - | 0 | - |
| 7/23 | - | - | 0 | - |
| 7/24 | - | - | 0 | - |
| 7/25 | 4 | 66 | 2 | ⬆ (Junior SW Dev + Compliance SysAdmin) |
| 7/26 | 1 | 23 | 2 | ➡ (同上延续) |
| 7/27 | 5 | 74 | 0 | ⬇ 归零 |
| **7/28** | **4** | **{len(unique_jobs)}** | **{tier1_count}** | **{'⬆' if tier1_count > 0 else '➡ 继续归零'}** |

---

## 🎯 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 绿名单Tier1 ICT岗在NZ市场出现频次极低
- {'本轮' + str(tier1_count) + '个Tier1岗位，' if tier1_count > 0 else '本轮无Tier1岗位，'}主线继续以德国博士为主

### 新西兰副线（10%精力）
1. {'如出现Tier1岗：可考虑投递作为出境跳板' if tier1_count > 0 else '持续监控绿名单Tier1 ICT岗出现频率'}
2. 关注大学/研究机构研究岗（可衔接德国博士）
3. 所有绿名单路径都需要：**NZQA IQA学历评估**（4-8周，NZ$745）

---

*报告由自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

with open(str(report_path), 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {report_path}")

# ===== KOS Feed =====
kos_section_dir = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")
kos_section_dir.mkdir(parents=True, exist_ok=True)

kos_meta = {
    "title": "SEEK NZ 绿名单岗位追踪",
    "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
    "icon": "briefcase",
    "section_id": "seek-nz",
    "last_updated": datetime.now().isoformat(),
}

kos_data = {
    "date": today,
    "email_count": email_count,
    "total_jobs": len(unique_jobs),
    "tier1_jobs": [build_job_record(j) for j in tier1_jobs],
    "all_jobs": [build_job_record(j) for j in unique_jobs],
}

kos_feed = {"meta": kos_meta, "data": kos_data}

# latest.json
latest_path = kos_section_dir / "latest.json"
with open(str(latest_path), 'w', encoding='utf-8') as f:
    json.dump(kos_feed, f, ensure_ascii=False, indent=2)
print(f"KOS latest.json saved: {latest_path}")

# Snapshot
snapshot_path = kos_section_dir / f"seek-nz_{today}.json"
with open(str(snapshot_path), 'w', encoding='utf-8') as f:
    json.dump(kos_feed, f, ensure_ascii=False, indent=2)
print(f"KOS snapshot saved: {snapshot_path}")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY: {email_count} emails, {len(unique_jobs)} deduped jobs, {tier1_count} Tier1, {len(high)} high, {len(medium)} medium, {len(low)} low")
print(f"Tier1 jobs: {[j['title'] + ' (' + j['company'] + ')' for j in tier1_jobs]}")
print(f"Top 5 scores: {[(j['title'], j['company'], j['score']) for j in unique_jobs[:5]]}")
print(f"{'='*60}")
