#!/usr/bin/env python3
"""
GitHub 自动推送模块

把本地 Agent 生成的数据、报告自动 commit + push 到 GitHub，触发 GitHub Actions 重新部署 KOS。

用法：
    from git_pusher import push_to_github
    push_to_github(
        repo_root=Path(".."),
        token=os.environ.get("GITHUB_TOKEN"),
        commit_message="Auto: SEEK NZ scan 2026-07-01"
    )

或者命令行：
    set GITHUB_TOKEN=ghp_xxx
    python git_pusher.py
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("seek_email_agent")


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", *args]
    logger.debug("Run: %s (cwd=%s)", " ".join(cmd), cwd)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def ensure_git_repo(repo_root: Path) -> bool:
    if not (repo_root / ".git").exists():
        logger.warning("GitHub 自动推送：%s 不是 git 仓库，跳过推送。", repo_root)
        return False
    return True


def has_changes(repo_root: Path) -> bool:
    result = run_git(["status", "--porcelain"], cwd=repo_root, check=False)
    return bool(result.stdout.strip())


def configure_remote(repo_root: Path, owner: str, repo: str, token: str) -> None:
    """把 origin remote 配置成带 token 的 HTTPS URL，用于无交互 push。"""
    remote_url = f"https://{token}@github.com/{owner}/{repo}.git"
    run_git(["remote", "remove", "origin"], cwd=repo_root, check=False)
    run_git(["remote", "add", "origin", remote_url], cwd=repo_root)


def push_to_github(
    repo_root: Path,
    token: str | None = None,
    owner: str = "MrWang202606",
    repo: str = "immigration-tracker",
    commit_message: str | None = None,
    files_to_add: list[str] | None = None,
) -> bool:
    """
    自动提交并推送。返回 True 表示成功推送，False 表示跳过或失败。
    """
    if not ensure_git_repo(repo_root):
        return False

    if not token:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if not token:
        logger.warning(
            "GitHub 自动推送：未提供 GITHUB_TOKEN，跳过推送。"
            "如需自动闭环，请在环境变量中设置 GITHUB_TOKEN=ghp_xxx。"
        )
        return False

    try:
        # 配置 user（若未设置则使用默认值）
        for key, value in [("user.email", "WJR2026@hotmail.com"), ("user.name", "Wang Private Agent")]:
            result = run_git(["config", key], cwd=repo_root, check=False)
            if not result.stdout.strip():
                run_git(["config", key, value], cwd=repo_root)

        configure_remote(repo_root, owner, repo, token)

        # 拉取远端变更，避免冲突（rebase 模式）
        run_git(["pull", "origin", "main", "--rebase"], cwd=repo_root, check=False)

        # 添加指定文件或默认数据目录
        if files_to_add:
            for f in files_to_add:
                run_git(["add", f], cwd=repo_root)
        else:
            for d in ["data", "reports", "kos/public/data"]:
                p = repo_root / d
                if p.exists():
                    run_git(["add", d], cwd=repo_root, check=False)

        if not has_changes(repo_root):
            logger.info("GitHub 自动推送：没有变更，无需提交。")
            return True

        message = commit_message or f"Auto: agent update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        run_git(["commit", "-m", message], cwd=repo_root)
        run_git(["push", "origin", "main"], cwd=repo_root)

        logger.info("GitHub 自动推送成功：%s/%s @ main", owner, repo)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("GitHub 自动推送失败：%s\nSTDOUT: %s\nSTDERR: %s", e, e.stdout, e.stderr)
        return False


def main():
    logging.basicConfig(level=logging.INFO)
    repo_root = Path(__file__).resolve().parent.parent
    push_to_github(repo_root=repo_root)


if __name__ == "__main__":
    main()
