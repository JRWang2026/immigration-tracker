#!/usr/bin/env python3
"""
SEEK NZ Job Scanner - 2026-07-17
Processes 4 SEEK job alert emails from 7/16 (ICT x2 + Admin x1 + NZ General x1)
Generates Green List Tier1 focused report + KOS JSON feed
"""
import json, re, os, html as html_mod
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# Email files saved by QQ Mail connector GetMessage
EMAIL_FILES = [
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\1d183e89-7e3d-47a8-9a60-1b469ec4a27b\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784246765130-7d031d.txt',
     '2026-07-16 ICT 15jobs'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr-Wang-WorkBuddy-2026-06-20-14-48-36\1d183e89-7e3d-47a8-9a60-1b469ec4a27b\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784246765051-0b2e40.txt',
     '2026-07-16 Admin 20jobs'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr-Wang-WorkBuddy-2026-06-20-14-48-36\1d183e89-7e3d-47a8-9a60-1b469ec4a27b\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784246765201-c9f9b4.txt',
     '2026-07-16 ICT 20jobs'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr-Wang-WorkBuddy-2026-06-20-14-48-36\1d183e89-7e3d-47a8-9a60-1b469ec4a27b\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784246765274-e1a300.txt',
     '2026-07-16 NZ General 20jobs'),
]

