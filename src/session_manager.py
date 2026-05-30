"""
Session management with persistent JSON storage and backup.
"""
import json
import os
import logging
import shutil
from typing import Dict, List, Optional

from .config import config

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages conversation sessions with disk persistence."""

    def __init__(self, session_path: Optional[str] = None, max_history: Optional[int] = None):
        self.session_path = session_path or config.session.path
        self.max_history = max_history or config.session.max_history
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self._ensure_storage_dir()
        self._load_sessions()

    def _ensure_storage_dir(self) -> None:
        storage_dir = os.path.dirname(self.session_path)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)

    def _load_sessions(self) -> None:
        if not os.path.exists(self.session_path):
            return
        try:
            with open(self.session_path, 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)
            logger.info("Loaded %d sessions", len(self.sessions))
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Session load error: %s, trying backup", e)
            backup_path = self.session_path + ".bak"
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        self.sessions = json.load(f)
                    logger.info("Recovered %d sessions from backup", len(self.sessions))
                    return
                except Exception:
                    pass
            self.sessions = {}

    def _save_sessions(self) -> None:
        try:
            tmp_path = self.session_path + ".tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)

            if config.session.backup_enabled and os.path.exists(self.session_path):
                try:
                    shutil.copy2(self.session_path, self.session_path + ".bak")
                except Exception:
                    pass

            os.replace(tmp_path, self.session_path)
        except IOError as e:
            logger.error("Save sessions failed: %s", e)

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(user_id, [])

    def add_message(self, user_id: str, role: str, content: str) -> None:
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        self.sessions[user_id].append({"role": role, "content": content})
        if len(self.sessions[user_id]) > self.max_history:
            self.sessions[user_id] = self.sessions[user_id][-self.max_history:]
        self._save_sessions()

    def add_user_message(self, user_id: str, content: str) -> None:
        self.add_message(user_id, "user", content)

    def add_assistant_message(self, user_id: str, content: str) -> None:
        self.add_message(user_id, "assistant", content)

    def clear_session(self, user_id: str) -> None:
        if user_id in self.sessions:
            del self.sessions[user_id]
            self._save_sessions()
            logger.info("Cleared session for: %s", user_id)

    def clear_all_sessions(self) -> None:
        self.sessions = {}
        self._save_sessions()
        logger.info("All sessions cleared")
