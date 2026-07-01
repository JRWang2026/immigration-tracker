"""
SEEK 邮件 HTML 解析器：从 QQ Mail 拉取的 SEEK 推送邮件中提取岗位信息。

v0.2 — 修复 MSO 条件注释导致标题解析失败的问题。
SEEK 邮件用 MJML 模板，标题被 <!--[if mso | IE]>...<![endif]--> 包裹，
旧版正则 [^<]+ 在注释的 < 处断开，导致 0 匹配。
"""

import html
import re
from typing import List, Dict


def _strip_mso_comments(body: str) -> str:
    """移除 MJML/Outlook 条件注释，暴露纯文本内容。"""
    return re.sub(r'<!--\[if mso \| IE\]>.*?<!\[endif\]-->', '', body, flags=re.DOTALL)


def extract_jobs_from_html(body: str) -> List[Dict[str, str]]:
    """
    从单封 SEEK 邮件 HTML 中提取所有岗位卡片。
    返回字段：title, company, location, salary, posted_date, url, source
    """
    jobs = []

    # Step 1: 清除 MSO 条件注释
    cleaned = _strip_mso_comments(body)

    # Step 2: 按 <a style="display: block"> 分割岗位卡片
    card_pattern = '<a style="display: block"'
    cards = cleaned.split(card_pattern)

    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(
            r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card
        )
        loc_matches = re.findall(
            r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>',
            card,
        )
        salary_match = re.search(r'>\$[^<]+</div>', card)
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        url_match = re.search(r'href="([^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue

        # 地点：优先带逗号的完整地点
        location = "Unknown"
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm
                break
            elif lm and lm not in [title, company] and location == "Unknown":
                location = lm

        # 薪资：从 loc_matches 里找 $ 开头的，或从 salary_match 取
        salary = ""
        if salary_match:
            raw = salary_match.group(0)
            # 提取 $ 后面的内容
            m = re.search(r'\$[^<]+', raw)
            if m:
                salary = m.group(0).strip()
        else:
            # 从 loc_matches 里找薪资信息
            for lm in loc_matches:
                lm = lm.strip()
                if lm.startswith('$') or '$' in lm:
                    salary = lm
                    # 如果薪资被误当地点，修正
                    if location == salary:
                        location = "Unknown"
                    break

        # 如果 loc_matches 里第二个元素是薪资，清除它
        if salary and location == salary:
            # 重新找地点
            for lm in loc_matches:
                lm = lm.strip()
                if lm != salary and lm not in [title, company]:
                    location = lm
                    break

        posted_date = date_match.group(1) if date_match else ""
        url = url_match.group(1) if url_match else ""

        jobs.append({
            "title": html.unescape(title),
            "company": html.unescape(company),
            "location": html.unescape(location),
            "salary": html.unescape(salary),
            "posted_date": posted_date,
            "url": url,
            "source": "SEEK NZ email",
        })

    return jobs


def deduplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    """按 title + company 去重（不区分大小写）。"""
    seen = set()
    unique = []
    for j in jobs:
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique
