"""
Semantic retrieval from the ChromaDB knowledge base.

Project role:
  Provides retrieve() used by tools/search_tools.py to ground LLM answers
  in curated Korean real estate documents.

Requires: chromadb (pip install chromadb)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Retrieve the k most semantically relevant document chunks.

    Auto-seeds the knowledge base on first call if the collection is empty.

    Params:
        query: Natural language query (Korean or English).
        k: Number of chunks to return.

    Returns:
        List of dicts with keys 'content' (str) and 'source' (str).
        Returns an empty list if chromadb is not installed or no docs found.
    """
    try:
        from knowledge.loader import get_collection, seed_knowledge_base

        collection = get_collection()
        if collection.count() == 0:
            logger.info("Knowledge base empty — auto-seeding with built-in documents")
            seed_knowledge_base()

        if collection.count() == 0:
            return []

        results = collection.query(query_texts=[query], n_results=min(k, collection.count()))
        docs: list[dict] = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            docs.append({"content": doc, "source": meta.get("source", "unknown")})
        logger.info("retrieve: query='%s' returned %d chunks", query[:50], len(docs))
        return docs

    except ImportError:
        logger.debug("chromadb not installed — returning empty results")
        return []
    except Exception as exc:
        logger.warning("retrieve failed: %s", exc)
        return []
