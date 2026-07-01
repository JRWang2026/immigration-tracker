# 全球技术移民政策自动化追踪器（Global Skilled Immigration Policy Tracker）

> **目标**：把“移民政策研究”从一次性搜索升级为**可写进 CV 的开源项目/数据成果**，并辅助德国/新西兰/荷兰等主副线的长期决策。

---

## 1. 为什么这是个 CV 级成果？

- **展示跨学科能力**：数据工程（Python/爬虫/ETL）+ 信息科学（政策文本采集、结构化、版本控制）+ 国际移民政策研究。
- **可量化、可展示**：GitHub 仓库 + 每日自动运行的 GitHub Actions + 静态 Dashboard + 月度趋势报告。
- **解决真实问题**：不仅服务你自己，也能帮助全球技术移民申请人，天然适合做社区传播。
- **可发表**：整理成数据集论文、信息科学/政策分析期刊（如 *Online Information Review*、*Data Science Journal*、*Journal of International Migration*）或 arXiv/preprint。
- **长期价值**：毕业后仍可继续维护，作为你的开源项目品牌。

---

## 2. 项目定位

**名称**：`Global Skilled Immigration Policy Tracker`（简称 `GSIPT`）

**口号**：*Automated monitoring of skilled immigration policy changes across OECD destinations.*

**核心功能**：
1. 定期抓取官方移民政策页面。
2. 提取关键指标（薪资门槛、年龄上限、职业清单、英语要求、处理时间）。
3. 检测政策变化，生成 diff 报告。
4. 输出结构化数据集（JSON/CSV）和可视化 Dashboard。
5. 对重大变化发送邮件/微信/Slack 提醒。

**与你主线的结合**：
- 德国：监控 EU Blue Card / §18d Research / Chancenkarte 薪资门槛、短缺职业清单、博士政策。
- 新西兰：监控 Green List Tier 1 ICT、中位数工资、年龄上限、英语要求。
- 荷兰：监控 KMV 高技能移民、30% ruling、薪资门槛。
- 瑞典/芬兰：监控 work permit / specialist permit 薪资门槛。
- 加拿大/澳大利亚：监控 EE CRS / 州担保 / 年龄惩罚，但只做“观察”不抱希望。

---

## 3. 2026 年基线数据（来自 Visa Atlas 等公开来源）

> **数据来源**：以政府官方页面为主，第三方研究为辅。本表中的第三方数据仅作为项目初始 seed，正式上线后应以官方源为准。

| 国家/地区 | 主要路径 | 薪资门槛（2026） | 年龄上限 | 关键变化 |
|----------|---------|------------------|----------|----------|
| **新西兰** | Straight to Residence (Green List Tier 1) | 中位数工资 NZD 33.56/小时，年薪约 NZD 69,805 | ≤55 | 2026 年中位数工资从 35.00 下调至 33.56；Tier 1 ICT 8 岗稳定 |
| **德国** | EU Blue Card 普通 | €50,700/年 | 无 | 2026 年上涨约 4.97% |
| **德国** | EU Blue Card 短缺/年轻/IT 无学位 | €45,934/年 | 无 | 2026 年上涨约 4.97%；STEM/IT 受益 |
| **德国** | 普通技术工签 §18a/§18b | 约 €55,770/年 | 无 | 2026 年上涨 |
| **荷兰** | Kennismigrant (KMV) 30 岁以下 | €4,357/月 | 无 | 2026 年 1 月生效 |
| **荷兰** | Kennismigrant (KMV) 30 岁及以上 | €5,942/月 | 无 | 2026 年 1 月生效 |
| **荷兰** | KMV 应届生/名校毕业生 | €3,122/月 | 无 | 2026 年 1 月生效 |
| **荷兰** | EU Blue Card | €5,942/月 | 无 | 与 KMV 30+ 同 |
| **瑞典** | 工作许可 | 34,470 SEK/月（约） | 无 | 2026 年 6 月 1 日起需 ≥90% 中位工资；之前 80% |
| **芬兰** | Specialist Permit | 约 €3,000+/月（具体需查官方） | 无 | 连续 A 类 4 年→永居，需芬兰语 YKI 4 级 |
| **澳大利亚** | SID Core Skills / 186 | AUD 79,423/年 | 45 | 2026-07-01 起收入门槛上涨 |
| **澳大利亚** | Specialist Skills Pathway | AUD 146,576/年 | 45 | 2026-07-01 起上涨 |
| **加拿大** | Express Entry | 无固定，CRS 邀请分 | 无硬上限但年龄惩罚重 | 2025 年起分类邀请（category-based draws） |
| **爱尔兰** | Critical Skills Employment Permit | €40,904/年 | 无 | 2026 年 3 月 1 日从 €38,000 上调 |
| **爱尔兰** | General Employment Permit | €36,605/年 | 无 | 2026 年 3 月 1 日生效 |
| **英国** | Skilled Worker | £41,700/年 | 无 | 2025 年 7 月从 £38,700 上调；部分职业/学历可降 |
| **英国** | Health & Care / Education / STEM PhD | £33,400/年 | 无 |  Immigration Salary List 折扣 |
| **新加坡** | Employment Pass（非金融） | SGD 5,600/月 | 无 | 2024 年起 COMPASS 评分 |
| **新加坡** | Employment Pass（金融） | SGD 6,200/月 | 无 | COMPASS 框架 |
| **丹麦** | Pay Limit Scheme | DKK 552,000/年 | 无 | 较高门槛 |
| **法国** | Passeport Talent — Salaried Qualified | €39,582/年 | 无 | 适用于高技能雇员 |
| **法国** | EU Blue Card | €59,373/年 | 无 | 高于德国普通 Blue Card |
| **西班牙** | Highly Qualified Professional / EU Blue Card | €41,356/年 | 无 | Startup Law 框架 |
| **美国** | H-1B Level 1 prevailing wage | 约 $62,000/年 | 无 | 抽签制，不稳定 |

