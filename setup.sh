#!/usr/bin/env bash
# PocketLou Brain — Phase 1 Setup
# Run this once to get the brain working from terminal.
set -euo pipefail

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      POCKET LOU — BRAIN  SETUP           ║"
echo "║      Phase 1 — Desktop / Terminal        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Python version check ─────────────────────────────────────────────────────
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required="3.11"
if [[ "$(printf '%s\n' "$required" "$python_version" | sort -V | head -n1)" != "$required" ]]; then
    echo "✗ Python $required+ required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# ── Virtual environment ──────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
echo "✓ Virtual environment active"

# ── Core dependencies (Phase 1 required) ────────────────────────────────────
echo ""
echo "→ Installing Phase 1 core dependencies..."
pip install --quiet anthropic python-dotenv rich click pytest pytest-asyncio
echo "✓ Core dependencies installed"

# ── Optional: local LLM ──────────────────────────────────────────────────────
echo ""
read -rp "Install local LLM support (llama-cpp-python, ~500MB)? [y/N] " llm_choice
if [[ "${llm_choice:-n}" =~ ^[Yy]$ ]]; then
    echo "→ Installing llama-cpp-python..."
    pip install --quiet llama-cpp-python
    mkdir -p brain/models
    echo "✓ Local LLM installed"
    echo ""
    echo "  Download the model:"
    echo "  See docs/download_model.md for full instructions."
    echo ""
    echo "  Quick download:"
    echo "  huggingface-cli download bartowski/Meta-Llama-3-8B-Instruct-GGUF \\"
    echo "    Meta-Llama-3-8B-Instruct-Q4_K_M.gguf --local-dir brain/models/"
fi

# ── Optional: vector memory ───────────────────────────────────────────────────
echo ""
read -rp "Install vector memory (chromadb + sentence-transformers, ~1GB)? [y/N] " mem_choice
if [[ "${mem_choice:-n}" =~ ^[Yy]$ ]]; then
    echo "→ Installing vector memory..."
    pip install --quiet chromadb sentence-transformers
    echo "✓ Vector memory installed"
fi

# ── Environment file ─────────────────────────────────────────────────────────
echo ""
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo ""
    echo "  !! ACTION REQUIRED:"
    echo "  Edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    echo "  Get your key at: console.anthropic.com"
else
    echo "✓ .env already exists"
fi

# ── Make scripts executable ───────────────────────────────────────────────────
chmod +x setup.sh
chmod +x hardware/boot.sh 2>/dev/null || true

# ── Smoke test ───────────────────────────────────────────────────────────────
echo ""
echo "→ Running smoke test..."
python3 -c "
import sys
sys.path.insert(0, '.')
from brain.persona.system_prompt import build_system_prompt, MODES
prompt = build_system_prompt('STANDARD', {})
assert 'Pocket Lou' in prompt
assert len(MODES) == 6
print('  ✓ Persona system — OK')
from cloud.claude_api import CloudBurst
cb = CloudBurst()
print('  ✓ Cloud API module — OK')
from modes import get_mode, list_modes
assert len(list_modes()) == 6
print('  ✓ Mode registry — OK')
"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║              READY                       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Start the brain:"
echo "    source .venv/bin/activate"
echo "    python brain/brain.py"
echo "    python brain/brain.py --mode ACTOR"
echo ""
echo "  Run tests:"
echo "    pytest tests/ -v"
echo ""
echo "  RLL — Rose, Lily, Levi."
echo ""
