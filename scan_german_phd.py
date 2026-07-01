import json, re, os, time, html
import requests
from urllib.parse import urlencode, urljoin
from datetime import datetime, timedelta
from collections import OrderedDict

# User profile constants
PROFILE = {
    'interests': ['patent analysis', 'competitive intelligence', 'bibliometrics', 'scientometrics',
                  'information science', 'knowledge management', 'innovation management', 'technology management',
                  'data science', 'text mining', 'nlp', 'natural language processing'],
    'skills': ['python', 'data analysis', 'sql', 'power bi', 'tableau', 'machine learning'],
}

KEYWORDS = [
    'information science', 'patent analysis', 'competitive intelligence', 'bibliometrics',
    'scientometrics', 'knowledge management', 'innovation management', 'technology management',
    'data science', 'text mining', 'nlp'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# ---------------- EURAXESS ----------------

def fetch_euraxess(keyword):
    """Fetch EURAXESS search results for a keyword."""
    base = 'https://euraxess.ec.europa.eu/jobs/search'
    params = {
        'keywords': keyword,
        'country': 'de',
        'f[0]': 'job_research_profile:447',  # First Stage Researcher (R1) / PhD level
    }
    url = base + '?' + urlencode(params)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text, url
    except Exception as e:
        print(f"EURAXESS error for '{keyword}': {e}")
        return '', url

def parse_euraxess(html_text, source_url, keyword):
    """Parse EURAXESS search result page."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')
    jobs = []

    # Each job teaser is wrapped in <div id="job-teaser-content">
    for card in soup.find_all('div', id='job-teaser-content'):
        try:
            # Title
            title_tag = card.find('h3', class_='ecl-content-block__title')
            if not title_tag:
                continue
            a_tag = title_tag.find('a')
            title = a_tag.get_text(strip=True) if a_tag else title_tag.get_text(strip=True)
            url = a_tag.get('href', '') if a_tag else ''
            url = urljoin('https://euraxess.ec.europa.eu', url)

            # Organisation
            org = ''
            primary_meta = card.find('ul', class_='ecl-content-block__primary-meta-container')
            if primary_meta:
                org_tag = primary_meta.find('a')
                if org_tag:
                    org = org_tag.get_text(strip=True)
                # Posted date
                posted_tag = primary_meta.find('li', class_='ecl-content-block__primary-meta-item')
                if posted_tag:
                    posted_text = posted_tag.get_text(strip=True)
                else:
                    posted_text = ''
            else:
                posted_text = ''

            posted = ''
            m = re.search(r'Posted on:\s*(.+)', posted_text)
            if m:
                posted = m.group(1).strip()

            # Description
            desc = ''
            desc_tag = card.find('div', class_='ecl-content-block__description')
            if desc_tag:
                desc = desc_tag.get_text(strip=True)

            # Secondary meta: work location, research field, deadline, etc.
            location = 'Germany'
            research_field = ''
            deadline = ''
            funding = ''
            secondary_meta = card.find('ul', class_='ecl-content-block__secondary-meta-container')
            if secondary_meta:
                for item in secondary_meta.find_all('li', class_='ecl-content-block__secondary-meta-item'):
                    # Find the label div and value div inside the item
                    label_div = item.find('div', class_=re.compile(r'id-Work-Locations|id-Research-Field|id-Application-Deadline|id-Funding-Programme|id-Researcher-Profile'))
                    if not label_div:
                        continue
                    # Extract text from the value div (the second child div)
                    value_div = label_div.find_all('div', recursive=False)
                    if len(value_div) < 2:
                        continue
                    value_text = value_div[1].get_text(strip=True)
                    if 'id-Work-Locations' in str(label_div.get('class', [])):
                        # Clean "Number of offers: N, Country, ..." to just the location part
                        loc = value_text
                        loc = re.sub(r'Number of offers:\s*\d+,?\s*', '', loc, flags=re.I)
                        # Try to keep city/institution, remove leading country if present
                        parts = [p.strip() for p in loc.split(',') if p.strip()]
                        if len(parts) > 1 and parts[0].lower() in ['germany', 'deutschland', 'sweden', 'denmark', 'norway', 'netherlands', 'switzerland', 'austria', 'belgium', 'france']:
                            parts = parts[1:]
                        location = ', '.join(parts[:3])
                    elif 'id-Research-Field' in str(label_div.get('class', [])):
                        research_field = value_text
                    elif 'id-Application-Deadline' in str(label_div.get('class', [])):
                        deadline = value_text
                    elif 'id-Funding-Programme' in str(label_div.get('class', [])):
                        funding = value_text

            if title and len(title) > 3:
                jobs.append({
                    'title': html.unescape(title),
                    'company': html.unescape(org),
                    'location': html.unescape(location),
                    'research_field': html.unescape(research_field),
                    'deadline': html.unescape(deadline),
                    'funding': html.unescape(funding),
                    'posted_date': html.unescape(posted),
                    'description': html.unescape(desc),
                    'url': url,
                    'source': 'EURAXESS',
                    'search_keyword': keyword
                })
        except Exception as e:
            print(f"EURAXESS parse error: {e}")
            continue
    return jobs

# ---------------- academics.de ----------------

def fetch_academics(keyword):
    """Fetch academics.de search results."""
    base = 'https://www.academics.de/stellenanzeigen'
    params = {
        'q': keyword,
        'location': 'de',
    }
    url = base + '?' + urlencode(params)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text, url
    except Exception as e:
        print(f"academics.de error for '{keyword}': {e}")
        return '', url

def parse_academics(html_text, source_url, keyword):
    """Parse academics.de search result page."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')
    jobs = []

    # Job teasers are <li id="job-teaser-<id>-container"> containing an <a id="job-<id>">
    for li in soup.find_all('li', id=re.compile(r'job-teaser-\d+-container')):
        try:
            a_tag = li.find('a', id=re.compile(r'job-\d+'))
            if not a_tag:
                continue
            title = a_tag.get('title', '').strip()
            url = a_tag.get('href', '')
            url = urljoin('https://www.academics.de', url)

            # Fallback title
            if not title:
                h2 = a_tag.find('h2', class_='inline')
                if h2:
                    title = h2.get_text(strip=True)

            # Company
            company = ''
            p_tag = a_tag.find('p', class_='text-style-paragraph-sm')
            if p_tag:
                company = p_tag.get_text(strip=True)

            # Location and date from badges
            location = ''
            posted = ''
            badges = a_tag.find_all('span', class_='truncate')
            for badge in badges:
                txt = badge.get_text(strip=True)
                if re.match(r'\d{2}\.\d{2}\.\d{4}', txt):
                    posted = txt
                elif not location and len(txt) > 2 and not txt.lower() in ['vollzeit', 'teilzeit', 'befristet', 'unbefristet']:
                    location = txt

            # Description - academics teaser has no description, use title for matching
            desc = title

            if title and len(title) > 3:
                jobs.append({
                    'title': html.unescape(title),
                    'company': html.unescape(company),
                    'location': html.unescape(location) or 'Germany',
                    'research_field': '',
                    'deadline': '',
                    'funding': '',
                    'posted_date': html.unescape(posted),
                    'description': html.unescape(desc),
                    'url': url,
                    'source': 'academics.de',
                    'search_keyword': keyword
                })
        except Exception as e:
            print(f"academics.de parse error: {e}")
            continue
    return jobs

# ---------------- Scoring ----------------

def is_phd_position(title):
    """Check if the position is a PhD / doctoral candidate position."""
    t = title.lower()
    phd_keywords = ['phd', 'doktorand', 'doktorandin', 'doctoral', 'doctorate',
                    'predoctoral', 'predoc', 'wissenschaftlicher mitarbeiter',
                    'wissenschaftliche mitarbeiterin', 'wissenschaftliche/r mitarbeiter',
                    'research assistant', 'ph.d.', 'phd-student', 'phd student',
                    'early stage researcher', 'first stage researcher']
    return any(k in t for k in phd_keywords)

def is_non_phd_academic(title):
    """Check for postdoc / professorship / lecturer positions (not suitable now)."""
    t = title.lower()
    non_phd = ['postdoc', 'postdoctoral', 'professor', 'professur', 'professorship',
               'lecturer', 'dozent', 'junior professor', 'juniorprofessur',
               'senior researcher', 'group leader', 'team leader']
    return any(k in t for k in non_phd)

def is_management_position(title):
    """Check for management / administrative positions."""
    t = title.lower()
    mgmt = ['manager', 'managerin', 'referent', 'referentin', 'administrator',
            'administrative', 'project manager', 'projektmanager', 'project leader',
            'geschäftsstelle', 'vorstand', 'head of']
    return any(k in t for k in mgmt)

def score_job(job):
    title = job['title'].lower()
    desc = (job.get('description', '') + ' ' + job.get('research_field', '')).lower()
    company = job.get('company', '').lower()
    text = title + ' ' + desc + ' ' + company
    score = 0
    reasons = []

    # Role type penalty (apply first)
    if is_phd_position(title):
        score += 10
        reasons.append('博士岗位')
    elif is_non_phd_academic(title):
        score -= 30
        reasons.append('博士后/教职岗(暂不适合)')
    elif is_management_position(title):
        score -= 25
        reasons.append('管理岗(偏离目标)')

    # Direct interest match (0-60)
    if any(k in text for k in ['patent analysis', 'patent analytics', 'patent mining', 'patent text mining', 'patent information']):
        score += 60
        reasons.append('专利分析直接对口')
    elif 'competitive intelligence' in text or 'business intelligence' in text:
        score += 55
        reasons.append('竞争情报直接对口')
    elif 'bibliometric' in text or 'scientometric' in text or 'science of science' in text:
        score += 55
        reasons.append('文献计量/科学计量对口')
    elif 'knowledge management' in text:
        score += 45
        reasons.append('知识管理对口')
    elif 'innovation management' in text or 'technology management' in text:
        score += 45
        reasons.append('创新/技术管理对口')
    elif 'information science' in text or 'library and information' in text:
        score += 40
        reasons.append('信息科学对口')
    elif 'data science' in text or 'machine learning' in text or 'nlp' in text or 'natural language processing' in text or 'text mining' in text:
        score += 30
        reasons.append('数据科学/ML/NLP相关')
    else:
        score += 5
        reasons.append('弱相关')

    # Institution quality (0-20)
    top_institutions = ['fraunhofer', 'kit', 'tum', 'rwth', 'gesis', 'leibniz', 'max planck', 'helmholtz',
                        'goettingen', 'potsdam', 'hasso plattner', 'tu munich', 'karlsruhe', 'aachen', 'berlin', 'munich',
                        'university of bonn', 'university of cologne', 'university of heidelberg']
    if any(k in company for k in top_institutions):
        score += 20
        reasons.append('顶级研究机构')
    elif 'university' in company:
        score += 12
        reasons.append('大学岗位')
    elif 'research' in company or 'forschung' in company:
        score += 8
        reasons.append('研究机构')

    # Skills alignment (0-15) - more precise
    if 'python' in text or 'programming' in text:
        score += 8
        reasons.append('Python/编程相关')
    # R language - require exact pattern to avoid matching "research"
    if re.search(r'\br\b', title + ' ' + desc) or ' r语言' in text or 'sprache r' in text:
        score += 3
        reasons.append('R语言相关')
    if 'text mining' in text or 'data mining' in text:
        score += 8
        reasons.append('文本/数据挖掘')
    if 'machine learning' in text:
        score += 5
        reasons.append('机器学习')
    if 'sql' in text or 'database' in text:
        score += 3
        reasons.append('数据库经验')

    # Location (0-5)
    loc = job.get('location', '').lower()
    if 'germany' in loc or 'deutschland' in loc:
        score += 5
        reasons.append('德国岗位')
    elif any(k in loc for k in ['denmark', 'norway', 'sweden', 'netherlands', 'switzerland']):
        score += 3
        reasons.append('欧洲备选国')

    # Funding clarity
    if any(k in text for k in ['funded', 'salary', 'tv-l', 'e13', 'stipend', 'grant']) or is_phd_position(title):
        score += 3
        reasons.append('资金/薪资较明确')

    return max(0, min(100, score)), reasons

# ---------------- Main ----------------

if __name__ == '__main__':
    all_jobs = []

    print('Scanning EURAXESS...')
    for kw in KEYWORDS:
        print(f"  keyword: {kw}")
        html_text, url = fetch_euraxess(kw)
        if html_text:
            jobs = parse_euraxess(html_text, url, kw)
            print(f"    -> {len(jobs)} jobs")
            all_jobs.extend(jobs)
        time.sleep(1.5)

    print('Scanning academics.de...')
    for kw in KEYWORDS:
        print(f"  keyword: {kw}")
        html_text, url = fetch_academics(kw)
        if html_text:
            jobs = parse_academics(html_text, url, kw)
            print(f"    -> {len(jobs)} jobs")
            all_jobs.extend(jobs)
        time.sleep(1.5)

    # Deduplicate by title+company (case-insensitive)
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        key = (j['title'].lower().strip(), j['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)

    print(f"\nTotal unique jobs: {len(unique_jobs)}")

    # Score and sort
    for j in unique_jobs:
        s, r = score_job(j)
        j['score'] = s
        j['reasons'] = r
    unique_jobs.sort(key=lambda x: x['score'], reverse=True)

    # Generate report
    today = datetime.now().strftime('%Y-%m-%d')
    report_path = f'Germany_PhD_Scan_Report_{today}.md'

    high = [j for j in unique_jobs if j['score'] >= 60]
    medium = [j for j in unique_jobs if 40 <= j['score'] < 60]
    low = [j for j in unique_jobs if 25 <= j['score'] < 40]

    report = f"""# 德国博士岗位扫描报告 - {today}

> 📅 扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 🔍 来源：EURAXESS + academics.de
> 🎯 关键词：{', '.join(KEYWORDS[:5])}...
> 🎓 目标：德国岗位制博士（信息科学/专利分析/竞争情报方向）

---

## 📊 本轮概览

| 指标 | 数值 |
|------|------|
| 扫描关键词数 | {len(KEYWORDS)} |
| 来源平台 | EURAXESS, academics.de |
| 去重岗位总数 | {len(unique_jobs)} |
| 🏆最佳匹配 | {high[0]['title'] if high else (unique_jobs[0]['title'] if unique_jobs else '无')} ({high[0]['company'] if high else (unique_jobs[0]['company'] if unique_jobs else '-')}) {high[0]['score'] if high else (unique_jobs[0]['score'] if unique_jobs else '-')}分 |
| 高匹配(60+) | {len(high)} |
| 中匹配(40-59) | {len(medium)} |
| 低匹配(25-39) | {len(low)} |

---

## 🏆 高匹配岗位 (60+分) — 强烈建议查看

"""

    for idx, j in enumerate(high, 1):
        report += f"""### {idx}. {'⭐' if idx == 1 else ''} {j['title']}
| 字段 | 详情 |
|------|------|
| **匹配度** | **{j['score']}分** {'🔥' if idx == 1 else ''} |
| **机构** | {j['company']} |
| **地点** | {j['location']} |
| **研究领域** | {j['research_field'] if j['research_field'] else '未标注'} |
| **来源** | {j['source']} |
| **截止日期** | {j['deadline'] if j['deadline'] else '未公布'} |
| **发布日期** | {j['posted_date'] if j['posted_date'] else '未公布'} |
| **资金** | {j['funding'] if j['funding'] else '未标注'} |
| **匹配分析** | {'；'.join(j['reasons'][:5])} |
| **链接** | {j['url']} |

**职位简介：** {j['description'][:300] if j['description'] else '无'}

"""

    report += """---

## 🟡 中匹配岗位 (40-59分) — 值得一看

| # | 职位 | 机构 | 地点 | 来源 | 匹配度 | 核心匹配点 |
|---|------|------|------|------|--------|-----------|
"""
    for idx, j in enumerate(medium, start=len(high)+1):
        report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {j['source']} | {j['score']} | {'；'.join(j['reasons'][:3])} |\n"

    report += """
---

## 🔵 低匹配岗位 (25-39分) — 可快速浏览

| # | 职位 | 机构 | 地点 | 来源 | 匹配度 | 原因 |
|---|------|------|------|------|--------|------|
"""
    for idx, j in enumerate(low, start=len(high)+len(medium)+1):
        report += f"| {idx} | {j['title']} | {j['company']} | {j['location']} | {j['source']} | {j['score']} | {'；'.join(j['reasons'][:2])} |\n"

    report += f"""
---

## 🎯 下一步行动建议

### 立即做
1. **查看高匹配岗位**：点击链接，确认申请截止日期和具体要求
2. **准备陶瓷信模板**：针对专利分析/竞争情报方向，写一封通用陶瓷信
3. **准备学术三件套**：CV + Research Statement + Writing Sample（论文草稿）

### 短期（1-2个月）
4. **锁定3-5个目标教授**：Fraunhofer ISI、KIT、GESIS、TUM、RWTH
5. **发送第一封陶瓷信**：附上硕士成绩单、论文草稿、KOS网站链接
6. **德语学习启动**：A1起步，博士期间需达到B1（永居要求）

### 中期（到2028年硕士毕业）
7. **发表至少1篇CSSCI/SSCI论文** — 这是申请德国博士的硬通货
8. **完善KOS学术网站**：展示研究成果、项目代码、学术身份
9. **GitHub项目整理**：潜油电缆数据项目、专利文本挖掘代码

---

## 💡 德国博士申请关键要点

| 项目 | 说明 |
|------|------|
| 学位要求 | 必须硕士毕业（2028年） |
| 资金 | 岗位制博士带薪（TV-L E13，约€3,500-4,500/月） |
| 语言 | 博士可用英语；永居需德语B1 |
| 签证 | §18d博士签证，毕业后18个月找工作签 |
| 永居 | 博士3-4年 + 工作4年 ≈ 7-8年 |
| 关键材料 | 研究计划 + 硕士论文 + 推荐信 + 发表记录 |

---

*报告由德国博士岗位扫描脚本自动生成 | 数据来源：EURAXESS, academics.de*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved: {report_path}")