---

## 4. 技术架构

### 4.1 数据流

```text
官方源 URLs → 爬虫/抓取器 → 原始 HTML 存储 → 文本提取 → 指标抽取 → 结构化数据 → 版本控制/数据库 → Diff 检测 → 报告/告警 → Dashboard
```

### 4.2 技术栈

| 层级 | 工具/库 | 说明 |
|------|---------|------|
| 语言 | Python 3.13 | 你已熟悉 |
| 爬虫 | requests, httpx, curl_cffi | 处理反爬 |
| HTML 解析 | BeautifulSoup4, lxml, trafilatura | 提取正文 |
| 结构化数据 | Pydantic, pandas | 校验与处理 |
| 变化检测 | git diff, hashlib, difflib | 识别政策变化 |
| 调度 | GitHub Actions / cron | 每日/每周自动跑 |
| 存储 | GitHub repo (JSON/CSV/YAML) | 天然版本化 |
| 数据库（可选） | SQLite / PostgreSQL | 复杂查询 |
| 可视化 | GitHub Pages + Chart.js / Streamlit | 静态或交互 |
| 报告 | Jinja2 + Markdown | 生成 Markdown 报告 |
| 提醒 | email, Slack webhook, 微信（可选） | 变化通知 |

### 4.3 数据模型（Pydantic 示例）

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal

class PolicyMetric(BaseModel):
    country: str                       # 国家/地区
    pathway: str                       # 签证路径
    metric: str                        # 指标名称
    value: float                       # 数值
    currency: Optional[str] = None     # 币种
    unit: Literal["annual", "monthly", "hourly"] = "annual"
    effective_date: date               # 生效日期
    source_url: str                    # 官方来源 URL
    last_checked: date                 # 上次检查日期
    notes: Optional[str] = None          # 备注
    change_status: Literal["stable", "increased", "decreased", "new", "removed"] = "stable"
```

### 4.4 项目目录结构

```text
global-skilled-immigration-policy-tracker/
├── README.md
├── LICENSE
├── requirements.txt
├── config/
│   └── sources.yaml                    # 所有官方源
├── data/
│   ├── raw/                            # 原始 HTML
│   ├── metrics/                        # 结构化指标 JSON/CSV
│   └── history/                        # 历史快照
├── src/
│   ├── fetcher.py                      # 抓取模块
│   ├── extractor.py                    # 文本/指标提取
│   ├── diff_engine.py                  # 变化检测
│   ├── reporter.py                     # 报告生成
│   └── notifier.py                     # 通知
├── reports/
│   └── 2026-07-01-policy-report.md
├── dashboard/
│   ├── index.html
│   └── app.js
├── .github/
│   └── workflows/
│       └── daily-scan.yml
└── tests/
    └── test_extractor.py
