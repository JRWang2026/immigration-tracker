#!/usr/bin/env python3
"""
GitHub 自动推送模块（API 版）

绕过中国大陆对 github.com:443 的直连阻断，通过 api.github.com 逐个推送文件变更，
触发 GitHub Actions 重新部署 KOS。

用法：
    from git_pusher import push_to_github
    push_to_github(
        repo_root=Path(".."),
        token=os.environ.get("GITHUB_TOKEN"),
        owner="JRWang2026",
        repo="immigration-tracker",
        commit_message="Auto: SEEK NZ scan 2026-07-01"
    )

命令行：
    set GITHUB_TOKEN=ghp_xxx
    python git_pusher.py
"""

from __future__ import annotations

import base64
import json
import logging
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("seek_email_agent")

DEFAULT_OWNER = "JRWang2026"
DEFAULT_REPO = "immigration-tracker"
DEFAULT_BRANCH = "main"
MAX_FILE_SIZE = 1024 * 1024  # GitHub Contents API 限制 1MB


def _find_git_exe() -> Optional[str]:
    """查找 git.exe 可执行文件的完整路径。

    WorkBuddy 的 Python 环境不继承 shell 的 PATH，需要手动定位。
    """
    # 1. shutil.which（覆盖标准 PATH）
    found = shutil.which("git")
    if found:
        return found
    # 2. WorkBuddy 内置 PortableGit
    portable = Path.home() / ".workbuddy" / "vendor" / "PortableGit" / "mingw64" / "bin" / "git.exe"
    if portable.exists():
        return str(portable)
    # 3. 常见安装路径
    for p in (
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ):
        if Path(p).exists():
            return p
    return None


_GIT_EXE = _find_git_exe()


class GitHubAPIError(Exception):
    """GitHub API 返回非 2xx 状态码。"""

    def __init__(self, status: int, body: str, url: str):
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"GitHub API {status} for {url}: {body[:200]}")


