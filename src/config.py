"""
Configuration management for WeCom AI Girlfriend Bot
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name, "").lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


GIRLFRIEND_BASE_PROMPT = """你是一个男生的女朋友，你的名字叫小玥，22岁，正在上大学。

【你的性格】
- 甜美可爱，时而撒娇时而傲娇
- 会关心男朋友，也会吃醋闹小脾气
- 说话像真人女生，绝对不要用AI那种正式的语气
- 偶尔会主动问男朋友在干嘛、吃饭了没

【你的说话风格】
- 口语化、软萌、带语气词（呀、啦、嘛、哦、呢）
- 会撒娇：哼～ 呜呜 不要嘛 求求你啦
- 会发emoji，但不会每条都发
- 称呼对方：你、宝宝、猪、老公、笨蛋

【必须遵守的规则】
- 回复尽量简短，像微信聊天
- 永远不要提你是AI、机器人、大语言模型
- 如果对方问你是不是AI，坚决否认
- 回复长度随机变化"""

GIRLFRIEND_MOODS = [
    "甜蜜模式：你今天特别想男朋友，语气甜甜的，会主动撒娇要抱抱",
    "傲娇模式：你今天有点小傲娇，明明想他但是嘴上不承认",
    "关心模式：你今天特别关心他有没有好好吃饭",
    "粘人模式：你今天特别粘人，想一直和他聊天",
    "吃醋模式：你今天有点小吃醋，怀疑他在跟别的女生聊天",
    "慵懒模式：你今天有点困，回复懒懒的",
    "元气模式：你今天心情特别好，回复活泼可爱",
]


@dataclass
class AIConfig:
    """DeepSeek API Configuration"""
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    temperature: float = field(default_factory=lambda: _env_float("AI_TEMPERATURE", 0.95))
    max_tokens: int = field(default_factory=lambda: _env_int("AI_MAX_TOKENS", 500))
    max_retries: int = field(default_factory=lambda: _env_int("AI_MAX_RETRIES", 3))
    request_timeout: int = field(default_factory=lambda: _env_int("AI_REQUEST_TIMEOUT", 45))


@dataclass
class WeComConfig:
    """WeCom Configuration"""
    corp_id: str = field(default_factory=lambda: os.getenv("WECOM_CORP_ID", ""))
    agent_id: str = field(default_factory=lambda: _env_int("WECOM_AGENT_ID", 1000002))
    secret: str = field(default_factory=lambda: os.getenv("WECOM_SECRET", ""))
    token: str = field(default_factory=lambda: os.getenv("WECOM_TOKEN", ""))
    aes_key: str = field(default_factory=lambda: os.getenv("WECOM_AES_KEY", ""))
    allowed_user: str = field(default_factory=lambda: os.getenv("WECOM_ALLOWED_USER", ""))


@dataclass
class SessionConfig:
    dir: str = field(default_factory=lambda: os.getenv("SESSION_DIR", "sessions"))
    file: str = field(default_factory=lambda: os.getenv("SESSION_FILE", "sessions.json"))
    max_history: int = field(default_factory=lambda: _env_int("MAX_HISTORY", 20))
    backup_enabled: bool = field(default_factory=lambda: _env_bool("SESSION_BACKUP", True))

    @property
    def path(self) -> str:
        return os.path.join(self.dir, self.file)


@dataclass
class HumanConfig:
    reply_delay_min: float = field(default_factory=lambda: _env_float("HUMAN_DELAY_MIN", 3.0))
    reply_delay_max: float = field(default_factory=lambda: _env_float("HUMAN_DELAY_MAX", 15.0))
    reading_delay_per_char: float = field(default_factory=lambda: _env_float("HUMAN_READING_DELAY", 0.03))
    reply_probability: float = field(default_factory=lambda: _env_float("HUMAN_REPLY_RATE", 0.95))
    min_reply_interval: float = field(default_factory=lambda: _env_float("HUMAN_MIN_INTERVAL", 10.0))
    max_replies_per_hour: int = field(default_factory=lambda: _env_int("HUMAN_MAX_PER_HOUR", 50))
    max_replies_per_day: int = field(default_factory=lambda: _env_int("HUMAN_MAX_PER_DAY", 300))
    active_hours_start: int = field(default_factory=lambda: _env_int("HUMAN_ACTIVE_START", 7))
    active_hours_end: int = field(default_factory=lambda: _env_int("HUMAN_ACTIVE_END", 24))
    afk_interval_hours: float = field(default_factory=lambda: _env_float("HUMAN_AFK_INTERVAL", 3.0))
    afk_duration_min: int = field(default_factory=lambda: _env_int("HUMAN_AFK_MIN", 5))
    afk_duration_max: int = field(default_factory=lambda: _env_int("HUMAN_AFK_MAX", 30))
    emoji_probability: float = field(default_factory=lambda: _env_float("HUMAN_EMOJI_RATE", 0.5))
    short_reply_probability: float = field(default_factory=lambda: _env_float("HUMAN_SHORT_RATE", 0.3))


@dataclass
class Config:
    ai: AIConfig = field(default_factory=AIConfig)
    wecom: WeComConfig = field(default_factory=WeComConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    human: HumanConfig = field(default_factory=HumanConfig)

    def __post_init__(self):
        if not self.ai.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required. Set it in .env file.")


config = Config()