```

---

## 5. 初始数据源配置（config/sources.yaml）

```yaml
sources:
  - country: New Zealand
    pathway: Green List Straight to Residence
    priority: P0
    urls:
      - https://www.immigration.govt.nz/live/resident-visas-to-live-in-new-zealand/skilled-residence-pathways-in-new-zealand/green-list-pathway-to-residence/
      - https://www.immigration.govt.nz/visas/straight-to-residence-visa/
    metrics:
      - median_wage_hourly
      - age_limit
      - english_requirement
      - green_list_occupations

  - country: Germany
    pathway: EU Blue Card
    priority: P0
    urls:
      - https://www.make-it-in-germany.com/en/visa-residence/types/eu-blue-card
      - https://www.bamf.de/EN/Themen/Statistik/BlaueKarteEU/blauekarteeu-node.html
    metrics:
      - annual_salary_threshold_standard
      - annual_salary_threshold_shortage
      - shortage_occupations
      - age_limit

  - country: Germany
    pathway: Opportunity Card (Chancenkarte)
    priority: P0
    urls:
      - https://www.make-it-in-germany.com/en/visa-residence/types/opportunity-card
    metrics:
      - points_criteria
      - language_requirements
      - work_restrictions

  - country: Netherlands
    pathway: Highly Skilled Migrant
    priority: P1
    urls:
      - https://ind.nl/en/required-amounts-income-requirements
    metrics:
      - monthly_salary_under_30
      - monthly_salary_30_plus
      - monthly_salary_reduced_rate

  - country: Sweden
    pathway: Work Permit
    priority: P1
    urls:
      - https://www.migrationsverket.se/English/Private-individuals/Working-in-Sweden.html
    metrics:
      - median_salary_percentage
      - mandatory_health_insurance

  - country: Finland
    pathway: Specialist Permit
    priority: P1
    urls:
      - https://migri.fi/en/information-bank/specialists
    metrics:
      - minimum_salary
      - permanent_residence_years
      - language_requirement

  - country: Australia
    pathway: Skills in Demand (subclass 482) Core Skills
    priority: P2
    urls:
      - https://immi.homeaffairs.gov.au/visas/employing-and-sponsoring-someone/sponsoring-workers/nominating-a-position/salary-requirements
    metrics:
      - core_skills_income_threshold
      - specialist_skills_income_threshold
      - age_limit

  - country: Canada
    pathway: Express Entry
    priority: P2
    urls:
      - https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html
    metrics:
      - latest_crs_cutoff
      - category_based_draws

  - country: Ireland
    pathway: Critical Skills Employment Permit
    priority: P1
    urls:
      - https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/critical-skills-employment-permit/
    metrics:
      - annual_salary_threshold
      - eligible_occupations

  - country: United Kingdom
    pathway: Skilled Worker Visa
    priority: P2
    urls:
      - https://www.gov.uk/skilled-worker-visa
    metrics:
      - general_salary_threshold
      - immigration_salary_list_discount
      - english_requirement

  - country: Singapore
    pathway: Employment Pass
    priority: P2
    urls:
      - https://www.mom.gov.sg/passes-and-permits/employment-pass
    metrics:
      - monthly_salary_threshold
      - compass_framework_points
```

---

## 6. 启动脚本（src/fetcher.py）

```python
#!/usr/bin/env python3
"""Minimal policy tracker fetcher: checks all configured URLs and reports changes."""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "sources.yaml"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
HISTORY_DIR = DATA_DIR / "history"
REPORTS_DIR = ROOT / "reports"

RAW_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GSIPT-PolicyBot/1.0; +https://github.com/yourname/gsipt)"
}


def fetch(url: str) -> tuple[str, bool]:
    """Return (text, ok)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text, True
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {exc}", False


def extract_text(html: str) -> str:
    """Basic text extraction; can be replaced with trafilatura/readability."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def latest_snapshot(url: str) -> Path:
    return HISTORY_DIR / f"{url_hash(url)}.txt"


def check_changes(url: str, text: str) -> dict:
    snapshot = latest_snapshot(url)
    current_hash = hashlib.sha256(text.encode()).hexdigest()
    changed = True
    if snapshot.exists():
        old = snapshot.read_text(encoding="utf-8")
        changed = hashlib.sha256(old.encode()).hexdigest() != current_hash

    if changed:
        snapshot.write_text(text, encoding="utf-8")

    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "changed": changed,
        "hash": current_hash,
        "checked_at": datetime.utcnow().isoformat(),
        "ok": True,
    }