def load_body(path):
    """Load email body from QQ Mail connector JSON response"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # QQ Mail GetMessage returns: data.data.body
    return data['data']['data']['body']

def extract_jobs_mjml(body):
    """Extract jobs from MJML-formatted SEEK email (post July 2026 template)"""
    jobs = []

    # MJML template: jobs are in <a style="display: block" ...> cards
    # Title is in <!--[if mso]><a>...<![endif]-->TITLE<!--[if mso]></a><![endif]-->
    # or directly in div with text-decoration:underline
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        # Title: look for text-decoration:underline pattern (MJML template)
        title_match = re.search(r'text-decoration:underline[^>]*>(?:<!--\[if mso\]><a[^>]*>.*?<!\[endif\]-->)?([^<]+)(?:<!--\[if mso\]></a><!\[endif\]-->)?</div>', card, re.DOTALL)

        # Alternative title pattern
        if not title_match:
            title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)

        # Company: font-size:14px;line-height:21px;padding-bottom:12px
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)

        # Location and salary: color:#2E3849 divs
        info_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)

        # Salary pattern: $amount
        salary_match = re.search(r'>\$[^<]+</div>', card)

        # URL
        url_match = re.search(r'href="([^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        # Skip cards without title/company
        if not title or not company or len(title) > 200:
            # Try alternative extraction for MJML template
            # Sometimes title is in a different div structure
            alt_title = re.search(r'font-weight:700[^>]*font-size:18px[^>]*>([^<]+)</div>', card)
            if alt_title:
                title = alt_title.group(1).strip()
            else:
                continue

        if not company:
            continue

        # Location: first info match with comma pattern (City, Region)
        location = 'Unknown'
        salary = ''

        for im in info_matches:
            im = im.strip()
            if not im or im == title or im == company:
                continue
            # Location pattern: "City, Region"
            if ',' in im and not im.startswith('$') and not re.match(r'^\d', im):
                if location == 'Unknown':
                    location = im
            # Salary pattern: starts with $ or contains "per year" / "per hour"
            elif im.startswith('$') or 'per year' in im.lower() or 'per hour' in im.lower() or 'per annum' in im.lower():
                if not salary:
                    salary = im
            # Other text might be salary description
            elif not salary and not re.match(r'^\d+ \w+ \d+$', im):
                # Could be salary description like "Competitive Salary + Benefits"
                if re.search(r'(competitive|salary|benefits|insurance|super|bonus|market related|remuneration)', im, re.I):
                    salary = im

        # Also try direct salary match
        if not salary and salary_match:
            salary = salary_match.group(0).replace('>', '').replace('</div>', '').strip()

        # URL
        url = url_match.group(1) if url_match else ''

        # Clean HTML entities
        title = html_mod.unescape(title).strip()
        company = html_mod.unescape(company).strip()
        location = html_mod.unescape(location).strip()
        salary = html_mod.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': '',
            'url': url,
            'source': ''
        })

    return jobs


# ===== Scoring system (Green List Tier1 focused) =====

def is_research_org(company):
    kws = ['university', 'research institute', 'research centre', 'crown research',
           'gns science', 'callaghan innovation', 'agresearch', 'plant & food',
           'scion', 'landcare', 'niwa', 'branz', 'esr', 'institute of canterbury',
           'ara institute', 'otago', 'canterbury university', 'auckland university',
           'massey university', 'victoria university', 'lincoln university',
           'waikato university', 'aut university']
    company_lower = company.lower()
    return any(k in company_lower for k in kws)

def is_green_list_tier1(title):
    tier1_keywords = [
        'software engineer', 'software developer', 'full stack developer',
        'backend developer', 'frontend developer', 'full-stack developer',
        'database administrator', 'dba',
        'systems administrator', 'system administrator',
        'analyst programmer', 'programmer analyst',
        'developer programmer', 'application developer',
        'software and applications programmer',
        'multimedia specialist',
        'ict project manager', 'it project manager',
        'ict security specialist', 'cyber security specialist',
        'information security specialist', 'ict security',
        'chief information officer', 'chief digital officer',
    ]
    title_lower = title.lower()
    return any(k in title_lower for k in tier1_keywords)

def green_list_anzsco(title):
    t = title.lower()
    if any(k in t for k in ['software engineer', 'software developer', 'full stack', 'full-stack', 'backend developer', 'frontend developer']):
        return '261313', 'Software Engineer'
    elif 'database administrator' in t or 'dba' in t:
        return '262111', 'Database Administrator'
    elif 'systems administrator' in t or 'system administrator' in t:
        return '262113', 'Systems Administrator'
    elif 'analyst programmer' in t:
        return '261311', 'Analyst Programmer'
    elif 'developer programmer' in t or 'application developer' in t:
        return '261312', 'Developer Programmer'
    elif 'multimedia specialist' in t:
        return '261211', 'Multimedia Specialist'
    elif 'ict project manager' in t or 'it project manager' in t:
        return '135112', 'ICT Project Manager'
    elif 'ict security' in t or 'cyber security' in t or 'information security' in t:
        return '262112', 'ICT Security Specialist'
    elif 'chief information officer' in t:
        return '135111', 'Chief Information Officer'
    return '', ''

def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    salary = j['salary'].lower()
    score = 0
    reasons = []

    research = is_research_org(company)

    # === Role matching (0-55) ===
    if is_green_list_tier1(title):
        score += 55
        code, name = green_list_anzsco(title)
        reasons.append(f'绿名单Tier1: {name} ({code})')
    elif research and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'research scientist', 'research analyst', 'research officer']):
        score += 50
        reasons.append('大学/研究机构研究岗')
    elif research and 'data scientist' in title:
        score += 48
        reasons.append('大学研究型Data Scientist')
    elif research and ('information management' in title or 'knowledge management' in title or 'research information' in title):
        score += 45
        reasons.append('大学信息管理研究岗')
    elif 'data scientist' in title or 'machine learning engineer' in title or 'ai engineer' in title:
        score += 35
        reasons.append('绿名单Tier2: Data Scientist/ML')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30
        reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    elif 'data engineer' in title or 'platform engineer' in title or 'devops' in title:
        score += 28
        reasons.append('Data Engineer/DevOps (非绿名单但ICT相关)')
    elif 'systems support' in title or 'system support' in title or 'it support' in title:
        score += 25
        reasons.append('IT/Systems Support (近ICT基础设施)')
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8
        reasons.append('非绿名单:BSA/BA(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title or 'business insights analyst' in title:
        score += 8
        reasons.append('非绿名单:Data Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator', 'customer service', 'accounts administrator']):
        score += 2
        reasons.append('行政/客服岗:忽略')
    else:
        score += 5
        reasons.append('非目标岗位')

    # === Domain bonus (0-15) ===
    if research:
        score += 15
        reasons.append('大学/研究机构')
    elif any(k in company for k in ['government', 'ministry', 'council', 'education review', 'transport agency', 'waka kotahi']):
        score += 10
        reasons.append('政府/公共部门')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber', 'tech ']):
        score += 12
        reasons.append('ICT/科技公司')

    # === Skills bonus (0-15) ===
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10
        reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin', 'systems admin']):
        score += 10
        reasons.append('ICT基础设施技能')
    if 'data' in title and any(k in title for k in ['scientist', 'engineer', 'machine learning', 'ml']):
        score += 8
        reasons.append('高级数据技能')

    # === Location bonus (0-8) ===
    non_akl = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'otago',
               'bay of plenty', 'hawkes bay', 'napier', 'hastings', 'palmerston north',
               'manawatu', 'marlborough', 'gisborne', 'whanganui', 'taranaki', 'nelson']
    if any((', ' + k in location or location.endswith(', ' + k) or location == k) for k in non_akl):
        score += 8
        reasons.append('非奥克兰地区加分')
    elif ', wellington' in location or location == 'wellington':
        score += 5
        reasons.append('惠灵顿地区')

    # === Penalties ===
    if 'part-time' in title or 'part time' in title:
        score -= 10
        reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry', 'entry level']):
        score -= 10
        reasons.append('初级岗降分')

    return max(0, min(100, score)), reasons

def suggest_skills(j):
    title = j['title'].lower()
    if is_green_list_tier1(title):
        return '1)英文简历突出具体技术栈(Python/SQL/Cloud/Security);2)GitHub作品集;3)准备NZ本地面试题;4)NZQA IQA学历评估'
    elif is_research_org(j['company']):
        return '1)突出研究经历和论文;2)准备Research Statement;3)联系相关导师'
    elif 'data scientist' in title or 'machine learning' in title:
        return '1)Python/R + ML项目作品集;2)Kaggle/GitHub展示;3)统计学基础补强'
    elif 'data engineer' in title or 'devops' in title:
        return '1)Python/SQL + ETL管道经验;2)云平台认证(AWS/Azure);3)数据建模'
    else:
        return '非目标岗位，不建议投入精力'

def immigration_note(j):
    title = j['title'].lower()
    code, name = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence | {code} {name} — 有offer即可直申居留'
    elif 'data scientist' in title or 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif is_research_org(j['company']):
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    else:
        return '非绿名单，移民路径弱，建议忽略'

# ===== Main processing =====

all_jobs = []
email_count = 0

for path, label in EMAIL_FILES:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body(path)
    jobs = extract_jobs_mjml(body)
    print(f"{label}: {len(jobs)} jobs extracted")
    all_jobs.extend(jobs)
    email_count += 1

# Deduplicate by title+company (case-insensitive)
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal raw jobs: {len(all_jobs)}")
print(f"Total unique jobs after dedup: {len(unique_jobs)}")

# Score all jobs
for j in unique_jobs:
    s, r = score_job(j)
    j['score'] = s
    j['reasons'] = r

# Sort by score desc
unique_jobs.sort(key=lambda x: x['score'], reverse=True)

# Filter relevant jobs (score >= 35)
relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)

tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']) and not is_green_list_tier1(j['title']))

high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

# Generate report
today = datetime.now().strftime('%Y-%m-%d')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
report_path = f'SEEK_NZ_Job_Report_{today}.md'

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 来源：QQ邮箱SEEK推送（{email_count}封邮件，7/16 ICT x2 + Admin x1 + NZ General x1）
> 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {email_count}（7/16 ICT x2 + Admin x1 + NZ General x1） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示>=35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 最佳匹配 | {high[0]['title'] if high else (relevant_jobs[0]['title'] if relevant_jobs else '无')} ({high[0]['company'] if high else (relevant_jobs[0]['company'] if relevant_jobs else '-')}) {high[0]['score'] if high else (relevant_jobs[0]['score'] if relevant_jobs else '-')}分 |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |

---

## 策略提醒

当前只保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence，有offer即可直申居留）
2. **大学/研究机构的研究岗**（可走雇主担保工签，研究方向可衔接德国博士）

> 绝大多数BSA/Data Analyst岗位虽然工作内容匹配你的经验，但**不在绿名单**，移民路径弱，已被过滤到低分/忽略区。
> **绿名单Tier1连续归零天数**：{8 if tier1_count == 0 else 0}天（7/10 HR Systems Admin最后出现后持续归零）

---

"""

