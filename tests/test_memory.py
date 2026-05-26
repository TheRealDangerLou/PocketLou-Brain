"""Tests for the memory subsystem."""

import json
import pytest

from brain.memory.session import SessionMemory
from brain.memory.profile import ProfileManager


@pytest.fixture
def session_config():
    return {"memory": {"max_session_messages": 5}}


@pytest.fixture
def profile_config(tmp_path):
    data = {
        "identity": {"name": "Louis Octeau Piché", "location": "Hudson, QC"},
        "career": {"primary": "Full-time actor", "rep": {"name": "Constantine", "agency": "Top Talents", "city": "Toronto"}},
        "languages": {"french": "native", "english": "fluent"},
        "family": {
            "wife": "Mackenzie",
            "children": [
                {"name": "Rosie", "age_approx": 5.5},
                {"name": "Lily", "age_approx": 2.5},
                {"name": "Levi", "status": "incoming"},
            ],
        },
        "sobriety": {"sober": True, "significance": "Core to identity."},
        "spiritual_framework": ["Hemi-Sync", "Gateway Process"],
        "active_projects": [
            {"name": "Actor's Companion", "description": "Rehearsal app"},
        ],
        "values": ["privacy", "family"],
        "voice_and_communication": {
            "style": "Direct.",
            "dislikes": ["hedging"],
            "prefers": ["straight talk"],
        },
    }
    p = tmp_path / "lou.json"
    p.write_text(json.dumps(data))
    return {"memory": {"profile_path": str(p)}}


# ── SessionMemory ────────────────────────────────────────────────────────────

def test_add_and_retrieve(session_config):
    s = SessionMemory(session_config)
    s.add_message("user", "Hello")
    s.add_message("assistant", "Hey Lou")
    msgs = s.get_recent()
    assert len(msgs) == 2
    assert msgs[0] == {"role": "user", "content": "Hello"}
    assert msgs[1] == {"role": "assistant", "content": "Hey Lou"}


def test_max_messages_enforced(session_config):
    s = SessionMemory(session_config)
    for i in range(10):
        s.add_message("user", f"msg {i}")
    assert len(s.get_recent()) == 5


def test_oldest_messages_dropped(session_config):
    s = SessionMemory(session_config)
    for i in range(7):
        s.add_message("user", f"msg {i}")
    msgs = s.get_recent()
    assert msgs[0]["content"] == "msg 2"
    assert msgs[-1]["content"] == "msg 6"


def test_clear(session_config):
    s = SessionMemory(session_config)
    s.add_message("user", "Hello")
    s.clear()
    assert len(s) == 0
    assert s.get_recent() == []


def test_get_recent_n(session_config):
    s = SessionMemory(session_config)
    for i in range(4):
        s.add_message("user", f"msg {i}")
    assert len(s.get_recent(n=2)) == 2
    assert s.get_recent(n=2)[-1]["content"] == "msg 3"


def test_len(session_config):
    s = SessionMemory(session_config)
    s.add_message("user", "a")
    s.add_message("assistant", "b")
    assert len(s) == 2


# ── ProfileManager ───────────────────────────────────────────────────────────

def test_profile_loads(profile_config):
    p = ProfileManager(profile_config)
    assert p.get("identity")["name"] == "Louis Octeau Piché"


def test_profile_get_context_actor(profile_config):
    p = ProfileManager(profile_config)
    ctx = p.get_context("ACTOR")
    assert "identity" in ctx
    assert "career" in ctx
    assert "active_projects" in ctx


def test_profile_get_context_translation(profile_config):
    p = ProfileManager(profile_config)
    ctx = p.get_context("TRANSLATION")
    assert "languages" in ctx
    assert "identity" in ctx


def test_profile_update_and_persist(profile_config, tmp_path):
    p = ProfileManager(profile_config)
    p.update("test_key", "test_value")
    assert p.get("test_key") == "test_value"

    # Reload to verify persistence
    p2 = ProfileManager(profile_config)
    assert p2.get("test_key") == "test_value"


def test_profile_get_all(profile_config):
    p = ProfileManager(profile_config)
    all_data = p.get_all()
    assert isinstance(all_data, dict)
    assert "identity" in all_data


def test_profile_missing_file():
    p = ProfileManager({"memory": {"profile_path": "/nonexistent/lou.json"}})
    assert p.get_all() == {}
