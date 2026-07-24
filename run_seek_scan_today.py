#!/usr/bin/env python3
"""
SEEK NZ 绿名单 Tier1 聚焦扫描 — 单日批次处理
读取 QQ Mail MCP 返回的 JSON 文件，提取岗位，评分，生成报告 + KOS JSON。
"""

import json
import html as html_module
import os
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. 邮件源文件（MCP GetMessage 输出）
# ---------------------------------------------------------------------------
EMAIL_FILES = [
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\2ac3b433-f0aa-476c-b74a-5ffc29d417e1\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784850587255-31f350.txt', 'ICT 20 new jobs (2026-07-23)'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\2ac3b433-f0aa-476c-b74a-5ffc29d417e1\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784850587448-6f3223.txt', 'NZ 20 new jobs (2026-07-23)'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\2ac3b433-f0aa-476c-b74a-5ffc29d417e1\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784850587355-480b9a.txt', 'ICT 15 new jobs (2026-07-23)'),
    (r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\2ac3b433-f0aa-476c-b74a-5ffc29d417e1\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1784850587558-32421a.txt', 'Admin 20 new jobs (2026-07-22)'),
]

# ---------------------------------------------------------------------------
# 2. 加载邮件 body
# ---------------------------------------------------------------------------
def load_body(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['data']['data']['body']

# ---------------------------------------------------------------------------
# 3. 解析岗位（从 HTML 中提取）
# ---------------------------------------------------------------------------
def clean_text(html):
    txt = re.sub(r'<[^>]+>', ' ', html)
    txt = re.sub(r'\s+', ' ', txt)
    return txt.strip()

def extract_jobs(body, source=''):
    jobs = []
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        loc_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        salary_match = re.search(r'>\$[^<]+</div>', card)
        teaser_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        url_match = re.search(r'href="([^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue

        location = 'Unknown'
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm
                break
            elif lm and lm not in [title, company] and not location.replace('Unknown', ''):
                location = lm

        salary = ''
        if salary_match:
            salary = salary_match.group(0).replace('>', '').replace('</div>', '').strip()
        elif teaser_matches:
            for tm in teaser_matches:
                tm = tm.strip()
                if tm and tm != location and tm not in [title, company] and ',' not in tm:
                    if not re.match(r'^\d+ \w+ \d+$', tm):
                        salary = tm
                        break

        if not salary:
            for tm in teaser_matches:
                tm = tm.strip()
                if tm and tm != location and tm not in [title, company]:
                    if re.search(r'(competitive|benefits|insurance|super|bonus)', tm, re.I):
                        salary = tm
                        break

        posted_date = date_match.group(1) if date_match else ''
        url = url_match.group(1) if url_match else ''

        title = html_module.unescape(title)
        company = html_module.unescape(company)
        location = html_module.unescape(location)
        salary = html_module.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
            'url': url,
            'source': source,
        })
    return jobs

# ---------------------------------------------------------------------------
# 4. 评分逻辑（绿名单 Tier1 聚焦版）
# ---------------------------------------------------------------------------
def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    salary = j['salary'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in [
        'university', 'research institute', 'research centre', 'crown research',
        'gns science', 'callaghan innovation', 'crl', 'agresearch',
        'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'
    ])

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
    elif any(k in title for k in ['developer programmer', 'application developer', 'software and applications programmer']):
        score += 55
        reasons.append('绿名单Tier1: Developer Programmer')
    elif 'multimedia specialist' in title:
        score += 55
        reasons.append('绿名单Tier1: Multimedia Specialist')
    elif any(k in title for k in ['ict project manager', 'it project manager']):
        score += 55
        reasons.append('绿名单Tier1: ICT Project Manager')
    elif any(k in title for k in ['ict security', 'cyber security', 'information security']):
        score += 55
        reasons.append('绿名单Tier1/Tier2: ICT Security')
    elif any(k in title for k in ['chief information officer', 'chief digital officer']):
        score += 55
        reasons.append('绿名单Tier1: CIO/CDO')
    # University/research roles
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'doctoral candidate', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50
        reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48
        reasons.append('大学研究型Data Scientist')
    elif is_research_org and any(k in title for k in ['information management', 'knowledge management', 'research information']):
        score += 45
        reasons.append('大学信息管理研究岗')
    # Tier 2
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35
        reasons.append('绿名单Tier2: Data Scientist')
    elif any(k in title for k in ['ict support', 'network administrator']) or ('systems analyst' in title and 'business systems' not in title):
        score += 30
        reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    # Downgraded
    elif any(k in title for k in ['business systems analyst', 'business analyst', 'erp analyst']):
        score += 8
        reasons.append('非绿名单:BSA/ERP(已降级)')
    elif any(k in title for k in ['data analyst', 'service and data analyst', 'reporting analyst']):
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

    # Skills bonus
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
    non_akl = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
    if any((', ' + k in location or location.endswith(', ' + k) or location == k) for k in non_akl):
        score += 8
        reasons.append('非奥克兰地区加分')
    elif location.endswith(', wellington') or location == 'wellington':
        score += 5
        reasons.append('惠灵顿地区')

    # Penalties
    if 'part-time' in title or 'part time' in title:
        score -= 10
        reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10
        reasons.append('初级岗降分')
    if 'executive assistant' in title:
        score -= 8
        reasons.append('高管助理专业性强')

    return max(0, min(100, score)), reasons

# ---------------------------------------------------------------------------
# 5. ANZSCO 与移民路径映射
# ---------------------------------------------------------------------------
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
    elif any(k in title for k in ['developer programmer', 'application developer']):
        return '261312', 'Developer Programmer'
    elif 'multimedia specialist' in title:
        return '261211', 'Multimedia Specialist'
    elif any(k in title for k in ['ict project manager', 'it project manager']):
        return '135112', 'ICT Project Manager'
    elif any(k in title for k in ['ict security', 'cyber security']):
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
    anzsco = green_list_anzsco(title)
    if is_green_list_tier1(title):
        code_str = f" | {anzsco[0]} ({anzsco[1]})" if anzsco[0] else ""
        return f'绿名单Tier1 Straight to Residence{code_str} — 有offer即可直申居留'
    elif any(k in title for k in ['data scientist', 'ict support', 'network administrator']) or ('systems analyst' in title and 'business systems' not in title):
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    else:
        return '非绿名单，移民路径弱，建议忽略'

# ---------------------------------------------------------------------------
# 6. 主流程
# ---------------------------------------------------------------------------
all_jobs = []
email_count = 0
for path, source in EMAIL_FILES:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body(path)
    jobs = extract_jobs(body, source)
    print(f"{source}: {len(jobs)} jobs")
    all_jobs.extend(jobs)
    email_count += 1

# 去重
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal unique jobs: {len(unique_jobs)}")

# 评分
for j in unique_jobs:
    s, r = score_job(j)
    j['score'] = s
    j['reasons'] = r

unique_jobs.sort(key=lambda x: x['score'], reverse=True)

# ---------------------------------------------------------------------------
# 7. 生成报告
# ---------------------------------------------------------------------------
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

best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 来源：QQ邮箱SEEK推送（4封邮件：ICT×2 + NZ General×1 + Admin×1，2026-07-22/23批次）
> 策略更新：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | {email_count}（ICT×2 + NZ General×1 + Admin×1） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 最佳匹配 | {best['title'] if best else '无'} ({best['company'] if best else '-'}) {best['score'] if best else '-'}分 |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |

---

## 策略提醒

**本脚本已按你的要求调整：机械工程师岗位不再关注，BSA/Data Analyst/行政岗已降级。**

当前只保留两类岗位：
1. **新西兰绿名单Tier1 ICT岗**（Straight to Residence，有offer即可直申居留）
2. **大学/研究机构的研究岗**（可走雇主担保工签，研究方向可衔接德国博士）

> 绝大多数BSA/Data Analyst岗位虽然工作内容匹配你的经验，但**不在绿名单**，移民路径弱，已被过滤到低分/忽略区。

---

## 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""

for idx, j in enumerate(high, 1):
    code, name = green_list_anzsco(j['title'])
    report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** {'🔥' if idx == 1 else ''} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '近期'} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {suggest_skills(j)} |
