"""
SEEK NZ 扫描脚本 - 2026-07-31 早 8:00 自动化触发
扫描2026-07-30的4封未读SEEK推送邮件（Admin×1 + ICT×2 + NZ General×1）
"""
import json, re, os
from collections import OrderedDict
from datetime import datetime, timedelta

# File paths - 2026-07-31 扫描 7/30 4封未读邮件
files = [
    # 7/30 23:58:15 Admin (20 jobs)
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\7ddff467-4541-459a-b55a-70cf22893928\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1785456500584-b25cee.txt', 'json'),
    # 7/30 21:47:15 ICT (20 jobs)
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\7ddff467-4541-459a-b55a-70cf22893928\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1785456501114-8dd7ba.txt', 'json'),
    # 7/30 20:28:29 NZ General (20 jobs)
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\7ddff467-4541-459a-b55a-70cf22893928\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1785456501650-36592a.txt', 'json'),
    # 7/30 20:25:32 ICT (18 jobs)
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\7ddff467-4541-459a-b55a-70cf22893928\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1785456502184-c4c2c5.txt', 'json'),
]

def load_body(path, ftype):
    with open(path, 'r', encoding='utf-8') as f:
        if ftype == 'json':
            data = json.load(f)
            return data['data']['data']['body']
        else:
            return f.read()

def clean_text(html):
    txt = re.sub(r'<[^>]+>', ' ', html)
    txt = re.sub(r'\s+', ' ', txt)
    return txt.strip()

def extract_jobs(body):
    import html
    jobs = []
    # SEEK MJML 模板 2026-07-30+: job card anchor = <a style="display: block" href="...">
    card_pattern = r'<a\s+style="display:\s*block"\s+href="([^"]+)"'
    cards = re.split(card_pattern, body)

    # cards[0] is header, then alternating (url, content), starting from index 1
    for i in range(1, len(cards), 2):
        url = cards[i]
        card = cards[i+1] if i+1 < len(cards) else ''

        # Title: <div ...text-decoration:underline">TITLE</div>
        title_match = re.search(r'text-decoration:\s*underline[^>]*>([^<]+)</div>', card)
        title = title_match.group(1).strip() if title_match else None

        # Company: <td style="font-size:14px;line-height:21px;padding-bottom:12px">COMPANY</td>
        company_match = re.search(r'font-size:\s*14px;\s*line-height:\s*21px;\s*padding-bottom:\s*12px[^>]*>([^<]+)</td>', card)
        company = company_match.group(1).strip() if company_match else ''

        # Location: <div ...color:#2E3849;">LOCATION</div> (after company)
        loc_match = re.search(r'color:\s*#2E3849[^>]*>([^<]+)</div>', card)
        location = loc_match.group(1).strip() if loc_match else 'Unknown'

        # Salary: <div ...>$XX,XXX - $XX,XXX per year</div> or "Competitive..."
        salary_match = re.search(r'>\s*(\$[\d,]+(?:\s*[\-–]\s*\$[\d,]+)?(?:\s*(?:per\s+(?:year|hour|annum|day)|p\.\s*a\.|\+\s*Kiwisaver)?)?|Competitive[^<]{0,80}|Attractive[^<]{0,80})\s*</div>', card)
        salary = salary_match.group(1).strip() if salary_match else ''

        # Posted date
        date_match = re.search(r'Posted on\s+(\d+\s+\w+\s+\d+)', card)
        posted_date = date_match.group(1).strip() if date_match else ''

        # Skip invalid
        if not title or not company or len(title) > 200 or title == company:
            continue
        # Skip obvious non-jobs (footer/header)
        if any(skip in title.lower() for skip in ['missed job', 'view all', 'update preferences', 'unsubscribe', 'view job']):
            continue

        # Clean HTML entities
        title = html.unescape(title)
        company = html.unescape(company)
        location = html.unescape(location)
        salary = html.unescape(salary).strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
            'url': url,
            'source': 'SEEK NZ',
        })
    return jobs

# Load and extract
all_jobs = []
for path, ftype in files:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body(path, ftype)
    jobs = extract_jobs(body)
    print(f"{os.path.basename(path)}: {len(jobs)} jobs")
    all_jobs.extend(jobs)

# Deduplicate by title+company
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal unique jobs: {len(unique_jobs)}")

