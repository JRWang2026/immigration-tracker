"""
SEEK NZ 岗位扫描处理脚本 (2026-07-11)
从 QQ Mail connector 保存的邮件文件中提取岗位、评分、生成报告和 KOS JSON
"""
import json, re, os, sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict

WORKSPACE = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36")
KOS_PUBLIC_DATA = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")

# 邮件文件列表 (以 filepath, subject, date 形式)
EMAIL_FILES = [
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964323-4dfd7c.txt", "Admin & Office Support", "2026-07-11"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964138-8e8b30.txt", "ICT", "2026-07-10"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964012-45701b.txt", "NZ General", "2026-07-10"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964260-3c7fc5.txt", "ICT", "2026-07-10"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964517-ff3eb6.txt", "Admin & Office Support", "2026-07-09"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964452-382019.txt", "ICT", "2026-07-09"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964199-1424e0.txt", "NZ General", "2026-07-09"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964389-4f5a14.txt", "ICT", "2026-07-09"),
    (r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\42cc750d-0945-4f30-adbd-78675f4ab221\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1783732964075-bebdd1.txt", "Admin & Office Support", "2026-07-08"),
]

def load_body(path):
    """加载邮件正文 HTML"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 尝试从 tool result JSON 中提取
    try:
        data = json.loads(content)
        # 数据在 data.data.data.body
        body = data.get('data', {}).get('data', {}).get('body', '')
        if not body:
            # 备用路径
            body = data.get('body', '')
        if not body:
            body = data.get('text', '')
    except json.JSONDecodeError:
        # 直接就是 HTML 文本
        body = content
    return body

def extract_jobs(body):
    """从 SEEK 邮件 HTML 提取岗位信息 (MJML 新模板 2026-07)"""
    jobs = []
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        # Title: MJML template with IE conditional comments
        title_match = re.search(r'text-decoration:underline[^>]*>.*?<\!\[endif\]-->\s*([^<]+)\s*<', card, re.DOTALL)
        if not title_match:
            # Fallback: old format
            title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)

        # Company
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)

        # Info blocks for location / salary
        info_blocks = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        # Also try with different color
        info_blocks2 = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#\w+[^>]*>([^<]+)</div>', card)
        all_blocks = info_blocks + [b for b in info_blocks2 if b not in info_blocks]

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        # Skip non-job cards
        if not title or not company or len(title) > 200:
            continue
        if title.lower() in ['nz.seek.com', 'view all matching jobs', 'how to make your saved search',
                              'edit this alert', 'seek.co.nz']:
            continue
        # Skip "you have saved" type text
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

        # Fallback $ pattern
        if not salary:
            sal_match = re.search(r'>\$[^<]+</div>', card)
            if sal_match:
                salary = sal_match.group(0).replace('>', '').replace('</div>', '').strip()

        # Fallback from snippet data
        if not salary:
            snippet_sal = re.findall(r'[\$][\d,]+[–\-\s]+[\$][\d,]+(?:\.\d+)?', card)
            if snippet_sal:
                salary = snippet_sal[0].strip()

        posted_date = ''
        url_match = re.search(r'href="([^"]+)"', card)
        url = url_match.group(1) if url_match else ''

        import html as _html
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
    print(f"📧 处理 {len(EMAIL_FILES)} 封 SEEK 邮件...")
    valid_count = 0
    all_jobs = []
    for path, cat, date in EMAIL_FILES:
        if not os.path.exists(path):
            print(f"  ⚠️ MISSING: {os.path.basename(path)} ({cat}, {date})")
            continue
        body = load_body(path)
        if not body:
            print(f"  ⚠️ EMPTY body: {os.path.basename(path)} ({cat}, {date})")
            continue
        valid_count += 1
        jobs = extract_jobs(body)
        for j in jobs:
            j['source'] = f"{cat} ({date})"
        print(f"  ✅ {cat:25s} ({date}): {len(jobs):3d} jobs | {os.path.basename(path)[-20:]}")
        all_jobs.extend(jobs)

    print(f"\n共处理 {valid_count} 封邮件，原始 {len(all_jobs)} 个岗位")

    # 2. Deduplicate
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        key = (j['title'].lower().strip(), j['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
    print(f"去重后: {len(unique_jobs)} 个岗位")

    # 3. Score
    print("评分中...")
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
    print("生成报告中...")
    best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)

    # Determine date range
    dates = sorted(set(d for _, _, d in EMAIL_FILES))
    date_range = f"{dates[0]} – {dates[-1]}" if dates else "unknown"

    report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送（{valid_count}封邮件，{date_range}）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {valid_count}（覆盖 {date_range}） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 🏆最佳匹配 | {best['title'] if best else '无'} ({best['company'] if best else '-'}) {best['score'] if best else '-'}分 |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |

---

## 🚨 策略提醒

**本脚本已按你的要求调整：机械工程师岗位不再关注，BSA/Data Analyst/行政岗已降级。**

当前只保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence，有offer即可直申居留）
2. **大学/研究机构的研究岗**（可走雇主担保工签，研究方向可衔接德国博士）

> 💡 绝大多数BSA/Data Analyst岗位虽然工作内容匹配你的经验，但**不在绿名单**，移民路径弱，已被过滤到低分/忽略区。

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""

    if high:
        for idx, j in enumerate(high, 1):
            star = '⭐' if idx == 1 else ''
            fire = ' 🔥' if idx == 1 else ''
            src = j.get('source', '')
            report += f"""### {idx}. {star}{j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分**{fire} |
