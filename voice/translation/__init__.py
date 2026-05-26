"""
Phase 2 — Real-time Translation via NLLB-200 (Meta, offline).

200 languages. No internet required.
Lou's languages: French (native), English (fluent), Italian (conv.), Spanish (basic).

NLLB-200 model sizes:
  - nllb-200-distilled-600M  (~1.2GB, fits Pi Zero with patience)
  - nllb-200-distilled-1.3B  (~2.5GB, Pi 4/5 recommended)
  - nllb-200-1.3B            (~2.5GB)
  - nllb-200-3.3B            (~6.6GB, desktop only)

Phase 2 target: distilled-600M on Pi Zero 2W.
"""

from __future__ import annotations
from typing import Optional


# NLLB-200 FLORES-200 language codes for Lou's languages
LANGUAGE_CODES = {
    "french":  "fra_Latn",
    "english": "eng_Latn",
    "italian": "ita_Latn",
    "spanish": "spa_Latn",
}


class NLLBTranslator:
    """Offline translation via Meta's NLLB-200. 200 languages, no cloud."""

    DEFAULT_MODEL = "facebook/nllb-200-distilled-600M"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model_name = model_name
        self._model = None
        self._tokenizer = None

    def load(self) -> bool:
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self._model_name)
            return True
        except ImportError:
            return False

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """
        Translate text between any two supported languages.

        Args:
            text: Input text to translate
            source_lang: FLORES-200 language code (e.g. "fra_Latn")
            target_lang: FLORES-200 language code (e.g. "eng_Latn")
        """
        if not self._model or not self._tokenizer:
            raise RuntimeError("NLLB model not loaded. Call load() first.")

        raise NotImplementedError("Phase 2: NLLB-200 inference")

    def detect_and_translate(self, text: str, target_lang: str = "eng_Latn") -> str:
        """Auto-detect source language and translate to target."""
        raise NotImplementedError("Phase 2: Language detection + translation")

    def is_available(self) -> bool:
        return self._model is not None
