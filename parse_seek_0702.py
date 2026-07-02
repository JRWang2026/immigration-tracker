import json, re, os
from collections import OrderedDict
from datetime import datetime, timedelta
import html as html_mod

# New 2026-07-01 emails (saved from tool results)
files = [
    ('Admin 7/1 23:58', r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\66dc5a7d-23e7-403c-aea6-4b44cf3baafe\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782950535277-d5cf64.txt', 'json'),
    ('ICT 7/1 21:47', r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\66dc5a7d-23e7-403c-aea6-4b44cf3baafe\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782950535337-319a30.txt', 'json'),
    ('NZ general 7/1 20:28', r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\66dc5a7d-23e7-403c-aea6-4b44cf3baafe\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782950535460-e60df1.txt', 'json'),
    ('ICT 7/1 20:25', r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\66dc5a7d-23e7-403c-aea6-4b44cf3baafe\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782950535398-a56055.txt', 'json'),
]

def load_body(path, ftype):
    with open(path, 'r', encoding='utf-8') as f:
        if ftype == 'json':
            data = json.load(f)
            return data['data']['data']['body']
        else:
            return f.read()

def extract_jobs(body):
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

        title = html_mod.unescape(title)
        company = html_mod.unescape(company)
        location = html_mod.unescape(location)
        salary = html_mod.unescape(salary).replace('</div', '').strip()

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

all_jobs = []
for label, path, ftype in files:
    if not os.path.exists(path):
        print(f"MISSING: {label} ({path})")
        continue
    body = load_body(path, ftype)
    jobs = extract_jobs(body)
    print(f"{label}: {len(jobs)} jobs extracted")
    for j in jobs:
        j['source'] = label
    all_jobs.extend(jobs)

# Deduplicate by title+company (case-insensitive)
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal: {len(all_jobs)} raw, {len(unique_jobs)} unique\n")
for j in unique_jobs:
    print(f"  {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['posted_date']} | [{j['source']}]")

def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    salary = j['salary'].lower()
    score = 0
    reasons = []

    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])

    # Tier 1 Green List ICT (Straight to Residence)
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55
        reasons.append('绿名单Tier1: Software Engineer (261313)')
    elif 'database administrator' in title or 'dba' in title:
        score += 55
        reasons.append('绿名单Tier1: Database Administrator (262111)')
    elif 'systems administrator' in title or 'system administrator' in title:
        score += 55
        reasons.append('绿名单Tier1: Systems Administrator (262113)')
    elif any(k in title for k in ['analyst programmer', 'programmer analyst']):
        score += 55
        reasons.append('绿名单Tier1: Analyst Programmer (261311)')
    elif 'developer programmer' in title or 'application developer' in title or 'software and applications programmer' in title:
        score += 55
        reasons.append('绿名单Tier1: Developer Programmer (261312)')
    elif 'multimedia specialist' in title:
        score += 55
        reasons.append('绿名单Tier1: Multimedia Specialist')
    elif 'ict project manager' in title or 'it project manager' in title:
        score += 55
        reasons.append('绿名单Tier1: ICT Project Manager (135112)')
    elif 'ict security' in title or 'cyber security' in title or 'information security' in title:
        score += 55
        reasons.append('绿名单Tier1/Tier2: ICT Security')
    elif 'chief information officer' in title or 'chief digital officer' in title:
        score += 55
        reasons.append('绿名单Tier1: CIO/CDO (135111)')
    elif is_research_org and any(k in title for k in ['research fellow', 'postdoctoral', 'postdoc', 'doctoral candidate', 'phd candidate', 'research scientist', 'research analyst']):
        score += 50
        reasons.append('大学/研究机构研究岗')
    elif is_research_org and 'data scientist' in title:
        score += 48
        reasons.append('大学研究型Data Scientist')
    elif is_research_org and ('information management' in title or 'knowledge management' in title or 'research information' in title):
        score += 45
        reasons.append('大学信息管理研究岗')
    elif 'data scientist' in title or 'machine learning engineer' in title:
        score += 35
        reasons.append('绿名单Tier2: Data Scientist')
    elif 'ict support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title):
        score += 30
        reasons.append('绿名单Tier2: ICT Support/Network/Systems Analyst')
    elif any(k in title for k in ['it support technician', 'it support specialist', 'service desk analyst', 'service desk administrator', 'it field engineer', 'desktop support']):
        score += 30
        reasons.append('绿名单Tier2: ICT Support')
    elif 'data engineer' in title:
        score += 35
        reasons.append('近绿名单: Data Engineer(Tier2可能)')
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8
        reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'service and data analyst' in title or 'reporting analyst' in title:
        score += 8
        reasons.append('非绿名单:Data Analyst(已降级)')
    elif 'product analyst' in title or 'programme management analyst' in title:
        score += 8
        reasons.append('非绿名单:Analyst(已降级)')
    elif any(k in title for k in ['office manager', 'administrator', 'admin support', 'reception', 'executive assistant', 'coordinator', 'administration manager']):
        score += 2
        reasons.append('行政岗:忽略')
    elif any(k in title for k in ['customer service', 'client services', 'store manager', 'logistics', 'production', 'dairy farm', 'microbiology', 'quality advisor', 'sampling', 'laboratory', 'qc chemist', 'environmental technician']):
        score += 0
        reasons.append('无关岗位:忽略')
    else:
        score += 5
        reasons.append('非目标岗位')

    # Domain bonus (0-15)
    if any(k in company + ' ' + title for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation']):
        score += 15
        reasons.append('大学/研究机构')
    elif any(k in company + ' ' + title for k in ['government', 'ministry', 'council', 'education review', 'department of', 'nz police', 'stats nz', 'mbie', 'dia']):
        score += 10
        reasons.append('政府/公共部门')
    elif any(k in company + ' ' + title for k in ['ict', 'technology', 'software', 'data', 'digital', 'cloud', 'cyber']):
        score += 12
        reasons.append('ICT/科技公司')
    elif any(k in company + ' ' + title for k in ['engineering', 'manufacturing', 'industrial', 'cable', 'pump']):
        score += 5
        reasons.append('工程制造背景(已降级)')

    # Skills/keyword bonus (0-15)
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

    # Location bonus (0-8)
    non_akl_regions = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
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
    if any(k in title for k in ['junior', 'graduate', 'entry']):
        score -= 10
        reasons.append('初级岗降分')

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
    title_l = title.lower()
    return any(k in title_l for k in tier1)

def green_list_anzsco(title):
    title_l = title.lower()
    if 'software engineer' in title_l or 'software developer' in title_l:
        return '261313 (Software Engineer)'
    elif 'database administrator' in title_l or 'dba' in title_l:
        return '262111 (Database Administrator)'
    elif 'systems administrator' in title_l or 'system administrator' in title_l:
        return '262113 (Systems Administrator)'
    elif 'analyst programmer' in title_l:
        return '261311 (Analyst Programmer)'
    elif 'developer programmer' in title_l or 'application developer' in title_l:
        return '261312 (Developer Programmer)'
    elif 'multimedia specialist' in title_l:
        return '261211 (Multimedia Specialist)'
    elif 'ict project manager' in title_l or 'it project manager' in title_l:
        return '135112 (ICT Project Manager)'
    elif 'ict security' in title_l or 'cyber security' in title_l:
        return '262112 (ICT Security Specialist)'
    elif 'chief information officer' in title_l:
        return '135111 (Chief Information Officer)'
    return ''

def suggest_skills_enhanced(j):
    title = j['title'].lower()
    if is_green_list_tier1(title):
        if 'database' in title:
            return '1)SQL性能优化+数据建模作品集；2)Oracle/PostgreSQL实战经验；3)NZ雇主看重实际运维能力；4)NZQA IQA学历评估'
        elif 'software' in title or 'developer' in title or 'programmer' in title:
            return '1)GitHub作品集(2-3个完整项目)；2)LeetCode算法题准备；3)目标公司技术栈匹配；4)NZQA IQA学历评估'
        elif 'systems admin' in title:
            return '1)Windows/Linux系统管理认证；2)网络/安全实操经验；3)ITIL基础；4)NZQA IQA学历评估'
        else:
            return '1)英文简历突出具体技术栈；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '1)突出研究经历和论文；2)准备Research Statement；3)联系相关导师'
    elif 'data engineer' in title:
        return '1)Python+SQL+ETL工具栈；2)Cloud Platform认证(AWS/Azure/GCP)；3)数据管道项目展示'
    elif 'it support' in title or 'service desk' in title:
        return '1)CompTIA A+/Network+认证；2)ITIL Foundation；3)客户服务经验包装'
    else:
        return '非目标岗位，不建议投入精力'

