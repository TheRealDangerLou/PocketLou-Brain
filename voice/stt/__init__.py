"""
Phase 2 — Speech-to-Text via OpenAI Whisper (offline).

Target hardware: ReSpeaker 2-Mic Pi HAT on Raspberry Pi Zero 2W.
Model: whisper base (best size/speed trade-off for Pi Zero).
"""

from __future__ import annotations
from typing import Optional


class WhisperSTT:
    """Offline speech-to-text. No audio leaves the device."""

    SUPPORTED_MODELS = ["tiny", "base", "small"]  # base is Phase 2 target

    def __init__(self, model_size: str = "base"):
        self._model_size = model_size
        self._model = None

    def load(self) -> bool:
        try:
            import whisper
            self._model = whisper.load_model(self._model_size)
            return True
        except ImportError:
            return False

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        if not self._model:
            raise RuntimeError("Whisper model not loaded. Call load() first.")
        result = self._model.transcribe(audio_path, language=language)
        return result["text"].strip()

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Phase 2: stream from ReSpeaker mic via sounddevice."""
        raise NotImplementedError("Phase 2: streaming transcription from mic")

    def is_available(self) -> bool:
        return self._model is not None
