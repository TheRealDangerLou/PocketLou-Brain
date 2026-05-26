#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     POCKET LOU — BRAIN INSTALLER     ║"
echo "║         Phase 1 — Desktop            ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Core — always required
echo "→ Installing core dependencies..."
pip install anthropic click rich python-dotenv

# Local LLM
echo ""
read -p "Install local LLM support (llama-cpp-python)? Requires ~500MB. [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Installing llama-cpp-python..."
    pip install "llama-cpp-python"
    echo ""
    echo "  After install, download the model:"
    echo "  mkdir -p models"
    echo "  # Download Llama 3 8B Q4_K_M GGUF from HuggingFace"
    echo "  # Place at: models/llama-3-8b-q4_k_m.gguf"
fi

# Vector memory
echo ""
read -p "Install vector memory (chromadb + sentence-transformers)? Requires ~1GB. [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Installing chromadb and sentence-transformers..."
    pip install chromadb sentence-transformers
fi

# Dev tools
echo ""
read -p "Install dev tools (pytest)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Installing pytest..."
    pip install pytest pytest-asyncio
fi

# Environment setup
echo ""
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "→ Created .env from .env.example"
    echo "  Add your ANTHROPIC_API_KEY to .env"
else
    echo "→ .env already exists — skipping"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║              READY                   ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Start chatting:"
echo "  python main.py chat"
echo ""
echo "Run tests:"
echo "  pytest tests/ -v"
echo ""
echo "RLL — Rose, Lily, Levi."
echo ""
