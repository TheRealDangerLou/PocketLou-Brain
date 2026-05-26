"""
Phase 2 — Text-to-Speech via Piper TTS (offline, human-sounding).

Target: Bluetooth earpiece, single ear, discrete.
Chosen for: quality + latency on constrained Pi Zero hardware.
Voice target: en_US-lessac-medium (natural, not robotic).
"""

from __future__ import annotations
from typing import Generator, Optional


class PiperTTS:
    """Offline TTS. Human-sounding. Low latency. Nothing to the cloud."""

    def __init__(
        self,
        voice: str = "en_US-lessac-medium",
        model_path: Optional[str] = None,
    ):
        self._voice = voice
        self._model_path = model_path
        self._model = None

    def load(self) -> bool:
        try:
            from piper import PiperVoice
            self._model = PiperVoice.load(self._model_path or self._voice)
            return True
        except ImportError:
            return False

    def speak(self, text: str) -> bytes:
        """Generate audio bytes for the given text."""
        if not self._model:
            raise RuntimeError("Piper model not loaded. Call load() first.")
        raise NotImplementedError("Phase 2: TTS audio generation")

    def speak_stream(self, text: str) -> Generator[bytes, None, None]:
        """Stream audio chunks directly to Bluetooth earpiece."""
        raise NotImplementedError("Phase 2: TTS streaming to Bluetooth")

    def is_available(self) -> bool:
        return self._model is not None
