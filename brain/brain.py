#!/usr/bin/env python3
"""
PocketLou Brain — Core Orchestrator Loop
God-tier upgrade: multi-model routing + long-term memory + live web search

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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Ensure project root is on path when running this file directly
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from brain.persona.system_prompt import build_system_prompt, MODES
from brain.llm.router import LLMRouter
from brain.memory.long_term_memory import LongTermMemory


@dataclass
class ThinkResult:
    response:   str
    latency_ms: int
    backend:    str
    mode:       str
    memories_injected: bool = False


class PocketLouBrain:
    """
    The brain. One operator. RLL.

    Phase 1  — Multi-model cloud (Claude Sonnet + GPT-4o-mini + Perplexity)
    Phase 1  — Long-term memory (ChromaDB semantic store)
    Phase 1  — Live web search (auto-triggered)
    Phase 2  — Voice pipeline (Whisper + Piper)
    Phase 3+ — Local-first (Llama 3 8B) with cloud fallback
    """

    def __init__(self, mode: str = "STANDARD"):
        self.router = LLMRouter()
        self.ltm    = LongTermMemory()
        self.history: list[dict] = []
        self.profile = self._load_profile()
        self.mode = "STANDARD"
        self.set_mode(mode)
        self._last_backend = "—"

    # ── Profile ──────────────────────────────────────────────────────────────

    def _load_profile(self) -> dict:
        path = Path(__file__).parent / "persona" / "lou_profile.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"[warning] Profile not found: {path}")
            return {}

    # ── Mode ─────────────────────────────────────────────────────────────────

    def set_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode not in MODES:
            raise ValueError(
                f"Unknown mode: {mode!r}. Valid: {', '.join(MODES)}"
            )
        self.mode = mode

    # ── Core think loop ───────────────────────────────────────────────────────

    def think(self, user_input: str) -> ThinkResult:
        """
        One call = one full brain cycle.

        1. Build system prompt with Lou's full persona
        2. Inject relevant long-term memories
        3. Route to best model (web search / GPT-4o-mini / Claude Sonnet)
        4. Store exchange in long-term memory
        5. Return ThinkResult
        """
        # Build base system prompt
        system = build_system_prompt(self.mode, self.profile)

        # Inject relevant long-term memories
        memory_context = self.ltm.inject_memories(user_input)
        memories_injected = bool(memory_context)
        if memory_context:
            system += f"\n\n{memory_context}"

        # Add user message to history
        self.history.append({"role": "user", "content": user_input})

        # Route to best model
        start = time.monotonic()
        response, backend = self.router.route(
            messages=self.history,
            system_prompt=system,
            mode=self.mode,
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        # Store in session + long-term memory
        self.history.append({"role": "assistant", "content": response})
        self.ltm.store(user_input, response, mode=self.mode)
        self._last_backend = backend

        return ThinkResult(
            response=response,
            latency_ms=latency_ms,
            backend=backend,
            mode=self.mode,
            memories_injected=memories_injected,
        )

    # ── Session ───────────────────────────────────────────────────────────────

    def clear_session(self) -> None:
        self.history.clear()

    def status(self) -> dict:
        return {
            "mode":               self.mode,
            "session_messages":   len(self.history),
            "profile_loaded":     bool(self.profile),
            "long_term_memories": self.ltm.count(),
            "memory_available":   self.ltm.is_available(),
            "web_search":         self.router._web_search.is_available(),
            "last_backend":       self._last_backend,
        }

    # ── Terminal loop ─────────────────────────────────────────────────────────

    def run(self) -> None:
        """Interactive terminal session."""
        _print_banner(self.mode, self.ltm.count())

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
                result = self.think(raw)
                print(f"\nPocket Lou: {result.response}")
                _print_meta(result)
            except Exception as e:
                print(f"\n[error] {e}")

    def _handle_command(self, raw: str) -> bool:
        """Handle /commands. Returns False to quit, True to continue."""
        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

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
            s = self.status()
            for k, v in s.items():
                print(f"  {k}: {v}")

        elif cmd == "/clear":
            self.clear_session()
            print("Session cleared.")

        elif cmd == "/memory":
            print(f"  Long-term memories: {self.ltm.count()}")
            print(f"  Available: {self.ltm.is_available()}")

        elif cmd == "/recall":
            if arg:
                memories = self.ltm.recall(arg, n_results=5)
                if not memories:
                    print("  No relevant memories found.")
                for m in memories:
                    ts = m.get("timestamp", "")[:10]
                    print(f"  [{ts}] {m['text'][:100]}...")
            else:
                print("  Usage: /recall <query>")

        elif cmd == "/help":
            print(
                "  /mode <MODE>     Switch operating mode\n"
                "  /modes           List all modes\n"
                "  /status          Full system status\n"
                "  /memory          Memory stats\n"
                "  /recall <query>  Search long-term memory\n"
                "  /clear           Clear session history\n"
                "  /quit            Exit"
            )

        else:
            print("  Unknown command. Type /help")

        return True


# ── Display helpers ───────────────────────────────────────────────────────────

def _print_banner(mode: str, memory_count: int = 0) -> None:
    print("\n" + "═" * 58)
    print("  POCKET LOU — BRAIN  v0.2  [God-tier upgrade]")
    print(f"  Mode: {mode}  |  Memories: {memory_count}")
    print("  RLL — Rose, Lily, Levi")
    print("═" * 58)
    print("  /mode  /modes  /status  /memory  /recall  /clear  /quit")
    print("═" * 58)


def _print_meta(result: ThinkResult) -> None:
    flag = "✓" if result.latency_ms < 2000 else "△" if result.latency_ms < 4000 else "✗"
    mem  = " · mem" if result.memories_injected else ""
    print(f"\n  {flag} {result.latency_ms}ms · {result.backend}{mem}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Pocket Lou Brain — God-tier upgrade"
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
