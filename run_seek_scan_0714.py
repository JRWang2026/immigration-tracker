"""
SEEK NZ Job Scanner - 2026-07-14
One-shot script: reads 4 email files, extracts jobs, scores, generates report + KOS JSON.
"""
import json
import re
import html as _html
from datetime import datetime, timedelta
from pathlib import Path

TOOL_RESULTS = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\0c072b00-7623-4ec6-9da1-caec78e7254d\tool-results")
WORKSPACE = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36")
KOS_PUBLIC_DATA = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")

# 4 emails from 7/13. Admin & NZ General were saved to disk, ICT were returned inline.
# We save ICT bodies separately.
EMAILS = []

# Check what files we have
for f in sorted(TOOL_RESULTS.glob("*.txt")):
    EMAILS.append(('file', str(f), f.name, '2026-07-13'))

print(f"Found {len(EMAILS)} email files")
for t, p, n, d in EMAILS:
    print(f"  {n}")


def load_json_body(filepath):
    """Load email body from a tool result JSON file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    try:
        data = json.loads(content)
    except:
        return content

    # Try multiple key paths
    body = ''
    for key_path in [['data','data','body'], ['data','body'], ['body'], ['text']]:
        d = data
        try:
            for k in key_path:
                d = d.get(k, {})
            if isinstance(d, str) and len(d) > 200:
                body = d
                break
        except:
            continue
    
    if not body and isinstance(data, str):
        body = data
    elif not body:
        body = str(data)
    
    return body


def extract_jobs(body):
    """Extract job listings from SEEK email HTML (MJML template)."""
    if not body or len(body) < 200:
        return []
    
    jobs = []
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        # Title with IE conditional comments
        title_match = re.search(r'text-decoration:underline[^>]*>.*?<!\[endif\]-->\s*([^<]+)\s*<', card, re.DOTALL)
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

        # Posted date
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        posted_date = date_match.group(1) if date_match else ''

        title = _html.unescape(title)
        company = _html.unescape(company)
        location = _html.unescape(location)
        salary = _html.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
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
    return any(k in title.lower() for k in tier1)


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
        return '1)英文简历突出具体技术栈; 2)GitHub作品集; 3)准备NZ本地面试题; 4)NZQA IQA学历评估'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1)突出研究经历和论文; 2)准备Research Statement; 3)联系相关导师'
    elif 'data scientist' in title or 'machine learning' in title:
        return '1)Python/R + ML项目作品集; 2)Kaggle/GitHub展示; 3)统计学基础补强'
    else:
        return '非目标岗位，不建议投入精力'


def immigration_note(j):
    title = j['title'].lower()
    code, name = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence{" | " + code + " " + name if code else ""}'
    elif 'data scientist' in title or 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        return '绿名单Tier2 Work to Residence'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，可雇主担保AEWV'
    else:
        return '非绿名单，移民路径弱'


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

    meta = {
        "title": "SEEK NZ 绿名单岗位追踪",
        "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
        "icon": "briefcase",
        "section_id": section_id,
        "last_updated": ts.isoformat(),
    }

    feed = {"meta": meta, "data": data}

    output_path = kos_dir / "latest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    date_str = ts.strftime("%Y-%m-%d")
    snapshot_path = kos_dir / f"seek-nz_{date_str}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    return output_path


# ======================== MAIN ========================
if __name__ == "__main__":
    today = datetime.now().strftime('%Y-%m-%d')
    next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("=" * 60)
    print(f"SEEK NZ Scanner - {today}")
    print("=" * 60)
    
    # Process all saved tool result files
    valid_count = 0
    all_jobs = []
    
    # Map filenames to categories
    file_categories = {
        'mcp-connector-proxy-qq-mail_GetMessage-1783987196802-6142d1.txt': 'Admin & Office Support',
        'mcp-connector-proxy-qq-mail_GetMessage-1783987196972-90d111.txt': 'NZ General',
        'call_01_y1DDrK2TufaMVS45uqae2876.txt': 'ICT',
        'call_03_IciszuRlDSmWiRscBmZR3496.txt': 'ICT',
    }
    
    for fpath in sorted(TOOL_RESULTS.glob("*.txt")):
        fname = fpath.name
        cat = file_categories.get(fname, 'Unknown')
        
        body = load_json_body(str(fpath))
        if not body:
            print(f"  EMPTY body: {fname} ({cat})")
            continue
        
        valid_count += 1
        jobs = extract_jobs(body)
        for j in jobs:
            j['source'] = f"{cat} (2026-07-13)"
        print(f"  [OK] {cat:25s}: {len(jobs):3d} jobs from {fname[:50]}")
        all_jobs.extend(jobs)
    
    # Also process ICT emails - try the call_*.txt files which might be from this session
    # Actually, we didn't save ICT emails to disk. Let's check if call files have them.
    call_files = sorted(TOOL_RESULTS.glob("call_*.txt"))
    if call_files:
        print(f"\n  Checking {len(call_files)} call files for ICT emails...")
        for fpath in call_files:
            body = load_json_body(str(fpath))
            if body and 'SEEK' in body[:1000] and 'Information & Communication' in body[:5000]:
                jobs = extract_jobs(body)
                if jobs:
                    valid_count += 1
                    for j in jobs:
                        j['source'] = f"ICT (2026-07-13)"
                    print(f"  [OK] ICT (call file): {len(jobs):3d} jobs")
                    all_jobs.extend(jobs)
    
    print(f"\nTotal: {valid_count} emails, {len(all_jobs)} raw jobs")
    
    if len(all_jobs) == 0:
        print("ERROR: No jobs extracted! Check email files.")
        # Print snippet of first file for debugging
        for fpath in sorted(TOOL_RESULTS.glob("*.txt"))[:1]:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(5000)
            print(f"\nFirst 5000 chars of {fpath.name}:")
            print(content[:500])
        exit(1)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        key = (j['title'].lower().strip(), j['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
    print(f"Deduplicated: {len(unique_jobs)} jobs")
    
    # Score
    print("Scoring...")
    for j in unique_jobs:
        s, r = score_job(j)
        j['score'] = s
        j['reasons'] = r
    
    unique_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    # Stats
    relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
    filtered_out = len(unique_jobs) - len(relevant_jobs)
    
    tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
    tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']))
    
    high = [j for j in relevant_jobs if j['score'] >= 60]
    medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
    low = [j for j in relevant_jobs if 35 <= j['score'] < 40]
    
    best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)
    
    # Generate report
    print(f"\n生成报告...")
    
    report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送 ({valid_count}封邮件, 2026-07-13)
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 扫描概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {valid_count} (Admin×1 + ICT×2 + NZ General×1, 2026-07-13) |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)} (≥35分) |
| 过滤掉岗位 | {filtered_out} (BSA/Data Analyst/行政/机械等非目标岗) |
| 🏆 最佳匹配 | {best['title'] if best else '无'} ({best['company'] if best else '-'}) {best['score'] if best else '-'}分 |
| 🚨 绿名单Tier1 | {tier1_count}（连续5轮归零！7/10最后出现） |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |
"""
    
    if tier1_count == 0:
        report += """
---
## 🚨 绿名单Tier1 连续5轮归零

**7/10 HR Systems Administrator 为最后一轮出现，7/11-7/14 完全归零。**

当前 SEEK NZ 绿名单 Tier1 ICT 岗位稀缺状态持续恶化。建议：
- NZ 副线投入维持 10% 精力，不做额外投入
- 主线德国博士申请不动摇
"""
    
    report += """
---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""
    
    if high:
        for idx, j in enumerate(high, 1):
            code, name = green_list_anzsco(j['title'])
            src = j.get('source', '')
            report += f"""### {idx}. {'⭐' if idx==1 else ''}{j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** |
