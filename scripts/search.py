#!/usr/bin/env python3
"""Sanity check: raw similarity search against ChromaDB."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from sentence_transformers import SentenceTransformer
from src.ingest import MODEL_NAME, COLLECTION_NAME

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
TOP_K = 3


def search(query: str) -> None:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)

    embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=TOP_K)

    print(f"\nQuery: {query!r}")
    print("=" * 60)
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        print(f"\n[{i+1}] {meta['story_title']} — {meta['author']}  (chunk {meta['chunk_index']}, dist={dist:.4f})")
        print("-" * 40)
        print(doc[:300].strip() + ("..." if len(doc) > 300 else ""))


QUERIES = [
    "What does the monkey's paw grant?",
    "How does the narrator escape death?",
    "What happens to Fortunato in the catacombs?",
    "What does the wub want to talk about?",
    "Describe the cold and snow in the story.",
]

if __name__ == "__main__":
    queries = sys.argv[1:] if len(sys.argv) > 1 else QUERIES
    model = SentenceTransformer(MODEL_NAME)  # load once
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    for query in queries:
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=TOP_K)
        print(f"\nQuery: {query!r}")
        print("=" * 60)
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            print(f"\n[{i+1}] {meta['story_title']} — {meta['author']}  (chunk {meta['chunk_index']}, dist={dist:.4f})")
            print("-" * 40)
            print(doc[:300].strip() + ("..." if len(doc) > 300 else ""))
    print()