def run():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    results = []
    for source in config["sources"]:
        for url in source["urls"]:
            html, ok = fetch(url)
            if not ok:
                results.append({"url": url, "ok": False, "error": html})
                continue
            text = extract_text(html)
            RAW_DIR.joinpath(f"{url_hash(url)}.html").write_text(html, encoding="utf-8")
            result = check_changes(url, text)
            result["country"] = source["country"]
            result["pathway"] = source["pathway"]
            results.append(result)

    # Save run log
    run_log = DATA_DIR / f"run_{datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')}.json"
    run_log.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate simple markdown report
    changed = [r for r in results if r.get("changed")]
    report_path = REPORTS_DIR / f"report_{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    lines = [
        f"# Policy Tracker Report — {datetime.utcnow().strftime('%Y-%m-%d')}",
        "",
        f"- Total URLs checked: {len(results)}",
        f"- Changed: {len(changed)}",
        "",
        "## Changed Pages",
        "",
    ]
    for r in changed:
        lines.append(f"- **{r['country']} / {r['pathway']}**: [{r['domain']}]({r['url']})")
    lines.append("")
    lines.append("## All Results")
    lines.append("")
    lines.append("| Country | Pathway | URL | Changed | OK |")
    lines.append("|---------|---------|-----|---------|----|")
    for r in results:
        lines.append(
            f"| {r.get('country', '-')} | {r.get('pathway', '-')} | {r['url']} | "
            f"{r.get('changed', False)} | {r['ok']} |"
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    run()
```

---

## 7. 实施路线图（建议 8 周）

| 周 | 任务 | 产出 |
|----|------|------|
| 1 | 搭建仓库、写 README、配置 sources.yaml、跑通 fetcher.py | 3 国 P0 源可抓取 |
| 2 | 增加文本提取、指标结构化、CSV/JSON 输出 | 可生成 metrics.json |
| 3 | 加入 diff 与告警，生成 Markdown 报告 | 每日变化报告 |
| 4 | GitHub Actions 自动化、静态 Dashboard | 每日自动运行 + GitHub Pages |
| 5-6 | 扩展国家至 10+，增加 P1/P2 源 | 完整数据集 |
| 7 | 写一份方法论文档 / 数据说明 | docs/methodology.md |
| 8 | 包装 CV、发博客 / preprint | CV 更新、LinkedIn/GitHub 宣传 |

---

## 8. CV 写法建议

### 作为项目经验

> **Global Skilled Immigration Policy Tracker** — Maintainer & Lead Researcher  
> 2026 – Present · Open-source project (github.com/yourname/gsipt)
>
> - Built an automated Python-based policy intelligence system that monitors skilled immigration salary thresholds, age limits, and occupation lists across 10+ OECD countries.
> - Implemented daily data collection, web page change detection, structured data pipelines, and versioned datasets using GitHub Actions.
> - Produced monthly trend reports and a public dashboard used by international skilled workers and researchers.
> - Applied web scraping, data modeling, and reproducible research methods in Python, Pandas, and Pydantic.

### 作为研究技能

- **Policy Information Retrieval & Monitoring**: designed and maintained a large-scale policy tracking system.
- **Reproducible Data Engineering**: automated ETL pipelines with version control and CI/CD.
- **Comparative Policy Analysis**: produced cross-country analyses of skilled immigration pathways.

---

## 9. 可发表方向

| 类型 | 目标 | 说明 |
|------|------|------|
| 数据集论文 | *Data Science Journal* 或 *Scientific Data* | 发布结构化数据集、API、方法 |
| 信息科学方法论文 | *Online Information Review* | 政策文本采集、变化检测、知识组织 |
| 迁移/政策研究论文 | *Journal of International Migration* | 跨国技术移民门槛比较 |
| 预印本 | arXiv / SSRN / ResearchGate | 快速建立学术可见度 |
| 技术博客 | 个人学术网站 (KOS) / Medium / Dev.to | 吸引关注，增强个人品牌 |

---

## 10. 风险与注意事项

- **法律合规**：只抓官方/公开页面，遵守 robots.txt，不爬付费/敏感内容。
- **数据准确性**：项目产出必须标注“非法律建议”，重要决策前咨询移民律师。
- **反爬**：对官方政府站点保持友好频率（每日一次足够），避免被封。
- **维护成本**：P0 源必须优先维护，P2 源可降低频率。
- **政治敏感性**：只陈述政策事实，不做政治评论；涉及中国香港、中国台湾时，使用“中国香港”“中国台湾”或“Hong Kong, China / Taiwan, China”表述。

---

## 11. 下一步建议

1. **今晚**：在 GitHub 创建 `global-skilled-immigration-policy-tracker` 仓库。
2. **明天**：写 README + sources.yaml + 跑通 `fetcher.py`（至少 NZ、Germany、Netherlands）。
3. **本周内**：让 GitHub Actions 每日自动运行，dashboard 可用。
4. **两周内**：扩展到 10 国，产出第一份月度报告。
5. **一个月内**：把项目链接写进 CV、KOS 学术网站、GitHub profile。

---

**结论**：这不仅是“更好的政策追踪”，而是能让你在申博/求职中拿出**可验证、可访问、可引用**的成果。行动起来，比“想”更重要。
