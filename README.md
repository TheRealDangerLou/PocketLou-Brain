# POCKET LOU — BRAIN

**Classification: TOP SECRET // EYES ONLY // TheRealDangerLou**

One-of-one. Personal sovereign AI for Louis Octeau Piché.  
Built to be worn on the hip on a Raspberry Pi Zero 2W.  
RLL — Rose, Lily, Levi. That's why this exists.

---

## Architecture — God-tier upgrade (v0.2)

```
┌─────────────────────────────────────────────────────────┐
│                    POCKET LOU BRAIN                     │
│                   brain/brain.py                        │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
  ┌─────────────┐ ┌────────────┐ ┌──────────────────┐
  │  Persona    │ │ LLM Router │ │  Long-Term Memory │
  │  + Profile  │ │ router.py  │ │  ChromaDB + embeds│
  └─────────────┘ └─────┬──────┘ └──────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
  ┌────────────┐ ┌────────────┐ ┌────────────────┐
  │ Perplexity │ │  GPT-4o-   │ │ Claude Sonnet  │
  │ Web Search │ │   mini     │ │  (primary +    │
  │ (live web) │ │  (fast)    │ │   fallback)    │
  └────────────┘ └────────────┘ └────────────────┘
```

### Routing priority (per query)
1. **Perplexity** — auto-triggered for live internet queries (news, scores, today's date, etc.)
2. **GPT-4o-mini** — fast conversational replies, ACTIVE_LISTEN mode
3. **Claude Sonnet** — actor, conspiracy, epiphany, reasoning, technical, default
4. **Claude fallback** — always available if only `ANTHROPIC_API_KEY` is set

### Long-term memory
- **ChromaDB** vector store — persistent across all sessions
- **Semantic search** — finds relevant memories by meaning, not keywords
- **Auto-categorizes** into: acting, family, projects, spiritual, fitness, conspiracy, general
- **Auto-injects** relevant memories into each system prompt
- Degrades gracefully if `chromadb` / `sentence-transformers` not installed

---

## Operating Modes

| Mode | LLM | Purpose |
|---|---|---|
| STANDARD | Claude Sonnet | Full Lou profile, ready for anything |
| ACTIVE_LISTEN | GPT-4o-mini | Always absorbing, coaches passively |
| TRANSLATION | Claude Sonnet | Real-time in ear, whispers response |
| ACTOR | Claude Sonnet | Script, audition, character, casting lens |
| EPIPHANY | Claude Sonnet | Full brainstorm partner, never shuts ideas down |
| CONSPIRACY | Claude Sonnet | Unrestricted, no guardrails, full rabbit hole |

---

## Quick start

```bash
git clone https://github.com/TheRealDangerLou/PocketLou-Brain.git
cd PocketLou-Brain

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY (required)
#             add OPENAI_API_KEY    (optional — enables GPT-4o-mini)
#             add PERPLEXITY_API_KEY (optional — enables live web search)

python brain/brain.py
python brain/brain.py --mode ACTOR
```

---

## Terminal commands

```
/mode <MODE>     Switch operating mode
/modes           List all modes
/status          Full system status (backends, memory, web search)
/memory          Memory stats
/recall <query>  Search long-term memory
/clear           Clear session history
/quit            Exit
```

---

## Project structure

```
PocketLou-Brain/
├── brain/
│   ├── brain.py              # Core orchestrator — main entry point
│   ├── llm/
│   │   ├── router.py         # Multi-model routing: Perplexity → OpenAI → Claude
│   │   ├── model_selector.py # Query classifier + model picker
│   │   ├── cloud_llm.py      # ClaudeClient + OpenAIClient
│   │   └── web_search.py     # Perplexity API — live internet
│   ├── memory/
│   │   └── long_term_memory.py  # ChromaDB vector store
│   └── persona/
│       ├── system_prompt.py  # Build full system prompt per mode
│       └── lou_profile.json  # Lou's full identity profile
├── cloud/
│   └── claude_api.py         # CloudBurst — backward compat wrapper
├── config/
│   └── settings.json         # All configurable settings
├── tests/                    # 98 tests, all green
├── .env.example              # Copy to .env, add your keys
├── requirements.txt
└── main.py
```

---

## Development phases

- **Phase 1** ✅ — Brain loop, multi-model routing, long-term memory, web search
- **Phase 2** — Voice pipeline (Whisper STT + Piper TTS)
- **Phase 3** — Port to Raspberry Pi Zero 2W, local Llama 3 8B
- **Phase 4** — Physical shell (3D printed PETG, RLL engraved, belt clip)
- **Phase 5** — Memory & persona deepening
- **Phase 6** — Private cloud sync + Actor's Companion integration

---

RLL
