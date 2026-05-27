"""
Query classifier and model selector.

Classifies each query by type, picks the optimal model + provider.
Invisible to Lou — just makes responses smarter and faster.
"""

from __future__ import annotations

# ── Query keyword classifiers ────────────────────────────────────────────────

QUERY_CLASSIFIERS: dict[str, list[str]] = {
    "conversational": [
        "hey", "what's up", "how are", "tell me", "what do you think",
        "just wanted", "checking in", "yo", "what's good", "honestly",
    ],
    "web_search": [
        "latest", "news", "current", "today", "what happened", "who won",
        "weather", "just announced", "breaking", "right now", "this week",
        "recently", "any news", "what's going on", "did they", "score",
        "standings", "just dropped", "trailer", "release date",
    ],
    "actor": [
        "script", "audition", "character", "scene", "monologue", "casting",
        "subtext", "role", "performance", "director", "on set", "dialogue",
        "motivation", "backstory", "broken oath", "last fix", "armstrong",
        "callback", "self-tape", "sides", "agency", "constantine",
    ],
    "conspiracy": [
        "conspiracy", "rabbit hole", "hidden", "suppressed", "they don't want",
        "anunnaki", "aliens", "sumerian", "gateway", "hemi-sync", "cia",
        "government secret", "they knew", "cover up", "occult", "deep state",
        "remote viewing", "monroe institute", "suppressed tech",
    ],
    "technical": [
        "code", "python", "error", "debug", "how do i build", "how does",
        "function", "bug", "stack trace", "api", "deploy", "git",
        "javascript", "database", "server", "endpoint",
    ],
    "translation": [
        "translate", "what did they say", "how do i say", "en français",
        "in french", "in italian", "in spanish", "what does that mean in",
        "traduction", "comment dit-on",
    ],
    "reasoning": [
        "analyze", "explain", "why", "what does this mean", "help me understand",
        "break down", "what's your take", "make sense of", "deep dive",
        "walk me through", "what's the difference",
    ],
}

# ── Model assignment per query type ──────────────────────────────────────────

MODEL_ASSIGNMENTS: dict[str, tuple[str, str]] = {
    "conversational": ("gpt-4o-mini",                         "openai"),
    "web_search":     ("llama-3.1-sonar-large-128k-online",   "perplexity"),
    "actor":          ("claude-sonnet-4-5",                   "anthropic"),
    "conspiracy":     ("claude-sonnet-4-5",                   "anthropic"),
    "technical":      ("claude-sonnet-4-5",                   "anthropic"),
    "translation":    ("claude-sonnet-4-5",                   "anthropic"),
    "reasoning":      ("claude-sonnet-4-5",                   "anthropic"),
    "default":        ("claude-sonnet-4-5",                   "anthropic"),
}

# Mode always overrides query classification
MODE_OVERRIDES: dict[str, tuple[str, str]] = {
    "ACTOR":         ("claude-sonnet-4-5", "anthropic"),
    "CONSPIRACY":    ("claude-sonnet-4-5", "anthropic"),
    "EPIPHANY":      ("claude-sonnet-4-5", "anthropic"),
    "TRANSLATION":   ("claude-sonnet-4-5", "anthropic"),
    "ACTIVE_LISTEN": ("gpt-4o-mini",       "openai"),
}


class ModelSelector:
    """Classifies queries and selects the optimal model + provider."""

    def classify(self, query: str) -> str:
        """Return the query type with the highest keyword match score."""
        query_lower = query.lower()
        scores: dict[str, int] = {}
        for query_type, keywords in QUERY_CLASSIFIERS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[query_type] = score
        return max(scores, key=scores.get) if scores else "default"

    def select(self, query: str, mode: str = "STANDARD") -> tuple[str, str]:
        """
        Return (model_id, provider) for this query + mode combination.
        Mode overrides take precedence over query classification.
        """
        if mode in MODE_OVERRIDES:
            return MODE_OVERRIDES[mode]
        query_type = self.classify(query)
        return MODEL_ASSIGNMENTS.get(query_type, MODEL_ASSIGNMENTS["default"])