def immigration_note(j):
    title = j['title'].lower()
    anzsco = green_list_anzsco(title)
    if is_green_list_tier1(title):
        return f'绿名单Tier1 Straight to Residence{anzsco and " | " + anzsco} — 有offer即可直申居留'
    elif 'data scientist' in title or 'ict support' in title or 'it support' in title or 'network administrator' in title or ('systems analyst' in title and 'business systems' not in title) or 'service desk' in title:
        return '绿名单Tier2 Work to Residence — 需工作2年转居留'
    elif 'university' in j['company'].lower() or 'research' in j['company'].lower():
        return '大学/研究机构岗位，通常可雇主担保Accredited Employer Work Visa'
    else:
        return '非绿名单，移民路径弱，建议忽略'

# Generate report
today = datetime.now().strftime('%Y-%m-%d')
today_display = datetime.now().strftime('%Y-%m-%d %H:%M')
next_scan = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
report_path = f'SEEK_NZ_Job_Report_{today}.md'

# Filter to relevant jobs only (>= 35)
relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)

tier1_count = sum(1 for j in relevant_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if not is_green_list_tier1(j['title']) and any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'it support', 'network administrator', 'systems analyst', 'service desk', 'data engineer']))

high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{today_display} | 📧 来源：QQ邮箱SEEK推送（4封新邮件，7/1）
> 🎯 策略：仅关注**绿名单Tier1 ICT岗** + **Tier2 ICT** + **大学/研究机构研究岗**；BSA/Data Analyst/行政/无关岗已过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | 4（ICTx2 + Adminx1 + NZ Generalx1，均7/1） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政/非ICT等） |
| 🏆最佳匹配 | {high[0]['title'] if high else (relevant_jobs[0]['title'] if relevant_jobs else '无')} ({high[0]['company'] if high else (relevant_jobs[0]['company'] if relevant_jobs else '-')}) {high[0]['score'] if high else (relevant_jobs[0]['score'] if relevant_jobs else '-')}分 |
| 绿名单Tier1 | {tier1_count} |
| 绿名单Tier2/近绿名单 | {tier2_count} |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(35-39) | {len(low)} |

