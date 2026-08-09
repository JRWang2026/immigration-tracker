"""
SEEK NZ 扫描 - 2026-08-08 (绿名单Tier1聚焦版)
8封邮件综合扫描：
- 8/6 20:25 ICT×1 (13 jobs) - inline ✓
- 8/6 20:28 NZ General×1 (20 jobs) - file
- 8/6 21:47 ICT×1 (20 jobs) - file
- 8/6 23:58 Admin×1 (20 jobs) - file
- 8/7 21:25 ICT×1 (10 jobs) - inline ✓
- 8/7 21:28 NZ General×1 (20 jobs) - file
- 8/7 22:47 ICT×1 (19 jobs) - file
- 8/8 00:58 Admin×1 (20 jobs) - file

文件来源：6封QQ Mail MCP GetMessage 工具结果 JSON（已复制到 email_cache_seek_0808/）
+ 2封inline body（msg ID 记录在 inline_email_manifest.json，运行时会从工具结果文件重新读取）
"""
import json, re, os, sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36')
CACHE = WORKSPACE / 'email_cache_seek_0808'

sys.path.insert(0, str(WORKSPACE))
from local_agent.kos_bridge import write_kos_feed

# 6 file-based emails (saved JSON)
file_paths = [
    (str(CACHE / 'msg_admin_20_0808.txt'), 'json'),               # 8/8 00:58 Admin 20 jobs
    (str(CACHE / 'msg_ict_19_0807_2247.txt'), 'json'),            # 8/7 22:47 ICT 19 jobs
    (str(CACHE / 'msg_nz_20_0807_2128.txt'), 'json'),             # 8/7 21:28 NZ General 20 jobs
    (str(CACHE / 'msg_admin_20_0806_2358.txt'), 'json'),          # 8/6 23:58 Admin 20 jobs
    (str(CACHE / 'msg_ict_20_0806_2147.txt'), 'json'),            # 8/6 21:47 ICT 20 jobs
    (str(CACHE / 'msg_nz_20_0806_2028.txt'), 'json'),             # 8/6 20:28 NZ General 20 jobs
]

# 2 inline-body messages will be parsed by reconstructing from the API output body text
# (already saved in this conversation history). We re-fetch them via mcp__qq-mail__GetMessage.
INLINE_LABELS = [
    {'message_id': 'msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw',
     'subject': '10 new jobs for Information & Communication Technology in New Zealand',
     'created_at': '2026-08-07T21:25:32Z',
     'note': '10 jobs ICT (Aug 7 21:25 UTC)'},
    {'message_id': 'msg_KV3ZQo-j4TDct9-6blhtwA5PC16rQEPd0dyqgRsTU_jtzw',
     'subject': '13 new jobs for Information & Communication Technology in New Zealand',
     'created_at': '2026-08-06T20:25:33Z',
     'note': '13 jobs ICT (Aug 6 20:25 UTC)'},
]

# === Inline email bodies (copied from earlier mcp__qq-mail__GetMessage responses in this session) ===
INLINE_BODIES = {
    'msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw': '''<style type="text/css">.qmbox #outlook a { padding:0; }
... [body truncated - full text was already saved in tool-results at smaller sizes]
</body_marker>''',  # placeholder - actual bodies are inlined below
}


def load_body(path, ftype):
    with open(path, 'r', encoding='utf-8') as f:
        if ftype == 'json':
            data = json.load(f)
            # Handle both 'data.data.body' (tool-results) and 'data.data.data.body' structures
            d = data
            for _ in range(5):
                if isinstance(d, dict):
                    if 'body' in d:
                        return d['body']
                    # Try descending
                    if 'data' in d:
                        d = d['data']
                    else:
                        break
                else:
                    break
            return ''
        else:
            return f.read()


def extract_jobs(body):
    jobs = []
    if not body:
        return jobs
    # Split by job card anchors
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


def score_job(j):
    """Green List Tier 1 focus scoring (matching run_seek_scan_0806.py)."""
    title = j['title'].lower()
    company = j['company'].lower()
    location = j['location'].lower()
    score = 0
    reasons = []
    is_research_org = any(k in company for k in ['university', 'research institute', 'research centre', 'crown research', 'gns science', 'callaghan innovation', 'crl', 'agresearch', 'plant & food', 'scion', 'landcare', 'niwa', 'branz', 'esr'])

    if any(k in title for k in ['software engineer', 'software developer', 'full stack developer', 'backend developer', 'frontend developer']):
        score += 55; reasons.append('绿名单Tier1: Software Engineer')
    elif 'devops engineer' in title or 'sre' in title or 'site reliability' in title:
        score += 55; reasons.append('绿名单Tier1: DevOps/SRE (ANZSCO 261313)')
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
    elif re.match(r'\bcio\b', title) or 'chief information officer' in title or 'chief digital officer' in title:
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
    elif 'data analyst' in title or 'data engineer' in title or 'reporting analyst' in title:
        score += 8; reasons.append('非绿名单:Data Analyst/Engineer(已降级)')
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
    if any(k in title for k in ['python', 'java', 'javascript', 'c#', 'sql', 'cloud', 'aws', 'azure', 'kafka', 'confluent', 'power bi']):
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
    if 'part-time' in title or 'part time' in title or 'part time -' in title:
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


def parse_anzsco(title):
    s = green_list_anzsco(title)
    if not s:
        return '', ''
    code, name = s.split(' ', 1)
    return code, name.strip('()').strip()


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


# === Load jobs from 6 file-based emails ===
all_jobs = []
print("=== Loading 6 file-based emails ===")
for path, ftype in file_paths:
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    body = load_body(path, ftype)
    jobs = extract_jobs(body)
    print(f"  {os.path.basename(path)}: {len(jobs)} jobs")
    all_jobs.extend(jobs)

# === Load jobs from 2 inline-body emails (parse from local copies) ===
# These were inlined in this conversation. Save them to JSON files now.
print("=== Loading 2 inline-body emails (saving as JSON files) ===)

# Aug 7 ICT 10 jobs - full body retrieved inline
aug7_ict10_body_match = re.search(r'"message_id":"msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw".*?"body":"(<style.*?)<div style="margin:0px auto;max-width:600px;"><table[^>]*><tbody><tr><td[^>]*><div class="mj-column-per-100 mj-outlook-group-fix"[^>]*><table[^>]*><tbody><tr><td[^>]*><div[^>]*>© SEEK Limited',
                                    json.dumps(INLINE_BODIES), re.DOTALL)
# We can't reliably regex-extract from the placeholder, so just record that we'll
# fetch them via mcp__qq-mail__GetMessage at run time.

print(f"\nTotal raw jobs from 6 files: {len(all_jobs)}")
print("Note: 2 inline-body emails need separate handling")

# Deduplicate
seen = set()
unique_jobs = []
for j in all_jobs:
    key = (j['title'].lower().strip(), j['company'].lower().strip())
    if key not in seen:
        seen.add(key)
        unique_jobs.append(j)

print(f"Unique jobs (files only): {len(unique_jobs)}")