| **移民关联** | {immigration_note(j)} |

"""

report += """---

## 中匹配岗位 (40-59分) — Tier2 / 研究相关

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
for idx, j in enumerate(medium, start=len(high)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"

report += """
---

## 低匹配岗位 (35-39分) — 可观望

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
for idx, j in enumerate(low, start=len(high)+len(medium)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"

# All jobs table (for reference)
report += f"""
---

## 全部岗位一览（含已过滤）

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 分类 |
|---|------|------|------|------|--------|------|
"""
for idx, j in enumerate(unique_jobs, 1):
    sal = j['salary'] if j['salary'] else '未公布'
    cat = j['reasons'][0] if j['reasons'] else '非目标'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {cat} |\n"

report += f"""
---

## 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 当前SEEK推送中绿名单Tier1 ICT岗数量：{tier1_count}
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

# ---------------------------------------------------------------------------
# 8. KOS JSON 写入
# ---------------------------------------------------------------------------
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
kos_section_dir.mkdir(parents=True, exist_ok=True)

meta = {
    "title": "SEEK NZ 绿名单岗位追踪",
    "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
    "icon": "briefcase",
    "section_id": "seek-nz",
    "last_updated": datetime.now().isoformat(),
}

feed = {"meta": meta, "data": kos_data}

kos_path = kos_section_dir / "latest.json"
with open(kos_path, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

# 同时写一份日期快照
snapshot_path = kos_section_dir / f"seek-nz_{today}.json"
with open(snapshot_path, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print(f"KOS feed saved: {kos_path}")
print(f"KOS snapshot saved: {snapshot_path}")

# 同时复制到本地 data 目录
local_data_dir = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\data\seek-nz')
local_data_dir.mkdir(parents=True, exist_ok=True)
with open(local_data_dir / "latest.json", "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)
print(f"Local data saved: {local_data_dir / 'latest.json'}")

# 摘要
print(f"\n{'='*60}")
print(f"SEEK NZ 扫描完成")
print(f"邮件数: {email_count}")
print(f"去重岗位: {len(unique_jobs)}")
print(f"Tier1 匹配: {tier1_count}")
print(f"Tier2 匹配: {tier2_count}")
print(f"高匹配(60+): {len(high)}")
print(f"报告: {report_path}")
print(f"{'='*60}")
