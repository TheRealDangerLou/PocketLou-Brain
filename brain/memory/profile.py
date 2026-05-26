"""
Profile Manager — loads and serves Lou's full context.

lou.json is the source of truth. It's a living document.
Update it as Lou's life evolves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProfileManager:
    """Serves the right slice of Lou's profile for each mode."""

    # Each mode gets the keys most relevant to its purpose
    MODE_CONTEXT_KEYS: dict[str, list[str]] = {
        "STANDARD": [
            "identity", "career", "family", "sobriety",
            "values", "active_projects", "voice_and_communication",
        ],
        "ACTOR": [
            "identity", "career", "active_projects", "voice_and_communication",
        ],
        "TRANSLATION": [
            "identity", "languages", "voice_and_communication",
        ],
        "ACTIVE_LISTEN": [
            "identity", "values", "active_projects", "voice_and_communication",
        ],
        "EPIPHANY": [
            "identity", "values", "active_projects",
            "spiritual_framework", "voice_and_communication",
        ],
        "CONSPIRACY": [
            "identity", "spiritual_framework", "values", "voice_and_communication",
        ],
    }

    def __init__(self, config: dict):
        self._path = Path(config["memory"]["profile_path"])
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            self._data = json.loads(self._path.read_text(encoding="utf-8"))

    def get_context(self, mode: str) -> dict:
        keys = self.MODE_CONTEXT_KEYS.get(mode, list(self._data.keys()))
        return {k: self._data[k] for k in keys if k in self._data}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def get_all(self) -> dict:
        return self._data.copy()

    def update(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
