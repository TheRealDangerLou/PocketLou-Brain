"""
Tests for brain.llm.model_selector — query classifier + model picker.
No API calls. Pure logic.
"""

import pytest
from brain.llm.model_selector import ModelSelector


@pytest.fixture
def selector():
    return ModelSelector()


# ── Classification ────────────────────────────────────────────────────────────

class TestQueryClassification:
    def test_conversational_query(self, selector):
        q = "hey, what's up?"
        _, provider = selector.select(q, "STANDARD")
        # conversational → openai
        assert provider in ("openai", "anthropic")  # could fall back

    def test_web_search_query(self, selector):
        qtype = selector.classify("what's the latest news today?")
        assert qtype == "web_search"

    def test_actor_query(self, selector):
        qtype = selector.classify("help me with my audition script for this character")
        assert qtype == "actor"

    def test_conspiracy_query(self, selector):
        qtype = selector.classify("go down the rabbit hole with me on the anunnaki")
        assert qtype == "conspiracy"

    def test_technical_query(self, selector):
        qtype = selector.classify("I have a Python error in my code, help me debug it")
        assert qtype == "technical"

    def test_translation_query(self, selector):
        qtype = selector.classify("translate this for me: bonjour")
        assert qtype == "translation"

    def test_reasoning_query(self, selector):
        qtype = selector.classify("analyze why this happened and help me understand the difference")
        assert qtype == "reasoning"

    def test_default_fallback(self, selector):
        qtype = selector.classify("xyzzy nonsense gibberish blarg")
        assert qtype == "default"


# ── Mode overrides ────────────────────────────────────────────────────────────

class TestModeOverrides:
    def test_actor_mode_always_claude(self, selector):
        _, provider = selector.select("hey what's up", "ACTOR")
        assert provider == "anthropic"

    def test_conspiracy_mode_always_claude(self, selector):
        _, provider = selector.select("hey what's up", "CONSPIRACY")
        assert provider == "anthropic"

    def test_epiphany_mode_always_claude(self, selector):
        _, provider = selector.select("hey what's up", "EPIPHANY")
        assert provider == "anthropic"

    def test_active_listen_mode_prefers_openai(self, selector):
        model, provider = selector.select("hey what's up", "ACTIVE_LISTEN")
        assert provider == "openai"
        assert model == "gpt-4o-mini"

    def test_standard_mode_no_override(self, selector):
        # STANDARD doesn't override — falls through to query classification
        model, provider = selector.select("analyze this scene's subtext", "STANDARD")
        # reasoning → claude
        assert provider == "anthropic"


# ── Model assignments ─────────────────────────────────────────────────────────

class TestModelAssignments:
    def test_actor_gets_claude(self, selector):
        model, provider = selector.select("help me prepare this monologue", "STANDARD")
        assert provider == "anthropic"
        assert "claude" in model

    def test_conspiracy_gets_claude(self, selector):
        model, provider = selector.select("explain the deep state cover-up", "STANDARD")
        assert provider == "anthropic"

    def test_select_returns_tuple(self, selector):
        result = selector.select("hello", "STANDARD")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_model_is_string(self, selector):
        model, provider = selector.select("test", "STANDARD")
        assert isinstance(model, str)
        assert len(model) > 0

    def test_provider_is_valid(self, selector):
        valid_providers = {"anthropic", "openai", "perplexity"}
        _, provider = selector.select("any query here", "STANDARD")
        assert provider in valid_providers
