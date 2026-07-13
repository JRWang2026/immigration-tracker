"""
SEEK NZ Job Scanner - 2026-07-12
Processes saved email files from QQ Mail connector, extracts jobs, scores & generates report + KOS JSON.
"""
import json
import re
import os
import html as _html
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\afc79256-0e57-4eb2-b583-18a3488c6fe1\tool-results")
WORKSPACE = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36")
KOS_PUBLIC_DATA = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")

# Email files to process
EMAIL_FILES = [
    (BASE_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1783823848687-64dab7.txt", "ICT", "2026-07-11"),
    (BASE_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1783823848559-6dbcfb.txt", "ICT", "2026-07-11"),
    (BASE_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1783823848620-3109e8.txt", "NZ General", "2026-07-11"),
    (BASE_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1783823848485-70830d.txt", "Admin & Office Support", "2026-07-12"),
]


def load_body(path):
    """Load email body HTML from saved tool result JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    data = json.loads(content)
    body = data.get('data', {}).get('data', {}).get('body', '')
    if not body:
        body = data.get('body', '')
    if not body:
        body = data.get('text', '')
    return body


def extract_jobs(body):
    """Extract job listings from SEEK email HTML (MJML template)."""
    jobs = []
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        # Title: MJML template with IE conditional comments
        title_match = re.search(r'text-decoration:underline[^>]*>.*?<\!\[endif\]-->\s*([^<]+)\s*<', card, re.DOTALL)
        if not title_match:
            title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)

        # Company
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)

        # Info blocks
        info_blocks = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        info_blocks2 = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#\w+[^>]*>([^<]+)</div>', card)
        all_blocks = info_blocks + [b for b in info_blocks2 if b not in info_blocks]

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue
        if title.lower() in ['nz.seek.com', 'view all matching jobs', 'how to make your saved search',
                              'edit this alert', 'seek.co.nz']:
            continue
        if any(skip in title.lower() for skip in ['based on your saved', 'we found', 'hi wang']):
            continue

        # Location
        location = 'Unknown'
        for ib in all_blocks:
            ib = ib.strip()
            if ',' in ib and ib != title and ib != company:
                location = ib
                break

        # Salary
        salary = ''
        found_loc = False
        for ib in all_blocks:
            ib = ib.strip()
            if ib == location:
                found_loc = True
                continue
            if not found_loc:
                continue
            if ib != title and ib != company and ',' not in ib:
                if not re.match(r'^\d+ \w+ \d+$', ib):
                    salary = ib
                    break

        if not salary:
            sal_match = re.search(r'>\$[^<]+</div>', card)
            if sal_match:
                salary = sal_match.group(0).replace('>', '').replace('</div>', '').strip()

        if not salary:
            snippet_sal = re.findall(r'[\$][\d,]+[–\-\s]+[\$][\d,]+(?:\.\d+)?', card)
            if snippet_sal:
                salary = snippet_sal[0].strip()

        # URL
        url_match = re.search(r'href="([^"]+)"', card)
        url = url_match.group(1) if url_match else ''

        # Decode HTML entities
        title = _html.unescape(title)
        company = _html.unescape(company)
        location = _html.unescape(location)
        salary = _html.unescape(salary).replace('</div', '').strip()

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


def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in [
        'university', 'research institute', 'research centre', 'crown research',
        'gns science', 'callaghan innovation', 'crl', 'agresearch',
        'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'
    ])

    # Tier 1 Green List ICT
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55; reasons.append('绿名单Tier1: Software Engineer')
    elif 'database administrator' in title or 'dba' in title:
        score += 55; reasons.append('绿名单Tier1: Database Administrator')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55; reasons.append('绿名单Tier1: Systems Administrator')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55; reasons.append('绿名单Tier1: Analyst Programmer')
    elif 'developer programmer' in title or 'application developer' in title or 'software and applications programmer' in title:
        score += 55; reasons.append('绿名单Tier1: Developer Programmer')
    elif 'multimedia specialist' in title:
        score += 55; reasons.append('绿名单Tier1: Multimedia Specialist')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55; reasons.append('绿名单Tier1: ICT Project Manager')
    elif 'ict security' in title or 'cyber security' in title or 'information security' in title:
        score += 55; reasons.append('绿名单Tier1/Tier2: ICT Security')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55; reasons.append('绿名单Tier1: CIO/CDO')
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'doctoral candidate', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50; reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48; reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title or 'research information' in title):
        score += 45; reasons.append('大学信息管理研究岗')
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35; reasons.append('绿名单Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30; reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8; reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title:
        score += 8; reasons.append('非绿名单:Data Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator']):
        score += 2; reasons.append('行政岗:忽略')
    else:
        score += 5; reasons.append('非目标岗位')

    # Domain bonus
    if any(k in company + ' ' + title for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation']):
        score += 15; reasons.append('大学/研究机构')
    elif any(k in company + ' ' + title for k in ['government', 'ministry', 'council', 'education review']):
        score += 10; reasons.append('政府/公共部门')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12; reasons.append('ICT/科技公司')
    elif any(k in company + ' ' + title for k in ['engineering', 'manufacturing', 'industrial', 'cable', 'pump']):
        score += 5; reasons.append('工程制造背景(已降级)')

    # Skills bonus
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10; reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin']):
        score += 10; reasons.append('ICT基础设施技能')
    if 'data' in title and any(k in title for k in ['scientist', 'engineer', 'machine learning', 'ml']):
        score += 8; reasons.append('高级数据技能')
    if 'sharepoint' in title or 'information management' in title:
        score += 5; reasons.append('Sharepoint/IM(非绿名单降权)')

    # Location bonus
    non_akl_regions = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
    if any((', ' + k in location or location.endswith(', ' + k) or location == k) for k in non_akl_regions):
        score += 8; reasons.append('非奥克兰地区加分')
    elif location.endswith(', wellington') or location == 'wellington':
        score += 5; reasons.append('惠灵顿地区')

    # Penalties
    if 'part-time' in title or 'part time' in title:
        score -= 10; reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10; reasons.append('初级岗降分')
    if 'executive assistant' in title:
        score -= 8; reasons.append('高管助理专业性强')

    return max(0, min(100, score)), reasons


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
    code, name = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence{" | " + code + " " + name if code else ""} — 有offer即可直申居留'
    elif 'data scientist' in title or 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
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


def write_kos_feed(kos_dir, section_id, data, timestamp=None):
    ts = timestamp or datetime.now()
    kos_dir.mkdir(parents=True, exist_ok=True)

    sections = {
        "seek-nz": {
            "title": "SEEK NZ 绿名单岗位追踪",
            "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
            "icon": "briefcase",
        }
    }

    meta = sections[section_id].copy()
    meta["section_id"] = section_id
    meta["last_updated"] = ts.isoformat()

    feed = {"meta": meta, "data": data}

    output_path = kos_dir / "latest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    date_str = ts.strftime("%Y-%m-%d")
    snapshot_path = kos_dir / f"seek-nz_{date_str}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    return output_path


# ============== MAIN ==============
if __name__ == "__main__":
    today = datetime.now().strftime('%Y-%m-%d')
    next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # 1. Load emails
    print("=" * 60)
    print(f"Processing {len(EMAIL_FILES)} SEEK emails...")
    valid_count = 0
    all_jobs = []
    for path, cat, date in EMAIL_FILES:
        if not os.path.exists(path):
            print(f"  MISSING: {path.name} ({cat}, {date})")
            continue
        body = load_body(path)
        if not body:
            print(f"  EMPTY body: {path.name} ({cat}, {date})")
            continue
        valid_count += 1
        jobs = extract_jobs(body)
        for j in jobs:
            j['source'] = f"{cat} ({date})"
        print(f"  [OK] {cat:25s} ({date}): {len(jobs):3d} jobs")
        all_jobs.extend(jobs)

    print(f"\nTotal: {valid_count} emails, {len(all_jobs)} raw jobs")

    # 2. Deduplicate
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        key = (j['title'].lower().strip(), j['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
    print(f"Deduplicated: {len(unique_jobs)} jobs")

    # 3. Score
    print("Scoring...")
    for j in unique_jobs:
        s, r = score_job(j)
        j['score'] = s
        j['reasons'] = r

    unique_jobs.sort(key=lambda x: x['score'], reverse=True)

    # 4. Filter
    relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
    filtered_out = len(unique_jobs) - len(relevant_jobs)

    tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
    tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']))

    high = [j for j in relevant_jobs if j['score'] >= 60]
    medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
    low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

    # 5. Generate report
    print("Generating report...")
    best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)

    dates = sorted(set(d for _, _, d in EMAIL_FILES if os.path.exists(str(_))))
    date_range = f"{dates[0]} - {dates[-1]}" if dates else "unknown"

    report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Source: QQ邮箱SEEK推送 ({valid_count} emails, {date_range})
> Strategy: Green List Tier 1 ICT + university/research roles only; BSA/Data Analyst/Admin DEGRADED

---

## Scan Summary

| Metric | Value |
|--------|-------|
| Emails scanned | {valid_count} ({date_range}) |
| Unique jobs | {len(unique_jobs)} |
| Relevant (>=35) | {len(relevant_jobs)} |
| Filtered out | {filtered_out} (BSA/Data Analyst/Admin/Non-target) |
| Best match | {best['title'] if best else 'NONE'} ({best['company'] if best else '-'}) {best['score'] if best else '-'}pts |
| Green List Tier1 | {tier1_count} |
| Green List Tier2 | {tier2_count} |
| High match (60+) | {len(high)} |
| Medium match (40-59) | {len(medium)} |
| Low match (35-39) | {len(low)} |

---

## STRATEGY REMINDER

Green List Tier1 ICT ONLY (Straight to Residence):
1. Software Engineer (261313)
2. Database Administrator (262111)
3. Systems Administrator (262113)
4. Analyst Programmer (261311)
5. Developer Programmer (261312)
6. ICT Project Manager (135112)
7. ICT Security Specialist (262112)
8. CIO (135111)
9. Multimedia Specialist (261211)

BSA/Data Analyst/Admin/Mechanical = DEGRADED/FILTERED.

---

## HIGH MATCH (60+ pts) - Green List Tier1 / University Research

"""

    if high:
        for idx, j in enumerate(high, 1):
            star = '⭐' if idx == 1 else ''
            code, name = green_list_anzsco(j['title'])
            src = j.get('source', '')
            report += f"""### {idx}. {star}{j['title']} | {j['company']}
| Field | Detail |
|-------|--------|
| **Score** | **{j['score']}pts** |
| **ANZSCO** | {code + ' ' + name if code else 'N/A'} |
| **Location** | {j['location']} |
| **Salary** | {j['salary'] if j['salary'] else 'Not disclosed'} |
| **Source** | {src} |
| **Match Analysis** | {'; '.join(j['reasons'])} |
| **Skills Gap** | {suggest_skills(j)} |
| **Immigration** | {immigration_note(j)} |
| **SEEK Link** | {j['url'] if j['url'] else 'N/A'} |

"""
    else:
        report += "**NO high-match jobs (>=60pts) this round**\n\n"

    report += """---

## MEDIUM MATCH (40-59pts) - Tier2 / Research-related

| # | Title | Company | Location | Salary | Score | Key Matches |
|---|-------|---------|----------|--------|-------|-------------|
"""
    if medium:
        for idx, j in enumerate(medium, start=len(high)+1):
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'; '.join(j['reasons'][:3])} |\n"
    else:
        report += "| - | No medium match | - | - | - | - | - |\n"

    report += """
---

## LOW MATCH (35-39pts) - Watch

| # | Title | Company | Location | Salary | Score | Reason |
|---|-------|---------|----------|--------|-------|--------|
"""
    if low:
        for idx, j in enumerate(low, start=len(high)+len(medium)+1):
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'; '.join(j['reasons'][:2])} |\n"
    else:
        report += "| - | No low match | - | - | - | - | - |\n"

    # Tier1 detail table
    all_tier1 = [j for j in unique_jobs if is_green_list_tier1(j['title'])]
    report += f"""
---

## GREEN LIST TIER1 DETAIL ({len(all_tier1)} total)

"""
    if all_tier1:
        report += "| # | Title | ANZSCO | Company | Location | Salary | Score | Path |\n"
        report += "|---|-------|--------|---------|----------|--------|-------|------|\n"
        for idx, j in enumerate(all_tier1, 1):
            code, name = green_list_anzsco(j['title'])
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {code} {name} | {j['company']} | {j['location']} | {sal} | {j['score']} | Straight to Residence |\n"
    else:
        report += "**NO Green List Tier1 jobs this round**\n"

    report += f"""
---

## ACTION ITEMS

### Main: Germany PhD (90% effort)
- SEEK NZ Green List Tier1 ICT jobs are scarce (only {tier1_count} this round)
- NZ is backup exit channel only; DO NOT apply to non-Green-List jobs

### NZ Side (10% effort)
1. ONLY Green List Tier1 ICT: Software Engineer / DBA / Systems Administrator / Analyst Programmer / Developer Programmer / ICT PM / ICT Security / CIO
2. ONLY university/research roles with visa sponsorship potential
3. If Green List Tier1 offer appears: use as exit jump, then apply for Germany PhD later

### Resume Prep (Green List ICT)
- Highlight: Python/SQL/Cloud/GitHub portfolio
- Software Engineer path: LeetCode + system design basics
- DBA path: SQL optimization, data modeling, ERP DB experience
- ALL Green List paths need: NZQA IQA assessment (4-8 weeks, NZ$745)

---

## GREEN LIST IMMIGRATION SUMMARY

| Occupation | ANZSCO | Tier | Path | Your Fit |
|-----------|--------|------|------|----------|
| Software Engineer | 261313 | **Tier1** | Straight to Residence | Low |
| Database Administrator | 262111 | **Tier1** | Straight to Residence | Medium |
| Systems Administrator | 262113 | **Tier1** | Straight to Residence | Low-Med |
| Analyst Programmer | 261311 | **Tier1** | Straight to Residence | Low |
| Developer Programmer | 261312 | **Tier1** | Straight to Residence | Low |
| ICT Project Manager | 135112 | **Tier1** | Straight to Residence | Low |
| ICT Security Specialist | 262112 | **Tier1** | Straight to Residence | Low |
| Multimedia Specialist | 261211 | **Tier1** | Straight to Residence | Low |
| Data Scientist | - | Tier2 | Work to Residence (2yr) | Medium |

---

*Auto-generated by SEEK NZ scanner (Green List Tier1 focus) | Next scan: {next_scan}*
"""

    report_path = WORKSPACE / f"SEEK_NZ_Job_Report_{today}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved: {report_path}")

    # 6. Write KOS feed
    print("Writing KOS JSON feed...")
    kos_data = {
        'date': today,
        'email_count': valid_count,
        'total_jobs': len(unique_jobs),
        'tier1_jobs': [build_job_record(j) for j in unique_jobs if is_green_list_tier1(j['title'])],
        'all_jobs': [build_job_record(j) for j in unique_jobs],
    }

    kos_path = write_kos_feed(KOS_PUBLIC_DATA, 'seek-nz', kos_data, timestamp=datetime.now())
    print(f"KOS feed saved: {kos_path}")

    # 7. Summary
    print("\n" + "=" * 60)
    print(f"SEEK NZ Scan Complete!")
    print(f"   Emails: {valid_count}")
    print(f"   Unique jobs: {len(unique_jobs)}")
    print(f"   Green List Tier1: {tier1_count}")
    print(f"   High/Med/Low: {len(high)}/{len(medium)}/{len(low)}")
    if high:
        print(f"   BEST: {high[0]['title']} ({high[0]['score']}pts)")
    elif relevant_jobs:
        print(f"   No high match, best: {relevant_jobs[0]['title']} ({relevant_jobs[0]['score']}pts)")
    else:
        print(f"   NO relevant jobs (all filtered)")
    print("=" * 60)

    # Print top 20
    print("\nTOP 20 Jobs:")
    for idx, j in enumerate(unique_jobs[:20], 1):
        icon = "⭐" if j['score'] >= 60 else ("🟡" if j['score'] >= 40 else ("🔵" if j['score'] >= 35 else "⚪"))
        print(f"  {idx:2d}. {icon} [{j['score']:3d}] {j['title'][:50]:50s} | {j['company'][:30]:30s} | {j['location']}")
