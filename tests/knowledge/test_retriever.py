"""
Tests for knowledge/retriever.py — ChromaDB semantic retrieval.

ChromaDB is an optional dependency. When it is not installed the retriever
must return an empty list rather than raising. When it is installed, we use a
temporary in-memory collection to avoid touching the real persisted database.
"""

from __future__ import annotations

import pytest

# Try to import chromadb so we can decide whether to run live tests.
chromadb = pytest.importorskip("chromadb", reason="chromadb not installed")


class TestRetrieveFallback:
    """retrieve() must not crash when the DB is empty or chromadb is missing."""

    def test_retrieve_returns_list(self, tmp_path, monkeypatch):
        """retrieve() on an empty seeded DB returns a list (may be empty)."""
        monkeypatch.setenv("CHROMADB_PATH", str(tmp_path / "db"))
        from knowledge.retriever import retrieve

        result = retrieve("전세 보증금", k=3)
        assert isinstance(result, list)

    def test_retrieve_items_have_content_and_source(self, tmp_path, monkeypatch):
        """Each returned item has 'content' and 'source' keys."""
        monkeypatch.setenv("CHROMADB_PATH", str(tmp_path / "db"))
        from knowledge.retriever import retrieve

        results = retrieve("전세 보증금", k=5)
        for item in results:
            assert "content" in item
            assert "source" in item

    def test_retrieve_respects_k_limit(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CHROMADB_PATH", str(tmp_path / "db"))
        from knowledge.retriever import retrieve

        results = retrieve("아파트", k=2)
        assert len(results) <= 2


class TestLoaderChunkText:
    """Test the chunking logic independently of ChromaDB."""

    def test_short_text_returns_single_chunk(self):
        from knowledge.loader import chunk_text

        text = "짧은 텍스트"
        chunks = chunk_text(text, chunk_size=400)
        assert chunks == [text]

    def test_long_text_splits(self):
        from knowledge.loader import chunk_text

        text = "가" * 1000
        chunks = chunk_text(text, chunk_size=400, overlap=80)
        assert len(chunks) > 1

    def test_chunks_cover_full_text(self):
        from knowledge.loader import chunk_text

        text = "나" * 900
        chunks = chunk_text(text, chunk_size=400, overlap=80)
        # All characters must appear in at least one chunk
        combined = "".join(chunks)
        for char in set(text):
            assert char in combined

    def test_overlap_between_consecutive_chunks(self):
        from knowledge.loader import chunk_text

        text = "a" * 600
        chunks = chunk_text(text, chunk_size=400, overlap=100)
        assert len(chunks) >= 2
        # The overlap ensures consecutive chunks share content
        end_of_first = chunks[0][-100:]
        start_of_second = chunks[1][:100]
        assert end_of_first == start_of_second
