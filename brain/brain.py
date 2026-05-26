#!/usr/bin/env python3
"""
PocketLou Brain — Core Orchestrator Loop
Phase 1: Terminal-testable with Claude API as cloud burst

Run from project root:
    python brain/brain.py
    python brain/brain.py --mode ACTOR
    python main.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Ensure project root is on path when running this file directly
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.persona.system_prompt import build_system_prompt, MODES
from cloud.claude_api import CloudBurst


class PocketLouBrain:
    """
    The brain. One operator. RLL.

    Phase 1  — Cloud burst via Claude API (you are here)
    Phase 2  — Voice pipeline (Whisper + Piper)
    Phase 3+ — Local-first (Llama 3 8B) with cloud fallback
    """

    def __init__(self, mode: str = "STANDARD"):
        self.cloud = CloudBurst()
        self.history: list[dict] = []
        self.profile = self._load_profile()
        self.mode = "STANDARD"
        self.set_mode(mode)

    # ── Profile ─────────────────────────────────────────────────────────────

    def _load_profile(self) -> dict:
        path = Path(__file__).parent / "persona" / "lou_profile.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"[warning] Profile not found: {path}")
            return {}

    # ── Mode ────────────────────────────────────────────────────────────────

    def set_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode not in MODES:
            raise ValueError(
                f"Unknown mode: {mode!r}. Valid: {', '.join(MODES)}"
            )
        self.mode = mode

    # ── Core think loop ──────────────────────────────────────────────────────

    def think(self, user_input: str) -> tuple[str, int]:
        """
        The core function. One call = one full brain cycle.
        Returns (response_text, latency_ms).
        """
        system = build_system_prompt(self.mode, self.profile)
        self.history.append({"role": "user", "content": user_input})

        start = time.monotonic()
        response = self.cloud.complete(messages=self.history, system=system)
        latency_ms = int((time.monotonic() - start) * 1000)

        self.history.append({"role": "assistant", "content": response})
        return response, latency_ms

    # ── Session ──────────────────────────────────────────────────────────────

    def clear_session(self) -> None:
        self.history.clear()

    def status(self) -> dict:
        return {
            "mode":               self.mode,
            "session_messages":   len(self.history),
            "profile_loaded":     bool(self.profile),
            "backend":            "cloud — Claude API (Phase 1)",
        }

    # ── Terminal loop ────────────────────────────────────────────────────────

    def run(self) -> None:
        """Interactive terminal session. Phase 1 entry point."""
        _print_banner(self.mode)

        while True:
            try:
                raw = input(f"\n[{self.mode}] Lou > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nShutting down. RLL.\n")
                break

            if not raw:
                continue

            if raw.startswith("/"):
                if not self._handle_command(raw):
                    break
                continue

            try:
                response, ms = self.think(raw)
                print(f"\nPocket Lou: {response}")
                latency_flag = "✓" if ms < 2000 else "△" if ms < 4000 else "✗"
                print(f"\n  {latency_flag} {ms}ms · {self.mode} · cloud")
            except Exception as e:
                print(f"\n[error] {e}")

    def _handle_command(self, raw: str) -> bool:
        """Handle /commands. Returns False to quit, True to continue."""
        parts = raw.split(None, 1)
        cmd  = parts[0].lower()
        arg  = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("/quit", "/exit", "/q"):
            print("\nShutting down. RLL.\n")
            return False

        elif cmd == "/mode":
            if arg:
                try:
                    self.set_mode(arg)
                    print(f"Mode → {self.mode}")
                except ValueError as e:
                    print(f"[error] {e}")
            else:
                print(f"Current: {self.mode}")
                print(f"Available: {', '.join(MODES)}")

        elif cmd == "/modes":
            for m in MODES:
                marker = "▶" if m == self.mode else " "
                print(f"  {marker} {m}")

        elif cmd == "/status":
            for k, v in self.status().items():
                print(f"  {k}: {v}")

        elif cmd == "/clear":
            self.clear_session()
            print("Session cleared.")

        elif cmd == "/help":
            print(
                "  /mode <MODE>   Switch operating mode\n"
                "  /modes         List all modes\n"
                "  /status        System status\n"
                "  /clear         Clear session history\n"
                "  /quit          Exit"
            )

        else:
            print("  Unknown command. Type /help")

        return True


# ── Banner ───────────────────────────────────────────────────────────────────

def _print_banner(mode: str) -> None:
    print("\n" + "═" * 54)
    print("  POCKET LOU — BRAIN  v0.1  [Phase 1 · Desktop]")
    print(f"  Mode: {mode}")
    print("  RLL — Rose, Lily, Levi")
    print("═" * 54)
    print("  /mode <MODE>  /modes  /status  /clear  /quit  /help")
    print("═" * 54)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Pocket Lou Brain — Phase 1 Terminal"
    )
    parser.add_argument(
        "--mode", "-m",
        default="STANDARD",
        choices=MODES,
        metavar="MODE",
        help=f"Starting mode. Options: {', '.join(MODES)} (default: STANDARD)",
    )
    args = parser.parse_args()

    brain = PocketLouBrain(mode=args.mode)
    brain.run()
