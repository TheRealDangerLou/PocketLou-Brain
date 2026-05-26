"""Tests for operating modes and prompt builder."""

import json
import pytest

from brain.modes import get_mode
from brain.modes.base import BaseMode
from brain.prompt.builder import PromptBuilder


ALL_MODES = ["STANDARD", "ACTIVE_LISTEN", "TRANSLATION", "ACTOR", "EPIPHANY", "CONSPIRACY"]


# ── Mode registry ────────────────────────────────────────────────────────────

def test_all_modes_instantiate():
    for name in ALL_MODES:
        mode = get_mode(name)
        assert isinstance(mode, BaseMode)


def test_mode_names_match():
    for name in ALL_MODES:
        assert get_mode(name).name == name


def test_case_insensitive():
    assert get_mode("actor").name == "ACTOR"
    assert get_mode("conspiracy").name == "CONSPIRACY"
    assert get_mode("Epiphany").name == "EPIPHANY"


def test_invalid_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        get_mode("UNKNOWN")


# ── Mode system prompts ──────────────────────────────────────────────────────

def test_all_modes_have_nonempty_prompt():
    for name in ALL_MODES:
        mode = get_mode(name)
        assert isinstance(mode.system_prompt_additions, str)
        assert len(mode.system_prompt_additions) > 10


def test_conspiracy_covers_lou_topics():
    prompt = get_mode("CONSPIRACY").system_prompt_additions
    assert "Anunnaki" in prompt
    assert "Sumerian" in prompt
    assert "paranormal" in prompt.lower()
    assert "Gateway" in prompt


def test_actor_covers_lou_projects():
    prompt = get_mode("ACTOR").system_prompt_additions
    assert "Broken Oath" in prompt or "Last Fix" in prompt or "audition" in prompt


def test_epiphany_is_expansive():
    prompt = get_mode("EPIPHANY").system_prompt_additions
    assert any(word in prompt.lower() for word in ["never", "shut", "expand", "amplif"])


def test_translation_includes_languages():
    prompt = get_mode("TRANSLATION").system_prompt_additions
    assert "French" in prompt
    assert "English" in prompt


def test_active_listen_is_minimal():
    prompt = get_mode("ACTIVE_LISTEN").system_prompt_additions
    assert "short" in prompt.lower() or "minimal" in prompt.lower() or "brief" in prompt.lower()


# ── Mode pre/post processing ─────────────────────────────────────────────────

def test_default_pre_post_process_passthrough():
    for name in ALL_MODES:
        mode = get_mode(name)
        text = "test message"
        assert mode.pre_process(text) == text
        assert mode.post_process(text) == text


# ── Prompt builder ───────────────────────────────────────────────────────────

@pytest.fixture
def builder():
    config = {"llm": {}, "memory": {}}
    return PromptBuilder(config)


@pytest.fixture
def sample_profile():
    return {
        "identity": {"name": "Louis Octeau Piché", "location": "Hudson, QC"},
        "career": {
            "primary": "Full-time actor",
            "rep": {"name": "Constantine", "agency": "Top Talents", "city": "Toronto"},
        },
        "languages": {"french": "native", "english": "fluent"},
        "family": {
            "wife": "Mackenzie",
            "children": [
                {"name": "Rosie", "age_approx": 5.5},
                {"name": "Levi", "status": "incoming"},
            ],
        },
        "values": ["privacy", "family"],
    }


def test_system_prompt_contains_identity(builder, sample_profile):
    prompt = builder.build_system_prompt("STANDARD", sample_profile, [])
    assert "Louis" in prompt or "Louie" in prompt
    assert "Pocket Lou" in prompt


def test_system_prompt_contains_rll(builder, sample_profile):
    prompt = builder.build_system_prompt("STANDARD", sample_profile, [])
    assert "RLL" in prompt


def test_system_prompt_contains_mode(builder, sample_profile):
    prompt = builder.build_system_prompt("ACTOR", sample_profile, [])
    assert "ACTOR" in prompt


def test_system_prompt_includes_memories(builder, sample_profile):
    memories = ["Lou talked about The Broken Oath script last session."]
    prompt = builder.build_system_prompt("STANDARD", sample_profile, memories)
    assert "Broken Oath" in prompt


def test_build_messages_appends_user(builder):
    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hey"}]
    messages = builder.build_messages(history, "New question")
    assert messages[-1] == {"role": "user", "content": "New question"}
    assert len(messages) == 3


def test_build_messages_empty_history(builder):
    messages = builder.build_messages([], "First message")
    assert messages == [{"role": "user", "content": "First message"}]
