"""
Session Memory — in-memory conversation history for the current session.

Cleared on /clear or new session start.
Persists across think() calls within a session.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional


@dataclass
class Message:
    role: str
    content: str


class SessionMemory:
    """Rolling window of recent messages. Bounded by config max."""

    def __init__(self, config: dict):
        self._max = config["memory"].get("max_session_messages", 20)
        self._messages: Deque[Message] = deque(maxlen=self._max)

    def add_message(self, role: str, content: str) -> None:
        self._messages.append(Message(role=role, content=content))

    def get_recent(self, n: Optional[int] = None) -> list[dict]:
        msgs = list(self._messages)
        if n is not None:
            msgs = msgs[-n:]
        return [{"role": m.role, "content": m.content} for m in msgs]

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
