"""
Phase 3 — GPIO Tactile Button Controller.

Interaction model:
- Tap  → toggle continuous hands-free conversation
- Hold → single exchange (push-to-talk)

Haptic feedback confirms state changes.
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, Optional


class ButtonEvent(Enum):
    TAP = "tap"
    HOLD = "hold"
    RELEASE = "release"


class ButtonController:
    """Tactile button on GPIO 17 (BCM). Pull-up, active-low."""

    HOLD_THRESHOLD_MS = 800
    DEBOUNCE_MS = 50

    def __init__(self, pin: int = 17):
        self._pin = pin
        self._gpio = None
        self._on_tap: Optional[Callable] = None
        self._on_hold: Optional[Callable] = None
        self._continuous_mode = False

    def init(self) -> bool:
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._gpio = GPIO
            return True
        except ImportError:
            return False

    def on_tap(self, callback: Callable) -> None:
        self._on_tap = callback

    def on_hold(self, callback: Callable) -> None:
        self._on_hold = callback

    def toggle_continuous(self) -> bool:
        self._continuous_mode = not self._continuous_mode
        return self._continuous_mode

    def start_listening(self) -> None:
        # Phase 3: event loop with GPIO interrupt
        raise NotImplementedError("Phase 3: GPIO event loop")

    def stop(self) -> None:
        if self._gpio:
            self._gpio.cleanup()

    def is_available(self) -> bool:
        return self._gpio is not None
