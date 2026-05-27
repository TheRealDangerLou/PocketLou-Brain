"""
LLM Clients — Claude (Anthropic) + GPT-4o-mini (OpenAI).

ClaudeClient  — best reasoning, creative, actor, conspiracy, code
OpenAIClient  — fast conversational replies, sub-second

Both degrade gracefully with clear error messages when keys aren't set.
"""

from __future__ import annotations

import os
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)


# ── Claude ────────────────────────────────────────────────────────────────────

class ClaudeClient:
    """Claude Sonnet via Anthropic SDK. Best for complex reasoning and creativity."""

    DEFAULT_MODEL       = "claude-sonnet-4-5"
    DEFAULT_MAX_TOKENS  = 1024
    DEFAULT_TEMPERATURE = 0.75

    def __init__(
        self,
        config:      Optional[dict] = None,
        model:       str   = DEFAULT_MODEL,
        max_tokens:  int   = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        cfg = (config or {}).get("llm", {})
        self._model       = cfg.get("cloud_model", model)
        self._max_tokens  = cfg.get("max_tokens", max_tokens)
        self._temperature = cfg.get("temperature", temperature)
        self._client      = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("anthropic not installed. Run: pip install anthropic")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set.\n"
                "Add it to .env: ANTHROPIC_API_KEY=your_key_here"
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def complete(
        self,
        messages:    list[dict],
        system:      str   = "",
        temperature: Optional[float] = None,
        max_tokens:  Optional[int]   = None,
    ) -> str:
        client = self._get_client()
        kwargs: dict = {
            "model":       self._model,
            "max_tokens":  max_tokens  or self._max_tokens,
            "messages":    messages,
            "temperature": temperature if temperature is not None else self._temperature,
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text

    def stream(
        self,
        messages: list[dict],
        system:   str = "",
    ) -> Generator[str, None, None]:
        client = self._get_client()
        kwargs: dict = {
            "model":      self._model,
            "max_tokens": self._max_tokens,
            "messages":   messages,
        }
        if system:
            kwargs["system"] = system
        with client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text


# ── OpenAI ────────────────────────────────────────────────────────────────────

class OpenAIClient:
    """GPT-4o-mini via OpenAI API. Fast, cheap, great for quick exchanges."""

    DEFAULT_MODEL       = "gpt-4o-mini"
    DEFAULT_MAX_TOKENS  = 512
    DEFAULT_TEMPERATURE = 0.75

    def __init__(
        self,
        model:       str   = DEFAULT_MODEL,
        max_tokens:  int   = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self._model       = model
        self._max_tokens  = max_tokens
        self._temperature = temperature
        self._client      = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import openai
        except ImportError:
            raise RuntimeError("openai not installed. Run: pip install openai")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not set.\n"
                "Add it to .env: OPENAI_API_KEY=your_key_here"
            )
        self._client = openai.OpenAI(api_key=api_key)
        return self._client

    def complete(
        self,
        messages:    list[dict],
        system:      str   = "",
        temperature: Optional[float] = None,
        max_tokens:  Optional[int]   = None,
    ) -> str:
        client = self._get_client()
        all_messages: list[dict] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)
        response = client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature if temperature is not None else self._temperature,
        )
        return response.choices[0].message.content


# ── Backward compat aliases ───────────────────────────────────────────────────

# brain/llm/router.py (old version) used CloudLLM
class CloudLLM(ClaudeClient):
    """Alias for backward compatibility with old router."""
    def __init__(self, config: dict):
        super().__init__(config=config)

    def complete(self, messages, system_prompt="", **kwargs):
        return super().complete(messages, system=system_prompt, **kwargs)

    def complete_stream(self, messages, system_prompt=""):
        return super().stream(messages, system=system_prompt)


# cloud/claude_api.py uses CloudBurst
CloudBurst = ClaudeClient