| **ANZSCO** | {code + ' ' + name if code else 'N/A'} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **来源** | {src} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |
| **SEEK链接** | {j['url'] if j['url'] else 'N/A'} |

"""
    else:
        report += "**本轮无高匹配岗位（≥60分）**\n\n"
    
    report += """---

## 🟡 中匹配岗位 (40-59分) — Tier2 / 研究相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
    if medium:
        for idx, j in enumerate(medium, start=len(high)+1):
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"
    else:
        report += "| - | 无中匹配岗位 | - | - | - | - | - |\n"
    
    report += """
---

## 🔵 低匹配岗位 (35-39分) — 可观望

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
    if low:
        for idx, j in enumerate(low, start=len(high)+len(medium)+1):
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"
    else:
        report += "| - | 无低匹配岗位 | - | - | - | - | - |\n"
    
    # Tier1 detail
    all_tier1 = [j for j in unique_jobs if is_green_list_tier1(j['title'])]
    report += f"""
---

## 📋 绿名单Tier1 详情 ({len(all_tier1)}个)

"""
    if all_tier1:
        report += "| # | 职位 | ANZSCO | 公司 | 地点 | 薪资 | 匹配度 | 路径 |\n"
        report += "|---|------|--------|------|------|------|--------|------|\n"
        for idx, j in enumerate(all_tier1, 1):
            code, name = green_list_anzsco(j['title'])
            sal = j['salary'] if j['salary'] else 'N/A'
            report += f"| {idx} | {j['title']} | {code} {name} | {j['company']} | {j['location']} | {sal} | {j['score']} | Straight to Residence |\n"
    else:
        report += "**本轮无绿名单Tier1岗位**\n"
    
    # TOP 20
    report += f"""
