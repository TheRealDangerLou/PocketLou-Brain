"""
PocketLou Brain — Core Orchestrator

One operator. One voice. RLL.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from brain.llm.router import LLMRouter
from brain.memory.profile import ProfileManager
from brain.memory.session import SessionMemory
from brain.memory.vector_store import VectorStore
from brain.modes import get_mode
from brain.modes.base import BaseMode
from brain.prompt.builder import PromptBuilder


@dataclass
class ThinkResult:
    response: str
    mode: str
    backend_used: str
    latency_ms: int
    tokens_used: Optional[int] = None


class PocketLou:
    """
    The brain. Loaded with Lou's full context.
    Route → think → remember. Under 2 seconds.
    """

    VALID_MODES = [
        "STANDARD",
        "ACTIVE_LISTEN",
        "TRANSLATION",
        "ACTOR",
        "EPIPHANY",
        "CONSPIRACY",
    ]

    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self._setup_env()
        self.profile = ProfileManager(self.config)
        self.session = SessionMemory(self.config)
        self.vector_store = VectorStore(self.config)
        self.router = LLMRouter(self.config)
        self.prompt_builder = PromptBuilder(self.config)
        self.current_mode: str = "STANDARD"
        self._mode_instance: BaseMode = get_mode("STANDARD")

    def _load_config(self, path: str) -> dict:
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        return json.loads(config_file.read_text())

    def _setup_env(self) -> None:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

    def switch_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Unknown mode: {mode}. Valid modes: {', '.join(self.VALID_MODES)}"
            )
        self.current_mode = mode
        self._mode_instance = get_mode(mode)

    def think(self, user_input: str) -> ThinkResult:
        start = time.monotonic()

        processed_input = self._mode_instance.pre_process(user_input)

        profile_context = self.profile.get_context(self.current_mode)
        recent_memories = self.vector_store.search(processed_input, k=5)
        session_history = self.session.get_recent()

        system_prompt = self.prompt_builder.build_system_prompt(
            mode=self.current_mode,
            profile=profile_context,
            memories=recent_memories,
        )
        messages = self.prompt_builder.build_messages(
            session_history=session_history,
            user_input=processed_input,
        )

        response, backend = self.router.route(
            messages=messages,
            system_prompt=system_prompt,
            mode=self.current_mode,
        )

        response = self._mode_instance.post_process(response)

        self.session.add_message("user", processed_input)
        self.session.add_message("assistant", response)

        self.vector_store.add(
            text=f"Lou said: {user_input}\nPocket Lou: {response}",
            metadata={"mode": self.current_mode, "timestamp": time.time()},
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)

        return ThinkResult(
            response=response,
            mode=self.current_mode,
            backend_used=backend,
            latency_ms=elapsed_ms,
        )

    def remember(self, text: str, metadata: Optional[dict] = None) -> None:
        self.vector_store.add(
            text=text,
            metadata=metadata or {"type": "manual", "timestamp": time.time()},
        )

    def clear_session(self) -> None:
        self.session.clear()

    def status(self) -> dict:
        return {
            "mode": self.current_mode,
            "session_messages": len(self.session),
            "local_llm_available": self.router.local.is_available(),
            "vector_store_entries": self.vector_store.count(),
            "profile_loaded": bool(self.profile.get_all()),
        }
