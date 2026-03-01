"""
Document ingestion into the ChromaDB knowledge base.

Project role:
  Chunks plain-text documents, embeds them, and stores them in a persistent
  ChromaDB collection. Called by knowledge/ingest.py (CLI) and auto-invoked
  on first import of knowledge/retriever.py if the DB is empty.

Requires: chromadb (pip install chromadb)
Optional: sentence-transformers for multilingual embeddings
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Resolve DB path relative to this file so it works regardless of cwd.
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(_MODULE_DIR, "db")
CHROMA_DB_PATH = os.getenv("CHROMADB_PATH", DEFAULT_DB_PATH)
COLLECTION_NAME = "korean_realestate"

# Chunk parameters — tuned for Korean prose paragraphs.
CHUNK_SIZE = 400      # characters
CHUNK_OVERLAP = 80    # characters


def _get_embedding_function():
    """
    Return the best available embedding function for Korean text.

    Prefers paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers).
    Falls back to ChromaDB's built-in ONNX-based embedding if unavailable.
    """
    try:
        from chromadb.utils.embedding_functions import (
            SentenceTransformerEmbeddingFunction,
        )
        return SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
    except Exception:
        logger.info("sentence-transformers not available; using ChromaDB default embeddings")
        return None  # ChromaDB uses its own default


def get_collection():
    """
    Return the persistent ChromaDB collection, creating it if needed.

    Raises:
        ImportError: If chromadb is not installed.
    """
    import chromadb

    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    ef = _get_embedding_function()
    kwargs = {"name": COLLECTION_NAME}
    if ef is not None:
        kwargs["embedding_function"] = ef
    return client.get_or_create_collection(**kwargs)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Params:
        text: Source document text.
        chunk_size: Maximum characters per chunk.
        overlap: Characters shared between consecutive chunks.

    Returns:
        List of text chunks. Always at least one chunk even for short text.
    """
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def ingest_document(text: str, source: str, collection=None) -> int:
    """
    Ingest a document into the ChromaDB collection.

    Chunks the document, generates embeddings, and upserts into the collection.
    Using upsert means re-ingesting the same source_id updates existing chunks.

    Params:
        text: Full document text.
        source: Unique source identifier (e.g. "jeonse_guide", "path/to/file.txt").
        collection: Optional pre-opened ChromaDB collection. Opened if None.

    Returns:
        Number of chunks ingested.

    Raises:
        ImportError: If chromadb is not installed.
    """
    if collection is None:
        collection = get_collection()

    chunks = chunk_text(text)
    ids = [f"{source}__{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    logger.info("Ingested %d chunks from source='%s'", len(chunks), source)
    return len(chunks)


def seed_knowledge_base() -> int:
    """
    Ingest the built-in seed documents if the collection is empty.

    Returns:
        Total chunks ingested (0 if already seeded).
    """
    from knowledge.seed_data import SEED_DOCUMENTS

    collection = get_collection()
    if collection.count() > 0:
        logger.debug("Knowledge base already seeded (%d chunks present)", collection.count())
        return 0

    total = 0
    for source_id, text in SEED_DOCUMENTS:
        total += ingest_document(text, source_id, collection)
    logger.info("Knowledge base seeded with %d total chunks", total)
    return total
