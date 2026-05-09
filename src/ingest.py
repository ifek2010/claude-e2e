import re
import os
from pathlib import Path
from dataclasses import dataclass

import chromadb
from sentence_transformers import SentenceTransformer


CHUNK_SIZE = 1000      # target chars per chunk
CHUNK_OVERLAP = 100    # chars of overlap between chunks
COLLECTION_NAME = "stories"
MODEL_NAME = "all-MiniLM-L6-v2"


@dataclass
class Chunk:
    text: str
    story_title: str
    author: str
    chunk_index: int
    char_start: int
    char_end: int


def _parse_filename(path: Path) -> tuple[str, str]:
    """Return (author, title) from 'Author-Name_Story-Title.txt'."""
    stem = path.stem
    if "_" not in stem:
        return ("Unknown", stem.replace("-", " "))
    author_part, title_part = stem.split("_", 1)
    author = author_part.replace("-", " ")
    title = title_part.replace("-", " ")
    return author, title


def load_story(filepath: Path) -> tuple[str, str, str]:
    """Strip Gutenberg header/footer; return (text, author, title)."""
    raw = filepath.read_text(encoding="utf-8-sig")

    start_match = re.search(r"\*\*\* START OF .+? \*\*\*", raw)
    end_match = re.search(r"\*\*\* END OF .+? \*\*\*", raw)

    if start_match and end_match:
        text = raw[start_match.end(): end_match.start()]
    elif start_match:
        text = raw[start_match.end():]
    else:
        text = raw

    author, title = _parse_filename(filepath)
    return text.strip(), author, title


def chunk_text(text: str, story_title: str, author: str) -> list[Chunk]:
    """Paragraph-based chunking with character overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[Chunk] = []
    current_chars: list[str] = []
    current_start = 0
    char_cursor = 0
    chunk_index = 0

    for para in paragraphs:
        current_chars.append(para)
        joined = "\n\n".join(current_chars)

        if len(joined) >= CHUNK_SIZE:
            chunk_text_str = joined
            char_end = char_cursor + len(chunk_text_str)
            chunks.append(Chunk(
                text=chunk_text_str,
                story_title=story_title,
                author=author,
                chunk_index=chunk_index,
                char_start=current_start,
                char_end=char_end,
            ))
            chunk_index += 1
            char_cursor = char_end

            # overlap: keep trailing CHUNK_OVERLAP chars as seed for next chunk
            overlap_text = chunk_text_str[-CHUNK_OVERLAP:]
            current_chars = [overlap_text]
            current_start = char_end - CHUNK_OVERLAP

    # flush remainder
    if current_chars:
        chunk_text_str = "\n\n".join(current_chars)
        chunks.append(Chunk(
            text=chunk_text_str,
            story_title=story_title,
            author=author,
            chunk_index=chunk_index,
            char_start=current_start,
            char_end=current_start + len(chunk_text_str),
        ))

    return chunks


def ingest_corpus(corpus_dir: Path, chroma_dir: Path) -> None:
    story_files = sorted(corpus_dir.glob("*.txt"))
    if not story_files:
        raise FileNotFoundError(f"No .txt files found in {corpus_dir}")

    print(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=str(chroma_dir))
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(COLLECTION_NAME)

    total_chunks = 0
    for story_file in story_files:
        text, author, title = load_story(story_file)
        chunks = chunk_text(text, title, author)

        texts = [c.text for c in chunks]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        ids = [f"{story_file.stem}_{c.chunk_index}" for c in chunks]
        metadatas = [
            {
                "story_title": c.story_title,
                "author": c.author,
                "chunk_index": c.chunk_index,
                "char_start": c.char_start,
                "char_end": c.char_end,
            }
            for c in chunks
        ]

        collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)
        print(f"  {title} ({author}) — {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nDone. {len(story_files)} stories, {total_chunks} total chunks stored in '{chroma_dir}'.")
