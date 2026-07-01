#!/usr/bin/env python3
"""Parse SEEK job alert emails from QQ mail - 6/25 daily scan.
Focus on newest emails (6/24) and produce structured analysis report."""
import os, re, json
from pathlib import Path
from html.parser import HTMLParser

# New email files from 6/24
NEW_TOOL_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\f1af200b-656b-4623-b2a4-9cc9f0f9d654\tool-results")

class SeekEmailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.all_links = []
        self.in_a_tag = False
        self.current_href = ""
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.in_a_tag = True
            self.current_href = dict(attrs).get('href', '')
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_a_tag:
            self.in_a_tag = False
            text = self.current_text.strip()
            if text:
                self.all_links.append({'text': text, 'href': self.current_href})
            self.current_text = ""
            self.current_href = ""

    def handle_data(self, data):
        if self.in_a_tag:
            self.current_text += data


def extract_jobs_from_email(filepath):
    """Parse a SEEK email file and extract all job listings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    try:
        data = json.loads(raw)
        body = data.get('data', {}).get('data', {}).get('body', '')
        subject = data.get('data', {}).get('data', {}).get('subject', '')
        date = data.get('data', {}).get('data', {}).get('created_at', '')
    except json.JSONDecodeError:
        body = raw
        subject = ''
        date = ''

    # Clean HTML
    body_clean = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body_clean = re.sub(r'<script[^>]*>.*?</script>', '', body_clean, flags=re.DOTALL)

    # Parse links
    parser = SeekEmailParser()
    parser.feed(body_clean)

    # Plain text
    plain = re.sub(r'<[^>]+>', '\n', body_clean)
    plain = re.sub(r'\n\s*\n', '\n', plain)

    # Extract text blocks between job items
    # SEEK emails format: title, company, location, salary in separate lines
    lines = [l.strip() for l in plain.split('\n') if l.strip()]

    # Skip boilerplate lines
    skip_words = ['hi wang', 'based on', 'we\'ve found', 'could be right',
                  'seek limited', 'view all', 'unsubscribe', 'update',
                  'delete', 'manage', 'privacy', 'contact', 'registered user',
                  'save this', 'job alert', 'seek profile']

    jobs = []

    # Method 1: Extract from SEEK job links
    seek_links = [l for l in parser.all_links if 'nz.seek.co.nz' in l.get('href', '')]
    job_links = []
    for link in seek_links:
        text = link['text']
        href = link['href']
        if any(s in text.lower() for s in ['view all', 'unsubscribe', 'update', 'delete',
                                            'manage', 'privacy', 'contact', 'seek profile',
                                            'start my search', 'save this', 'see all']):
            continue
        if '/job/' in href or 'jobid' in href.lower():
            job_links.append(link)

    # Method 2: Parse plain text blocks for job listings
    # Pattern: Title line, Company line, Location line, Salary line
    nz_locations = ['Auckland CBD', 'Wellington Central', 'Christchurch Central',
                    'Hamilton Central', 'Tauranga Central', 'Invercargill Central',
                    'New Plymouth Central', 'Rotorua Central', 'Auckland', 'Wellington',
                    'Christchurch', 'Hamilton', 'Tauranga', 'Invercargill', 'New Plymouth',
                    'Napier', 'Dunedin', 'Henderson', 'Mount Wellington', 'Parnell',
                    'Takapuna', 'Onehunga', 'East Tamaki', 'Manukau', 'Penrose',
                    'Matangi', 'Te Rapa', 'Ellerslie', 'Southland', 'Canterbury',
                    'Waikato', 'Bay of Plenty', 'Taranaki']

    salary_pattern = r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum))?'
    competitive_pattern = r'Competitive|Expected starting salary'

    # Group lines into job blocks - each job typically has 3-4 consecutive lines
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip boilerplate
        if any(s in line.lower() for s in skip_words) or len(line) < 3:
            i += 1
            continue

        # Check if this line could be a job title
        # Job titles don't contain email boilerplate, are not too short
        # They often appear before a location line
        title_candidate = line

        # Look at next lines for company, location, salary
        company = ''
        location = ''
        salary = ''
        link = ''

        # Check if title_candidate matches a job link
        for jl in job_links:
            if jl['text'].strip() == title_candidate.strip() or jl['text'].strip()[:30] == title_candidate.strip()[:30]:
                link = jl['href']
                break

        # Scan next few lines
        next_lines = lines[i+1:i+5] if i+1 < len(lines) else []

        for nl in next_lines:
            # Check for location
            for loc in nz_locations:
                if loc in nl and not location:
                    location = nl
                    break

            # Check for salary
            sal_m = re.search(salary_pattern, nl)
            comp_m = re.search(competitive_pattern, nl, re.IGNORECASE)
            if sal_m and not salary:
                salary = sal_m.group()
            elif comp_m and not salary:
                salary = nl.strip()

        # If we found location or salary nearby, this is likely a job entry
        # Company is often between title and location
        if location or salary:
            # Try to find company in next lines
            for nl in next_lines:
                if nl != location and nl != salary and len(nl) > 2 and len(nl) < 80:
                    # Not a boilerplate line
                    if not any(s in nl.lower() for s in skip_words):
                        if not re.search(salary_pattern, nl) and not any(loc in nl for loc in nz_locations):
                            company = nl
                            break

            # Also check if company is embedded in the location line
            if location and ',' in location:
                # Location format: "Area, City, Region" or company before location
                pass

            jobs.append({
                'title': title_candidate,
                'company': company,
                'location': location,
                'salary': salary,
                'link': link,
                'email_date': date,
                'email_subject': subject
            })
            # Skip the lines we already processed
            i += 1 + min(len(next_lines), 3)
        else:
            # Might still be a job without clear location/salary
            # Check if title matches known job patterns
            job_keywords = ['analyst', 'engineer', 'developer', 'consultant', 'manager',
                           'administrator', 'support', 'specialist', 'coordinator',
                           'technician', 'assistant', 'officer', 'lead', 'architect',
                           'scientist', 'designer']
            if any(k in title_candidate.lower() for k in job_keywords):
                # Look harder for company
                for nl in next_lines[:2]:
                    if len(nl) > 2 and len(nl) < 80 and not any(s in nl.lower() for s in skip_words):
                        if not any(loc in nl for loc in nz_locations):
                            company = nl
                            break
                        else:
                            location = nl

                jobs.append({
                    'title': title_candidate,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'link': link,
                    'email_date': date,
                    'email_subject': subject
                })
                i += 1 + min(len(next_lines), 2)
            else:
                i += 1

    return jobs, subject, date


def deduplicate_jobs(all_jobs):
    seen = set()
    unique = []
    for job in all_jobs:
        key = f"{job.get('title', '').strip()}|{job.get('company', '').strip()}|{job.get('location', '').strip()}"
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


# === Process the 3 newest email files ===
all_jobs = []
files = list(NEW_TOOL_DIR.glob("mcp-connector-proxy-qq-mail_GetMessage*.txt"))
print(f"Found {len(files)} new email files to process")

for f in sorted(files):
    print(f"\nProcessing: {f.name}")
    jobs, subject, date = extract_jobs_from_email(f)
    print(f"  Subject: {subject}")
    print(f"  Date: {date}")
    print(f"  Jobs extracted: {len(jobs)}")
    for j in jobs:
        print(f"    - {j['title']} | {j['company']} | {j['location']} | {j['salary']}")
    all_jobs.extend(jobs)

# === Also add jobs from the SearchMessages snippets (from today's search) ===
# These are the newest emails from 6/24 that we can see from the search results
snippet_jobs = [
    # msg_tZwWNWjacLu6 - Admin, 6/24 23:58 (NEW unread)
    {"title": "Service Desk Support", "company": "Rotorua Lakes Council", "location": "Rotorua Central, Bay of Plenty", "salary": "$65,000 – $75,000 per year", "link": "", "email_date": "2026-06-24T23:58:15Z"},
    {"title": "Service Desk Administrator", "company": "The Audit Office", "location": "Wellington Central, Wellington", "salary": "Expected starting salary between $66,000-$77,000", "link": "", "email_date": "2026-06-24T23:58:15Z"},
    {"title": "Office Administrator", "company": "A.J. TUTILL & SONS LIMITED", "location": "Penrose, Auckland", "salary": "$65,000 – $70,000 per year", "link": "", "email_date": "2026-06-24T23:58:15Z"},
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Henderson, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-24T23:58:15Z"},

    # msg_hJBeJs-YNNNYcVo3sKRGn - ICT, 6/24 21:47 (NEW unread)
    {"title": "Technical Business Analyst", "company": "Maori Television", "location": "East Tamaki, Auckland", "salary": "", "link": "", "email_date": "2026-06-24T21:47:15Z"},
    {"title": "Research and Development Scientist", "company": "Sanitarium Health Food Company", "location": "Epsom, Auckland", "salary": "", "link": "", "email_date": "2026-06-24T21:47:15Z"},
    {"title": "Business Analyst", "company": "Rotorua Lakes Council", "location": "Rotorua Central, Bay of Plenty", "salary": "$92,000 – $102,000 per year", "link": "", "email_date": "2026-06-24T21:47:15Z"},
    {"title": "Data Engineer", "company": "REINZ", "location": "Auckland CBD, Auckland", "salary": "$90,000 – $115,000 per year", "link": "", "email_date": "2026-06-24T21:47:15Z"},
    {"title": "Business Analyst - ICT", "company": "New Zealand Police", "location": "Wellington Central, Wellington", "salary": "$110,425", "link": "", "email_date": "2026-06-24T21:47:15Z"},
    {"title": "Business Operations Analyst", "company": "Cultivate – SEEK", "location": "", "salary": "", "link": "", "email_date": "2026-06-24T21:47:15Z"},

    # msg_MH43aXI6IgyJA37c9uCUVla - ICT, 6/24 20:25 (NEW unread)
    {"title": "Technical Business Analyst", "company": "Maori Television", "location": "East Tamaki, Auckland", "salary": "", "link": "", "email_date": "2026-06-24T20:25:32Z"},
    {"title": "Data Engineer", "company": "REINZ", "location": "Auckland CBD, Auckland", "salary": "$90,000 – $115,000 per year", "link": "", "email_date": "2026-06-24T20:25:32Z"},
    {"title": "Business Analyst", "company": "Rotorua Lakes Council", "location": "Rotorua Central, Bay of Plenty", "salary": "$92,000 – $102,000 per year", "link": "", "email_date": "2026-06-24T20:25:32Z"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-24T20:25:32Z"},
    {"title": "Data & Reporting Analyst", "company": "", "location": "Te Rapa, Waikato", "salary": "$90,000 - $110,000", "link": "", "email_date": "2026-06-24T20:25:32Z"},
    {"title": "Business Operations Analyst", "company": "Cultivate – SEEK", "location": "", "salary": "", "link": "", "email_date": "2026-06-24T20:25:32Z"},
]

all_jobs.extend(snippet_jobs)
unique_jobs = deduplicate_jobs(all_jobs)

# === Load previous scan data to identify truly NEW jobs ===
prev_scan_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw_0624.json")
prev_jobs = []
if prev_scan_path.exists():
    with open(prev_scan_path, 'r', encoding='utf-8') as f:
        prev_jobs = json.loads(f.read())
    prev_keys = set()
    for j in prev_jobs:
        prev_keys.add(f"{j.get('title', '').strip()}|{j.get('company', '').strip()}|{j.get('location', '').strip()}")

    # Filter to only truly new jobs
    new_jobs = []
    for j in unique_jobs:
        key = f"{j.get('title', '').strip()}|{j.get('company', '').strip()}|{j.get('location', '').strip()}"
        if key not in prev_keys:
            new_jobs.append(j)

    print(f"\n=== DEDUPLICATION RESULTS ===")
    print(f"Total unique from this scan: {len(unique_jobs)}")
    print(f"Previously known: {len(prev_keys)}")
    print(f"Truly NEW jobs: {len(new_jobs)}")
else:
    new_jobs = unique_jobs
    print(f"\nNo previous scan data found. All {len(unique_jobs)} jobs treated as new.")

# === Match Analysis ===
# User profile: 45yo, Mechanical Engineering bachelor + ISTIC Information Resource Management master (86+)
# 20 years quality engineering experience, Python data analysis, ERP(SAP/Oracle), cable data project

def match_score(job):
    """Calculate match score (0-100) based on user profile."""
    title = job.get('title', '').lower()
    company = job.get('company', '').lower()
    location = job.get('location', '').lower()
    salary = job.get('salary', '')
    score = 0
    notes = []
    green_list = False
    green_tier = ''
    immigration_path = ''

    # === Green List Tier 1 (highest priority) ===
    # Mechanical Engineer - ANZSCO 233512
    if 'mechanical engineer' in title:
        score = 95
        green_list = True
        green_tier = 'Tier 1'
        immigration_path = 'Straight to Residence (有offer直申居留)'
        notes.append('绿名单Tier1！机械工程学士直接匹配')
        notes.append('20年质量工程经验是加分项')
        notes.append('需NZQA IQA学历评估')

    # === Green List Tier 2 ===
    # ICT roles on green list
    elif any(k in title for k in ['data engineer', 'data scientist']):
        score = 70
        green_list = True
        green_tier = 'Tier 2'
        immigration_path = 'Work to Residence (2年后申居留)'
        notes.append('绿名单Tier2：Data Engineer/Scientist')

    # === High Match: BSA/BA with ERP ===
    elif 'business system' in title and 'erp' in title.lower():
        score = 80
        immigration_path = 'Work to Residence (需2年工作经验转居留)'
        notes.append('ERP+业务系统分析：完美匹配SAP/Oracle经验')
        notes.append('需补充：NZ ERP市场知识(Dynamics 365常见)')

    # === High Match: Business Analyst ===
    elif 'business analyst' in title:
        if 'senior' in title or 'technical' in title:
            score = 75
            notes.append('高级/技术BA：质量工程+数据分析经验可转化')
            notes.append('需补充：NZ公共部门BA方法论(NZ Police等)')
        elif 'ict' in title or 'ict' in company:
            score = 78
            notes.append('ICT BA：直接匹配信息资源管理背景')
        else:
            score = 65
            notes.append('通用BA：需要行业知识转化')
        immigration_path = 'Essential Skills Work Visa → 2年后转居留'

    # === Medium-High: Data Analyst ===
    elif 'data analyst' in title:
        score = 72
        immigration_path = 'Essential Skills Work Visa → 2年后转居留'
        notes.append('Python数据分析能力直接匹配')
        notes.append('需补充：NZ数据治理法规、统计软件(R/SPSS)')
        if 'stats nz' in company.lower():
            score = 75
            notes.append('Stats NZ是政府核心数据机构，稳定性高')

    # === Medium: Data Engineer ===
    elif 'data engineer' in title:
        score = 68
        immigration_path = 'Work to Residence (绿名单Tier2，2年后申居留)'
        notes.append('绿名单Tier2！Python+数据库经验可转化')
        notes.append('需补充：ETL工具(Python+SQL已够)、云平台(AWS/Azure)')

    # === Medium: System Analyst ===
    elif 'system analyst' in title:
        score = 65
        immigration_path = 'Essential Skills Work Visa → 2年后转居留'
        notes.append('系统分析：ERP+质量管理经验可转化')

    # === Medium: Functional Consultant ===
    elif 'functional consultant' in title or 'graduate functional' in title:
        score = 60
        immigration_path = 'Essential Skills Work Visa'
        notes.append('ERP功能顾问：SAP/Oracle经验相关')
        notes.append('Graduate级别可能要求NZ学历认证')

    # === Medium: Operations Analyst ===
    elif 'operations analyst' in title or 'business operations' in title:
        score = 55
        immigration_path = 'Essential Skills Work Visa'
        notes.append('运营分析：质量管理+流程优化经验可转化')

    # === Medium-Low: ICT Support ===
    elif any(k in title for k in ['service desk', 'it support', 'support engineer', 'support analyst',
                                    'information system', 'ict support', 'entry level support']):
        score = 45
        immigration_path = 'Essential Skills Work Visa (薪资需达标)'
        notes.append('ICT支持：技术基础匹配但岗位偏低')
        if 'entry level' in title:
            score = 35
            notes.append('入门级，薪资偏低，非最优路径')

    # === Low: Office/Admin ===
    elif any(k in title for k in ['office', 'admin', 'coordinator', 'customer service']):
        score = 30
        immigration_path = '非技术移民路径（薪资通常不达标）'
        notes.append('行政岗位：移民路径弱，薪资常低于$55K门槛')

    # === Medium: R&D/Research ===
    elif 'research' in title or 'scientist' in title:
        score = 50
        immigration_path = 'Essential Skills Work Visa'
        notes.append('研究岗位：需要特定领域专业知识')

    # === Default ===
    else:
        score = 40
        immigration_path = 'Essential Skills Work Visa'
        notes.append('需进一步评估岗位匹配度')

    # Location bonus
    if 'wellington' in location:
        score += 3  # Wellington has more govt BA roles
        notes.append('惠灵顿：政府机构集中，BA岗位多')
    elif 'auckland' in location:
        score += 2  # Auckland has most jobs
        notes.append('奥克兰：就业市场最大')

    # Salary info bonus
    if salary and '$' in salary:
        notes.append(f'薪资范围: {salary}')

    return {
        'score': min(score, 100),
        'notes': notes,
        'green_list': green_list,
        'green_tier': green_tier,
        'immigration_path': immigration_path
    }


# === Generate Report ===
# Sort all jobs by match score
matched_jobs = []
for j in unique_jobs:
    m = match_score(j)
    matched_jobs.append({**j, **m})

matched_jobs.sort(key=lambda x: x['score'], reverse=True)

# Categorize
high_match = [j for j in matched_jobs if j['score'] >= 70]
mid_match = [j for j in matched_jobs if 50 <= j['score'] < 70]
low_match = [j for j in matched_jobs if j['score'] < 50]

# Find truly new high/mid matches
new_high = [j for j in new_jobs if match_score(j)['score'] >= 70] if new_jobs else []
new_mid = [j for j in new_jobs if 50 <= match_score(j)['score'] < 70] if new_jobs else []

# Generate markdown report
today = "2026-06-25"
report = f"""# SEEK NZ 岗位扫描报告 - {today}