def _api_request(
    method: str,
    url: str,
    token: str,
    data: Optional[dict] = None,
) -> dict:
    """发送 GitHub API 请求并返回 JSON 响应。"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "WangPrivateAgent/0.2",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    if body:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        raise GitHubAPIError(e.code, raw, url) from e


def _content_url(owner: str, repo: str, path: str, branch: str = DEFAULT_BRANCH) -> str:
    """构建 Contents API URL，正确处理中文路径。"""
    encoded_path = urllib.parse.quote(path, safe="/")
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref={branch}"


def _ensure_git_repo(repo_root: Path) -> bool:
    if not (repo_root / ".git").exists():
        logger.warning("GitHub 自动推送：%s 不是 git 仓库，跳过推送。", repo_root)
        return False
    return True


def _get_status(repo_root: Path) -> list[tuple[str, str]]:
    """
    获取 git 变更列表。

    返回 [(status_code, path), ...]，status_code 遵循 `git status --porcelain` 格式。
    """
    if not _GIT_EXE:
        logger.error("未找到 git.exe，无法获取变更列表。")
        return []
    result = subprocess.run(
        [_GIT_EXE, "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    changes: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path_str = line[3:].strip()
        # 重命名格式 "R  old -> new"，取新路径
        if " -> " in path_str:
            path_str = path_str.split(" -> ", 1)[1]
        changes.append((status, path_str))
    return changes


def _get_remote_sha(owner: str, repo: str, path: str, token: str, branch: str) -> Optional[str]:
    """获取远端文件 sha，不存在则返回 None。"""
    url = _content_url(owner, repo, path, branch)
    try:
        data = _api_request("GET", url, token)
        # 如果是文件，返回 sha；如果是目录，返回列表，取第一个可能不是我们想要的
        if isinstance(data, dict) and "sha" in data:
            return data["sha"]
    except GitHubAPIError as e:
        if e.status == 404:
            return None
        logger.warning("获取远端 sha 失败 %s: %s", path, e)
    return None


def _push_file(
    repo_root: Path,
    owner: str,
    repo: str,
    rel_path: str,
    token: str,
    message: str,
    branch: str,
) -> bool:
    """推送单个新增/修改文件到 GitHub。"""
    local_file = repo_root / rel_path
    if not local_file.exists():
        logger.warning("本地文件不存在，跳过：%s", rel_path)
        return False

    size = local_file.stat().st_size
    if size > MAX_FILE_SIZE:
        logger.warning("文件超过 1MB，跳过：%s (%s bytes)", rel_path, size)
        return False

    content = local_file.read_bytes()
    encoded = base64.b64encode(content).decode("ascii")
    sha = _get_remote_sha(owner, repo, rel_path, token, branch)

    payload: dict = {
        "message": message,
        "content": encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    try:
        _api_request("PUT", _content_url(owner, repo, rel_path, branch), token, payload)
        logger.info("已推送：%s", rel_path)
        return True
    except GitHubAPIError as e:
        logger.error("推送失败 %s: %s", rel_path, e)
        return False


def _delete_file(
    owner: str,
    repo: str,
    rel_path: str,
    token: str,
    message: str,
    branch: str,
) -> bool:
    """从 GitHub 删除单个文件。"""
    sha = _get_remote_sha(owner, repo, rel_path, token, branch)
    if not sha:
        logger.info("远端不存在，无需删除：%s", rel_path)
        return True

    payload = {
        "message": message,
        "sha": sha,
        "branch": branch,
    }
    try:
        _api_request("DELETE", _content_url(owner, repo, rel_path, branch), token, payload)
        logger.info("已删除：%s", rel_path)
        return True
    except GitHubAPIError as e:
        logger.error("删除失败 %s: %s", rel_path, e)
        return False


def push_to_github(
    repo_root: Path,
    token: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    branch: str = DEFAULT_BRANCH,
    commit_message: Optional[str] = None,
    files_to_add: Optional[list[str]] = None,
) -> bool:
    """
    自动将本地变更推送到 GitHub。

    参数:
        repo_root: git 仓库根目录
        token: GitHub Personal Access Token（默认从 GITHUB_TOKEN 环境变量读取）
        owner/repo: GitHub 仓库归属
        branch: 目标分支
        commit_message: 提交信息（默认自动生成）
        files_to_add: 显式指定要推送的文件列表（相对 repo_root），None 则按 git status 自动推送

    返回 True 表示至少成功推送了一个文件（或无需推送）。
    """
    if not _ensure_git_repo(repo_root):
        return False

    if not token:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if not token:
        logger.warning(
            "GitHub 自动推送：未提供 GITHUB_TOKEN，跳过推送。"
            "如需自动闭环，请在环境变量中设置 GITHUB_TOKEN=ghp_xxx。"
        )
        return False

    # 配置本地 git 用户信息（仅用于本地状态跟踪，不用于远程 push）
    if _GIT_EXE:
        for key, value in [("user.email", "WJR2026@hotmail.com"), ("user.name", "Wang Private Agent")]:
            result = subprocess.run([_GIT_EXE, "config", key], cwd=repo_root, capture_output=True, text=True, check=False)
            if not result.stdout.strip():
                subprocess.run([_GIT_EXE, "config", key, value], cwd=repo_root, check=False)
    else:
        logger.warning("未找到 git.exe，跳过本地 git config。")

    message = commit_message or f"Auto: agent update {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    if files_to_add:
        target_files = [("A ", p) for p in files_to_add]
    else:
        target_files = _get_status(repo_root)
        if not target_files:
            logger.info("GitHub 自动推送：没有变更，无需推送。")
            return True

    # 过滤路径：只推送常规文件，不推送 .git/、node_modules/、大文件等
    allowed = []
    for status, rel_path in target_files:
        p = repo_root / rel_path
        if rel_path.startswith(".") or "/." in rel_path or rel_path.startswith("node_modules/"):
            continue
        if p.is_dir():
            continue
        if p.is_file() and p.stat().st_size > MAX_FILE_SIZE:
            logger.warning("文件过大，跳过：%s", rel_path)
            continue
        allowed.append((status, rel_path))

    if not allowed:
        logger.info("GitHub 自动推送：没有允许推送的变更。")
        return True

    # 分批推送：先新增/修改，再删除
    pushed = 0
    for status, rel_path in allowed:
        # git status 第一位是索引状态，第二位是工作区状态
        idx = status[0]
        work = status[1]

        if idx in ("A", "M") or work in ("A", "M") or status == "??":
            if _push_file(repo_root, owner, repo, rel_path, token, message, branch):
                pushed += 1
        elif idx == "D" or work == "D":
            if _delete_file(owner, repo, rel_path, token, message, branch):
                pushed += 1
        else:
            logger.debug("忽略状态 %s 的文件：%s", status, rel_path)

    logger.info("GitHub 自动推送完成：%s/%s 个文件成功", pushed, len(allowed))
    return pushed > 0 or not allowed


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    repo_root = Path(__file__).resolve().parent.parent
    push_to_github(repo_root=repo_root)


if __name__ == "__main__":
    main()
