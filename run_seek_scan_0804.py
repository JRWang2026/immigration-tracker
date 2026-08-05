"""
SEEK NZ 扫描 - 2026-08-04 (绿名单Tier1聚焦版)
- 2 large emails: email_cache/email_admin_0804.json + email_nz_0804.json
- 2 small ICT emails: hardcoded jobs (8 + 3 cards each, mostly overlapping)
"""
import json, re, os, sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36')
sys.path.insert(0, str(WORKSPACE))
from local_agent.kos_bridge import write_kos_feed

# 2 file-based emails
file_paths = [
    (str(WORKSPACE / 'email_cache' / 'email_admin_0804.json'), 'json'),
    (str(WORKSPACE / 'email_cache' / 'email_nz_0804.json'), 'json'),
]

# 2 ICT emails (msg_571C = 8 jobs, msg_l0tF = 3 jobs)
# Extracted directly from GetMessage inline results
ICT_JOBS = [
    # msg_571C: 8 new ICT jobs (2026-08-03T21:47:14Z)
    {'title': 'Laboratory Technician', 'company': 'EUROFINS REGIONAL SERVICE CENTRE ANZ PTY LTD', 'location': 'Penrose, Auckland', 'salary': '', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5Ce2rIkwLmml0KDgDt68jS-tro9Lbw0xvM8jpnQ7ZEZerCs0dTl8pKrDTaVnEMTYBd3X20NJaiQJCAuyY_x-3qUEiblUDgiGYDXEyZ-Z-ARkwgKB_KXVbcA6EJheFavR8'},
    {'title': 'Food Safety and Quality Manager', 'company': 'Private Advertiser', 'location': 'Mount Wellington, Auckland', 'salary': '$120,000 – $140,000 per year', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6ZRa_afa-eKQiD6C6WMk4pjasq6fD_mKyUbrxfph1IfP3xtfeBSYsBTFZ02X4Ps4uGocALd7TeMRzqqWYaWJe10247Xp9H6pno91GI5Bmg6V3fV6PyN8HnDtCUxohdGEg'},
    {'title': 'Brewer / Brewery Operator', 'company': 'bStudio Ltd', 'location': 'Ahuriri, Hawkes Bay', 'salary': '', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv72ndnq6ku7maOVkbNxar-RXHBNcjConElrdLWdoQ7zYj2wXcmVowAWwvuXClU85YSrFX35MsWONMuD1Lm3iayDoYSH-AKup7xvyIbkelhge6BG9TmOzlIeHHgN4B6El40'},
    {'title': 'Associate Data Engineer (Power BI) (9-months Fixed Term Contract)', 'company': 'Douglas', 'location': 'Henderson, Auckland', 'salary': 'Market related salary + benefits', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv7U4pSP9h4xq73H5kKuPQyS__HcnLhLVlNhnr-5kz9EhOsJ0c-NG9EOiWFkbhNn6szMVQUExf3RxMOnyIFSh1QTfNXpkpBfKzNfLNUUlTWSlge4_7hdyCBr11HMrpHmeWg'},
    {'title': 'Senior Technical Business Analyst', 'company': 'Techspace Consulting Limited', 'location': 'Te Puke, Bay of Plenty', 'salary': '', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6fybxQ2wahvB2h2taXrxMvXW_RbsA9QPe5ns41g7a1XCZ6hVrCEbyZ5Xg-RJTJw4D1e9mFAhMoIeh_tISNoC8DlqKILYv7htSBlyT_DaCggbnEAsOuYjwP8lXwFekhPN0'},
    {'title': 'SRE / DevOps Engineer - Kafka & Confluent (Azure) Data & Platform', 'company': 'Walker Smith', 'location': 'Auckland CBD, Auckland', 'salary': '', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv41S5V4qZ98PV259igDKSfCpfQecgoX68eOZKntJoNgbaeTvV5fKnCVqoGDeBijN7DWAs43jAq5XyqaBNQI8tZZt5rzEhcyS-2AM4eMxkVbuS5Up4a7YtCydO7c0LpJaf4'},
    {'title': 'Senior Adviser AMR Technical', 'company': 'Ministry for Primary Industries', 'location': 'Wellington Central, Wellington', 'salary': '$102,953 – $137,778', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv6ivDmZHNpVY30cQR6YVCy3dMSbucjlQxFSgstuFLI2ZWimhflt2jt0r6g9KbH1JKiSGhAL4__BcIu1CmmE-ueiK9QZwab6pY5AMnD53gI5FrRA4Jz5PZmPHeiy2iIsCqY'},
    {'title': 'Medical Laboratory Scientist, Part time - Palmerston North Blood Bank', 'company': 'NZ Blood Service', 'location': 'Palmerston North Central, Manawatu', 'salary': '$72,847 - $110,290', 'posted_date': '', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv72BM3ci6zcsW55PSLRwgT3ye8e59c67XpmL12HqQTrwEcP0JEa7t7zrEQgP_22oRNoWQO3y_OX4oStDsupA_1GTZECVaqc4MEgsqZpQFDESexIVv-tKUWxW4RuPFSjLYA'},
    # msg_571C: 3 "Jobs you may have missed" - older jobs, skip Posted date in our dedup
    {'title': 'Business Systems Analyst', 'company': 'Hawkes Bay Regional Council', 'location': 'Napier Central, Hawkes Bay', 'salary': '$88,995 – $104,700 per year', 'posted_date': '31 Jul 2026', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv7b7euDEw8QZ9i4j2XXaEAciyn0kcfcw-cp3aDwVZbKalVmL81GVc8h4zK3xT7IUKppErMC-Z2T1It0jLPa4W6bWYDe8ORuk5hqcu3DVKUICKct7PHqEJNkkvLDRYnrj2Q'},
    {'title': 'Process Analyst', 'company': 'AA Insurance', 'location': 'Auckland CBD, Auckland', 'salary': '', 'posted_date': '26 Jul 2026', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv4WcM3XIEpPMhiQ_u_8HM03URgE0WVDJbm95oI4kEkpD_noKbLYLJSg73VFXKqApaYJuhZ9vUV59dHaureRBQ1z2ZEQ3kq_tRzNn-WyovT8MpEGqNOTcYa33tgEas0IWi8'},
    {'title': 'Data Analyst - Guidance', 'company': 'Halter', 'location': 'Auckland CBD, Auckland', 'salary': '$100,000 – $125,000 per year', 'posted_date': '22 Jul 2026', 'url': 'https://email.s.seek.co.nz/uni/ss/c/u001.l5tc4iXB2-Bk7UR8KdEfXVqCAR5PUSSiJ59vaNz9vv5FSxZj3aBRWYVX9g2_5RZBj624c6tdkRDvyB1gitGgF-Sq9E5SZdOlVUmMh7XaLgxwezn66DRIncxUCKEhTBkK5hN4jdd6eMF_rkqdbJoxalYRtECIRSW4pGoeAPv4x7Y'},
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
                    if re.search(r'(competitive|benefits|insurance|super|bonus|market)', tm, re.I):
                        salary = tm
                        break
        posted_date = date_match.group(1) if date_match else ''
        url = url_match.group(1) if url_match else ''
        import html
        title = html.unescape(title)
        company = html.unescape(company)
        location = html.unescape(location)
        salary = html.unescape(salary).replace('</div', '').strip()
        jobs.append({
            'title': title, 'company': company, 'location': location,
            'salary': salary, 'posted_date': posted_date, 'url': url, 'source': '',
        })
    return jobs

all_jobs = list(ICT_JOBS)  # start with hardcoded ICT jobs

# Add file-based email jobs
for path, ftype in file_paths:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body(path, ftype)
    jobs = extract_jobs(body)
    print(f"{os.path.basename(path)}: {len(jobs)} jobs")
    all_jobs.extend(jobs)

# Deduplicate
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"\nTotal unique jobs: {len(unique_jobs)}")
for j in unique_jobs:
    print(f"  {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['posted_date']}")

def score_job(j):
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []
    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])
    # Tier 1 Green List ICT
    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55
        reasons.append('绿名单Tier1: Software Engineer')
    elif 'devops engineer' in title or 'sre' in title or 'site reliability' in title:
        score += 55
        reasons.append('绿名单Tier1: DevOps/SRE (ANZSCO 261313)')
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
    elif re.match(r'\bcio\b', title) or 'chief information officer' in title or 'chief digital officer' in title:
        score += 55
        reasons.append('绿名单Tier1: CIO/CDO')
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
    elif 'business systems analyst' in title or 'business analyst' in title or 'erp analyst' in title:
        score += 8
        reasons.append('非绿名单:BSA/ERP(已降级)')
    elif 'data analyst' in title or 'data engineer' in title or 'reporting analyst' in title:
        score += 8
        reasons.append('非绿名单:Data Analyst/Engineer(已降级)')
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
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure', 'kafka', 'confluent', 'power bi']):
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
    non_akl_regions = ['canterbury', 'christchurch', 'waikato', 'hamilton', 'dunedin', 'bay of plenty', 'whakatane', 'hawkes bay', 'napier', 'hastings', 'palmerston north', 'manawatu', 'marlborough', 'otago']
    if any((', ' + k in location or location.endswith(', ' + k) or location == k) for k in non_akl_regions):
        score += 8
        reasons.append('非奥克兰地区加分')
    elif location.endswith(', wellington') or location == 'wellington':
        score += 5
        reasons.append('惠灵顿地区')
    # Penalties
    if 'part-time' in title or 'part time' in title or 'part time -' in title:
        score -= 10
        reasons.append('兼职降分')
    if any(k in title for k in ['junior', 'graduate', 'entry']):
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
        'ict security specialist', 'chief information officer', 'chief digital officer',
        'devops engineer', 'sre', 'site reliability',
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
    elif 'devops engineer' in title or 'sre' in title or 'site reliability' in title:
        return '261313 (Software Engineer) - DevOps/SRE'
    elif re.match(r'\bcio\b', title) or 'chief information officer' in title:
        return '135111 (Chief Information Officer)'
    return ''

def suggest_skills(j):
    title = j['title'].lower()
    if is_green_list_tier1(title):
        return '1)英文简历突出具体技术栈(Python/SQL/Cloud/Kafka/Azure)；2)GitHub作品集；3)准备NZ本地面试题；4)NZQA IQA学历评估'
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
report_path = str(WORKSPACE / f'SEEK_NZ_Job_Report_{today}.md')

relevant_jobs = [j for j in unique_jobs if j['score'] >= 35]
filtered_out = len(unique_jobs) - len(relevant_jobs)
tier1_count = sum(1 for j in unique_jobs if is_green_list_tier1(j['title']))
tier2_count = sum(1 for j in relevant_jobs if any(k in j['title'].lower() for k in ['data scientist', 'ict support', 'network administrator', 'systems analyst']) and not is_green_list_tier1(j['title']))
high = [j for j in relevant_jobs if j['score'] >= 60]
medium = [j for j in relevant_jobs if 40 <= j['score'] < 60]
low = [j for j in relevant_jobs if 35 <= j['score'] < 40]

best = high[0] if high else (relevant_jobs[0] if relevant_jobs else None)
best_str = f"{best['title']} ({best['company']}) {best['score']}分" if best else '无'

report = f"""# SEEK NZ 岗位扫描报告 - {today} (绿名单Tier1聚焦版)

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 📧 来源：QQ邮箱SEEK推送（4封邮件：8/3 Admin + 8/3 ICT×2 + 8/3 NZ General）
> 🎯 策略更新：仅关注**绿名单Tier1 ICT岗** + **大学/研究机构研究岗**；BSA/Data Analyst/行政岗已降级/过滤

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描邮件数 | 4（8/3 Admin + 8/3 ICT×2 + 8/3 NZ General） |
| 去重岗位总数 | {len(unique_jobs)} |
| 过滤后相关岗位 | {len(relevant_jobs)}（仅显示≥35分） |
| 过滤掉岗位 | {filtered_out}（BSA/Data Analyst/行政等非绿名单岗） |
| 🏆最佳匹配 | {best_str} |
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

for idx, j in enumerate(high, 1):
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

report += """
---

## 📈 持续开放岗位跟踪（绿名单/研究岗）

| 职位 | 公司 | 首次出现 | 本轮匹配度 | 状态 |
|------|------|----------|-----------|------|
| Online Research Candidates | PanelPlace | 2026-08-03 | 35 | 🆕研究型（持续） |
| LEVEL ONE Service Desk Engineer | Appoint Limited | 2026-08-02 | 30 | 绿名单Tier2近（持续） |
| IT Support Analyst | Alliance Group Ltd | 2026-08-02 | 30 | 绿名单Tier2近（持续） |
| Senior IT Support Engineer | Computer Clinic | 2026-08-04 | 30 | 绿名单Tier2近（🆕本轮） |
| **SRE / DevOps Engineer - Kafka & Confluent** | Walker Smith | 2026-08-04 | **47** | **🆕Tier1 DevOps/SRE (ANZSCO 261313)** |
| Associate Data Engineer (Power BI) | Douglas | 2026-08-04 | 25 | Data Engineer(非绿名单) |
| Senior Technical Business Analyst | Techspace Consulting | 2026-08-04 | 13 | BSA(已降级) |

---
"""

report += f"""
## 🎯 行动建议

### 主线不变：德国岗位制博士（90%精力）
- 当前SEEK推送中绿名单Tier1 ICT岗密度极低（连续30+天Tier1归零/极少）
- 新西兰作为"备选出境通道"保留，但**不建议主动投递非绿名单岗位**

### 新西兰副线（10%精力）
1. **只关注绿名单Tier1 ICT岗**：Software Engineer / Database Administrator / Systems Administrator / Analyst Programmer / Developer Programmer / ICT Project Manager / ICT Security Specialist / CIO / DevOps Engineer / SRE
2. **只关注大学/研究机构的研究岗**：可衔接德国博士方向
3. **如出现绿名单Tier1 offer**：可作为一个出境跳板，后续再申德国博士

### 简历准备（绿名单ICT方向）
- 英文简历突出：**Python/SQL/Cloud/Kafka/Azure/GitHub作品集**
- 如投DevOps/SRE：突出CI/CD、容器化、监控等基础设施经验
- 如投Software Engineer：准备LeetCode风格算法题 + 系统设计基础
- 所有绿名单ICT岗都需要：**NZQA IQA学历评估**（4-8周，NZ$745）

---

## 📋 绿名单移民路径提醒

| 职业 | ANZSCO | 绿名单层级 | 移民路径 | 你的匹配度 |
|------|--------|-----------|---------|----------|
| Software Engineer | 261313 | **Tier1** ⭐ | Straight to Residence | 低（非程序员背景） |
| DevOps Engineer / SRE | 261313 | **Tier1** ⭐ | Straight to Residence | 中（系统化经验） |
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

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\nReport saved: {report_path}")

# --- KOS feed generation ---
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

email_count = sum(1 for path, _ in file_paths if os.path.exists(path)) + 2  # +2 for ICT emails

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