# Score jobs
def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    salary = j['salary'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])

    # Tier 1 Green List ICT
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55
        reasons.append('绿名单Tier1: Software Engineer')
    elif 'database administrator' in title or 'dba' in title:
        score += 55
        reasons.append('绿名单Tier1: Database Administrator')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55
        reasons.append('绿名单Tier1: Systems Administrator')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55
        reasons.append('绿名单Tier1: Analyst Programmer')
    elif 'developer programmer' in title or 'application developer' in title or 'software and applications programmer' in title:
        score += 55
        reasons.append('绿名单Tier1: Developer Programmer')
    elif 'multimedia specialist' in title:
        score += 55
        reasons.append('绿名单Tier1: Multimedia Specialist')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55
        reasons.append('绿名单Tier1: ICT Project Manager')
    elif 'ict security' in title or 'cyber security' in title or 'information security' in title:
        score += 55
        reasons.append('绿名单Tier1/Tier2: ICT Security')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55
        reasons.append('绿名单Tier1: CIO/CDO')
    # University/research roles
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'doctoral candidate', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50
        reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48
        reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title or 'research information' in title):
        score += 45
        reasons.append('大学信息管理研究岗')
    # Tier 2
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35
        reasons.append('绿名单Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30
        reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    # Penalties
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8
        reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title:
        score += 8
        reasons.append('非绿名单:Data Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator']):
        score += 2
        reasons.append('行政岗:忽略')
    else:
        score += 5
        reasons.append('非目标岗位')

    # Domain bonus
    if any(k in company + ' ' + title for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation']):
        score += 15
        reasons.append('大学/研究机构')
    elif any(k in company + ' ' + title for k in ['government', 'ministry', 'council', 'education review']):
        score += 10
        reasons.append('政府/公共部门')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12
        reasons.append('ICT/科技公司')
    elif any(k in company + ' ' + title for k in ['engineering', 'manufacturing', 'industrial', 'cable', 'pump']):
        score += 5
        reasons.append('工程制造背景(已降级)')

    # Skills/keyword bonus
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10
        reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin']):
        score += 10
        reasons.append('ICT基础设施技能')
    if 'data' in title and any(k in title for k in ['scientist', 'engineer', 'machine learning', 'ml']):
        score += 8
        reasons.append('高级数据技能')
    if 'sharepoint' in title or 'information management' in title:
        score += 5
        reasons.append('Sharepoint/IM(非绿名单降权)')

    # Location bonus
    non_akl_regions = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago', 'tauranga', 'palmerston', 'invercargill']
    if any((', ' + k in location or location.endswith(', ' + k) or location == k) for k in non_akl_regions):
        score += 8
        reasons.append('非奥克兰地区加分')
    elif location.endswith(', wellington') or location == 'wellington':
        score += 5
        reasons.append('惠灵顿地区')

    # Penalties
    if 'part-time' in title or 'part time' in title:
        score -= 10
        reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry', 'no experience']):
        score -= 10
        reasons.append('初级岗降分')
    if 'executive assistant' in title:
        score -= 8
        reasons.append('高管助理专业性强')

    return max(0, min(100, score)), reasons

for j in unique_jobs:
    s, r = score_job(j)
    j['score'] = s
    j['reasons'] = r

unique_jobs.sort(key=lambda x: x['score'], reverse=True)

def is_green_list_tier1(title):
    tier1 = [
        'software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer',
        'database administrator', 'dba',
        'systems administrator', 'system administrator',
        'analyst programmer', 'programmer analyst',
        'developer programmer', 'application developer', 'software and applications programmer',
        'multimedia specialist',
        'ict project manager', 'it project manager',
        'ict security specialist', 'chief information officer', 'chief digital officer'
    ]
    title = title.lower()
    return any(k in title for k in tier1)

def green_list_anzsco(title):
    title = title.lower()
    if 'software engineer' in title or 'software developer' in title:
        return '261313 (Software Engineer)'
    elif 'database administrator' in title or 'dba' in title:
        return '262111 (Database Administrator)'
    elif 'systems administrator' in title or 'system administrator' in title:
        return '262113 (Systems Administrator)'
    elif 'analyst programmer' in title:
        return '261311 (Analyst Programmer)'
    elif 'developer programmer' in title or 'application developer' in title:
        return '261312 (Developer Programmer)'
    elif 'multimedia specialist' in title:
        return '261211 (Multimedia Specialist)'
    elif 'ict project manager' in title or 'it project manager' in title:
        return '135112 (ICT Project Manager)'
    elif 'ict security' in title or 'cyber security' in title:
        return '262112 (ICT Security Specialist)'
    elif 'chief information officer' in title:
        return '135111 (Chief Information Officer)'
    return ''

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
    location = j['location'].lower()
    anzsco = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence{anzsco and " | " + anzsco} — 有offer即可直申居留'
    elif 'data scientist' in title or 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    else:
        return '非绿名单，移民路径弱，建议忽略'

# Generate report
today = datetime.now().strftime('%Y-%m-%d')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
report_path = f'SEEK_NZ_Job_Report_{today}.md'

relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)

tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']))

high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送（4封未读邮件，2026-07-30 Admin×1 + ICT×2 + NZ General×1）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | 4（2026-07-30 Admin×1 + ICT×2 + NZ General×1） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 🏆最佳匹配 | {high[0]['title'] if high else (relevant_jobs[0]['title'] if relevant_jobs else '无')} ({high[0]['company'] if high else (relevant_jobs[0]['company'] if relevant_jobs else '-')}) {high[0]['score'] if high else (relevant_jobs[0]['score'] if relevant_jobs else '-')}分 |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |

---

## 🚨 策略提醒

**本脚本严格按你的要求执行：机械工程师岗位不再关注，BSA/Data Analyst/行政岗已降级。**

当前只保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence，有offer即可直申居留）
2. **大学/研究机构的研究岗**（可走雇主担保工签，研究方向可衔接德国博士）

> 💡 绝大多数BSA/Data Analyst岗位虽然工作内容匹配你的经验，但**不在绿名单**，移民路径弱，已被过滤。

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""

for idx, j in enumerate(high, 1):
    report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** {'🔥' if idx == 1 else ''} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |

"""

report += """---

## 🟡 中匹配岗位 (40-59分) — Tier2 / 研究相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
for idx, j in enumerate(medium, start=len(high)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"

report += """
---

## 🔵 低匹配岗位 (35-39分) — 可观望

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
for idx, j in enumerate(low, start=len(high)+len(medium)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"

# TOP 20 raw jobs (always show for transparency)
report += f"""
---

## 📋 本轮全部去重岗位 TOP 20（按匹配度排序）

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 |
|---|------|------|------|------|--------|
"""
for idx, j in enumerate(unique_jobs[:20], 1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} |\n"

report += f"""
---

## 🎯 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 当前SEEK推送中绿名单Tier1 ICT岗极少
- 新西兰作为"备选出境通道"保留，但**不建议主动投递非绿名单岗位**

### 新西兰副线（10%精力）
1. **只关注绿名单Tier1 ICT岗**：Software Engineer / Database Administrator / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security Specialist / CIO
2. **只关注大学/研究机构的研究岗**
3. **如出现绿名单Tier1 offer**：可作为出境跳板，后续再申德国博士

---

## 📋 绿名单移民路径提醒

| 职业 | ANZSCO | 绿名单层级 | 移民路径 |
|------|--------|-----------|---------|
| Software Engineer | 261313 | **Tier1** ⭐ | Straight to Residence |
| Database Administrator | 262111 | **Tier1** ⭐ | Straight to Residence |
| Systems Administrator | 262113 | **Tier1** ⭐ | Straight to Residence |
| Analyst Programmer | 261311 | **Tier1** ⭐ | Straight to Residence |
| Developer Programmer | 261312 | **Tier1** ⭐ | Straight to Residence |
| ICT Project Manager | 135112 | **Tier1** ⭐ | Straight to Residence |
| ICT Security Specialist | 262112 | **Tier1** ⭐ | Straight to Residence |
| Data Scientist | - | Tier2 | Work to Residence（2年） |

> ⭐ Tier1 = Straight to Residence（有offer即可直申居留，无打分）
> Tier2 = Work to Residence（需为认证雇主工作2年）
> 所有绿名单路径都需要：**NZQA IQA学历评估** + 达到市场薪资中位数

---

*报告由SEEK NZ自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\nReport saved: {report_path}")

# --- KOS feed generation ---
from pathlib import Path
import sys

workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))
from local_agent.kos_bridge import write_kos_feed


def parse_anzsco(title):
    anzsco_str = green_list_anzsco(title)
    if not anzsco_str:
        return '', ''
    code, name = anzsco_str.split(' ', 1)
    name = name.strip('()').strip()
    return code, name


def build_job_record(j):
    code, name = parse_anzsco(j['title'])
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


email_count = sum(1 for path, _ in files if os.path.exists(path))

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

# Top 20 summary
print(f"\n--- Top 20 jobs by score ---")
for idx, j in enumerate(unique_jobs[:20], 1):
    print(f"{idx:2d}. [{j['score']:3d}] {j['title']} | {j['company']} | {j['location']} | {j['salary']}")
