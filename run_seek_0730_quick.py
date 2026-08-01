#!/usr/bin/env python
"""Quick SEEK NZ scan - 2026-07-30. 7 emails from QQ Mail MCP tool results."""
import json, re, os, html as html_mod
from datetime import datetime, timedelta
from pathlib import Path

TOOL_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\36784eec-b585-49cd-9c1d-aefa8fee1097\tool-results")
WORKSPACE = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36")
KOS_DIR = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz")

FILES = [
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370544943-c295fd.txt", "7/29 Admin"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370545457-194004.txt", "7/29 ICT"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370546001-e89dbf.txt", "7/29 NZ General"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370546507-e095df.txt", "7/29 ICT2"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370547000-66243e.txt", "7/28 Admin"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370547502-43eada.txt", "7/28 ICT"),
    (TOOL_DIR / "mcp-connector-proxy-qq-mail_GetMessage-1785370548016-288288.txt", "7/28 NZ General"),
]

def extract_jobs_mjml(body):
    jobs = []
    cards = body.split('<a style="display: block"')
    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        loc_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        salary_matches = re.findall(r'>(\$[^<]+)</div>', card)
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        url_match = re.search(r'href="(https://email\.s\.seek\.co\.nz[^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None
        if not title or not company or len(title) > 200:
            continue

        location = 'Unknown'
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm; break
            elif lm and lm not in [title, company] and location == 'Unknown':
                location = lm

        salary = ''
        if salary_matches:
            salary = salary_matches[0].strip()
        else:
            for lm in loc_matches:
                lm = lm.strip()
                if lm and lm != location and lm not in [title, company] and ',' not in lm:
                    if re.search(r'(competitive|benefits|insurance|super|bonus|salary)', lm, re.I):
                        salary = lm; break

        title = html_mod.unescape(title)
        company = html_mod.unescape(company)
        location = html_mod.unescape(location)
        salary = html_mod.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title, 'company': company, 'location': location,
            'salary': salary, 'posted_date': date_match.group(1) if date_match else '',
            'url': url_match.group(1) if url_match else '',
        })
    return jobs

