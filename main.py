#!/usr/bin/env python3
"""
Pocket Lou — Phase 1 Entry Point

Convenience launcher. Delegates to brain/brain.py.

Usage:
    python main.py                   # STANDARD mode
    python main.py --mode ACTOR      # ACTOR mode
    python main.py --mode CONSPIRACY
"""

import sys
from pathlib import Path

# Project root on path
sys.path.insert(0, str(Path(__file__).parent))

from brain.brain import PocketLouBrain, _print_banner, MODES


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pocket Lou Brain — Phase 1 Desktop Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Modes: {', '.join(MODES)}\n\nRLL — Rose, Lily, Levi.",
    )
    parser.add_argument(
        "--mode", "-m",
        default="STANDARD",
        metavar="MODE",
        help=f"Starting mode (default: STANDARD)",
    )
    args = parser.parse_args()

    try:
        brain = PocketLouBrain(mode=args.mode.upper())
    except ValueError as e:
        print(f"[error] {e}")
        sys.exit(1)

    brain.run()


if __name__ == "__main__":
    main()
