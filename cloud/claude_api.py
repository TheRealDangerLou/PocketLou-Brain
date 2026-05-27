"""
Cloud Burst — Claude API integration.

Phase 1: Always cloud. This is the primary LLM backend.
Phase 3+: Cloud is fallback only. Local Llama 3 runs first.

Requires: ANTHROPIC_API_KEY in environment (.env file or shell).

Note: Brain now routes through brain.llm.router → brain.llm.cloud_llm.ClaudeClient.
This module remains for backward compatibility and direct import.
"""

from __future__ import annotations

# Import the canonical ClaudeClient and alias it for backward compat
from brain.llm.cloud_llm import ClaudeClient as _ClaudeClient


class CloudBurst(_ClaudeClient):
    """
    Cloud Burst — backward-compatible wrapper for ClaudeClient.
    New code should use brain.llm.cloud_llm.ClaudeClient directly.
    """

    def __init__(
        self,
        model:       str   = _ClaudeClient.DEFAULT_MODEL,
        max_tokens:  int   = _ClaudeClient.DEFAULT_MAX_TOKENS,
        temperature: float = _ClaudeClient.DEFAULT_TEMPERATURE,
    ):
        super().__init__(model=model, max_tokens=max_tokens, temperature=temperature)

    def complete(
        self,
        messages,
        system:      str   = "",
        temperature: float | None = None,
        max_tokens:  int   | None = None,
    ) -> str:
        """Single-shot completion. Delegates to ClaudeClient."""
        return super().complete(
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def complete_stream(self, messages, system: str = ""):
        """Streaming completion. Delegates to ClaudeClient.stream()."""
        return self.stream(messages, system=system)
