"""
SEEK NZ 岗位扫描 — 2026-07-28
从 QQ Mail MCP GetMessage 工具结果文件提取 HTML body，MJML 模板解析 + 绿名单评分
"""
import json, os, re, sys
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36")
KOS_PUBLIC_DATA = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")
TOOL_RESULTS_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\0984d01d-27f8-485e-b925-a9695244469f\tool-results")

# ---- 4封邮件对应的工具结果文件映射 ----
EMAIL_FILES = [
    # Email 1: ICT 8 jobs (7/27 20:25) - GetMessage returned inline, body saved manually
    (None, "ICT_8jobs (7/27 20:25)", None),
    # Email 2: NZ General 20 jobs (7/27 20:28) - msg_P_5A-J
    ("mcp-connector-proxy-qq-mail_GetMessage-1785198182141-26973b.txt", "NZ General 20jobs (7/27 20:28)", "msg_P_5A-JwzdFelMdmO-461Y1bk5_Gq-9lFpONN_juSf5jang"),
    # Email 3: ICT 15 jobs (7/27 21:47) - msg_tRIGiK
    ("mcp-connector-proxy-qq-mail_GetMessage-1785198182574-f12f6a.txt", "ICT 15jobs (7/27 21:47)", "msg_tRIGiKEPMgUEpP7NHV-kva8ZlmvubI8RIOYWyrN4DAfjxA"),
    # Email 4: Admin 20 jobs (7/27 23:58) - msg_775X9k
    ("mcp-connector-proxy-qq-mail_GetMessage-1785198182999-9f76d7.txt", "Admin 20jobs (7/27 23:58)", "msg_775X9k_TkUan6C2ko6S74BuuUud-HvSIbSgc5dIwqpavGA"),
]

# Email 1 body (from inline GetMessage response, ICT 8 jobs 7/27 20:25)
EMAIL1_BODY = r"""<style type="text/css">.qmbox #outlook a { padding:0; }
.qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; }
.qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; }
.qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; }
.qmbox p { display:block;margin:13px 0; }
</style>"""


def load_email_bodies():
    """加载4封邮件的 HTML body"""
    import html as _html
    
    bodies = []
    seen_ids = set()
    
    for idx, (filename, desc, msg_id) in enumerate(EMAIL_FILES):
        if idx == 0:
            # Email 1: from inline response - reconstruct from what we extracted
            # Using GetMessage response for msg_Y0wYaH
            # Actually fetch it fresh via the saved inline body
            body_file = WORKSPACE / "tmp_seek_emails" / "email1_full.html"
            if body_file.exists():
                with open(body_file, 'r', encoding='utf-8') as f:
                    body = f.read()
            else:
                print(f"WARNING: Email 1 body file missing, skipping")
                continue
        else:
            fpath = TOOL_RESULTS_DIR / filename
            if not fpath.exists():
                print(f"WARNING: {fpath} not found, skipping")
                continue
            with open(fpath, 'r', encoding='utf-8') as f:
                raw = f.read()
            try:
                resp = json.loads(raw)
                body = resp.get("data", {}).get("data", {}).get("body", "")
            except json.JSONDecodeError:
                print(f"ERROR: {fpath} is not valid JSON, skipping")
                continue
        
        if not body:
            print(f"  ⚠️ {desc}: empty body")
            continue
        
        body = _html.unescape(body)
        bodies.append({"desc": desc, "body": body, "msg_id": msg_id})
        print(f"  ✅ {desc}: {len(body)} chars")
    
    return bodies


