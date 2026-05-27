"""
Long-Term Memory — ChromaDB vector store.

Every conversation builds a living, searchable map of Lou's life.
Stores by meaning, not just keywords.
Ask about something from 6 months ago — Pocket Lou knows it.

Degrades gracefully if chromadb is not installed.
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MEMORY_CATEGORIES = [
    "acting", "family", "projects", "spiritual",
    "fitness", "conspiracy", "general",
]

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "acting": [
        "role", "audition", "script", "character", "casting", "scene",
        "monologue", "director", "set", "filming", "agency", "callback",
        "broken oath", "last fix", "armstrong", "constantine", "self-tape",
        "sides", "booking", "recurring",
    ],
    "family": [
        "mackenzie", "rosie", "lily", "levi", "kids", "wife", "family",
        "home", "hudson", "daughter", "son", "baby", "pregnant", "school",
    ],
    "projects": [
        "app", "brain", "guitar", "code", "build", "deploy", "actor's companion",
        "pocket lou", "pocketlou", "sanctuary", "game changer", "broken oath",
        "last fix", "raspberry pi",
    ],
    "spiritual": [
        "consciousness", "hemi-sync", "gateway", "anunnaki", "meditation",
        "psychedelic", "awareness", "monroe", "remote viewing", "sumerian",
        "dmt", "psilocybin",
    ],
    "fitness": [
        "training", "workout", "gym", "nutrition", "diet", "body", "health",
        "run", "lift", "weight", "cardio", "sleep",
    ],
    "conspiracy": [
        "conspiracy", "hidden", "suppressed", "aliens", "government", "secret",
        "cover up", "occult", "they knew", "deep state", "cia",
    ],
}


class LongTermMemory:
    """
    Persistent semantic memory across all sessions.

    Stores every exchange in ChromaDB with embeddings.
    Recalls relevant past conversations by meaning.
    Injects them into the system prompt automatically.
    """

    COLLECTION_NAME = "pocket_lou_memory"

    def __init__(self, db_path: str = "./brain/memory/chroma_db"):
        self._db_path = db_path
        self._client = None
        self._collection = None
        self._init()

    def _init(self) -> None:
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            Path(self._db_path).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self._db_path)
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=ef,
            )
            logger.info(
                f"Long-term memory ready — {self._collection.count()} entries"
            )
        except ImportError:
            logger.warning(
                "chromadb or sentence-transformers not installed — "
                "long-term memory disabled. "
                "Run: pip install chromadb sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Long-term memory init failed: {e}")

    def is_available(self) -> bool:
        return self._collection is not None

    # ── Categorization ────────────────────────────────────────────────────────

    def _categorize(self, text: str) -> str:
        text_lower = text.lower()
        scores: dict[str, int] = {}
        for cat, keywords in _CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[cat] = score
        return max(scores, key=scores.get) if scores else "general"

    # ── Store ─────────────────────────────────────────────────────────────────

    def store(
        self,
        user_input: str,
        response: str,
        mode: str = "STANDARD",
        importance: str = "normal",
    ) -> None:
        """Store an exchange in long-term memory with auto-categorization."""
        if not self.is_available():
            return

        text = f"Lou: {user_input}\nPocket Lou: {response}"
        category = self._categorize(text)

        try:
            self._collection.add(
                documents=[text],
                metadatas=[{
                    "timestamp":        datetime.now().isoformat(),
                    "mode":             mode,
                    "category":         category,
                    "importance":       importance,
                    "user_snippet":     user_input[:300],
                    "response_snippet": response[:300],
                }],
                ids=[str(uuid.uuid4())],
            )
        except Exception as e:
            logger.warning(f"Memory store failed: {e}")

    # ── Recall ────────────────────────────────────────────────────────────────

    def recall(self, query: str, n_results: int = 5) -> list[dict]:
        """Semantic search — finds relevant memories by meaning."""
        if not self.is_available() or self.count() == 0:
            return []
        try:
            n = min(n_results, self.count())
            results = self._collection.query(
                query_texts=[query],
                n_results=n,
            )
            memories: list[dict] = []
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                memories.append({
                    "text":       doc,
                    "timestamp":  meta.get("timestamp", ""),
                    "mode":       meta.get("mode", ""),
                    "category":   meta.get("category", ""),
                    "importance": meta.get("importance", "normal"),
                })
            return memories
        except Exception as e:
            logger.warning(f"Memory recall failed: {e}")
            return []

    # ── Inject into system prompt ─────────────────────────────────────────────

    def inject_memories(self, query: str, n: int = 5) -> str:
        """
        Formats relevant memories for system prompt injection.
        Returns empty string if no relevant memories exist.

        Format:
            [RELEVANT MEMORIES]
            May 15 — Lou mentioned he was nervous about the Ottawa police job
            May 20 — Lou said Mackenzie was proud of the Mazda campaign
            [END MEMORIES]
        """
        memories = self.recall(query, n_results=n)
        if not memories:
            return ""

        lines = ["[RELEVANT MEMORIES]"]
        for mem in memories:
            ts = mem.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                date_str = dt.strftime("%b %d")
            except Exception:
                date_str = "Earlier"

            text = mem.get("text", "")
            first_line = text.split("\n")[0].replace("Lou: ", "").strip()
            if len(first_line) > 120:
                first_line = first_line[:117] + "..."
            lines.append(f"{date_str} — {first_line}")

        lines.append("[END MEMORIES]")
        return "\n".join(lines)

    # ── Utils ─────────────────────────────────────────────────────────────────

    def count(self) -> int:
        if not self.is_available():
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        if not self.is_available():
            return
        try:
            from chromadb.utils import embedding_functions
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self._client.delete_collection(self.COLLECTION_NAME)
            self._collection = self._client.create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=ef,
            )
        except Exception as e:
            logger.error(f"Memory clear failed: {e}")
