"""
Local LLM — llama.cpp inference via llama-cpp-python.

Target model: Llama 3 8B Q4_K_M (fits on Pi Zero 2W with patience)
Place model at: models/llama-3-8b-q4_k_m.gguf
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalLLM:
    """Offline inference. Privacy first. No data leaves the device."""

    def __init__(self, config: dict):
        self._cfg = config["llm"]
        self._model = None
        self._model_path = Path(self._cfg["local_model_path"])

    def load(self) -> bool:
        try:
            from llama_cpp import Llama

            if not self._model_path.exists():
                logger.warning(
                    f"Model file not found: {self._model_path}. "
                    "Download Llama 3 8B Q4_K_M and place it there. "
                    "Falling back to cloud."
                )
                return False

            self._model = Llama(
                model_path=str(self._model_path),
                n_ctx=self._cfg.get("local_context_size", 4096),
                n_threads=self._cfg.get("local_threads", 4),
                n_gpu_layers=self._cfg.get("local_gpu_layers", 0),
                verbose=False,
            )
            logger.info(f"Local LLM loaded: {self._model_path.name}")
            return True

        except ImportError:
            logger.warning(
                "llama-cpp-python not installed. "
                "Install with: pip install llama-cpp-python"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            return False

    def is_available(self) -> bool:
        return self._model is not None

    def complete(self, messages: list[dict], system_prompt: str = "") -> str:
        if not self._model:
            raise RuntimeError("Local LLM not loaded. Call load() first.")

        prompt = self._build_llama3_prompt(messages, system_prompt)

        result = self._model(
            prompt,
            max_tokens=self._cfg.get("max_tokens", 512),
            temperature=self._cfg.get("temperature", 0.75),
            stop=["<|eot_id|>", "<|end_of_text|>"],
            echo=False,
        )
        return result["choices"][0]["text"].strip()

    def _build_llama3_prompt(self, messages: list[dict], system_prompt: str) -> str:
        parts = ["<|begin_of_text|>"]

        if system_prompt:
            parts.append(
                f"<|start_header_id|>system<|end_header_id|>\n\n"
                f"{system_prompt}<|eot_id|>"
            )

        for msg in messages:
            parts.append(
                f"<|start_header_id|>{msg['role']}<|end_header_id|>\n\n"
                f"{msg['content']}<|eot_id|>"
            )

        parts.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
        return "".join(parts)
