"""
LLM Router — decides local or cloud for each request.

Default: try local first (privacy, speed, offline).
Burst to cloud when local is unavailable or the mode demands it.
"""

from __future__ import annotations

import logging

from brain.llm.local_llm import LocalLLM
from brain.llm.cloud_llm import CloudLLM

logger = logging.getLogger(__name__)

# These modes are complex enough to prefer cloud when available
CLOUD_PREFERRED_MODES = {"TRANSLATION", "EPIPHANY", "CONSPIRACY"}

# If user's message is longer than this, route to cloud
COMPLEX_QUERY_THRESHOLD = 500


class LLMRouter:
    """
    Routes between local llama.cpp and Claude cloud API.
    Returns (response_text, backend_name).
    """

    def __init__(self, config: dict):
        self.local = LocalLLM(config)
        self.cloud = CloudLLM(config)
        self._prefer_local = config["llm"].get("default_backend", "local") == "local"
        self.local.load()

    def route(
        self,
        messages: list[dict],
        system_prompt: str,
        mode: str,
    ) -> tuple[str, str]:
        use_cloud = self._should_use_cloud(messages, mode)

        if use_cloud:
            return self._try_cloud(messages, system_prompt, fallback_to_local=True)

        return self._try_local_then_cloud(messages, system_prompt)

    def _try_local_then_cloud(
        self, messages: list[dict], system_prompt: str
    ) -> tuple[str, str]:
        if self.local.is_available():
            try:
                response = self.local.complete(messages, system_prompt)
                return response, "local"
            except Exception as e:
                logger.warning(f"Local LLM failed ({e}), bursting to cloud")

        return self._try_cloud(messages, system_prompt, fallback_to_local=False)

    def _try_cloud(
        self,
        messages: list[dict],
        system_prompt: str,
        fallback_to_local: bool = False,
    ) -> tuple[str, str]:
        try:
            response = self.cloud.complete(messages, system_prompt)
            return response, "cloud"
        except Exception as e:
            logger.error(f"Cloud LLM failed: {e}")
            if fallback_to_local and self.local.is_available():
                logger.info("Falling back to local LLM")
                response = self.local.complete(messages, system_prompt)
                return response, "local"
            raise

    def _should_use_cloud(self, messages: list[dict], mode: str) -> bool:
        if not self._prefer_local:
            return True
        if not self.local.is_available():
            return True
        if mode in CLOUD_PREFERRED_MODES:
            return True
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        if len(last_user_msg) > COMPLEX_QUERY_THRESHOLD:
            return True
        return False
