"""
Human behavior simulation to minimize detection.
"""
import logging
import random
import time
from datetime import datetime
from collections import deque

from .config import config

logger = logging.getLogger(__name__)


class HumanSimulator:
    """Simulates human-like messaging patterns."""

    def __init__(self):
        self.cfg = config.human
        self._reply_timestamps: deque[float] = deque()
        self._last_reply: dict[str, float] = {}
        self._is_afk = False
        self._afk_until: float = 0.0
        self._next_afk_check = time.time() + random.uniform(1800, 5400)

    def should_reply(self, user_id: str, message_length: int) -> bool:
        if self._is_afk and time.time() < self._afk_until:
            logger.info("[AFK] Skipping message (resumes at %s)",
                        datetime.fromtimestamp(self._afk_until).strftime("%H:%M"))
            return False

        self._check_afk_transition()

        if not self._is_active_hours():
            logger.info("[Sleep] Outside active hours")
            return False

        if not self._check_global_limit():
            logger.warning("[Rate] Global limit reached")
            return False

        if not self._check_user_limit(user_id):
            return False

        if random.random() > self.cfg.reply_probability:
            logger.info("[Skip] Random drop (simulating human)")
            return False

        return True

    def get_reply_delay(self, user_msg_length: int) -> float:
        reading = user_msg_length * self.cfg.reading_delay_per_char
        thinking = random.uniform(self.cfg.reply_delay_min, self.cfg.reply_delay_max)
        if random.random() < 0.08:
            distraction = random.uniform(20, 60)
            logger.info("[Delay] Distracted +%.0fs", distraction)
            thinking += distraction
        return min(reading + thinking, 120.0)

    def record_reply(self, user_id: str) -> None:
        now = time.time()
        self._reply_timestamps.append(now)
        self._last_reply[user_id] = now
        self._log_stats()

    def is_active_now(self) -> bool:
        if self._is_afk and time.time() < self._afk_until:
            return False
        self._check_afk_transition()
        return self._is_active_hours()

    def _is_active_hours(self) -> bool:
        hour = datetime.now().hour
        return self.cfg.active_hours_start <= hour < self.cfg.active_hours_end

    def _check_afk_transition(self) -> None:
        now = time.time()
        if now < self._next_afk_check:
            return
        base_interval = self.cfg.afk_interval_hours * 3600
        self._next_afk_check = now + random.uniform(base_interval * 0.7, base_interval * 1.3)
        if self._is_afk:
            self._is_afk = False
            logger.info("[AFK] Waking up")
        elif random.random() < 0.4 and self._is_active_hours():
            duration = random.uniform(self.cfg.afk_duration_min * 60,
                                      self.cfg.afk_duration_max * 60)
            self._is_afk = True
            self._afk_until = now + duration
            logger.info("[AFK] Away for %.1f min", duration / 60)

    def _check_global_limit(self) -> bool:
        now = time.time()
        while self._reply_timestamps and self._reply_timestamps[0] < now - 86400:
            self._reply_timestamps.popleft()
        hour_ago = now - 3600
        if sum(1 for t in self._reply_timestamps if t > hour_ago) >= self.cfg.max_replies_per_hour:
            return False
        if len(self._reply_timestamps) >= self.cfg.max_replies_per_day:
            return False
        return True

    def _check_user_limit(self, user_id: str) -> bool:
        if user_id not in self._last_reply:
            return True
        return (time.time() - self._last_reply[user_id]) >= self.cfg.min_reply_interval

    def _log_stats(self) -> None:
        now = time.time()
        hour_ago = now - 3600
        hourly = sum(1 for t in self._reply_timestamps if t > hour_ago)
        daily = len(self._reply_timestamps)
        logger.info("[Stats] 1h=%d/%d 24h=%d/%d",
                    hourly, self.cfg.max_replies_per_hour,
                    daily, self.cfg.max_replies_per_day)
