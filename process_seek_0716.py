#!/usr/bin/env python3
"""SEEK NZ 7/16 scan - process 3 emails from 7/15 (ICT x2 + NZ General x1)"""
import json, re, os, html as html_mod
from datetime import datetime, timedelta
from pathlib import Path

TOOL_RESULTS_DIR = r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\fdb4afac-78e6-4228-bf75-7d94c5c812d0\tool-results'

EMAIL_FILES = [
    # 7/15 ICT 20 jobs (21:47 UTC = 7/16 05:47 GMT+8)
    (os.path.join(TOOL_RESULTS_DIR, 'mcp-connector-proxy-qq-mail_GetMessage-1784159889417-1597c4.txt'), '7/15 ICT-20'),
    # 7/15 NZ General 20 jobs (20:28 UTC)
    (os.path.join(TOOL_RESULTS_DIR, 'mcp-connector-proxy-qq-mail_GetMessage-1784159889196-366061.txt'), '7/15 NZ General-20'),
    # 7/15 ICT 17 jobs (20:25 UTC)
    (os.path.join(TOOL_RESULTS_DIR, 'mcp-connector-proxy-qq-mail_GetMessage-1784159889303-6e62a1.txt'), '7/15 ICT-17'),
]

def load_body_from_txt(path):
    """Load email body from saved QQ Mail JSON tool-result file"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Try to find JSON in the content (tool results may have extra metadata)
    # Find the body field - could be a nested JSON
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            # Navigate to body
            if 'data' in data and 'data' in data['data'] and 'body' in data['data']['data']:
                return data['data']['data']['body']
            elif 'body' in data:
                return data['body']
        except json.JSONDecodeError:
            pass
    # If not JSON, return raw content as HTML
    return content

def extract_jobs_mjml(body):
    """Extract jobs from MJML template SEEK email"""
    jobs = []
    # Split by job card anchors
    cards = body.split('<a style="display: block"')
    
    for card in cards[1:]:
        # Extract URL
        url_match = re.search(r'href="([^"]+)"', card)
        url = url_match.group(1) if url_match else ''
        
        # Title - multiple patterns
        title = None
        # Pattern 1: text-decoration:underline div
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        if title_match:
            title = title_match.group(1).strip()
        # Pattern 2: IE conditional comment wrapped
        if not title:
            title_match2 = re.search(r'<!\[endif\]-->([^<]+)<!\[if mso\]>', card)
            if title_match2:
                title = title_match2.group(1).strip()
        # Pattern 3: font-weight:bold or strong styling
        if not title:
            title_match3 = re.search(r'font-weight:bold[^>]*>([^<]+)</div>', card)
            if title_match3:
                title = title_match3.group(1).strip()
        # Pattern 4: Any div with job-like title content (long enough, not company)
        if not title:
            title_match4 = re.search(r'>([^<]{5,100})</div>', card)
            if title_match4:
                candidate = title_match4.group(1).strip()
                # Skip if it looks like a salary, location, date, or company
                if not re.match(r'^[\$€£]', candidate) and not re.match(r'^\d+ \w+ \d+$', candidate):
                    title = candidate
        
        # Company - in font-size:14px;line-height:21px;padding-bottom:12px td
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        company = company_match.group(1).strip() if company_match else None
        
        if not title or not company or len(title) > 200:
            continue
        
        # Unescape HTML entities
        title = html_mod.unescape(title)
        company = html_mod.unescape(company)
        
        # Location and salary - find all divs with color:#2E3849
        loc_salary_matches = re.findall(
            r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>',
            card
        )
        
        location = 'Unknown'
        salary = ''
        posted_date = ''
        
        # Also check for posted date
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        posted_date = date_match.group(1) if date_match else ''
        
        # Parse location and salary from matches
        for m in loc_salary_matches:
            m = m.strip()
            if not m or m == title or m == company:
                continue
            if re.match(r'^\d+ \w+ \d+$', m):  # Skip date-like strings
                if not posted_date:
                    posted_date = m
                continue
            if ',' in m or location == 'Unknown':
                if location == 'Unknown':
                    location = m
                elif not salary:
                    salary = m
        
        # Also check for salary patterns
        if not salary:
            sal_match = re.search(r'>\$[^<]+</div>', card)
            if sal_match:
                salary = sal_match.group(0).replace('>', '').replace('</div', '').strip()
        
        if not salary:
            sal_match2 = re.search(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]*(?:per annum|per hour|p\.h\.|p/a|salary|KiwiSaver|competitive|benefits|insurance|bonus)[^<]*)</div>', card, re.I)
            if sal_match2:
                salary = sal_match2.group(1).strip()
        
        # Also check for salary in different color divs
        if not salary:
            sal_match3 = re.search(r'>(\$[^<]{3,50})</div>', card)
            if sal_match3:
                salary = sal_match3.group(1).strip()
        
        # Clean up
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

# --- Process all emails ---
all_jobs = []
email_count = 0

for path, label in EMAIL_FILES:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body_from_txt(path)
    jobs = extract_jobs_mjml(body)
    print(f"{label}: {len(jobs)} jobs")
    all_jobs.extend(jobs)
    email_count += 1

# --- Deduplicate ---
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal raw jobs: {len(all_jobs)}")
print(f"Unique jobs after dedup: {len(unique_jobs)}")

# --- Scoring (Green List Tier1 focused) ---
def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []
    
    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])
    is_govt = any(k in company for k in ['government', 'ministry', 'council', 'education review', 'health new zealand', 'te whatu ora', 'dia', 'department'])
    
    # Tier 1 Green List ICT (Straight to Residence)
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55; reasons.append('Green List Tier1: Software Engineer')
    elif 'database administrator' in title or 'dba' in title:
        score += 55; reasons.append('Green List Tier1: Database Administrator')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55; reasons.append('Green List Tier1: Systems Administrator')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55; reasons.append('Green List Tier1: Analyst Programmer')
    elif 'developer programmer' in title or 'application developer' in title:
        score += 55; reasons.append('Green List Tier1: Developer Programmer')
    elif 'multimedia specialist' in title:
        score += 55; reasons.append('Green List Tier1: Multimedia Specialist')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55; reasons.append('Green List Tier1: ICT Project Manager')
    elif 'ict security' in title or 'cyber security' in title or 'information security' in title:
        score += 55; reasons.append('Green List Tier1: ICT Security')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55; reasons.append('Green List Tier1: CIO')
    # University/research roles
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'research scientist', 'research analyst']):
        score += 50; reasons.append('University/research role')
    elif is_research_org and 'data scientist' in title:
        score += 48; reasons.append('University Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title):
        score += 45; reasons.append('University IM role')
    # Tier 2 Green List
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35; reasons.append('Green List Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title:
        score += 30; reasons.append('Green List Tier2: ICT Support/Network Admin')
    elif 'systems support' in title or 'systems support analyst' in title:
        score += 30; reasons.append('Green List Tier2: Systems Support')
    elif 'systems analyst' in title and 'business systems' not in title and 'solutions analyst' not in title:
        score += 30; reasons.append('Green List Tier2: Systems Analyst')
    # Data Engineer - not on Green List but high demand
    elif 'data engineer' in title:
        score += 25; reasons.append('Data Engineer (not Green List, high demand)')
    # Non-Green List roles (filtered)
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8; reasons.append('Non-Green List: BSA/BA (filtered)')
    elif 'data analyst' in title or 'health analyst' in title or 'insights analyst' in title:
        score += 8; reasons.append('Non-Green List: Data/Insights Analyst (filtered)')
    elif 'operations analyst' in title or 'business planning' in title:
        score += 5; reasons.append('Non-Green List: Operations Analyst (filtered)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'coordinator']):
        score += 2; reasons.append('Admin role (ignored)')
    else:
        score += 5; reasons.append('Non-target role')
    
    # Domain bonus
    if is_research_org:
        score += 15; reasons.append('University/research org')
    elif is_govt:
        score += 10; reasons.append('Government/public sector')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12; reasons.append('ICT/tech company')
    
    # Skills bonus
    if any(k in title for k in ['python', 'java', 'javascript', 'sql', 'cloud', 'aws', 'azure']):
        score += 10; reasons.append('Programming/cloud skills')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin', 'systems admin']):
        score += 10; reasons.append('ICT infrastructure skills')
    if 'data' in title and any(k in title for k in ['engineer', 'scientist']):
        score += 8; reasons.append('Advanced data skills')
    if 'automation' in title or 'ai' in title:
        score += 5; reasons.append('Automation/AI skills')
    
    # Location bonus
    non_akl = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'hawkes bay', 'napier', 'palmerston north', 'manawatu', 'taranaki', 'otago']
    if any((', ' + k in location or location.endswith(', ' + k)) for k in non_akl):
        score += 8; reasons.append('Non-Auckland region bonus')
    elif 'wellington' in location:
        score += 5; reasons.append('Wellington region')
    
    # Penalties
    if 'part-time' in title or 'part time' in title:
        score -= 10; reasons.append('Part-time penalty')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10; reasons.append('Junior role penalty')
    
    return max(0, min(100, score)), reasons

for j in unique_jobs:
    s, r = score_job(j)
    j['score'] = s
    j['reasons'] = r

unique_jobs.sort(key=lambda x: x['score'], reverse=True)

# --- ANZSCO classification ---
def is_green_list_tier1(title):
    tier1 = ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer',
             'database administrator', 'dba', 'systems administrator', 'system administrator',
             'analyst programmer', 'programmer analyst', 'developer programmer', 'application developer',
             'multimedia specialist', 'ict project manager', 'it project manager',
             'ict security', 'cyber security', 'information security', 'chief information officer', 'chief digital officer']
    return any(k in title.lower() for k in tier1)

def green_list_anzsco(title):
    t = title.lower()
    if 'software engineer' in t or 'software developer' in t: return '261313', 'Software Engineer'
    elif 'database administrator' in t or 'dba' in t: return '262111', 'Database Administrator'
    elif 'systems administrator' in t or 'system administrator' in t: return '262113', 'Systems Administrator'
    elif 'analyst programmer' in t: return '261311', 'Analyst Programmer'
    elif 'developer programmer' in t or 'application developer' in t: return '261312', 'Developer Programmer'
    elif 'multimedia specialist' in t: return '261211', 'Multimedia Specialist'
    elif 'ict project manager' in t or 'it project manager' in t: return '135112', 'ICT Project Manager'
    elif 'ict security' in t or 'cyber security' in t: return '262112', 'ICT Security Specialist'
    elif 'chief information officer' in t: return '135111', 'Chief Information Officer'
    return '', ''

def suggest_skills(j):
    if is_green_list_tier1(j['title']):
        return '1) English CV highlighting tech stack (Python/SQL/Cloud/Security); 2) GitHub portfolio; 3) NZ local interview prep; 4) NZQA IQA assessment'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1) Highlight research experience and papers; 2) Prepare Research Statement; 3) Contact relevant supervisors'
    elif 'data engineer' in j['title'].lower():
        return '1) Python/SQL/ETL pipeline projects; 2) Cloud data platform (AWS/Azure); 3) GitHub portfolio'
    elif 'data scientist' in j['title'].lower():
        return '1) Python/R + ML projects; 2) Kaggle/GitHub; 3) Statistics foundation'
    else:
        return 'Non-target role, not recommended'

def immigration_note(j):
    title = j['title'].lower()
    code, name = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'Green List Tier1 Straight to Residence | {code} {name} - offer leads to direct PR application'
    elif 'data scientist' in title or 'ict support' in title or 'systems support' in title:
        return 'Green List Tier2 Work to Residence - requires 2 years work with accredited employer'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return 'University/research role - Accredited Employer Work Visa pathway'
    elif 'data engineer' in title:
        return 'Not on Green List - Accredited Employer Work Visa possible, but residency path is weaker'
    else:
        return 'Not on Green List - weak immigration path, recommend skipping'

# --- Generate report ---
today = datetime.now().strftime('%Y-%m-%d')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
report_path = f'SEEK_NZ_Job_Report_{today}.md'

relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)

tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'systems support', 'network administrator']) and not is_green_list_tier1(j['title']))

high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

report = f"""# SEEK NZ Job Scan Report - {today} (Green List Tier1 Focus)

> Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Source: QQ Mail SEEK alerts ({email_count} emails, 7/15 ICT x2 + NZ General x1)
> Strategy: Only **Green List Tier1 ICT roles** + **university/research roles** are tracked. BSA/Data Analyst/admin roles are filtered.

---

## Summary

| Metric | Value |
|--------|-------|
| Emails scanned | {email_count} (7/15 ICT x2 + NZ General x1) |
| Total unique jobs | {len(unique_jobs)} |
| Relevant jobs (score >= 35) | {len(relevant_jobs)} |
| Filtered out | {filtered_out} (BSA/Data Analyst/admin etc.) |
| Best match | {high[0]['title'] if high else (relevant_jobs[0]['title'] if relevant_jobs else 'None')} ({high[0]['company'] if high else (relevant_jobs[0]['company'] if relevant_jobs else '-')}) {high[0]['score'] if high else (relevant_jobs[0]['score'] if relevant_jobs else '-')} pts |
| Green List Tier1 | {tier1_count} |
| Green List Tier2 | {tier2_count} |
| High match (60+) | {len(high)} |
| Medium match (40-59) | {len(medium)} |
| Low match (35-39) | {len(low)} |

---

## Strategy Reminder

**Script configured per user requirements: Mechanical Engineer roles no longer tracked. BSA/Data Analyst/admin roles downgraded.**

