"""
DeepSeek API Client with retry + girlfriend persona.
"""
import json
import logging
import time
import random
from typing import Optional, List, Dict

import requests

from .config import config, GIRLFRIEND_BASE_PROMPT, GIRLFRIEND_MOODS

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API client with retry and mood system."""

    def __init__(self):
        self.api_key = config.ai.api_key
        self.base_url = config.ai.base_url
        self.model = config.ai.model
        self.endpoint = f"{self.base_url}/chat/completions"
        self._mood_idx = -1

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _get_mood_prompt(self) -> str:
        self._mood_idx = (self._mood_idx + 1) % len(GIRLFRIEND_MOODS)
        mood = GIRLFRIEND_MOODS[self._mood_idx]
        return f"{GIRLFRIEND_BASE_PROMPT}\n\n【今天的模式】{mood}"

    def generate_response(self, messages: List[Dict[str, str]],
                          temperature: Optional[float] = None,
                          max_tokens: Optional[int] = None) -> str:
        temperature = temperature or config.ai.temperature
        max_tokens = max_tokens or config.ai.max_tokens
        max_retries = config.ai.max_retries

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    self.endpoint,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=config.ai.request_timeout,
                )
                response.raise_for_status()
                result = response.json()

                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"].strip()

                return self._fallback_reply()

            except requests.exceptions.Timeout:
                logger.error("API timeout (attempt %d/%d)", attempt + 1, max_retries + 1)
                last_error = "timeout"
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else 0
                logger.error("API HTTP %d (attempt %d/%d)", status, attempt + 1, max_retries + 1)
                if status == 429:
                    wait = min(2 ** attempt + random.uniform(0, 1), 30)
                    time.sleep(wait)
                    continue
                if status >= 500:
                    last_error = "server_error"
                else:
                    return self._fallback_reply()
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                logger.error("API error (attempt %d/%d): %s", attempt + 1, max_retries + 1, e)
                last_error = "network"

            if attempt < max_retries:
                wait = min(2 ** attempt + random.uniform(0, 1), 16)
                time.sleep(wait)

        logger.error("All %d retries exhausted: %s", max_retries, last_error)
        return self._fallback_reply()

    def generate_girlfriend_reply(self, user_message: str,
                                  history: List[Dict[str, str]]) -> str:
        messages = [{"role": "system", "content": self._get_mood_prompt()}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return self.generate_response(messages)

    @staticmethod
    def _fallback_reply() -> str:
        fallbacks = [
            "刚刚在忙呢，你说什么呀～",
            "信号好像不太好，再说一次嘛",
            "呜呜刚才手机卡了",
            "不好意思呀，刚看到消息",
        ]
        return random.choice(fallbacks)