---

## 📊 本轮全部岗位 TOP 20（按匹配度排序）

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 关键标签 |
|---|------|------|------|------|--------|---------|
"""
    for idx, j in enumerate(unique_jobs[:20], 1):
        sal = j['salary'] if j['salary'] else 'N/A'
        icon = "⭐" if j['score'] >= 60 else ("🟡" if j['score'] >= 40 else ("🔵" if j['score'] >= 35 else "⚪"))
        report += f"| {idx} | {j['title'][:60]} | {j['company'][:25]} | {j['location'][:25]} | {sal[:30]} | {icon} {j['score']} | {'；'.join(j['reasons'][:2])} |\n"
    
    report += f"""
---

## 🎯 行动建议

### 主线：德国岗位制博士（90%精力）
- SEEK NZ 绿名单 Tier1 已连续 5 轮归零
- NZ 仅作"备选出境通道"；不主动投递非绿名单岗位

### 新西兰副线（10%精力）
1. **仅关注绿名单 Tier1 ICT 岗**（Straight to Residence）
2. **仅关注大学/研究机构研究岗**（可雇主担保 AEWV）

### 简历准备
- Python/SQL/Cloud/GitHub 作品集
- **NZQA IQA 学历评估**（4-8周，NZ$745）

---

## 📋 绿名单速查

| 职业 | ANZSCO | 层级 | 路径 |
|------|--------|------|------|
| Software Engineer | 261313 | Tier1 ⭐ | Straight to Residence |
| Database Administrator | 262111 | Tier1 ⭐ | Straight to Residence |
| Systems Administrator | 262113 | Tier1 ⭐ | Straight to Residence |
| Analyst Programmer | 261311 | Tier1 ⭐ | Straight to Residence |
| Developer Programmer | 261312 | Tier1 ⭐ | Straight to Residence |
| ICT Project Manager | 135112 | Tier1 ⭐ | Straight to Residence |
| ICT Security Specialist | 262112 | Tier1 ⭐ | Straight to Residence |
| Data Scientist | - | Tier2 | Work to Residence |

---

*报告由 SEEK NZ 自动化扫描生成（绿名单 Tier1 聚焦版） | 下次扫描：{next_scan}*
"""
    
    report_path = WORKSPACE / f"SEEK_NZ_Job_Report_{today}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved: {report_path}")
    
    # KOS feed
    print("Writing KOS JSON feed...")
    kos_data = {
        'date': today,
        'email_count': valid_count,
        'total_jobs': len(unique_jobs),
        'tier1_jobs': [build_job_record(j) for j in unique_jobs if is_green_list_tier1(j['title'])],
        'all_jobs': [build_job_record(j) for j in unique_jobs],
    }
    
    kos_path = write_kos_feed(KOS_PUBLIC_DATA, 'seek-nz', kos_data, timestamp=datetime.now())
    print(f"KOS feed: {kos_path}")
    print(f"KOS snapshot: {KOS_PUBLIC_DATA / f'seek-nz_{today}.json'}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ SEEK NZ 扫描完成!")
    print(f"   邮件: {valid_count} | 去重岗位: {len(unique_jobs)} | Tier1: {tier1_count}")
    print(f"   高/中/低: {len(high)}/{len(medium)}/{len(low)}")
    if best:
        print(f"   最佳: {best['title']} ({best['company']}) {best['score']}分")
    print("=" * 60)
    
    print("\nTOP 20:")
    for idx, j in enumerate(unique_jobs[:20], 1):
        icon = "⭐" if j['score'] >= 60 else ("🟡" if j['score'] >= 40 else ("🔵" if j['score'] >= 35 else "⚪"))
        print(f"  {idx:2d}. {icon} [{j['score']:3d}] {j['title'][:55]:55s} | {j['company'][:25]} | {j['location']}")