Only two categories are retained:
1. **NZ Green List Tier1 ICT roles** (Straight to Residence - offer leads to direct PR)
2. **University/research institution research roles** (Accredited Employer Work Visa pathway, can bridge to German PhD)

---

## High Match (60+ pts) - Green List Tier1 / University Research

"""

for idx, j in enumerate(high, 1):
    star = '***' if idx == 1 else ''
    report += f"""### {idx}. {star} {j['title']} | {j['company']}
| Field | Details |
|-------|---------|
| **Score** | **{j['score']} pts** |
| **Location** | {j['location']} |
| **Salary** | {j['salary'] if j['salary'] else 'Not listed'} |
| **Posted** | {j['posted_date'] if j['posted_date'] else 'Recent'} |
| **Match analysis** | {'; '.join(j['reasons'])} |
| **Skills needed** | {suggest_skills(j)} |
| **Immigration** | {immigration_note(j)} |

"""

report += """---

## Medium Match (40-59 pts) - Tier2 / Research Related

| # | Title | Company | Location | Salary | Score | Key match |
|---|-------|---------|----------|--------|-------|-----------|
"""
for idx, j in enumerate(medium, start=len(high)+1):
    sal = j['salary'] if j['salary'] else 'N/A'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'; '.join(j['reasons'][:3])} |\n"

report += """
---

