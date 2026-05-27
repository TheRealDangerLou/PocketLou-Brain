"""
Real-time web search via Perplexity API.

Auto-triggered when a query needs live internet.
Invisible to Lou — just happens when needed.
Degrades gracefully if PERPLEXITY_API_KEY is not set.
"""

from __future__ import annotations

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

WEB_SEARCH_TRIGGERS: list[str] = [
    "latest", "today", "current", "news", "who won", "weather",
    "what happened", "just announced", "breaking", "right now",
    "this week", "this year", "recently", "any news", "did they",
    "what's going on with", "score", "standings", "just dropped",
    "trailer", "release date", "box office", "chart", "trending",
]

CASTING_TRIGGERS: list[str] = [
    "casting call", "audition for", "production announcement",
    "who's cast", "who plays", "industry news", "greenlit",
    "in development", "pilot picked up",
]

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"


class WebSearch:
    """
    Live internet access via Perplexity API.
    Returns cited, real-time answers in 2-3 sentences.
    """

    def __init__(self):
        self._api_key: Optional[str] = os.environ.get("PERPLEXITY_API_KEY")

    def is_available(self) -> bool:
        return bool(self._api_key)

    def should_search(self, query: str) -> bool:
        """Return True if this query needs live internet data."""
        if not self.is_available():
            return False
        q = query.lower()
        return any(trigger in q for trigger in WEB_SEARCH_TRIGGERS)

    def search(self, query: str, max_tokens: int = 300) -> str:
        """
        Search the live web via Perplexity.
        Returns a concise, cited answer.
        """
        if not self._api_key:
            raise ValueError(
                "PERPLEXITY_API_KEY not set. "
                "Add it to .env to enable live web search."
            )

        try:
            import requests
        except ImportError:
            raise RuntimeError("requests not installed. Run: pip install requests")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": PERPLEXITY_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Answer in 2-3 sentences max. "
                        "Be precise. Cite sources inline when useful. "
                        "No fluff."
                    ),
                },
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "return_citations": True,
        }

        try:
            resp = requests.post(
                PERPLEXITY_URL,
                headers=headers,
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.Timeout:
            raise RuntimeError("Perplexity search timed out (>10s)")
        except requests.HTTPError as e:
            raise RuntimeError(f"Perplexity API error: {e}")

    def search_casting(self, query: str) -> str:
        """Casting-specific search — film/TV industry focus."""
        enriched = (
            f"Film and TV casting/production industry news: {query}. "
            "Focus on casting calls, production announcements, and actor news."
        )
        return self.search(enriched, max_tokens=400)
