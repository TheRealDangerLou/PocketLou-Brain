"""
Cloud Burst — Claude API integration.

Phase 1: Always cloud. This is the primary LLM backend.
Phase 3+: Cloud is fallback only. Local Llama 3 runs first.

Requires: ANTHROPIC_API_KEY in environment (.env file or shell).
"""

from __future__ import annotations

import os
from typing import Generator


class CloudBurst:
    """Claude API. The heavy iron when local can't handle it — or in Phase 1, always."""

    DEFAULT_MODEL     = "claude-opus-4-5"
    DEFAULT_MAX_TOKENS = 1024
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
            import anthropic
        except ImportError:
            raise RuntimeError(
                "anthropic not installed.\n"
                "Run: pip install anthropic"
            )

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set.\n"
                "Copy .env.example to .env and add your key, or:\n"
                "  export ANTHROPIC_API_KEY=your_key_here"
            )

        self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def complete(
        self,
        messages:    list[dict],
        system:      str   = "",
        temperature: float | None = None,
        max_tokens:  int   | None = None,
    ) -> str:
        """Single-shot completion. Returns full response text."""
        client = self._get_client()

        kwargs: dict = {
            "model":      self._model,
            "max_tokens": max_tokens or self._max_tokens,
            "messages":   messages,
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
        """Streaming completion. Yields text chunks as they arrive."""
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