# High match section
if high:
    report += "## 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗\n\n"
    for idx, j in enumerate(high, 1):
        star = '⭐' if idx == 1 else ''
        report += f"""### {idx}. {star} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |

"""
else:
    report += "## 高匹配岗位 (60+分)\n\n> 本轮无高匹配岗位\n\n"

report += "---\n\n## 中匹配岗位 (40-59分) — Tier2 / 研究相关\n\n"
if medium:
    report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |\n"
    report += "|---|------|------|------|------|--------|------------|\n"
    for idx, j in enumerate(medium, start=len(high)+1):
        sal = j['salary'] if j['salary'] else '未公布'
        report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"
else:
    report += "> 本轮无中匹配岗位\n"

report += "\n---\n\n## 低匹配岗位 (35-39分) — 可观望\n\n"
if low:
    report += "| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |\n"
    report += "|---|------|------|------|------|--------|------|\n"
    for idx, j in enumerate(low, start=len(high)+len(medium)+1):
        sal = j['salary'] if j['salary'] else '未公布'
        report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"
else:
    report += "> 本轮无低匹配岗位\n"

# All jobs summary (TOP 20)
report += "\n---\n\n## 本轮扫描到的全部岗位 TOP 20\n\n"
report += "| # | 职位 | 公司 | 地点 | 薪资 | 分数 |\n"
report += "|---|------|------|------|------|------|\n"
for idx, j in enumerate(unique_jobs[:20], 1):
    sal = j['salary'] if j['salary'] else '-'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} |\n"

