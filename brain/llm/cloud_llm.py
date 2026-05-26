"""
Cloud LLM — Claude API via anthropic SDK.

Used as burst mode when local is unavailable or query demands it.
Requires ANTHROPIC_API_KEY in environment.
"""

from __future__ import annotations

import os
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)


class CloudLLM:
    """Claude API — the heavy iron when local can't handle it."""

    def __init__(self, config: dict):
        self._cfg = config["llm"]
        self._client = None
        self._model = self._cfg.get("cloud_model", "claude-opus-4-5")

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            import anthropic
        except ImportError:
            raise RuntimeError(
                "anthropic SDK not installed. Run: pip install anthropic"
            )

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Copy .env.example to .env and add your key."
            )

        self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def complete(self, messages: list[dict], system_prompt: str = "") -> str:
        client = self._get_client()

        kwargs: dict = {
            "model": self._model,
            "max_tokens": self._cfg.get("max_tokens", 512),
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = client.messages.create(**kwargs)
        return response.content[0].text

    def complete_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        client = self._get_client()

        kwargs: dict = {
            "model": self._model,
            "max_tokens": self._cfg.get("max_tokens", 512),
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        with client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text
