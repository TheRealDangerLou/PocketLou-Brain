"""
Cloud Sync — transcript and memory sync to Lou's private cloud.

Phase 6: Self-hosted, encrypted, Lou's keys only.
Phase 1: Stub — no data leaves the device.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class CloudSync:
    """
    Syncs session transcripts and memories to Lou's private cloud.

    Phase 6 implementation requirements:
    - Self-hosted server (Lou's hardware, Lou's keys)
    - End-to-end encrypted
    - Never routed through third-party cloud storage
    - Accessible from Actor's Companion app (companion app reads, device writes)
    """

    def __init__(self, endpoint: Optional[str] = None, token: Optional[str] = None):
        self._endpoint = endpoint
        self._token = token

    def push_transcript(self, session_id: str, messages: list[dict]) -> None:
        """Upload a completed session transcript to private cloud."""
        raise NotImplementedError("Phase 6: Private cloud sync not yet implemented")

    def pull_memories(self, limit: int = 50) -> list[dict]:
        """Fetch recent memories from cloud for context injection."""
        raise NotImplementedError("Phase 6: Private cloud sync not yet implemented")

    def push_profile_update(self, key: str, value) -> None:
        """Sync a profile update across devices."""
        raise NotImplementedError("Phase 6: Private cloud sync not yet implemented")

    def is_connected(self) -> bool:
        return False

    def save_local(self, session_id: str, messages: list[dict], path: str = "data/sessions") -> None:
        """
        Phase 1 fallback: save transcript locally in JSON.
        Good enough for Phase 1 testing and debugging.
        """
        sessions_dir = Path(path)
        sessions_dir.mkdir(parents=True, exist_ok=True)
        out = sessions_dir / f"{session_id}.json"
        out.write_text(
            json.dumps({"session_id": session_id, "messages": messages}, indent=2),
            encoding="utf-8",
        )
