"""
Multi-model LLM Router — God-tier upgrade.

Routing priority:
  1. Web search (Perplexity) — if query needs live internet
  2. GPT-4o-mini (OpenAI)    — fast conversational replies
  3. Claude Sonnet            — reasoning, creative, actor, conspiracy
  4. Claude fallback          — always available if ANTHROPIC_API_KEY is set

Invisible to Lou. Just makes every answer better.
"""

from __future__ import annotations

import os
import logging
from typing import Optional

from brain.llm.model_selector import ModelSelector
from brain.llm.web_search import WebSearch

logger = logging.getLogger(__name__)


class _LocalLLMStub:
    """Phase 3 stub — Llama 3 not yet active."""
    def is_available(self) -> bool:
        return False
    def load(self) -> bool:
        return False


class LLMRouter:
    """
    Routes each query to the optimal model.
    Falls back gracefully when APIs are unavailable.
    Returns (response_text, backend_label).
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        self._selector = ModelSelector()
        self._web_search = WebSearch()
        self._claude: object = None
        self._openai: object = None
        self.local = _LocalLLMStub()

    # ── Lazy client init ──────────────────────────────────────────────────────

    def _claude_client(self):
        if self._claude is None:
            from brain.llm.cloud_llm import ClaudeClient
            self._claude = ClaudeClient(self._config)
        return self._claude

    def _openai_client(self):
        if self._openai is None:
            from brain.llm.cloud_llm import OpenAIClient
            self._openai = OpenAIClient()
        return self._openai

    # ── Main router ───────────────────────────────────────────────────────────

    def route(
        self,
        messages: list[dict],
        system_prompt: str,
        mode: str = "STANDARD",
    ) -> tuple[str, str]:
        """
        Route a query to the best available model.
        Returns (response_text, backend_label).
        """
        last_msg = _last_user_message(messages)

        # ── Step 1: Live web search ───────────────────────────────────────────
        if self._web_search.should_search(last_msg):
            try:
                logger.info("Routing to Perplexity (web search)")
                response = self._web_search.search(last_msg)
                return response, "perplexity"
            except Exception as e:
                logger.warning(f"Web search failed ({e}) — falling back to LLM")

        # ── Step 2: Select model by query type + mode ─────────────────────────
        model_id, provider = self._selector.select(last_msg, mode)
        logger.info(f"Routing to {provider}/{model_id} (mode={mode})")

        # ── Step 3: Call selected provider ────────────────────────────────────
        if provider == "openai" and os.environ.get("OPENAI_API_KEY"):
            try:
                response = self._openai_client().complete(messages, system_prompt)
                return response, f"openai/{model_id}"
            except Exception as e:
                logger.warning(f"OpenAI failed ({e}) — falling back to Claude")

        # ── Step 4: Claude (default + universal fallback) ─────────────────────
        response = self._claude_client().complete(messages, system_prompt)
        return response, "anthropic/claude-sonnet-4-5"


def _last_user_message(messages: list[dict]) -> str:
    return next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "",
    )