---

## 🚨 策略提醒

**主线不变：德国岗位制博士（90%精力）。** 新西兰SEEK扫描仅作为"副线出境通道"保留。

当前只保留：
1. **绿名单Tier1 ICT岗**（Straight to Residence）
2. **绿名单Tier2 ICT岗**（Work to Residence，2年转居留）
3. **大学/研究机构岗**（雇主担保工签+研究方向可衔接德国博士）

---

## 🏆 高匹配岗位 (60+分) — 绿名单Tier1 / 大学研究岗

"""

if high:
    for idx, j in enumerate(high, 1):
        anzsco_code = green_list_anzsco(j['title'])
        imm_note = immigration_note(j)
        skills = suggest_skills_enhanced(j)
        report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']} | {j['company']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** {'🔥' if j['score'] >= 75 else ''} |
| **ANZSCO** | {anzsco_code if anzsco_code else 'N/A'} |
| **地点** | {j['location']} |
| **薪资** | {j['salary'] if j['salary'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '近期'} |
| **来源邮件** | {j.get('source', '')} |
| **匹配分析** | {'；'.join(j['reasons'])} |
| **所需补充** | {skills} |
| **移民关联** | {imm_note} |

"""
else:
    report += "> ⚠️ 本轮**无高匹配岗位**（≥60分）。\n\n"

report += """---
## 🟡 中匹配岗位 (40-59分) — Tier2 / 近绿名单

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
for idx, j in enumerate(medium, start=len(high)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"

if not medium:
    report += "| - | - | - | - | - | - | 无 |\n"

report += """
---
## 🔵 低匹配岗位 (35-39分) — 可观望

| # | 职位 | 公司 | 地点 | 薪资 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
for idx, j in enumerate(low, start=len(high)+len(medium)+1):
    sal = j['salary'] if j['salary'] else '未公布'
    report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {sal} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"

if not low:
    report += "| - | - | - | - | - | - | 无 |\n"

# Print all jobs for debugging
print("\n===== ALL JOBS SCORED =====")
for j in unique_jobs:
    print(f"  [{j['score']:3d}] {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {';'.join(j['reasons'])}")

# Continuous tracking
report += """
---
## 📈 持续开放岗位跟踪

"""
# Compute tracking from current jobs
boei_dba = [j for j in unique_jobs if 'database administrator' in j['title'].lower() and 'boei' in j['company'].lower()]
canterbury_uni = [j for j in unique_jobs if 'university of canterbury' in j['company'].lower()]
silver_fern = [j for j in unique_jobs if 'silver fern' in j['company'].lower() and 'data' in j['title'].lower()]
windsor = [j for j in unique_jobs if 'windsor' in j['company'].lower()]

