from brain.modes.base import BaseMode
from brain.modes.standard import StandardMode
from brain.modes.active_listen import ActiveListenMode
from brain.modes.translation import TranslationMode
from brain.modes.actor import ActorMode
from brain.modes.epiphany import EpiphanyMode
from brain.modes.conspiracy import ConspiracyMode

_MODE_MAP: dict[str, type[BaseMode]] = {
    "STANDARD": StandardMode,
    "ACTIVE_LISTEN": ActiveListenMode,
    "TRANSLATION": TranslationMode,
    "ACTOR": ActorMode,
    "EPIPHANY": EpiphanyMode,
    "CONSPIRACY": ConspiracyMode,
}


def get_mode(name: str) -> BaseMode:
    cls = _MODE_MAP.get(name.upper())
    if cls is None:
        raise ValueError(
            f"Unknown mode: {name!r}. "
            f"Valid modes: {', '.join(_MODE_MAP)}"
        )
    return cls()


__all__ = [
    "get_mode",
    "BaseMode",
    "StandardMode",
    "ActiveListenMode",
    "TranslationMode",
    "ActorMode",
    "EpiphanyMode",
    "ConspiracyMode",
]
