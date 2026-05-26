#!/usr/bin/env bash
# PocketLou — Pi Boot Script
# Phase 3: Runs on Raspberry Pi Zero 2W at startup
# Add to /etc/rc.local or as a systemd service

set -euo pipefail

POCKET_LOU_DIR="/home/pi/PocketLou-Brain"
LOG_FILE="/home/pi/pocket_lou.log"
VENV="$POCKET_LOU_DIR/.venv"

echo "$(date) — Pocket Lou booting..." >> "$LOG_FILE"

# Activate virtual environment
if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
fi

# Load environment variables
if [ -f "$POCKET_LOU_DIR/.env" ]; then
    export $(grep -v '^#' "$POCKET_LOU_DIR/.env" | xargs)
fi

cd "$POCKET_LOU_DIR"

# Haptic feedback: 1 buzz = booted and ready
python -c "
from hardware.haptic import HapticFeedback
h = HapticFeedback()
if h.init():
    h.buzz('active')
" 2>/dev/null || true

echo "$(date) — Pocket Lou ready." >> "$LOG_FILE"

# Phase 3: Start voice pipeline
# python -m voice.pipeline --mode STANDARD &

# Phase 1: Start brain (terminal mode only, for debugging on Pi via SSH)
# python brain/brain.py --mode STANDARD