report += f"""

---

## 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 当前SEEK推送中绿名单Tier1 ICT岗已连续{8 if tier1_count == 0 else '0'}天归零
- 新西兰作为"备选出境通道"保留，但**不建议主动投递非绿名单岗位**

### 新西兰副线（10%精力）
1. **只关注绿名单Tier1 ICT岗**：Software Engineer / Database Administrator / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security Specialist / CIO
2. **只关注大学/研究机构的研究岗**
3. **如出现绿名单Tier1 offer**：可作为一个出境跳板，后续再申德国博士

### 简历准备（绿名单ICT方向）
- 英文简历突出：**Python/SQL/Cloud/GitHub作品集**
- 如投Software Engineer：准备LeetCode风格算法题 + 系统设计基础
- 如投Database Administrator：突出SQL优化、数据建模、ERP数据库经验
- 所有绿名单ICT岗都需要：**NZQA IQA学历评估**（4-8周，NZ$745）

---

## 绿名单移民路径提醒

| 职业 | ANZSCO | 绿名单层级 | 移民路径 | 你的匹配度 |
|------|--------|-----------|---------|----------|
| Software Engineer | 261313 | **Tier1** | Straight to Residence | 低（非程序员背景） |
| Database Administrator | 262111 | **Tier1** | Straight to Residence | 中（有数据分析+ERP数据库经验） |
| Systems Administrator | 262113 | **Tier1** | Straight to Residence | 低-中 |
| Analyst Programmer | 261311 | **Tier1** | Straight to Residence | 低 |
| Developer Programmer | 261312 | **Tier1** | Straight to Residence | 低 |
| ICT Project Manager | 135112 | **Tier1** | Straight to Residence | 低（无PM经验） |
| ICT Security Specialist | 262112 | **Tier1** | Straight to Residence | 低（需安全认证） |
| Multimedia Specialist | 261211 | **Tier1** | Straight to Residence | 低 |
| Data Scientist | - | Tier2 | Work to Residence（2年） | 中（Python数据分析背景） |
| ICT Support Engineer | - | Tier2 | Work to Residence（2年） | 中 |

> Tier1 = Straight to Residence（有offer即可直申居留，无打分）
> Tier2 = Work to Residence（需为认证雇主工作2年）
> 所有绿名单路径都需要：**NZQA IQA学历评估** + 达到市场薪资中位数

---

*报告由SEEK NZ自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {report_path}")

# ===== KOS JSON feed =====
sys_path = str(Path(__file__).parent)
import sys
sys.path.insert(0, sys_path)
from local_agent.kos_bridge import write_kos_feed

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

kos_data = {
    'date': today,
    'email_count': email_count,
    'total_jobs': len(unique_jobs),
    'tier1_jobs': [build_job_record(j) for j in unique_jobs if is_green_list_tier1(j['title'])],
    'all_jobs': [build_job_record(j) for j in unique_jobs],
}

kos_section_dir = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz')
kos_path = write_kos_feed(kos_section_dir, 'seek-nz', kos_data, timestamp=datetime.now())
print(f"KOS feed saved: {kos_path}")

# Print summary
print(f"\n===== SUMMARY =====")
print(f"Emails scanned: {email_count}")
print(f"Total unique jobs: {len(unique_jobs)}")
print(f"Relevant jobs (>=35): {len(relevant_jobs)}")
print(f"Green List Tier1: {tier1_count}")
print(f"Green List Tier2: {tier2_count}")
print(f"High match (60+): {len(high)}")
print(f"Medium match (40-59): {len(medium)}")
print(f"Low match (35-39): {len(low)}")
print(f"\nTop 10 jobs:")
for j in unique_jobs[:10]:
    print(f"  {j['score']:3d} | {j['title'][:50]:50s} | {j['company'][:30]:30s} | {j['location'][:30]}")
