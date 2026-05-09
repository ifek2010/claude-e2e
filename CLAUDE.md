# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Short Story Q&A — a RAG system over public-domain short stories, exposed as an MCP server. Stack: ChromaDB (local vector DB), `sentence-transformers` (`all-MiniLM-L6-v2`), Anthropic Claude API, MCP Python SDK, Typer CLI, Rich output, pytest.

Conda environment: `claude-e2e`

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest corpus into ChromaDB
python scripts/ingest.py

# Raw similarity search (sanity check)
python scripts/search.py

# Run Q&A CLI
python -m src.cli ask "your question here"
python -m src.cli list
python -m src.cli summarize "Story Title"

# Evaluate
python scripts/evaluate.py

# Run tests
pytest tests/

# Run a single test
pytest tests/test_ingestion.py::test_header_stripping -v

# Start MCP server
python -m src.mcp_server
```

## Architecture

```
short-story-qa/
├── corpus/          # Raw .txt stories (author_title.txt naming)
├── src/
│   ├── ingest.py    # Gutenberg header/footer stripping + chunking + embedding + ChromaDB storage
│   ├── retrieval.py # Similarity search against ChromaDB; returns chunks with metadata
│   ├── qa.py        # Retrieve → format context → call Claude API → parse cited answer
│   ├── cli.py       # Typer CLI (ask / list / info / summarize commands)
│   └── mcp_server.py# MCP server exposing ask_question, summarize_story, list_stories tools
├── eval/
│   ├── questions.json  # 20 hand-crafted Q&A pairs with difficulty labels
│   └── results/        # Evaluation run outputs (Markdown reports)
├── scripts/
│   ├── ingest.py    # Entry point: runs src/ingest.py over corpus/
│   ├── search.py    # Quick manual similarity search for sanity checks
│   └── evaluate.py  # Full eval harness: retrieval recall@k + LLM-as-judge scoring
└── chroma_db/       # Persistent ChromaDB storage (gitignored)
```

### Key data flow

1. **Ingest**: `scripts/ingest.py` → strip Gutenberg headers → paragraph-chunk with overlap → embed via `sentence-transformers` → store in ChromaDB with metadata (`story_title`, `author`, `chunk_index`, `char_start`, `char_end`)
2. **Q&A**: user question → ChromaDB top-k retrieval → context block with source attribution → Claude API prompt → cited answer
3. **MCP**: `src/mcp_server.py` wraps the same Q&A and summarization logic as MCP tools for Claude Desktop integration

### ChromaDB collections

- `stories` — chunked story text with full metadata
- `summaries` — one pre-computed summary per story (generated at ingest time)

### Environment

API keys go in `.env` (never committed). Load with `python-dotenv`:
- `ANTHROPIC_API_KEY`
