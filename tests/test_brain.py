"""Tests for PocketLou core brain."""

import json
import pytest
from unittest.mock import MagicMock, patch

from brain.core import PocketLou, ThinkResult


@pytest.fixture
def config_path(tmp_path):
    config = {
        "llm": {
            "default_backend": "cloud",
            "local_model_path": "models/llama.gguf",
            "local_context_size": 4096,
            "local_threads": 4,
            "local_gpu_layers": 0,
            "cloud_model": "claude-opus-4-5",
            "max_tokens": 512,
            "temperature": 0.7,
        },
        "memory": {
            "profile_path": str(tmp_path / "lou.json"),
            "vector_db_path": str(tmp_path / "vector"),
            "max_session_messages": 20,
            "max_context_memories": 5,
            "embedding_model": "all-MiniLM-L6-v2",
        },
        "response": {"target_latency_ms": 2000, "stream": False},
        "hardware": {
            "button_pin": 17,
            "haptic_pin": 27,
            "session_timeout_minutes": 60,
            "warning_at_minutes": 55,
        },
        "logging": {"level": "WARNING"},
    }
    cfg_file = tmp_path / "settings.json"
    cfg_file.write_text(json.dumps(config))

    profile = {
        "identity": {"name": "Louis Octeau Piché", "location": "Hudson, QC"},
        "career": {"primary": "Full-time actor"},
        "values": ["privacy", "family"],
    }
    (tmp_path / "lou.json").write_text(json.dumps(profile))

    return str(cfg_file)


def _make_lou(config_path):
    with patch("brain.core.LLMRouter") as MockRouter, \
         patch("brain.core.VectorStore") as MockVStore:
        MockRouter.return_value.local.is_available.return_value = False
        MockVStore.return_value.count.return_value = 0
        MockVStore.return_value.search.return_value = []
        lou = PocketLou(config_path=config_path)
        lou._router = MockRouter.return_value
        lou._vector_store_mock = MockVStore.return_value
    return lou


def test_default_mode(config_path):
    with patch("brain.core.LLMRouter"), patch("brain.core.VectorStore") as MockVS:
        MockVS.return_value.count.return_value = 0
        MockVS.return_value.search.return_value = []
        lou = PocketLou(config_path=config_path)
    assert lou.current_mode == "STANDARD"


def test_switch_mode_valid(config_path):
    with patch("brain.core.LLMRouter"), patch("brain.core.VectorStore") as MockVS:
        MockVS.return_value.count.return_value = 0
        MockVS.return_value.search.return_value = []
        lou = PocketLou(config_path=config_path)

    for mode in ["ACTOR", "EPIPHANY", "CONSPIRACY", "TRANSLATION", "ACTIVE_LISTEN"]:
        lou.switch_mode(mode)
        assert lou.current_mode == mode


def test_switch_mode_case_insensitive(config_path):
    with patch("brain.core.LLMRouter"), patch("brain.core.VectorStore") as MockVS:
        MockVS.return_value.count.return_value = 0
        MockVS.return_value.search.return_value = []
        lou = PocketLou(config_path=config_path)
    lou.switch_mode("actor")
    assert lou.current_mode == "ACTOR"


def test_switch_mode_invalid(config_path):
    with patch("brain.core.LLMRouter"), patch("brain.core.VectorStore") as MockVS:
        MockVS.return_value.count.return_value = 0
        MockVS.return_value.search.return_value = []
        lou = PocketLou(config_path=config_path)
    with pytest.raises(ValueError, match="Unknown mode"):
        lou.switch_mode("GODMODE")


def test_think_returns_result(config_path):
    with patch("brain.core.LLMRouter") as MockRouter, \
         patch("brain.core.VectorStore") as MockVStore:
        MockRouter.return_value.route.return_value = ("On it, Lou.", "cloud")
        MockRouter.return_value.local.is_available.return_value = False
        MockVStore.return_value.search.return_value = []
        MockVStore.return_value.count.return_value = 0

        lou = PocketLou(config_path=config_path)
        result = lou.think("What's the plan?")

    assert isinstance(result, ThinkResult)
    assert result.response == "On it, Lou."
    assert result.mode == "STANDARD"
    assert result.backend_used == "cloud"
    assert result.latency_ms >= 0


def test_think_stores_in_session(config_path):
    with patch("brain.core.LLMRouter") as MockRouter, \
         patch("brain.core.VectorStore") as MockVStore:
        MockRouter.return_value.route.return_value = ("Got it.", "cloud")
        MockRouter.return_value.local.is_available.return_value = False
        MockVStore.return_value.search.return_value = []
        MockVStore.return_value.count.return_value = 0

        lou = PocketLou(config_path=config_path)
        lou.think("Test")
        assert len(lou.session) == 2  # user + assistant


def test_clear_session(config_path):
    with patch("brain.core.LLMRouter") as MockRouter, \
         patch("brain.core.VectorStore") as MockVStore:
        MockRouter.return_value.route.return_value = ("Sure.", "cloud")
        MockRouter.return_value.local.is_available.return_value = False
        MockVStore.return_value.search.return_value = []
        MockVStore.return_value.count.return_value = 0

        lou = PocketLou(config_path=config_path)
        lou.think("Test")
        lou.clear_session()
        assert len(lou.session) == 0


def test_status_keys(config_path):
    with patch("brain.core.LLMRouter") as MockRouter, \
         patch("brain.core.VectorStore") as MockVStore:
        MockRouter.return_value.local.is_available.return_value = False
        MockVStore.return_value.count.return_value = 3

        lou = PocketLou(config_path=config_path)
        s = lou.status()

    assert "mode" in s
    assert "session_messages" in s
    assert "local_llm_available" in s
    assert "vector_store_entries" in s
    assert "profile_loaded" in s
