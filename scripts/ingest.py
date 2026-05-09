#!/usr/bin/env python3
"""Entry point: ingest all corpus stories into ChromaDB."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingest import ingest_corpus

CORPUS_DIR = Path(__file__).parent.parent / "corpus"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

if __name__ == "__main__":
    ingest_corpus(CORPUS_DIR, CHROMA_DIR)
