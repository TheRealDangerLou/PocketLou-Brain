"""TRANSLATION — Real-time translation, whisper delivery. NLLB-200 in Phase 2."""


class TranslationMode:
    name = "TRANSLATION"
    description = "Real-time translation — whispers the response"
    temperature = 0.3
    max_tokens = 250
    prefer_local = False  # cloud preferred for translation quality
    haptic_on_switch = "mode_switch"

    # Phase 2: NLLB-200 handles local translation
    # Supported language pairs: 200 languages via Meta's NLLB-200
    source_auto_detect = True
