"""
Tests for brain.llm.web_search — Perplexity API integration.
No real API calls — tests logic, trigger detection, and graceful degradation.
"""

import pytest
from unittest.mock import patch, MagicMock
from brain.llm.web_search import WebSearch, WEB_SEARCH_TRIGGERS, CASTING_TRIGGERS


@pytest.fixture
def search_with_key():
    with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "test-key-123"}):
        return WebSearch()


@pytest.fixture
def search_no_key():
    with patch.dict("os.environ", {}, clear=True):
        ws = WebSearch()
        ws._api_key = None
        return ws


# ── Availability ──────────────────────────────────────────────────────────────

class TestAvailability:
    def test_available_with_key(self, search_with_key):
        assert search_with_key.is_available() is True

    def test_unavailable_without_key(self, search_no_key):
        assert search_no_key.is_available() is False

    def test_no_search_without_key(self, search_no_key):
        assert search_no_key.should_search("what's the latest news today?") is False


# ── Trigger detection ─────────────────────────────────────────────────────────

class TestTriggerDetection:
    def test_detects_latest(self, search_with_key):
        assert search_with_key.should_search("what's the latest on the writer's strike?") is True

    def test_detects_today(self, search_with_key):
        assert search_with_key.should_search("what happened today in Hollywood?") is True

    def test_detects_news(self, search_with_key):
        assert search_with_key.should_search("any news about the SAG awards?") is True

    def test_detects_who_won(self, search_with_key):
        assert search_with_key.should_search("who won the Oscar for best actor?") is True

    def test_detects_current(self, search_with_key):
        assert search_with_key.should_search("what's the current box office?") is True

    def test_detects_breaking(self, search_with_key):
        assert search_with_key.should_search("breaking news from Cannes") is True

    def test_no_trigger_normal_query(self, search_with_key):
        assert search_with_key.should_search("help me with my audition prep") is False

    def test_no_trigger_memory_query(self, search_with_key):
        assert search_with_key.should_search("what did we talk about last week?") is False

    def test_case_insensitive(self, search_with_key):
        assert search_with_key.should_search("What's The LATEST news?") is True

    def test_all_triggers_exist(self):
        assert len(WEB_SEARCH_TRIGGERS) >= 10
        assert "latest" in WEB_SEARCH_TRIGGERS
        assert "today" in WEB_SEARCH_TRIGGERS
        assert "news" in WEB_SEARCH_TRIGGERS


# ── Search (mocked API) ───────────────────────────────────────────────────────

class TestSearchMocked:
    def test_search_returns_string(self, search_with_key):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "The latest news is XYZ."}}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_response):
            result = search_with_key.search("what's the latest news?")

        assert isinstance(result, str)
        assert result == "The latest news is XYZ."

    def test_search_raises_without_key(self, search_no_key):
        with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
            search_no_key.search("test query")

    def test_search_casting_enriches_query(self, search_with_key):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Casting info here."}}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_response) as mock_post:
            search_with_key.search_casting("who's cast in the new Netflix drama?")

        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"]
        user_msg = payload["messages"][-1]["content"]
        assert "casting" in user_msg.lower() or "industry" in user_msg.lower()

    def test_timeout_raises_runtime_error(self, search_with_key):
        import requests as req
        with patch("requests.post", side_effect=req.Timeout):
            with pytest.raises(RuntimeError, match="timed out"):
                search_with_key.search("test query")

    def test_http_error_raises_runtime_error(self, search_with_key):
        import requests as req
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = req.HTTPError("403 Forbidden")
        with patch("requests.post", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Perplexity API error"):
                search_with_key.search("test query")
