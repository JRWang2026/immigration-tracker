#!/usr/bin/env python3
"""
全球技术移民政策追踪器 MVP (Global Skilled Immigration Policy Tracker)

功能：
1. 抓取官方移民政策页面；
2. 计算正文哈希，检测内容变化；
3. 保存历史快照与原始 HTML；
4. 生成 Markdown 报告。

用法：
    python global_policy_tracker.py

依赖：
    pip install requests beautifulsoup4 lxml pyyaml
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
WORK_DIR = Path(__file__).resolve().parent
DATA_DIR = WORK_DIR / "policy_tracker_data"
RAW_DIR = DATA_DIR / "raw"
HISTORY_DIR = DATA_DIR / "history"
REPORTS_DIR = DATA_DIR / "reports"

for d in (RAW_DIR, HISTORY_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GlobalSkilledImmigrationPolicyTracker/1.0; "
        "+https://github.com/yourname/gsipt)"
    )
}

# 优先跟踪 P0 国家：新西兰、德国、荷兰。P1/P2 可按需扩展。
DEFAULT_SOURCES = [
    {
        "country": "New Zealand",
        "pathway": "Green List Straight to Residence",
        "priority": "P0",
        "urls": [
            "https://www.immigration.govt.nz/live/resident-visas-to-live-in-new-zealand/skilled-residence-pathways-in-new-zealand/green-list-pathway-to-residence/",
            "https://www.immigration.govt.nz/visas/straight-to-residence-visa/",
        ],
    },
    {
        "country": "Germany",
        "pathway": "EU Blue Card",
        "priority": "P0",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/eu-blue-card",
            "https://www.bamf.de/EN/Themen/Statistik/BlaueKarteEU/blauekarteeu-node.html",
        ],
    },
    {
        "country": "Germany",
        "pathway": "Opportunity Card (Chancenkarte)",
        "priority": "P0",
        "urls": [
            "https://www.make-it-in-germany.com/en/visa-residence/types/opportunity-card",
        ],
    },
    {
        "country": "Netherlands",
        "pathway": "Highly Skilled Migrant",
        "priority": "P1",
        "urls": [
            "https://ind.nl/en/required-amounts-income-requirements",
        ],
    },
    {
        "country": "Sweden",
        "pathway": "Work Permit",
        "priority": "P1",
        "urls": [
            "https://www.migrationsverket.se/English/Private-individuals/Working-in-Sweden.html",
        ],
    },
    {
        "country": "Finland",
        "pathway": "Specialist Permit",
        "priority": "P1",
        "urls": [
            "https://migri.fi/en/information-bank/specialists",
        ],
    },
    {
        "country": "Australia",
        "pathway": "Skills in Demand (subclass 482)",
        "priority": "P2",
        "urls": [
            "https://immi.homeaffairs.gov.au/visas/employing-and-sponsoring-someone/sponsoring-workers/nominating-a-position/salary-requirements",
        ],
    },
    {
        "country": "Canada",
        "pathway": "Express Entry",
        "priority": "P2",
        "urls": [
            "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html",
        ],
    },
    {
        "country": "Ireland",
        "pathway": "Critical Skills Employment Permit",
        "priority": "P1",
        "urls": [
            "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/permit-types/critical-skills-employment-permit/",
        ],
    },
    {
        "country": "United Kingdom",
        "pathway": "Skilled Worker Visa",
        "priority": "P2",
        "urls": [
            "https://www.gov.uk/skilled-worker-visa",
        ],
    },
    {
        "country": "Singapore",
        "pathway": "Employment Pass",
        "priority": "P2",
        "urls": [
            "https://www.mom.gov.sg/passes-and-permits/employment-pass",
        ],
    },
]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def load_sources() -> list[dict]:
    """加载外部配置 config/sources.yaml（如果存在），否则使用默认配置。"""
    config_path = WORK_DIR / "config" / "sources.yaml"
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return data.get("sources", DEFAULT_SOURCES)
    return DEFAULT_SOURCES


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def fetch(url: str) -> tuple[str, str | None]:
    """
    抓取 URL。
    返回 (html, error_or_none)。
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text, None
    except requests.RequestException as exc:
        return "", str(exc)