## 执行概要
- 扫描时间：{today} 08:04
- 邮件范围：6/24-6/25 SEEK推送（3封新邮件 + 搜索摘要）
- 去重岗位总数：{len(unique_jobs)}
- **本轮新增岗位**：{len(new_jobs)}

## 🎯 匹配分类

| 级别 | 数量 | 岗位列表 |
|------|------|----------|
| 🔴 高匹配(≥70) | {len(high_match)} | {', '.join([j['title'] for j in high_match[:5]])} |
| 🟡 中匹配(50-69) | {len(mid_match)} | {', '.join([j['title'] for j in mid_match[:5]])} |
| 🟢 低匹配(<50) | {len(low_match)} | {', '.join([j['title'] for j in low_match[:5]])} |

"""

# Add green list section
green_jobs = [j for j in matched_jobs if j.get('green_list')]
if green_jobs:
    report += "## 🚨 绿名单岗位（移民最优路径）\n\n"
    report += "| 职位 | 公司 | 地点 | 薪资 | 绿名单级别 | 移民路径 | 匹配度 |\n"
    report += "|------|------|------|------|-----------|---------|--------|\n"
    for j in green_jobs:
        report += f"| {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['green_tier']} | {j['immigration_path']} | {j['score']} |\n"
    report += "\n"

# Add high match section
report += "## 🔴 高匹配岗位（≥70分）\n\n"
report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 移民路径 | 关键说明 |\n"
report += "|---|------|------|------|------|--------|---------|----------|\n"
for i, j in enumerate(high_match, 1):
    notes_str = '；'.join(j['notes'][:3]) if j['notes'] else ''
    report += f"| {i} | {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['score']} | {j['immigration_path']} | {notes_str} |\n"
report += "\n"

# Add mid match section
report += "## 🟡 中匹配岗位（50-69分）\n\n"
report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 移民路径 | 关键说明 |\n"
report += "|---|------|------|------|------|--------|---------|----------|\n"
for i, j in enumerate(mid_match, 1):
    notes_str = '；'.join(j['notes'][:3]) if j['notes'] else ''
    report += f"| {i} | {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['score']} | {j['immigration_path']} | {notes_str} |\n"
report += "\n"

# Add low match section (brief)
report += "## 🟢 低匹配岗位（<50分）\n\n"
report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 |\n"
report += "|---|------|------|------|------|--------|\n"
for i, j in enumerate(low_match, 1):
    report += f"| {i} | {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['score']} |\n"
report += "\n"

# Add new jobs highlight
if new_jobs:
    report += "## 🆕 本轮新增岗位\n\n"
    new_matched = []
    for j in new_jobs:
        m = match_score(j)
        new_matched.append({**j, **m})
    new_matched.sort(key=lambda x: x['score'], reverse=True)

    report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 是否绿名单 |\n"
    report += "|---|------|------|------|------|--------|------------|\n"
    for i, j in enumerate(new_matched, 1):
        gl = '🚨' + j['green_tier'] if j['green_list'] else '—'
        report += f"| {i} | {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['score']} | {gl} |\n"
    report += "\n"

# Add key findings
report += "## 📌 关键发现与建议\n\n"

# Check for mechanical engineer
me_jobs = [j for j in matched_jobs if 'mechanical engineer' in j['title'].lower()]
if me_jobs:
    report += f"### 🚨 机械工程师岗位\n"
    for j in me_jobs:
        report += f"- **{j['title']}** @ {j['company']} ({j['location']}) — 匹配度{j['score']}分\n"
        report += f"  - 绿名单Tier1：有offer即可直申居留！\n"
        report += f"  - 需NZQA IQA学历评估（4-8周，NZ$745）\n"
else:
    report += f"### ⚠️ 本轮无机械工程师岗位\n"
    report += f"- 绿名单Tier1最优路径暂时缺位\n"
    report += f"- 建议：SEEK单独搜索\"Mechanical Engineer\"并保存提醒\n"

# BA trends
ba_jobs = [j for j in matched_jobs if 'business analyst' in j['title'].lower() or 'business system' in j['title'].lower()]
report += f"\n### Business Analyst趋势\n"
report += f"- 本轮BA/BSA岗位：{len(ba_jobs)}个\n"
for j in ba_jobs[:5]:
    report += f"- {j['title']} @ {j['company']} ({j['location']}) — {j['score']}分\n"

# Data Analyst trends
da_jobs = [j for j in matched_jobs if 'data analyst' in j['title'].lower() or 'data engineer' in j['title'].lower()]
report += f"\n### Data Analyst/Engineer趋势\n"
report += f"- 本轮Data岗位：{len(da_jobs)}个\n"
for j in da_jobs[:5]:
    report += f"- {j['title']} @ {j['company']} ({j['location']}) — {j['score']}分\n"

report += "\n### 🎯 行动建议\n"
report += "1. **机械工程师路径**：持续监控SEEK机械工程师岗位，一旦出现立即申请\n"
report += "2. **BA-ICT路径**：NZ Police BA-ICT ($110K) 和 Rotorua Lakes BA ($92-102K) 是当前最佳ICT路径\n"
report += "3. **Data路径**：REINZ Data Engineer ($90-115K) 绿名单Tier2，Python能力匹配\n"
report += "4. **NZQA评估**：无论哪条路径，学历评估都是前置条件，建议尽快启动\n"
report += "5. **语言准备**：PTE 58分（对标雅思6.5）需同步推进\n"

# Save report
report_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\SEEK_NZ_Job_Report_2026-06-25.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved to: {report_path}")

# Save raw jobs JSON for next scan dedup
raw_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw_0625.json")
with open(raw_path, 'w', encoding='utf-8') as f:
    json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
print(f"Raw jobs saved to: {raw_path}")

# Print summary
print(f"\n=== SCAN SUMMARY ===")
print(f"Total unique jobs: {len(unique_jobs)}")
print(f"High match (≥70): {len(high_match)}")
print(f"Mid match (50-69): {len(mid_match)}")
print(f"Low match (<50): {len(low_match)}")
print(f"Green list jobs: {len(green_jobs)}")
print(f"New this round: {len(new_jobs)}")
print(f"Mechanical Engineer found: {len(me_jobs) > 0}")
