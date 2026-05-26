"""
Vector Store — semantic long-term memory using ChromaDB.

Stores conversation fragments and manual memories.
Searched on every think() call to surface relevant context.
Degrades gracefully if chromadb is not installed.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent semantic memory. Optional — brain works without it."""

    COLLECTION_NAME = "pocket_lou_memory"

    def __init__(self, config: dict):
        self._db_path = config["memory"]["vector_db_path"]
        self._embedding_model = config["memory"].get(
            "embedding_model", "all-MiniLM-L6-v2"
        )
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
                model_name=self._embedding_model
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=ef,
            )
            logger.info(f"Vector store ready at {self._db_path}")

        except ImportError:
            logger.warning(
                "chromadb or sentence-transformers not installed — "
                "vector memory disabled. "
                "Install with: pip install chromadb sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Vector store init failed: {e}")

    def is_available(self) -> bool:
        return self._collection is not None

    def add(self, text: str, metadata: Optional[dict] = None) -> None:
        if not self.is_available():
            return
        try:
            self._collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[str(uuid.uuid4())],
            )
        except Exception as e:
            logger.warning(f"Vector store add failed: {e}")

    def search(self, query: str, k: int = 5) -> list[str]:
        if not self.is_available() or self.count() == 0:
            return []
        try:
            n = min(k, self.count())
            results = self._collection.query(
                query_texts=[query],
                n_results=n,
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return []

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
                model_name=self._embedding_model
            )
            self._client.delete_collection(self.COLLECTION_NAME)
            self._collection = self._client.create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=ef,
            )
        except Exception as e:
            logger.error(f"Vector store clear failed: {e}")
