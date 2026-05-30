"""
WeCom (企业微信) API Client.
Access token management + sending messages.
"""
import logging
import time
import threading
from typing import Optional

import requests

from .config import config

logger = logging.getLogger(__name__)

API_BASE = "https://qyapi.weixin.qq.com/cgi-bin"


class WeComAPI:
    """WeCom API client with automatic token caching."""

    def __init__(self):
        self.corp_id = config.wecom.corp_id
        self.agent_id = config.wecom.agent_id
        self.secret = config.wecom.secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._lock = threading.Lock()

    def get_access_token(self) -> str:
        if self._access_token and time.time() < (self._token_expires_at - 300):
            return self._access_token

        with self._lock:
            if self._access_token and time.time() < (self._token_expires_at - 300):
                return self._access_token

            logger.info("Fetching WeCom access_token...")
            resp = requests.get(
                f"{API_BASE}/gettoken",
                params={"corpid": self.corp_id, "corpsecret": self.secret},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("errcode", -1) != 0:
                raise RuntimeError(
                    f"access_token failed: {data.get('errcode')} {data.get('errmsg')}"
                )

            self._access_token = data["access_token"]
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            logger.info("access_token OK (expires in %ds)", data.get("expires_in"))
            return self._access_token

    def send_text(self, user_id: str, content: str) -> bool:
        token = self.get_access_token()

        payload = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {"content": content},
        }

        try:
            resp = requests.post(
                f"{API_BASE}/message/send",
                params={"access_token": token},
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            result = resp.json()
            errcode = result.get("errcode", -1)

            if errcode != 0:
                logger.error("Send failed: errcode=%d errmsg=%s",
                             errcode, result.get("errmsg", "unknown"))

                if errcode in (40014, 42001):  # Token expired
                    with self._lock:
                        self._access_token = None
                        self._token_expires_at = 0.0
                    return self.send_text(user_id, content)

                return False

            logger.info("Message sent -> %s", user_id[:16])
            return True

        except requests.exceptions.RequestException as e:
            logger.error("Send network error: %s", e)
            return False

    def send_text_safe(self, user_id: str, content: str) -> bool:
        if len(content) > 2000:
            content = content[:1997] + "..."
        return self.send_text(user_id, content)

    def check_connection(self) -> bool:
        try:
            self.get_access_token()
            return True
        except Exception as e:
            logger.error("Connection check failed: %s", e)
            return False
