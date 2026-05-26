"""
Root-level mode registry.

Each mode defines its own config: temperature, max_tokens, preferred backend,
description. The brain uses this to tune LLM behavior per mode.
"""

from modes.standard      import StandardMode
from modes.active_listen import ActiveListenMode
from modes.translation   import TranslationMode
from modes.actor         import ActorMode
from modes.epiphany      import EpiphanyMode
from modes.conspiracy    import ConspiracyMode

_REGISTRY: dict[str, type] = {
    "STANDARD":      StandardMode,
    "ACTIVE_LISTEN": ActiveListenMode,
    "TRANSLATION":   TranslationMode,
    "ACTOR":         ActorMode,
    "EPIPHANY":      EpiphanyMode,
    "CONSPIRACY":    ConspiracyMode,
}


def get_mode(name: str):
    """Instantiate a mode by name (case-insensitive)."""
    cls = _REGISTRY.get(name.upper())
    if cls is None:
        raise ValueError(
            f"Unknown mode: {name!r}. "
            f"Valid: {', '.join(_REGISTRY)}"
        )
    return cls()


def list_modes() -> list[str]:
    return list(_REGISTRY.keys())


__all__ = [
    "get_mode",
    "list_modes",
    "StandardMode",
    "ActiveListenMode",
    "TranslationMode",
    "ActorMode",
    "EpiphanyMode",
    "ConspiracyMode",
]
