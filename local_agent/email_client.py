"""
本地邮件客户端：IMAP 读取 + 安全凭据管理

安全原则：
1. 不硬编码密码；
2. 优先从环境变量读取；
3. 可选 Windows Credential Manager / macOS Keychain（keyring）；
4. 应用专用密码（App Password）而非主密码。
"""

import email
import imaplib
import os
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional


class IMAPClient:
    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
    ):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self._conn: Optional[imaplib.IMAP4_SSL] = None

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

    def search_emails(
        self,
        folder: str = "INBOX",
        keyword: str = "SEEK",
        lookback_days: int = 7,
        unread_only: bool = False,
        max_results: int = 50,
    ) -> List[dict]:
        """
        搜索邮件并返回结构化摘要。
        返回：list of dict，包含 subject, from, date, uid, body_html
        """
        if not self._conn:
            raise RuntimeError("IMAP not connected. Call connect() first.")

        status, _ = self._conn.select(folder)
        if status != "OK":
            raise RuntimeError(f"Cannot select folder {folder}")

        # 构造搜索条件
        since_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%d-%b-%Y")
        criteria_parts = [f'SINCE {since_date}', f'BODY "{keyword}"']
        if unread_only:
            criteria_parts.insert(0, "UNSEEN")

        # IMAP 搜索语法：("UNSEEN" "SINCE ..." "BODY \"SEEK\"")
        query = "(" + " ".join(criteria_parts) + ")"
        status, messages = self._conn.search(None, query)
        if status != "OK":
            return []

        uids = messages[0].split()[-max_results:]  # 取最近 N 封
        results = []

        for uid in uids:
            status, msg_data = self._conn.fetch(uid, "(RFC822)")
            if status != "OK" or not msg_data:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject = decode_subject(msg.get("Subject", ""))
            from_addr = msg.get("From", "")
            date_str = msg.get("Date", "")
            body_html = self._extract_html_body(msg)

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