## Low Match (35-39 pts) - Watch List

| # | Title | Company | Location | Salary | Score | Reason |
|---|-------|---------|----------|--------|-------|--------|
"""
for idx, j in enumerate(low, start=len(high)+len(medium)+1):
    sal = j['salary'] if j['salary'] else 'N/A'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'; '.join(j['reasons'][:2])} |\n"

# All jobs TOP 20 table
report += """
---

## All Scanned Jobs (TOP 20 by score)

| # | Title | Company | Location | Salary | Score |
|---|-------|---------|----------|--------|-------|
"""
for idx, j in enumerate(unique_jobs[:20], 1):
    sal = j['salary'] if j['salary'] else 'N/A'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} |\n"

report += f"""
---

## Action Plan

### Main track: German PhD (90% effort)
- Current SEEK alerts have almost no Green List Tier1 ICT roles
- NZ as backup exit channel, **do not actively apply for non-Green List roles**

### NZ side track (10% effort)
1. **Only watch Green List Tier1 ICT**: Software Engineer / DBA / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security / CIO
2. **Only watch university/research roles**: University of Canterbury / Crown Research Institutes
3. **If Tier1 offer appears**: can be an exit stepping stone, then apply for German PhD later

### CV prep (Green List ICT)
- English CV: highlight **Python/SQL/Cloud/GitHub portfolio**
- Software Engineer: LeetCode + system design basics
- DBA: SQL optimization, data modeling, ERP database experience
- All Green List ICT roles need: **NZQA IQA assessment** (4-8 weeks, NZ$745)

---

## Green List Immigration Path Reference

| Role | ANZSCO | Tier | Path | Your match |
|------|--------|------|------|-----------|
| Software Engineer | 261313 | **Tier1** | Straight to Residence | Low (non-programmer bg) |
| Database Administrator | 262111 | **Tier1** | Straight to Residence | Medium (data analysis + ERP DB) |
| Systems Administrator | 262113 | **Tier1** | Straight to Residence | Low-Medium |
| Analyst Programmer | 261311 | **Tier1** | Straight to Residence | Low |
| Developer Programmer | 261312 | **Tier1** | Straight to Residence | Low |
| ICT Project Manager | 135112 | **Tier1** | Straight to Residence | Low (no PM exp) |
| ICT Security Specialist | 262112 | **Tier1** | Straight to Residence | Low (need security cert) |
| Data Scientist | - | Tier2 | Work to Residence (2yr) | Medium (Python data analysis) |
| ICT Support Engineer | - | Tier2 | Work to Residence (2yr) | Medium |

> Tier1 = Straight to Residence (offer -> direct PR, no points)
> Tier2 = Work to Residence (2 years with accredited employer)
> All Green List paths need: **NZQA IQA assessment** + meet market median salary

---

*Report generated by SEEK NZ automated scan (Green List Tier1 focus) | Next scan: {next_scan}*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {report_path}")

# --- KOS feed ---
import sys
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))
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

kos_dir = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz')
kos_path = write_kos_feed(kos_dir, 'seek-nz', kos_data, timestamp=datetime.now())
print(f"KOS feed saved: {kos_path}")

# Also copy to local workspace
local_kos_dir = Path(workspace_root / 'kos' / 'public' / 'data' / 'seek-nz')
local_kos_dir.mkdir(parents=True, exist_ok=True)
import shutil
shutil.copy2(kos_path, local_kos_dir / 'latest.json')
print(f"KOS feed copied to local: {local_kos_dir / 'latest.json'}")

# Print summary
print(f"\n=== SCAN SUMMARY ===")
print(f"Emails: {email_count}")
print(f"Total unique jobs: {len(unique_jobs)}")
print(f"Relevant (>=35): {len(relevant_jobs)}")
print(f"Tier1: {tier1_count} | Tier2: {tier2_count}")
print(f"High: {len(high)} | Medium: {len(medium)} | Low: {len(low)}")
if relevant_jobs:
    print(f"Top match: {relevant_jobs[0]['title']} ({relevant_jobs[0]['company']}) - {relevant_jobs[0]['score']} pts")
