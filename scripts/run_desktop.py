#!/usr/bin/env python3
"""Quick desktop launcher for Phase 1 development."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

mode = sys.argv[1].upper() if len(sys.argv) > 1 else "STANDARD"

subprocess.run(
    [sys.executable, str(ROOT / "main.py"), "chat", "--mode", mode],
    cwd=str(ROOT),
)