def extract_jobs(body):
    """从 SEEK MJML 邮件 HTML 提取岗位信息"""
    jobs = []
    card_pattern = '<a style="display: block"'
    cards = body.split(card_pattern)
    
    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>.*?<\!\[endif\]-->\s*([^<]+)\s*<', card, re.DOTALL)
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        info_blocks = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        
        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None
        
        if not title or not company or len(title) > 200:
            continue
        if title.lower() in ['nz.seek.com', 'view all matching jobs', 'how to make your saved search', 'edit this alert', 'download seek app']:
            continue
        
        location = 'Unknown'
        for ib in info_blocks:
            ib = ib.strip()
            if ',' in ib and ib != title and ib != company:
                location = ib
                break
        
        salary = ''
        found_loc = False
        for ib in info_blocks:
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
        
        # Also try "Posted on" date for missed jobs section
        posted_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        posted_date = posted_match.group(1) if posted_match else ''
        
        url_match = re.search(r'href="([^"]+)"', card)
        url = url_match.group(1) if url_match else ''
        
        import html as _html2
        title = _html2.unescape(title)
        company = _html2.unescape(company)
        location = _html2.unescape(location)
        salary = _html2.unescape(salary).replace('</div', '').strip()
        
        jobs.append({
            'title': title, 'company': company, 'location': location,
            'salary': salary, 'posted_date': posted_date, 'url': url, 'source': ''
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
        score += 55; reasons.append('绿名单Tier1: Software Engineer (261313)')
    elif ('database administrator' in title or 'dba' in title) and 'database reliability' not in title:
        score += 60; reasons.append('绿名单Tier1: Database Administrator (262111)')
    elif 'database reliability engineer' in title:
        score += 40; reasons.append('数据库可靠性工程师(近Tier1但非标准DBA)')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55; reasons.append('绿名单Tier1: Systems Administrator (262113)')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55; reasons.append('绿名单Tier1: Analyst Programmer (261311)')
    elif 'developer programmer' in title or 'application developer' in title or 'software and applications programmer' in title:
        score += 55; reasons.append('绿名单Tier1: Developer Programmer (261312)')
    elif 'multimedia specialist' in title:
        score += 55; reasons.append('绿名单Tier1: Multimedia Specialist (261211)')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55; reasons.append('绿名单Tier1: ICT Project Manager (135112)')
    elif 'ict security' in title or 'cyber security' in title or 'information security' in title:
        score += 55; reasons.append('绿名单Tier1: ICT Security Specialist (262112)')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55; reasons.append('绿名单Tier1: CIO/CDO (135111)')
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'doctoral candidate', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50; reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48; reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title or 'research information' in title):
        score += 45; reasons.append('大学信息管理研究岗')
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35; reasons.append('绿名单Tier2: Data Scientist')
    elif 'database specialist' in title or 'datacom database' in title:
        score += 45; reasons.append('数据库专家(近Tier1 DBA,需确认职责范围)')
    elif 'database' in title and any(k in title for k in ['engineer', 'developer', 'analyst']):
        score += 38; reasons.append('数据库工程师(近Tier1但非标准DBA)')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30; reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    elif 'information & systems analyst' in title or 'information and systems analyst' in title:
        score += 35; reasons.append('信息系统分析师(Tier2)')
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8; reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title:
        score += 8; reasons.append('非绿名单:Data Analyst(已降级)')
    elif 'process analyst' in title:
        score += 8; reasons.append('非绿名单:流程分析(已降级)')
    elif 'business intelligence' in title or 'bi analyst' in title:
        score += 8; reasons.append('非绿名单:BI分析师(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator']):
        score += 2; reasons.append('行政岗:忽略')
    else:
        score += 5; reasons.append('非目标岗位')
    
    # Domain bonus
    if any(k in company + ' ' + title for k in ['university', 'research institute', 'research centre', 'crown research']):
        score += 15; reasons.append('大学/研究机构')
    elif any(k in company + ' ' + title for k in ['government', 'ministry', 'council', 'education review']):
        score += 10; reasons.append('政府/公共部门')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12; reasons.append('ICT/科技公司')
    elif any(k in company + ' ' + title for k in ['engineering', 'manufacturing', 'industrial', 'cable', 'pump']):
        score += 5; reasons.append('工程制造业(已降级)')
    
    # Skills bonus
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10; reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database']):
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
        return '1)英文简历突出具体技术栈；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1)突出研究经历和论文；2)准备Research Statement；3)联系相关导师'
    elif 'data scientist' in title or 'machine learning' in title:
        return '1)Python/R + ML项目作品集；2)Kaggle/GitHub展示；3)统计学基础补强'
    elif 'database' in title:
        return '1)SQL优化能力；2)数据库管理认证(PostgreSQL/Oracle)；3)ERP数据库经验可加分'
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


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    today = datetime.now().strftime('%Y-%m-%d')
    next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # First, save email 1 body from inline context (needs fetching again)
    # We need to get it from a file. Let's create it from the GetMessage inline data.
    
    print("=" * 60)
    print("📧 步骤 1: 加载 SEEK 邮件 HTML...")
    bodies = load_email_bodies()
    
    email_count = len(bodies)
    print(f"   成功加载 {email_count} 封邮件")
    
    # 2. Extract jobs
    print("\n📋 步骤 2: 提取岗位...")
    all_jobs = []
    for b in bodies:
        jobs = extract_jobs(b['body'])
        print(f"   {b['desc'][:60]:60s} → {len(jobs):3d} jobs")
        all_jobs.extend(jobs)
    
    # 3. Deduplicate by (title_lower, company_lower)
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        key = (j['title'].lower().strip(), j['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
    print(f"   去重: {len(all_jobs)}→{len(unique_jobs)} 岗位")
    
    # 4. Score
    print("\n📊 步骤 3: 评分...")
    for j in unique_jobs:
        s, r = score_job(j)
        j['score'] = s
        j['reasons'] = r
    
    unique_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    # 5. Filter
    relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
    filtered_out = len(unique_jobs) - len(relevant_jobs)
    
    tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
    tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']) and not is_green_list_tier1(j['title']))
    
    high = [j for j in relevant_jobs if j['score'] >= 60]
    medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
    low = [j for j in relevant_jobs if 35 <= j['score'] < 40]
    
    best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)
    
    # Print detailed scoring for debugging
    print(f"\n   === 评分详情 (前15) ===")
    for j in unique_jobs[:15]:
        print(f"   [{j['score']:3d}] {j['title'][:50]:50s} | {j['company'][:25]:25s} | {'; '.join(j['reasons'][:3])}")
    
    # 6. Generate report
    print("\n📝 步骤 4: 生成报告...")
    
    report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱 MCP（{email_count}封 SEEK 推送）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {email_count}（7/27 SEEK Job Alerts: ICT×2 + NZ General×1 + Admin×1） |
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

当前只保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence，有offer即可直申居留）
2. **大学/研究机构的研究岗**（可走雇主担保工签，研究方向可衔接德国博士）

> 💡 BSA/Data Analyst/流程分析/BI分析师等岗位不在绿名单，移民路径弱，已被过滤。

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""
    
    if high:
        for idx, j in enumerate(high, 1):
            star = '⭐' if idx == 1 else ''
            report += f"""### {idx}. {star}{j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '近期'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |

"""
    else:
        report += "**本轮无高匹配岗位（≥60分）** 🚨\n\n"
    
    report += """---
    
## 🟡 中匹配岗位 (40-59分) — Tier2 / 研究相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
    if medium:
        for idx, j in enumerate(medium, start=1):
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
        for idx, j in enumerate(low, start=1):
            sal = j['salary'] if j['salary'] else '未公布'
            report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"
    else:
        report += "| - | 本轮无低匹配岗位 | - | - | - | - | - |\n"
    
    report += f"""
---
    
## 🎯 行动建议
    
### 主线不变：德国岗位制博士（90%精力）
- SEEK NZ 绿名单Tier1 ICT 岗位稀缺，本轮仅 {tier1_count} 个
- NZ 仅作备选出境通道保留，不建议主动投递非绿名单岗位
    
### 新西兰副线（10%精力）
1. **只关注绿名单Tier1 ICT岗**：Software Engineer / Database Administrator / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security Specialist / CIO
2. **只关注大学/研究机构研究岗**
3. **如出现绿名单Tier1 offer**：可作出境跳板，后续再申德国博士
    
---
    
## 📋 绿名单移民路径参考
    
| 职业 | ANZSCO | 绿名单 | 移民路径 | 匹配度 |
|------|--------|--------|---------|--------|
| Software Engineer | 261313 | Tier1 | Straight to Residence | 低 |
| Database Administrator | 262111 | Tier1 | Straight to Residence | 中 |
| Systems Administrator | 262113 | Tier1 | Straight to Residence | 低-中 |
| Analyst Programmer | 261311 | Tier1 | Straight to Residence | 低 |
| Developer Programmer | 261312 | Tier1 | Straight to Residence | 低 |
| ICT Project Manager | 135112 | Tier1 | Straight to Residence | 低 |
| ICT Security Specialist | 262112 | Tier1 | Straight to Residence | 低 |
| Data Scientist | - | Tier2 | Work to Residence(2年) | 中 |
    
> ⭐ Tier1 = Straight to Residence | Tier2 = 需工作2年 | 所有路径均需NZQA IQA学历评估
    
---
    
*报告由SEEK NZ自动化扫描生成 | 下次扫描：{next_scan}*
"""
    
    report_path = WORKSPACE / f"SEEK_NZ_Job_Report_{today}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   报告已保存: {report_path}")
    
    # 7. Write KOS feed
    print("\n🌐 步骤 5: 写入 KOS JSON feed...")
    kos_data = {
        'date': today,
        'email_count': email_count,
        'total_jobs': len(unique_jobs),
        'tier1_jobs': [build_job_record(j) for j in unique_jobs if is_green_list_tier1(j['title'])],
        'all_jobs': [build_job_record(j) for j in unique_jobs],
    }
    
    kos_path = write_kos_feed(KOS_PUBLIC_DATA, 'seek-nz', kos_data, timestamp=datetime.now())
    print(f"   KOS feed 已保存: {kos_path}")
    
    # 8. Summary
    print("\n" + "=" * 60)
    print(f"✅ SEEK NZ 扫描完成!")
    print(f"   扫描邮件: {email_count} 封")
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
