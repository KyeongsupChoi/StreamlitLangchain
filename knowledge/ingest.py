"""
CLI script to ingest documents into the Korean real estate knowledge base.

Usage:
    python -m knowledge.ingest path/to/document.txt [--source my_source_id]
    python -m knowledge.ingest --seed   # re-ingest built-in seed documents

Requires: chromadb (pip install chromadb)
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest documents into the Korean real estate ChromaDB knowledge base."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to a UTF-8 text file to ingest.",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Source label for the document (default: file path).",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Force re-ingest the built-in seed documents.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete and recreate the collection before ingesting.",
    )
    args = parser.parse_args(argv)

    try:
        from knowledge.loader import get_collection, ingest_document, seed_knowledge_base
    except ImportError as exc:
        print(f"Error: chromadb is not installed. Run: pip install chromadb\n{exc}", file=sys.stderr)
        return 1

    if args.clear:
        import chromadb
        from knowledge.loader import CHROMA_DB_PATH, COLLECTION_NAME
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted collection '{COLLECTION_NAME}'.")
        except Exception:
            pass

    if args.seed:
        total = seed_knowledge_base()
        print(f"Seeded knowledge base with {total} chunks.")
        return 0

    if not args.path:
        parser.print_help()
        return 1

    try:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    source = args.source or args.path
    n = ingest_document(text, source)
    print(f"Ingested {n} chunks from '{source}' into the knowledge base.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
