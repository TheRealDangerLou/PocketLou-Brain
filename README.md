# PocketLou-Brain

The intelligence layer for Pocket Lou — a private, sovereign AI device built for one operator: Louis Octeau Piché.

**Current phase: Phase 1 — Brain (Desktop)**

---

## Quick start

```bash
git clone https://github.com/TheRealDangerLou/PocketLou-Brain.git
cd PocketLou-Brain

bash scripts/install.sh

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

python main.py chat
```

## Modes

| Mode | Use it for |
|---|---|
| `STANDARD` | Everything — full Lou context, ready for anything |
| `ACTIVE_LISTEN` | Absorb and coach passively |
| `TRANSLATION` | Real-time translation, whisper delivery |
| `ACTOR` | Script, audition, character, casting |
| `EPIPHANY` | Full brainstorm — no idea gets shut down |
| `CONSPIRACY` | Unrestricted rabbit hole |

Switch modes in chat: `/mode ACTOR`

## CLI commands

```
/mode <MODE>      Switch operating mode
/status           System status (LLM, memory, session)
/remember <text>  Store something to long-term memory
/clear            Clear current session
/modes            List all modes
/quit             Exit
```

## Architecture

```
brain/
├── core.py           Main orchestrator (PocketLou class)
├── llm/
│   ├── local_llm.py  llama.cpp inference (Llama 3 8B Q4_K_M)
│   ├── cloud_llm.py  Claude API (burst mode)
│   └── router.py     Smart routing between local and cloud
├── memory/
│   ├── profile.py    Lou's profile loader and context manager
│   ├── vector_store.py  ChromaDB semantic memory
│   └── session.py    In-session conversation history
├── modes/            Six operating modes with distinct prompts
└── prompt/
    └── builder.py    System prompt assembly

voice/              Phase 2 stubs — Whisper STT + Piper TTS
hardware/           Phase 3 stubs — GPIO button + haptic motor
config/             Settings and mode configuration
data/profiles/      Lou's profile (lou.json)
```

## Development phases

- **Phase 1** — Brain (desktop) ← you are here
- **Phase 2** — Voice pipeline (Whisper + Piper)
- **Phase 3** — Port to Raspberry Pi Zero 2W
- **Phase 4** — Physical shell (3D printed PETG, RLL engraved)
- **Phase 5** — Memory and persona training
- **Phase 6** — Private cloud sync + companion app

## Local LLM setup

Download the model (requires ~5GB):

```bash
mkdir -p models
# Download Llama 3 8B Q4_K_M GGUF from HuggingFace
# Place at: models/llama-3-8b-q4_k_m.gguf
```

Without the model file, the system automatically bursts to Claude API.

## Running tests

```bash
pytest tests/ -v
```

---

RLL — Rose, Lily, Levi. That's why this exists.