| **ANZSCO** | {green_list_anzsco(j['title'])[0] + ' ' + green_list_anzsco(j['title'])[1] if green_list_anzsco(j['title'])[0] else '无绿名单代码'} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **来源** | {src} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |
| **SEEK链接** | {j['url'] if j['url'] else '无'} |

"""
    else:
        report += "**🚨 本轮无高匹配岗位（≥60分）**\n\n"

    report += """---
    
## 🟡 中匹配岗位 (40-59分) — Tier2 / 研究相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
    if medium:
        for idx, j in enumerate(medium, start=len(high)+1):
            sal = j['salary'] if j['salary'] else '未公布'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"
    else:
        report += "| - | 本轮无中匹配岗位 | - | - | - | - | - |\n"

    report += """
---
    
## 🔵 低匹配岗位 (35-39分) — 可观望
    
| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
    if low:
        for idx, j in enumerate(low, start=len(high)+len(medium)+1):
            sal = j['salary'] if j['salary'] else '未公布'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"
    else:
        report += "| - | 本轮无低匹配岗位 | - | - | - | - | - |\n"

    # Tier1 detail table
    all_tier1 = [j for j in unique_jobs if is_green_list_tier1(j['title'])]
    report += f"""
---

## ⭐ 绿名单Tier1岗位详情（{len(all_tier1)}个）

"""
    if all_tier1:
        report += "| # | 职位 | ANZSCO | 公司 | 地点 | 薪资 | 分数 | 移民路径 |\n"
        report += "|---|------|--------|------|------|------|------|----------|\n"
        for idx, j in enumerate(all_tier1, 1):
            code, name = green_list_anzsco(j['title'])
            sal = j['salary'] if j['salary'] else '未公布'
            report += f"| {idx} | {j['title']} | {code} {name} | {j['company']} | {j['location']} | {sal} | {j['score']} | Straight to Residence |\n"
    else:
        report += "**本轮无绿名单Tier1岗位** 🚨\n"

    report += f"""
---

## 🎯 行动建议

### 主线不变：德国岗位制博士（90%精力）
- SEEK NZ 绿名单Tier1 ICT 岗位稀缺，本轮仅 {tier1_count} 个
- 新西兰作为"备选出境通道"保留，但**不建议主动投递非绿名单岗位**

### 新西兰副线（10%精力）
1. **只关注绿名单Tier1 ICT岗**：Software Engineer / Database Administrator / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security Specialist / CIO
2. **只关注大学/研究机构的研究岗**：University of Canterbury / Crown Research Institutes等的研究类职位
3. **如出现绿名单Tier1 offer**：可作为一个出境跳板，后续再申德国博士

