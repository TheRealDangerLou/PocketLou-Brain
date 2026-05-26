"""
Phase 3 — ERM Coin Vibration Motor Controller.

Feedback language:
- 1 buzz → active / listening
- 2 buzzes → mode switched
- 3 buzzes → 5-minute shutoff warning
- 1 firm buzz → action confirmed
"""

from __future__ import annotations

import time


class HapticFeedback:
    """ERM motor on GPIO 27 (BCM). Simple on/off control."""

    PATTERNS: dict[str, list[tuple[float, float]]] = {
        "active":          [(0.08, 0.05)],
        "mode_switch":     [(0.08, 0.05), (0.08, 0.05)],
        "shutoff_warning": [(0.08, 0.05), (0.08, 0.05), (0.08, 0.05)],
        "confirm":         [(0.2, 0.1)],
        "error":           [(0.05, 0.03)] * 4,
    }

    def __init__(self, pin: int = 27):
        self._pin = pin
        self._gpio = None

    def init(self) -> bool:
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT, initial=GPIO.LOW)
            self._gpio = GPIO
            return True
        except ImportError:
            return False

    def buzz(self, pattern: str = "active") -> None:
        if not self.is_available():
            return
        pulses = self.PATTERNS.get(pattern, self.PATTERNS["active"])
        for on_s, off_s in pulses:
            self._gpio.output(self._pin, self._gpio.HIGH)
            time.sleep(on_s)
            self._gpio.output(self._pin, self._gpio.LOW)
            time.sleep(off_s)

    def raw_buzz(self, duration_ms: int = 100) -> None:
        if not self.is_available():
            return
        self._gpio.output(self._pin, self._gpio.HIGH)
        time.sleep(duration_ms / 1000)
        self._gpio.output(self._pin, self._gpio.LOW)

    def is_available(self) -> bool:
        return self._gpio is not None

    def cleanup(self) -> None:
        if self._gpio:
            self._gpio.cleanup()
