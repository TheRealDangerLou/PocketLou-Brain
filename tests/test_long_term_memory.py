"""
Tests for brain.memory.long_term_memory — ChromaDB vector store.
Uses in-memory ChromaDB when available, degrades gracefully if not installed.
"""

import pytest
from unittest.mock import MagicMock, patch
from brain.memory.long_term_memory import LongTermMemory, MEMORY_CATEGORIES


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def ltm_no_chroma():
    """LTM instance with chromadb unavailable — tests graceful degradation."""
    with patch.dict("sys.modules", {"chromadb": None}):
        mem = LongTermMemory.__new__(LongTermMemory)
        mem._db_path = "/tmp/test_chroma"
        mem._client = None
        mem._collection = None
        return mem


@pytest.fixture
def ltm_mocked():
    """LTM instance with a fully mocked ChromaDB collection."""
    mem = LongTermMemory.__new__(LongTermMemory)
    mem._db_path = "/tmp/test_chroma"
    mem._client = MagicMock()

    collection = MagicMock()
    collection.count.return_value = 0
    mem._collection = collection
    return mem


# ── Availability ──────────────────────────────────────────────────────────────

class TestAvailability:
    def test_unavailable_without_chroma(self, ltm_no_chroma):
        assert ltm_no_chroma.is_available() is False

    def test_available_with_collection(self, ltm_mocked):
        assert ltm_mocked.is_available() is True

    def test_count_zero_when_unavailable(self, ltm_no_chroma):
        assert ltm_no_chroma.count() == 0

    def test_count_delegates_to_collection(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 42
        assert ltm_mocked.count() == 42


# ── Store (graceful degradation) ───────────────────────────────────────────────

class TestStore:
    def test_store_does_nothing_when_unavailable(self, ltm_no_chroma):
        # Should not raise
        ltm_no_chroma.store("hello", "response", mode="STANDARD")

    def test_store_calls_collection_add(self, ltm_mocked):
        ltm_mocked.store("audition prep", "here's how to nail it", mode="ACTOR")
        ltm_mocked._collection.add.assert_called_once()

    def test_store_includes_metadata(self, ltm_mocked):
        ltm_mocked.store("my script", "feedback here", mode="ACTOR")
        call_kwargs = ltm_mocked._collection.add.call_args[1]
        meta = call_kwargs["metadatas"][0]
        assert "timestamp" in meta
        assert "mode" in meta
        assert meta["mode"] == "ACTOR"
        assert "category" in meta

    def test_store_includes_user_snippet(self, ltm_mocked):
        ltm_mocked.store("my script question", "answer", mode="STANDARD")
        call_kwargs = ltm_mocked._collection.add.call_args[1]
        meta = call_kwargs["metadatas"][0]
        assert "user_snippet" in meta

    def test_store_handles_exception_gracefully(self, ltm_mocked):
        ltm_mocked._collection.add.side_effect = Exception("DB error")
        # Should not raise
        ltm_mocked.store("test", "test", mode="STANDARD")


# ── Recall ─────────────────────────────────────────────────────────────────────

class TestRecall:
    def test_recall_empty_when_unavailable(self, ltm_no_chroma):
        result = ltm_no_chroma.recall("audition", n_results=5)
        assert result == []

    def test_recall_empty_when_no_memories(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 0
        result = ltm_mocked.recall("anything")
        assert result == []

    def test_recall_returns_list(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 1
        ltm_mocked._collection.query.return_value = {
            "documents": [["Lou: test\nPocket Lou: answer"]],
            "metadatas": [[{
                "timestamp": "2024-05-15T10:00:00",
                "mode": "ACTOR",
                "category": "acting",
                "importance": "normal",
            }]],
        }
        result = ltm_mocked.recall("test query")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_recall_includes_text(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 1
        ltm_mocked._collection.query.return_value = {
            "documents": [["Lou: audition\nPocket Lou: great work"]],
            "metadatas": [[{
                "timestamp": "2024-05-15T10:00:00",
                "mode": "ACTOR",
                "category": "acting",
                "importance": "normal",
            }]],
        }
        result = ltm_mocked.recall("audition")
        assert "text" in result[0]
        assert "timestamp" in result[0]
        assert "category" in result[0]

    def test_recall_handles_exception_gracefully(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 5
        ltm_mocked._collection.query.side_effect = Exception("Query failed")
        result = ltm_mocked.recall("test")
        assert result == []


# ── Categorization ────────────────────────────────────────────────────────────

class TestCategorization:
    def test_categories_defined(self):
        assert "acting" in MEMORY_CATEGORIES
        assert "family" in MEMORY_CATEGORIES
        assert "projects" in MEMORY_CATEGORIES
        assert "spiritual" in MEMORY_CATEGORIES
        assert "fitness" in MEMORY_CATEGORIES
        assert "conspiracy" in MEMORY_CATEGORIES
        assert "general" in MEMORY_CATEGORIES

    def test_categorize_acting(self, ltm_mocked):
        cat = ltm_mocked._categorize("I need to prep for my audition script")
        assert cat == "acting"

    def test_categorize_family(self, ltm_mocked):
        cat = ltm_mocked._categorize("Rosie had a great day at school, Mackenzie was proud")
        assert cat == "family"

    def test_categorize_projects(self, ltm_mocked):
        cat = ltm_mocked._categorize("working on the pocket lou brain app build")
        assert cat == "projects"

    def test_categorize_spiritual(self, ltm_mocked):
        cat = ltm_mocked._categorize("let's talk about hemi-sync and the gateway process")
        assert cat == "spiritual"

    def test_categorize_conspiracy(self, ltm_mocked):
        cat = ltm_mocked._categorize("conspiracy cover up deep state aliens")
        assert cat == "conspiracy"

    def test_categorize_general_fallback(self, ltm_mocked):
        cat = ltm_mocked._categorize("xyzzy random words with no keywords")
        assert cat == "general"


# ── Memory injection ──────────────────────────────────────────────────────────

class TestInjectMemories:
    def test_inject_empty_when_no_memories(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 0
        result = ltm_mocked.inject_memories("test query")
        assert result == ""

    def test_inject_returns_string(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 1
        ltm_mocked._collection.query.return_value = {
            "documents": [["Lou: audition question\nPocket Lou: great answer"]],
            "metadatas": [[{
                "timestamp": "2024-05-15T10:00:00",
                "mode": "ACTOR",
                "category": "acting",
                "importance": "normal",
            }]],
        }
        result = ltm_mocked.inject_memories("audition")
        assert isinstance(result, str)
        assert "[RELEVANT MEMORIES]" in result
        assert "[END MEMORIES]" in result

    def test_inject_formats_date(self, ltm_mocked):
        ltm_mocked._collection.count.return_value = 1
        ltm_mocked._collection.query.return_value = {
            "documents": [["Lou: question\nPocket Lou: answer"]],
            "metadatas": [[{
                "timestamp": "2024-05-15T10:00:00",
                "mode": "STANDARD",
                "category": "general",
                "importance": "normal",
            }]],
        }
        result = ltm_mocked.inject_memories("anything")
        assert "May 15" in result

    def test_inject_unavailable_returns_empty(self, ltm_no_chroma):
        result = ltm_no_chroma.inject_memories("test")
        assert result == ""