def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])

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
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50; reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48; reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title):
        score += 45; reasons.append('大学信息管理研究岗')
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35; reasons.append('绿名单Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30; reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    elif any(k in title for k in ['database specialist', 'database reliability', 'database engineer', 'datacom database']):
        score += 32; reasons.append('近绿名单:数据库相关(非DBA)')
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8; reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title or 'bi analyst' in title or 'business intelligence' in title:
        score += 8; reasons.append('非绿名单:Data Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator']):
        score += 2; reasons.append('行政岗:忽略')
    else:
        score += 5; reasons.append('非目标岗位')

    if any(k in (company + ' ' + title) for k in ['university', 'research institute', 'crown research']):
        score += 15; reasons.append('大学/研究机构')
    elif any(k in (company + ' ' + title) for k in ['government', 'ministry', 'council', 'education review']):
        score += 10; reasons.append('政府/公共部门')
    elif any(k in (company + ' ' + title) for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12; reasons.append('ICT/科技公司')

    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure']):
        score += 10; reasons.append('编程/云计算技能')
    if any(k in title for k in ['security', 'cyber', 'network', 'database', 'system admin']):
        score += 10; reasons.append('ICT基础设施技能')
    if 'data' in title and any(k in title for k in ['scientist', 'engineer', 'machine learning']):
        score += 8; reasons.append('高级数据技能')

    non_akl = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
    matched = False
    for k in non_akl:
        if (', ' + k in location or location.endswith(', ' + k) or location == k):
            score += 8; reasons.append('非奥克兰地区加分'); matched = True; break
    if not matched and (location.endswith(', wellington') or location == 'wellington'):
        score += 5; reasons.append('惠灵顿地区')

    if 'part-time' in title or 'part time' in title:
        score -= 10; reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10; reasons.append('初级岗降分')

    return max(0, min(100, score)), reasons

def is_tier1(title):
    tier1 = ['software engineer', 'software developer', 'full stack developer',
             'database administrator', 'dba', 'systems administrator', 'system administrator',
             'analyst programmer', 'programmer analyst', 'developer programmer', 'application developer',
             'multimedia specialist', 'ict project manager', 'it project manager',
             'ict security specialist', 'chief information officer', 'chief digital officer']
    return any(k in title.lower() for k in tier1)

def anzsco(title):
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
    t = j['title'].lower()
    if is_tier1(t):
        return '1)英文简历突出具体技术栈(Python/SQL/Cloud/Security)；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1)突出研究经历和论文；2)准备Research Statement；3)联系相关导师'
    elif 'data scientist' in t or 'machine learning' in t:
        return '1)Python/R + ML项目作品集；2)Kaggle/GitHub展示；3)统计学基础补强'
    return '非目标岗位，不建议投入精力'

def imm_note(j):
    t = j['title'].lower()
    code, name = anzsco(t)
    if is_tier1(t):
        return f'绿名单Tier1 Straight to Residence{" | " + code + " " + name if code else ""} — 有offer即可直申居留'
    elif 'data scientist' in t or 'ict support' in t or 'network administrator' in t:
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    return '非绿名单，移民路径弱，建议忽略'

def build_record(j):
    code, name = anzsco(j['title'])
    return {
        'title': j['title'], 'company': j['company'], 'location': j['location'],
        'salary': j['salary'], 'url': j['url'], 'score': j['score'],
        'reasons': j['reasons'], 'immigration_path': imm_note(j),
        'suggested_skills': suggest_skills(j), 'anzsco_code': code, 'anzsco_name': name,
    }

# ===== MAIN =====
print("=" * 60)
print("SEEK NZ 岗位扫描 - 2026-07-30")
print("=" * 60)

all_jobs = []
email_count = 0
for path, label in FILES:
    with open(str(path), 'r', encoding='utf-8') as f:
        data = json.load(f)
        body = data['data']['data']['body']
    jobs = extract_jobs_mjml(body)
    email_count += 1
    print(f"[{label}] {len(jobs)} jobs extracted")
    for j in jobs: j['source'] = label
    all_jobs.extend(jobs)

print(f"\nEmails: {email_count}, Raw: {len(all_jobs)}")

# Dedup
seen = set()
unique = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique.append(j)
print(f"Deduped: {len(unique)}")

# Score
for j in unique:
    s, r = score_job(j)
    j['score'] = s; j['reasons'] = r

unique.sort(key=lambda x: x['score'], reverse=True)

relevant = [j for j in unique if j['score'] >= 35]
filtered = len(unique) - len(relevant)

t1_jobs = [j for j in unique if is_tier1(j['title'])]
high = [j for j in relevant if j['score'] >= 60]
medium = [j for j in relevant if 45 <= j['score'] < 60]
low = [j for j in relevant if 35 <= j['score'] < 45]

today = datetime.now().strftime('%Y-%m-%d')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# Generate Report
report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送（{email_count}封，7/28-7/29 Admin×2 + ICT×3 + NZ General×2）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {email_count}（7/28 Admin×1 + ICT×1 + NZ General×1 + 7/29 Admin×1 + ICT×2 + NZ General×1） |
| 去重岗位总数 | {len(unique)} |
| 过滤后相关岗位 | {len(relevant)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered}（BSA/Data Analyst/行政等非绿名单岗） |
| 🏆最佳匹配 | {high[0]['title'] + ' (' + high[0]['company'] + ') ' + str(high[0]['score']) + '分' if high else '无60+高匹配'} |
| 绿名单Tier1 | {len(t1_jobs)} |
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
        code, name = anzsco(j['title'])
        report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** |
| **ANZSCO** | {code} {name if code else '非绿名单'} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '近期'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {imm_note(j)} |

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
    code, name = anzsco(j['title'])
    astr = f"{code} {name}" if code else '-'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {astr} | {'；'.join(j['reasons'][:3])} |\n"
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

report += f"""
---
## 🎯 绿名单Tier1岗位详情

| 职位 | 公司 | 地点 | 薪资 | 匹配度 | ANZSCO | 移民路径 |
|------|------|------|------|--------|--------|---------|
"""
if t1_jobs:
    for j in t1_jobs:
        sal = j['salary'] if j['salary'] else '未公布'
        code, name = anzsco(j['title'])
        report += f"| {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {code} {name} | Straight to Residence |\n"
else:
    report += "| **本轮无绿名单Tier1岗位** 🚨 | - | - | - | - | - | - |\n"

report += f"""
---
## 📈 绿名单Tier1趋势（近7轮）

| 日期 | 扫描邮件 | 去重岗位 | 绿名单Tier1 | 趋势 |
|------|----------|----------|------------|------|
| 7/24 | - | - | 0 | - |
| 7/25 | 4 | 66 | 2 | ⬆ (Junior SW Dev + Compliance SysAdmin) |
| 7/26 | 1 | 23 | 2 | ➡ (同上延续) |
| 7/27 | 5 | 74 | 0 | ⬇ 归零 |
| 7/28 | 4 | 58 | 0 | ➡ 继续归零 |
| 7/29 | 4 | 42 | 0 | ➡ 继续归零 |
| **7/30** | **{email_count}** | **{len(unique)}** | **{len(t1_jobs)}** | **{'⬆' if t1_jobs else '🚨 继续归零（连续4轮）'}** |

---
## 🎯 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 绿名单Tier1 ICT岗在NZ市场出现频次极低
- {'本轮' + str(len(t1_jobs)) + '个Tier1岗位，' if t1_jobs else '本轮无Tier1岗位，'}主线继续以德国博士为主

### 新西兰副线（10%精力）
1. {'如出现Tier1岗：可考虑投递作为出境跳板' if t1_jobs else '持续监控绿名单Tier1 ICT岗出现频率'}
2. 关注大学/研究机构研究岗（可衔接德国博士）
3. 所有绿名单路径都需要：**NZQA IQA学历评估**（4-8周，NZ$745）

---
*报告由自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

report_path = WORKSPACE / f'SEEK_NZ_Job_Report_{today}.md'
with open(str(report_path), 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {report_path}")

# KOS Feed
KOS_DIR.mkdir(parents=True, exist_ok=True)

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
    "total_jobs": len(unique),
    "tier1_jobs": [build_record(j) for j in t1_jobs],
    "all_jobs": [build_record(j) for j in unique],
}

kos_feed = {"meta": kos_meta, "data": kos_data}

latest_path = KOS_DIR / "latest.json"
with open(str(latest_path), 'w', encoding='utf-8') as f:
    json.dump(kos_feed, f, ensure_ascii=False, indent=2)
print(f"KOS latest.json saved: {latest_path}")

snapshot_path = KOS_DIR / f"seek-nz_{today}.json"
with open(str(snapshot_path), 'w', encoding='utf-8') as f:
    json.dump(kos_feed, f, ensure_ascii=False, indent=2)
print(f"KOS snapshot saved: {snapshot_path}")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY: {email_count} emails, {len(unique)} jobs, {len(t1_jobs)} Tier1, {len(high)} high, {len(medium)} medium, {len(low)} low")
print(f"Tier1: {[j['title']+' ('+j['company']+')' for j in t1_jobs]}")
print(f"Top 10: {[(j['title'][:40], j['score']) for j in unique[:10]]}")
print(f"{'='*60}")