### 简历准备（绿名单ICT方向）
- 英文简历突出：**Python/SQL/Cloud/GitHub作品集**
- 如投Software Engineer：准备LeetCode风格算法题 + 系统设计基础
- 如投Database Administrator：突出SQL优化、数据建模、ERP数据库经验
- 所有绿名单ICT岗都需要：**NZQA IQA学历评估**（4-8周，NZ$745）

---

## 📋 绿名单移民路径提醒

| 职业 | ANZSCO | 绿名单层级 | 移民路径 | 你的匹配度 |
|------|--------|-----------|---------|----------|
| Software Engineer | 261313 | **Tier1** ⭐ | Straight to Residence | 低（非程序员背景） |
| Database Administrator | 262111 | **Tier1** ⭐ | Straight to Residence | 中（有数据分析+ERP数据库经验） |
| Systems Administrator | 262113 | **Tier1** ⭐ | Straight to Residence | 低-中 |
| Analyst Programmer | 261311 | **Tier1** ⭐ | Straight to Residence | 低 |
| Developer Programmer | 261312 | **Tier1** ⭐ | Straight to Residence | 低 |
| ICT Project Manager | 135112 | **Tier1** ⭐ | Straight to Residence | 低（无PM经验） |
| ICT Security Specialist | 262112 | **Tier1** ⭐ | Straight to Residence | 低（需安全认证） |
| Multimedia Specialist | 261211 | **Tier1** ⭐ | Straight to Residence | 低 |
| Data Scientist | - | Tier2 | Work to Residence（2年） | 中（Python数据分析背景） |
| ICT Support Engineer | - | Tier2 | Work to Residence（2年） | 中 |

> ⭐ Tier1 = Straight to Residence（有offer即可直申居留，无打分）
> Tier2 = Work to Residence（需为认证雇主工作2年）
> 所有绿名单路径都需要：**NZQA IQA学历评估** + 达到市场薪资中位数

---
    
*报告由SEEK NZ自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

    report_path = WORKSPACE / f"SEEK_NZ_Job_Report_{today}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存: {report_path}")

    # 6. Write KOS feed
    print("写入 KOS JSON feed...")
    kos_data = {
        'date': today,
        'email_count': valid_count,
        'total_jobs': len(unique_jobs),
        'tier1_jobs': [build_job_record(j) for j in unique_jobs if is_green_list_tier1(j['title'])],
        'all_jobs': [build_job_record(j) for j in unique_jobs],
    }

    kos_path = write_kos_feed(KOS_PUBLIC_DATA, 'seek-nz', kos_data, timestamp=datetime.now())
    print(f"KOS feed 已保存: {kos_path}")

    # 7. Summary
    print("\n" + "=" * 60)
    print(f"✅ SEEK NZ 扫描完成!")
    print(f"   扫描邮件: {valid_count} 封")
    print(f"   去重岗位: {len(unique_jobs)} 个")
    print(f"   绿名单Tier1: {tier1_count} 个")
    print(f"   高/中/低匹配: {len(high)}/{len(medium)}/{len(low)}")
    if high:
        print(f"   🏆 最佳: {high[0]['title']} ({high[0]['score']}分)")
    elif relevant_jobs:
        print(f"   ⚠️ 无高匹配，最高: {relevant_jobs[0]['title']} ({relevant_jobs[0]['score']}分)")
    else:
        print(f"   🚨 无相关岗位（全被过滤）")
    print("=" * 60)

    # Print top 20 for review
    print("\n📋 TOP 20 岗位:")
    for idx, j in enumerate(unique_jobs[:20], 1):
        icon = "⭐" if j['score'] >= 60 else ("🟡" if j['score'] >= 40 else ("🔵" if j['score'] >= 35 else "⚪"))
        print(f"  {idx:2d}. {icon} [{j['score']:3d}] {j['title'][:50]:50s} | {j['company'][:30]:30s} | {j['location']}")
