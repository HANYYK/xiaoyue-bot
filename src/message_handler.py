"""
Message handler - girlfriend persona + anti-ban + WeCom.
"""
import logging
import random
from typing import Optional, Tuple

from .config import config
from .ai_client import DeepSeekClient
from .session_manager import SessionManager
from .human_simulator import HumanSimulator

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles messages with girlfriend persona and anti-ban measures."""

    def __init__(self):
        self.allowed_user = config.wecom.allowed_user
        self.ai = DeepSeekClient()
        self.session = SessionManager()
        self.human = HumanSimulator()

    def should_process(self, from_user: str) -> bool:
        if self.allowed_user and from_user != self.allowed_user:
            return False
        return True

    def process_message(self, from_user: str, content: str) -> Tuple[Optional[str], str]:
        content = (content or "").strip()
        if not content:
            return None, from_user

        if not self.should_process(from_user):
            logger.info("User %s not allowed, skip", from_user[:16])
            return None, from_user

        # Special commands
        if content in ("#clear", "#清除"):
            self.session.clear_session(from_user)
            return random.choice([
                "好啦都忘掉啦～你刚才说什么？",
                "嗯嗯！重新开始～",
                "好哒，之前的都翻篇啦",
            ]), from_user

        if content in ("#help", "#帮助"):
            return "发消息就可以和我聊天啦～\n#清除 = 忘记对话\n#帮助 = 看这个", from_user

        if content in ("#status", "#状态"):
            active = "在线呀～" if self.human.is_active_now() else "在休息..."
            cnt = len(self.session.get_history(from_user))
            return f"{active}\n记住 {cnt} 条对话", from_user

        # Anti-ban check
        if not self.human.should_reply(from_user, len(content)):
            return None, from_user

        # Generate reply
        history = self.session.get_history(from_user)
        try:
            reply = self.ai.generate_girlfriend_reply(content, history)
        except Exception as e:
            logger.error("AI failed: %s", e)
            reply = self.ai._fallback_reply()

        if not reply:
            return None, from_user

        self.session.add_user_message(from_user, content)
        self.session.add_assistant_message(from_user, reply)

        return reply, from_user

    def get_delay_for(self, message_length: int) -> float:
        return self.human.get_reply_delay(message_length)

    def record_reply_sent(self, user_id: str) -> None:
        self.human.record_reply(user_id)