def extract_text(html: str) -> str:
    """从 HTML 提取正文文本（用于变化检测）。"""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def snapshot_path(url: str) -> Path:
    return HISTORY_DIR / f"{url_hash(url)}.txt"


def raw_path(url: str) -> Path:
    return RAW_DIR / f"{url_hash(url)}.html"


def check_change(url: str, text: str) -> bool:
    """检测内容是否变化。如果变化，保存新快照。"""
    path = snapshot_path(url)
    current_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if path.exists():
        old_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if old_hash == current_hash:
            return False
    path.write_text(text, encoding="utf-8")
    return True


def generate_report(results: list[dict]) -> Path:
    """生成 Markdown 报告。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changed = [r for r in results if r.get("changed")]
    errors = [r for r in results if not r.get("ok")]

    lines = [
        f"# 全球技术移民政策追踪报告 — {today}",
        "",
        f"**生成时间**: {now}",
        "",
        f"- 检查 URL 总数: {len(results)}",
        f"- 内容变化: {len(changed)}",
        f"- 抓取失败: {len(errors)}",
        "",
        "## 内容发生变化的页面",
        "",
    ]

    if changed:
        for r in changed:
            lines.append(
                f"- **{r['country']} / {r['pathway']}** — [{r['domain']}]({r['url']})"
            )
    else:
        lines.append("无变化。")

    lines.extend(["", "## 抓取失败", ""])
    if errors:
        for r in errors:
            lines.append(f"- {r['url']}: `{r.get('error', 'unknown')}`")
    else:
        lines.append("无失败。")

    lines.extend(["", "## 全部检查结果", "", "| 国家 | 路径 | 域名 | 状态 | 变化 |", "|------|------|------|------|------|"])
    for r in results:
        status = "✅ OK" if r["ok"] else "❌ FAIL"
        changed_mark = "🔄 是" if r.get("changed") else "—"
        lines.append(
            f"| {r['country']} | {r['pathway']} | {r['domain']} | {status} | {changed_mark} |"
        )

    lines.extend(["", "---", "", "_数据来源：各国官方移民局/劳工部公开页面。本报告仅供参考，不构成法律或移民建议。_"])

    report_path = REPORTS_DIR / f"report_{today}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def save_run_log(results: list[dict]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    log_path = DATA_DIR / f"run_{timestamp}.json"
    log_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return log_path


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    sources = load_sources()
    results: list[dict] = []

    for source in sources:
        country = source["country"]
        pathway = source["pathway"]
        for url in source["urls"]:
            print(f"[FETCH] {country} / {pathway}: {url}")
            html, error = fetch(url)
            if error:
                results.append(
                    {
                        "country": country,
                        "pathway": pathway,
                        "url": url,
                        "domain": urlparse(url).netloc,
                        "ok": False,
                        "changed": False,
                        "error": error,
                        "checked_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                continue

            raw_path(url).write_text(html, encoding="utf-8")
            text = extract_text(html)
            changed = check_change(url, text)
            results.append(
                {
                    "country": country,
                    "pathway": pathway,
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "ok": True,
                    "changed": changed,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            print(f"  -> {'CHANGED' if changed else 'stable'}")

    log_path = save_run_log(results)
    report_path = generate_report(results)

    print(f"\n[SAVED] 运行日志: {log_path}")
    print(f"[SAVED] 报告: {report_path}")
    print(f"[SUMMARY] 检查 {len(results)} 个 URL，发现 {sum(r.get('changed') for r in results)} 个变化，{sum(not r['ok'] for r in results)} 个失败。")


if __name__ == "__main__":
    main()
