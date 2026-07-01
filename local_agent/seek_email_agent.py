#!/usr/bin/env python3
"""
本地私人 Agent — SEEK NZ 绿名单岗位扫描器

功能：
1. 通过 IMAP 从 QQ Mail 拉取 SEEK 推送邮件；
2. 解析岗位信息；
3. 按新西兰绿名单 Tier1 ICT 严格评分；
4. 生成 Markdown 报告 + JSON 数据；
5. 输出到 KOS 数据目录，供学术网站展示。

用法：
    set QQ_MAIL_USER=349376374@qq.com
    set QQ_MAIL_APP_PASSWORD=your_app_password
    python seek_email_agent.py
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

from email_client import IMAPClient, load_credentials
from git_pusher import push_to_github
from green_list_scorer import get_anzsco, immigration_path, score_job, suggest_skills
from kos_bridge import write_kos_feed
from seek_parser import deduplicate_jobs, extract_jobs_from_html


# ---------------------------------------------------------------------------
# 配置与日志
# ---------------------------------------------------------------------------
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(cfg: dict) -> logging.Logger:
    log_cfg = cfg.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
    log_file = log_cfg.get("file", "../local_agent_output/logs/agent.log")
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("seek_email_agent")
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def ensure_dirs(cfg: dict):
    for key in ("base_dir", "reports_dir", "data_dir", "kos_data_dir", "logs_dir"):
        path = Path(cfg["output"][key])
        path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------
def generate_markdown_report(
    jobs: list,
    email_count: int,
    run_time: datetime,
    score_threshold: int,
) -> str:
    date_str = run_time.strftime("%Y-%m-%d")
    total = len(jobs)
    tier1 = [j for j in jobs if j["score"] >= 60]
    research = [j for j in jobs if 40 <= j["score"] < 60]
    others = [j for j in jobs if j["score"] < 40]

    lines = [
        f"# SEEK NZ 绿名单 Tier1 ICT 扫描报告 — {date_str}",
        "",
        f"> 运行时间：{run_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 扫描邮件：{email_count} 封 | 去重岗位：{total} 个 | 绿名单 Tier1 匹配：{len(tier1)} 个",
        "",
        "---",
        "",
        "## 一、绿名单 Tier1 ICT 高匹配岗位（≥60分）",
        "",
    ]

    if tier1:
        lines.append("| 匹配度 | 职位 | 公司 | 地点 | 薪资 | ANZSCO | 移民路径 | 需补充技能 |")
        lines.append("|--------|------|------|------|------|--------|----------|------------|")
        for j in tier1:
            code, name = get_anzsco(j["title"])
            anzsco = f"{code} {name}" if code else "-"
            lines.append(
                f"| **{j['score']}** | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {anzsco} | {immigration_path(j)} | {suggest_skills(j)} |"
            )
    else:
        lines.append("*今日无绿名单 Tier1 ICT 高匹配岗位。*")

    lines.extend(["", "---", "", "## 二、大学/研究机构岗位（40-59分）", ""])
    if research:
        lines.append("| 匹配度 | 职位 | 公司 | 地点 | 薪资 | 移民路径 | 需补充技能 |")
        lines.append("|--------|------|------|------|------|----------|------------|")
        for j in research:
            lines.append(
                f"| {j['score']} | [{j['title']}]({j['url']}) | {j['company']} | {j['location']} | {j['salary']} | {immigration_path(j)} | {suggest_skills(j)} |"
            )
    else:
        lines.append("*今日无大学/研究机构岗位。*")

    lines.extend(["", "---", "", "## 三、已过滤/降级岗位（<40分）", ""])
    if others:
        lines.append("| 匹配度 | 职位 | 公司 | 分类 | 原因 |")
        lines.append("|--------|------|------|------|------|")
        for j in others:
            reason = j["reasons"][0] if j["reasons"] else "非目标岗位"
            lines.append(f"| {j['score']} | {j['title']} | {j['company']} | {reason} | {', '.join(j['reasons'][:2])} |")
    else:
        lines.append("*无。*")

    lines.extend([
        "",
        "---",
        "",
        "## 四、操作摘要",
        "",
        f"- 评分阈值：{score_threshold}",
        f"- 高匹配（≥60）：{len(tier1)}",
        f"- 中匹配（40-59）：{len(research)}",
        f"- 低匹配/忽略（<40）：{len(others)}",
        "",
        "**下一步建议**：",
        "1. 对 Tier1 岗位，先上 INZ 官网查雇主是否在 [Accredited Employer List](https://www.immigration.govt.nz/employ-migrants/accreditation-and-job-checks/accredited-employers-list)。",
        "2. 准备英文简历 + Cover Letter + GitHub 作品集。",
        "3. 主线仍是德国岗位制博士；NZ 只作为副线机会。",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    cfg = load_config()
    logger = setup_logging(cfg)
    ensure_dirs(cfg)

    logger.info("=== SEEK NZ 本地 Agent 启动 ===")

    email_cfg = cfg["email"]
    seek_cfg = cfg["seek"]
    out_cfg = cfg["output"]
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    try:
        username, password = load_credentials(email_cfg)
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    client = IMAPClient(
        server=email_cfg["imap_server"],
        port=email_cfg["imap_port"],
        username=username,
        password=password,
        use_ssl=email_cfg.get("imap_ssl", True),
    )

    all_raw_jobs = []
    emails = []

    try:
        with client:
            logger.info(f"连接 IMAP {email_cfg['imap_server']}:{email_cfg['imap_port']} ...")
            emails = client.search_emails(
                folder=seek_cfg["search_folder"],
                keyword=seek_cfg["search_keyword"],
                lookback_days=seek_cfg["lookback_days"],
                unread_only=seek_cfg.get("unread_only", False),
                max_results=seek_cfg.get("max_emails", 50),
            )
            logger.info(f"获取 {len(emails)} 封 SEEK 邮件")

            for em in emails:
                jobs = extract_jobs_from_html(em["body_html"])
                logger.info(f"邮件 '{em['subject'][:60]}...' 提取 {len(jobs)} 个岗位")
                all_raw_jobs.extend(jobs)
    except Exception as e:
        logger.exception("IMAP 处理失败")
        sys.exit(1)

    unique_jobs = deduplicate_jobs(all_raw_jobs)
    logger.info(f"去重后岗位：{len(unique_jobs)}")

    # 评分
    for j in unique_jobs:
        score, reasons = score_job(j)
        j["score"] = score
        j["reasons"] = reasons
        j["immigration_path"] = immigration_path(j)
        j["suggested_skills"] = suggest_skills(j)
        code, name = get_anzsco(j["title"])
        j["anzsco_code"] = code
        j["anzsco_name"] = name

    unique_jobs.sort(key=lambda x: x["score"], reverse=True)

    # 保存 JSON
    data_dir = Path(out_cfg["data_dir"])
    json_path = data_dir / f"seek_nz_{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "email_count": len(emails),
            "total_jobs": len(unique_jobs),
            "jobs": unique_jobs,
        }, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON 数据已保存：{json_path}")

    # 保存 Markdown 报告
    reports_dir = Path(out_cfg["reports_dir"])
    md_path = reports_dir / f"SEEK_NZ_Job_Report_{date_str}.md"
    report = generate_markdown_report(
        unique_jobs, len(emails), now, seek_cfg.get("score_threshold", 35)
    )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Markdown 报告已保存：{md_path}")

    # KOS 桥接
    if cfg.get("kos", {}).get("enabled", False):
        kos_path = write_kos_feed(
            Path(out_cfg["kos_data_dir"]),
            section_id="seek-nz",
            data={
                "date": date_str,
                "email_count": len(emails),
                "total_jobs": len(unique_jobs),
                "tier1_jobs": [j for j in unique_jobs if j["score"] >= 60],
                "all_jobs": unique_jobs,
            },
        )
        logger.info(f"KOS 数据已同步：{kos_path}")

        # 同时复制到 KOS public/data，确保本地开发和 GitHub Actions 都能读到最新数据
        repo_root = Path(__file__).resolve().parent.parent
        kos_public_dir = repo_root / "kos" / "public" / "data" / "seek-nz"
        kos_public_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(kos_path, kos_public_dir / "latest.json")
        logger.info(f"KOS public 数据已同步：{kos_public_dir / 'latest.json'}")

    # 控制台摘要
    tier1_count = sum(1 for j in unique_jobs if j["score"] >= 60)
    print(f"\n✅ 完成：扫描 {len(emails)} 封邮件，{len(unique_jobs)} 个去重岗位，{tier1_count} 个 Tier1 匹配。")
    print(f"📄 报告：{md_path}")
    print(f"📊 JSON：{json_path}")

    # GitHub 自动闭环：commit + push，触发 GitHub Actions 重新部署 KOS
    gh_cfg = cfg.get("github", {})
    if gh_cfg.get("enabled", False) and gh_cfg.get("auto_push", False):
        repo_root = Path(__file__).resolve().parent.parent
        pushed = push_to_github(
            repo_root=repo_root,
            owner=gh_cfg.get("owner", "JRWang2026"),
            repo=gh_cfg.get("repo", "immigration-tracker"),
            commit_message=f"Auto: SEEK NZ scan {date_str} ({tier1_count} Tier1 matches)",
        )
        if pushed:
            print("🚀 已推送至 GitHub，GitHub Actions 将自动部署 KOS。")
        else:
            print("⚠️ GitHub 自动推送未执行（无 token 或无变更）。")


if __name__ == "__main__":
    main()