report += """| 职位 | 公司 | 首次出现 | 趋势 | 本轮状态 | 移民路径 |
|------|------|----------|------|---------|---------|
"""
if boei_dba:
    report += f"| Database Administrator | BOEI Solutions | 6/27 首次 | 🔥4轮持续 | ✅ 仍开放（{boei_dba[0]['score']}分） | 绿名单Tier1 Straight to Residence |\n"
else:
    report += f"| Database Administrator | BOEI Solutions | 6/27 首次 | ⚠️本轮消失 | ❌ 已关闭/下架 | 绿名单Tier1 Straight to Residence |\n"

if canterbury_uni:
    report += f"| Service and Data Analyst | University of Canterbury | 6/29 首次 | 持续 | ✅ 仍开放（{canterbury_uni[0]['score']}分） | 大学雇主担保AEWV |\n"
else:
    report += "| Service and Data Analyst | University of Canterbury | 6/29 首次 | ⚠️本轮消失 | ❌ 已关闭 | 大学雇主担保AEWV |\n"

if silver_fern:
    report += f"| Senior Data Analyst | Silver Fern Farms | 6/29 首次 | 持续 | ✅ 仍开放（{silver_fern[0]['score']}分） | 非绿名单 |\n"
else:
    report += "| Senior Data Analyst | Silver Fern Farms | 6/29 首次 | ⚠️本轮消失 | ❌ 已关闭 | 非绿名单 |\n"

if windsor:
    report += f"| BSA-ERP | Windsor Engineering | 6/16 首次 | ⚠️15天+ | ✅ 仍开放（非绿名单） | 非绿名单 |\n"

report += f"""
---
## 🎯 行动建议

### 主线：德国岗位制博士（90%精力）
- 当前SEEK绿名单Tier1 ICT岗位极稀少（本轮{len(high)}个高匹配）
- 新西兰作为"副线出境通道"保留，**不主动投递非绿名单岗位**

### 新西兰副线（10%精力）
- 紧盯BOEI DBA岗 — 绿名单Tier1唯一持续出现岗位
- 如有绿名单Tier1 offer，可作出境跳板后衔接德国博士
- NZQA IQA学历评估可提前启动（4-8周，NZ$745）

### 简历准备
- 英文简历突出Python/SQL/数据分析/IP
- BOEI DBA方向：SQL优化+数据库管理经验包装
- BSA岗不值得投入精力（非绿名单无移民路径）

---
## 📋 绿名单移民路径速查

| 职业 | ANZSCO | 绿名单层级 | 移民方式 | 本轮出现 |
|------|--------|-----------|---------|--------|
| Software Engineer | 261313 | Tier1 | Straight to Residence | {'✅' if any('software' in j['title'].lower() for j in unique_jobs) else '❌'} |
| Database Administrator | 262111 | Tier1 | Straight to Residence | {'✅' if any('database' in j['title'].lower() for j in unique_jobs) else '❌'} |
| Systems Administrator | 262113 | Tier1 | Straight to Residence | {'✅' if any('system' in j['title'].lower() and 'admin' in j['title'].lower() for j in unique_jobs) else '❌'} |
| Analyst Programmer | 261311 | Tier1 | Straight to Residence | ❌ |
| Developer Programmer | 261312 | Tier1 | Straight to Residence | ❌ |
| ICT Project Manager | 135112 | Tier1 | Straight to Residence | ❌ |
| ICT Security Specialist | 262112 | Tier1 | Straight to Residence | ❌ |
| CIO | 135111 | Tier1 | Straight to Residence | ❌ |

> ⚠️ NZ移民局7月1日更新：中位数工资$33.56/hr；绿名单Tier1 ICT无变动

---
## 📊 本轮全部岗位清单（按匹配度排序）

| # | 匹配度 | 职位 | 公司 | 地点 | 薪资 | 评估 |
|---|--------|------|------|------|------|------|
"""
for idx, j in enumerate(unique_jobs, 1):
    sal = j['salary'][:50] if j['salary'] else '未公布'
    report += f"| {idx} | {j['score']} | {j['title']} | {j['company']} | {j['location'][:40]} | {sal} | {';'.join(j['reasons'][:2])} |\n"

report += f"""

---
*报告由SEEK NZ自动化扫描生成（绿名单Tier1聚焦版） | 下次扫描：{next_scan}*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n=== Report saved: {report_path} ===")
print(f"Total: {len(unique_jobs)} jobs, {len(relevant_jobs)} relevant (>=35), Tier1: {tier1_count}, High: {len(high)}, Medium: {len(medium)}, Low: {len(low)}")
