# Downloading the Local LLM Model

**Phase 3+** — local inference on Raspberry Pi Zero 2W and desktop.
Phase 1 uses Claude API only. This guide prepares you for Phase 3.

---

## Target Model

**Llama 3 8B Q4_K_M** (GGUF format for llama.cpp)

| Property | Value |
|---|---|
| Model | Meta Llama 3 8B |
| Quantization | Q4_K_M |
| Format | GGUF |
| File size | ~4.9 GB |
| RAM required | ~6 GB (desktop) / tested on Pi 5, slow on Pi Zero |
| Inference speed | Pi Zero 2W: ~1–2 tok/s · Desktop: 10–50 tok/s |

---

## Download

### Option 1 — huggingface-cli (recommended)

```bash
pip install huggingface-hub

huggingface-cli download \
  bartowski/Meta-Llama-3-8B-Instruct-GGUF \
  Meta-Llama-3-8B-Instruct-Q4_K_M.gguf \
  --local-dir models/
```

### Option 2 — Direct download

```bash
mkdir -p models
cd models

# ~4.9 GB download
wget https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
```

### Option 3 — Smaller model for Pi Zero 2W

The Pi Zero 2W has only 512MB RAM. Llama 3 8B won't run on it natively.
For Pi Zero testing, use a quantized Llama 3.2 1B:

```bash
huggingface-cli download \
  bartowski/Llama-3.2-1B-Instruct-GGUF \
  Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  --local-dir models/
```

---

## Placement

Place the model file at:

```
PocketLou-Brain/
└── models/
    └── Meta-Llama-3-8B-Instruct-Q4_K_M.gguf  ← here
```

Update `config/settings.json`:

```json
{
  "llm": {
    "local_model_path": "models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
  }
}
```

---

## Install llama-cpp-python

```bash
# CPU only (Pi Zero, desktop without GPU)
pip install llama-cpp-python

# With CUDA (desktop with NVIDIA GPU — much faster)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# With Metal (Mac)
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python
```

---

## Test the model

```bash
python -c "
from llama_cpp import Llama
llm = Llama(model_path='models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf', n_ctx=2048, verbose=False)
output = llm('<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nSay hello.<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n', max_tokens=50, echo=False)
print(output['choices'][0]['text'])
"
```

---

## Pi Zero 2W Reality Check

The Pi Zero 2W has 512MB RAM. Llama 3 8B (even Q4_K_M at ~4.9GB) does **not** fit.

Options for Pi Zero:
1. **Cloud burst always** (Phase 1 approach — works great, needs WiFi/4G)
2. **Llama 3.2 1B Q4_K_M** (~0.7GB) — fits, ~0.5–1 tok/s, very limited capability
3. **Phi-3.5 Mini** — better quality, still small

Recommendation: **keep cloud burst as primary, add local as experimental** on Pi Zero.
Local inference is more viable on Pi 4/5 with 4–8GB RAM.

---

## For Pi Zero (Phase 3 prep)

```bash
# On Pi Zero 2W — run from project root
python brain/brain.py --mode STANDARD

# If local model loaded:
# brain auto-detects and prefers local
# Falls back to cloud if local fails or is slow
```

The `brain/models/` directory is git-ignored. **Never commit model files.**
