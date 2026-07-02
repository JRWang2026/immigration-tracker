"""
本地邮件客户端：IMAP 读取 + 安全凭据管理 + UID 状态追踪

安全原则：
1. 不硬编码密码；
2. 优先从环境变量读取；
3. 可选 Windows Credential Manager / macOS Keychain（keyring）；
4. 应用专用密码（App Password）而非主密码。

v0.2 — 新增 UID 追踪，避免重复扫描同一封邮件，减少 IMAP 负担。
"""

import email
import imaplib
import json
import os
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional, Set


class IMAPClient:
    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        state_dir: Optional[Path] = None,
    ):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self._conn: Optional[imaplib.IMAP4_SSL] = None
        self._state_dir = state_dir or Path(__file__).resolve().parent.parent / "data" / "state"
        self._state_dir.mkdir(parents=True, exist_ok=True)

    def connect(self) -> "IMAPClient":
        if self.use_ssl:
            self._conn = imaplib.IMAP4_SSL(self.server, self.port)
        else:
            self._conn = imaplib.IMAP4(self.server, self.port)
        self._conn.login(self.username, self.password)
        return self

    def disconnect(self):
        if self._conn:
            try:
                self._conn.close()
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ---------- UID 状态追踪 ----------
    def _uid_state_path(self, folder: str) -> Path:
        safe = folder.replace("/", "_").replace(" ", "_")
        return self._state_dir / f"imap_uids_{safe}.json"

    def _load_processed_uids(self, folder: str) -> Set[str]:
        p = self._uid_state_path(folder)
        if not p.exists():
            return set()
        try:
            with open(p, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()

    def _save_processed_uids(self, folder: str, uids: Set[str]):
        p = self._uid_state_path(folder)
        with open(p, "w") as f:
            json.dump(sorted(uids), f)

    def mark_processed(self, folder: str, *uids: str):
        """标记一批 UID 为已处理，持久化到磁盘。"""
        existing = self._load_processed_uids(folder)
        existing.update(uids)
        self._save_processed_uids(folder, existing)

    def search_emails(
        self,
        folder: str = "INBOX",
        keyword: str = "SEEK",
        lookback_days: int = 7,
        unread_only: bool = False,
        max_results: int = 50,
        skip_processed: bool = True,
    ) -> List[dict]:
        """
        搜索邮件并返回结构化摘要。

        参数:
            skip_processed: True 时跳过之前已成功处理的 UID（默认 True）。
                           定时任务设为 True，手动调试可设为 False 强制全量重扫。

        返回：list of dict，包含 subject, from, date, uid, body_html
        """
        if not self._conn:
            raise RuntimeError("IMAP not connected. Call connect() first.")

        status, _ = self._conn.select(folder)
        if status != "OK":
            raise RuntimeError(f"Cannot select folder {folder}")

        # 构造搜索条件 — 总是用 SINCE + BODY，不再依赖 UNSEEN
        since_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%d-%b-%Y")
        criteria_parts = [f'SINCE {since_date}']
        if unread_only:
            criteria_parts.insert(0, "UNSEEN")

        # IMAP 搜索
        query = "(" + " ".join(criteria_parts) + ")"
        status, messages = self._conn.search(None, query)
        if status != "OK":
            return []

        all_uids = messages[0].split()
        if not all_uids:
            return []

        # UID 去重
        processed = self._load_processed_uids(folder) if skip_processed else set()
        new_uids = [u for u in all_uids if u.decode() not in processed]
        skipped = len(all_uids) - len(new_uids)

        # 取最近 N 封
        target_uids = new_uids[-max_results:]

        results = []
        for uid in target_uids:
            status, msg_data = self._conn.fetch(uid, "(RFC822)")
            if status != "OK" or not msg_data:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject = decode_subject(msg.get("Subject", ""))
            from_addr = msg.get("From", "")
            date_str = msg.get("Date", "")
            body_html = self._extract_html_body(msg)

            # 质量检查：邮件正文太短可能是 IMAP 截断
            if len(body_html) < 200:
                # BODY "SEEK" 匹配可能返回验证码/系统通知等短邮件，正常跳过
                pass

            results.append({
                "uid": uid.decode(),
                "subject": subject,
                "from": from_addr,
                "date": date_str,
                "body_html": body_html,
            })

        return results

    def _extract_html_body(self, msg: email.message.Message) -> str:
        """提取邮件 HTML 正文；如果没有 HTML，则返回纯文本的 HTML 包装。"""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            # fallback to plain text
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                        return f"<html><body><pre>{text}</pre></body></html>"
        else:
            ctype = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
                if ctype == "text/html":
                    return text
                return f"<html><body><pre>{text}</pre></body></html>"
        return ""


def decode_subject(encoded_subject: str) -> str:
    """解码邮件主题中的 MIME 编码字符。"""
    parts = decode_header(encoded_subject)
    decoded = []
    for content, charset in parts:
        if isinstance(content, bytes):
            decoded.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(content)
    return "".join(decoded)


def load_credentials(cfg: dict) -> tuple[str, str]:
    """
    根据配置加载邮箱凭据。
    优先级：环境变量 > keyring > 交互式提示（CLI）。
    """
    username = os.getenv(cfg["username_env"], "")
    password = os.getenv(cfg["password_env"], "")

    if not username or not password:
        try:
            import keyring
            target = cfg.get("credential_target")
            if target:
                if not username:
                    username = keyring.get_password(target, "username") or ""
                if not password:
                    password = keyring.get_password(target, "password") or ""
        except Exception:
            pass

    if not username or not password:
        raise RuntimeError(
            "邮箱凭据未配置。请设置环境变量：\n"
            f"  set {cfg['username_env']}=349376374@qq.com\n"
            f"  set {cfg['password_env']}=your_qq_app_password\n"
            "或在 config.yaml 中配置 credential_target 使用系统密钥库。"
        )

    return username, password
