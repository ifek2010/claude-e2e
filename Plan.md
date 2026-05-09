# 4-Week Plan: Short Story Q&A System

A portfolio project demonstrating **Python**, **LLM**, **RAG**, **Vector Database**, and **MCP** skills.

---

## Overview

**Goal:** Build a Q&A and summarization system over a curated corpus of public-domain short stories, expose it as an MCP server, and ship it with a real evaluation harness.

**Scope assumption:** Part-time work, roughly 10–15 hours per week. Adjust pace if you have more or less time available.

**Deliverable:** A polished GitHub repo with working CLI, MCP integration, evaluation results, and a clean README.

---

## Tech Stack (Locked In)

Lock these on day one and resist the urge to swap:

- **Language:** Python 3.10+
- **Vector DB:** ChromaDB (simplest local-first option)
- **Embeddings:** `sentence-transformers` with `all-MiniLM-L6-v2`
- **LLM:** Anthropic Claude API (or OpenAI if you prefer)
- **MCP:** Official Python SDK (`mcp` package)
- **CLI:** `typer` or `argparse`
- **Testing:** `pytest`
- **Optional UI:** Streamlit (only if time permits in Week 4)

---

## Week 1 — Foundation

**Theme:** Get the plumbing in place and ingest the corpus cleanly.

### Phase 1.1 — Project Setup (≈3 hours)
- Create GitHub repo with MIT or Apache 2.0 license
- Initialize Python virtual environment
- Set up `pyproject.toml` or `requirements.txt` with pinned dependencies
- Add `.gitignore` (exclude `.env`, `__pycache__`, `chroma_db/`, etc.)
- Create a clean folder structure:
  ```
  short-story-qa/
  ├── src/
  ├── corpus/
  ├── tests/
  ├── eval/
  ├── scripts/
  └── README.md
  ```
  
- Configure `.env` for API keys; never commit them

**Done when:** Fresh clone + `pip install` works without errors.

### Phase 1.2 — Corpus Collection (≈3 hours)
- Download 10 short stories from Project Gutenberg as Plain Text UTF-8
- Suggested mix: 3 Sherlock Holmes, "The Monkey's Paw," "The Most Dangerous Game," "To Build a Fire," "An Occurrence at Owl Creek Bridge," "The Cask of Amontillado," "Beyond Lies the Wub," "The Necklace"
- Save to `corpus/` with consistent naming: `author_title.txt`
- Manually inspect each file for encoding issues

**Done when:** All 10 stories are in `corpus/` and readable as plain text.

### Phase 1.3 — Ingestion Pipeline (≈5 hours)
- Write a loader that strips Gutenberg headers and footers (`*** START OF` / `*** END OF` markers, plus license boilerplate)
- Implement paragraph-based chunking with overlap handling
- Attach metadata to each chunk: `story_title`, `author`, `chunk_index`, `char_start`, `char_end`
- Embed chunks using `sentence-transformers`
- Store in ChromaDB with persistent local storage
- Add a `scripts/ingest.py` entry point

**Done when:** Running `python scripts/ingest.py` populates ChromaDB with all chunks and metadata.

### Phase 1.4 — Sanity Check (≈2 hours)
- Write a small `scripts/search.py` to do raw similarity search
- Test 5 queries manually and verify retrieved chunks make sense
- Document any obvious issues (e.g., chunks too small, metadata wrong)

**Done when:** Manual queries return relevant chunks for at least 4 of 5 test questions.

### Week 1 Buffer (≈2 hours)
Reserved for unexpected issues — encoding bugs, chunking edge cases, dependency conflicts. Don't skip this.

### Week 1 Deliverable
A working ingestion pipeline with 10 stories chunked, embedded, and searchable in ChromaDB.

---

## Week 2 — Core Q&A System

**Theme:** Make it actually answer questions like a real product.

### Phase 2.1 — Q&A Pipeline (≈5 hours)
- Build the retrieve-and-answer loop:
  1. Take user question
  2. Retrieve top-k chunks (start with k=5)
  3. Format chunks into a context block with source attribution
  4. Call LLM with a clear prompt template
- Prompt template should instruct the LLM to:
  - Answer only from provided context
  - Cite the source story for each claim
  - Say "I don't know" if context is insufficient
- Parse LLM output and present cleanly

**Done when:** You can ask 5 different questions and get cited answers.

### Phase 2.2 — CLI Interface (≈3 hours)
- Build a clean CLI using `typer` or `argparse`
- Commands to support:
  - `ask "question"` — Q&A
  - `list` — show available stories
  - `info <story>` — show metadata
- Add colored output (use `rich` library) for better demos

**Done when:** A user can clone, install, and ask questions in under 5 minutes.

### Phase 2.3 — Initial Evaluation Set (≈3 hours)
- Hand-craft 20 Q&A pairs covering:
  - **Easy** (10 pairs): Single-chunk factual lookups ("What is the visitor's name in 'A Scandal in Bohemia'?")
  - **Medium** (7 pairs): Multi-chunk synthesis within a story ("How does Holmes deduce the visitor's identity?")
  - **Hard** (3 pairs): Cross-story or thematic ("Which stories involve a hunt?")
- Save as `eval/questions.json` with `question`, `expected_answer`, `expected_story`, `difficulty`

**Done when:** You have 20 hand-vetted Q&A pairs in version control.

### Phase 2.4 — Manual Quality Pass (≈2 hours)
- Run all 20 questions through the system
- Note failures and categorize them (retrieval miss vs. LLM hallucination vs. ambiguous question)
- Fix any obvious bugs

### Week 2 Buffer (≈2 hours)
Prompt tuning, edge case fixes.

### Week 2 Deliverable
A working CLI Q&A system with citations, plus a hand-crafted evaluation set.

---

## Week 3 — Evaluation & Enhancements

**Theme:** Move from "it works" to "I have evidence it works." This is the week that separates portfolio projects from tutorial output.

### Phase 3.1 — Evaluation Harness (≈5 hours)
- Build `scripts/evaluate.py` that:
  - Loads questions from `eval/questions.json`
  - Runs each through the full pipeline
  - Records retrieved chunks, generated answer, latency
- Implement two metrics:
  - **Retrieval recall@k**: did the expected story appear in top-k chunks?
  - **Answer quality**: use an LLM-as-judge to score answers 1–5 against expected
- Generate a Markdown report with results table

**Done when:** Running `python scripts/evaluate.py` produces a clear report with numbers.

### Phase 3.2 — Experiment 1: Chunking Strategy (≈3 hours)
- Try at least three chunking approaches:
  - Paragraph-based (baseline)
  - Fixed-size (e.g., 500 chars with 50-char overlap)
  - Sentence-window retrieval (small chunks for matching, larger context for LLM)
- Run evaluation for each
- Document findings in `EXPERIMENTS.md`

### Phase 3.3 — Experiment 2: Retrieval Improvements (≈3 hours)
Try one or two of these:
- Hybrid search (combine BM25 with dense vectors)
- Query rewriting (LLM expands the question before retrieval)
- Reranking (cross-encoder re-scores top-k results)
- Metadata filtering (filter by story when question mentions a title)

Document each experiment with before/after numbers.

### Phase 3.4 — Summarization Feature (≈3 hours)
- Pre-compute a summary for each story at ingestion time
- Store summaries as a separate ChromaDB collection or in a JSON file
- Add `summarize <story>` command to CLI
- This sidesteps the long-document summarization problem entirely

**Done when:** `summarize "The Monkey's Paw"` returns a coherent multi-paragraph summary.

### Phase 3.5 — Cross-Story Queries (≈2 hours, stretch goal)
- Add support for thematic queries that span multiple stories
- Strategy: retrieve from all stories, group by story, present synthesized answer
- Test against the "Hard" questions in your eval set

### Week 3 Buffer (≈2 hours)

### Week 3 Deliverable
Quantitative evaluation report, documented experiments, and a working summarization feature. This is the heart of your portfolio piece.

---

## Week 4 — MCP Integration & Portfolio Polish

**Theme:** Make it impressive, demoable, and reviewable.

### Phase 4.1 — MCP Server (≈5 hours)
- Install the `mcp` Python SDK
- Build an MCP server that exposes three tools:
  - `ask_question(question: str)` — full Q&A pipeline
  - `summarize_story(title: str)` — return pre-computed summary
  - `list_stories()` — return story list with metadata
- Test the server locally with the MCP inspector
- Add to Claude Desktop config and verify integration

**Done when:** You can chat with Claude Desktop, ask a question about your stories, and watch Claude call your tool and answer correctly.

### Phase 4.2 — Tests (≈3 hours)
- Write `pytest` tests for:
  - Ingestion (Gutenberg header stripping, chunking)
  - Retrieval (returns expected chunks for known queries)
  - Prompt construction (formats context correctly)
- Aim for the critical paths, not 100% coverage. Reviewers love to see tests.

### Phase 4.3 — Documentation (≈4 hours)
The README is half the project's impact. Include:
- **One-paragraph pitch** at the top
- **Architecture diagram** (Excalidraw or hand-drawn sketch is fine)
- **Quickstart** — clone-to-running in 5 minutes
- **Example interactions** with real Q&A snippets
- **Evaluation results** — show your numbers
- **Design decisions** — explain at least three non-obvious choices
- **Limitations and future work** — show engineering maturity
- **MCP setup section** — how to connect with Claude Desktop

Add a separate `EXPERIMENTS.md` linking experiment results.

### Phase 4.4 — Demo Materials (≈3 hours)
- Record a 30–60 second GIF showing the MCP integration in action (use Kap, ScreenToGif, or asciinema)
- Embed at the top of README
- Take a screenshot of the evaluation report
- Optional: record a 2-minute walkthrough video for LinkedIn

### Phase 4.5 — Final Polish (≈3 hours)
- Test the setup instructions on a completely fresh clone — yes, actually do this
- Fix any rough edges
- Add a CHANGELOG or version tag
- Push final commit
- Share on LinkedIn / personal site

### Week 4 Stretch Goals (only if ahead)
- Streamlit web UI
- Dockerfile for one-command setup
- Add a second corpus (e.g., Russian short stories) to demonstrate extensibility
- Publish to PyPI

### Week 4 Deliverable
A polished, demoable, well-documented portfolio repo with MCP integration, tests, and quantitative results.

---

## Risk Management — What to Cut if Behind Schedule

If you fall behind, cut in this strict order. Earlier items first.

1. **Streamlit UI** — never essential for a portfolio piece
2. **Cross-story queries** — nice to have, not core
3. **Reranking experiment** — keep at least one experiment, drop the second
4. **MCP server** — the project is still a complete RAG demo without it
5. **Summarization feature** — passage Q&A alone is enough

**Never cut:** the evaluation harness. A polished, evaluated RAG without MCP beats a messy, unevaluated RAG with MCP every single time.

---

## Success Criteria

By the end of Week 4, you should have:

- [ ] A clean GitHub repo with a 5-minute quickstart
- [ ] At least 10 short stories ingested, chunked, and queryable
- [ ] A working Q&A CLI with citations
- [ ] A summarization feature
- [ ] An MCP server integrated with Claude Desktop
- [ ] An evaluation harness with at least 20 Q&A pairs and reported metrics
- [ ] At least 3 documented experiments with before/after numbers
- [ ] `pytest` tests for critical paths
- [ ] A README with architecture, results, and a demo GIF
- [ ] A `EXPERIMENTS.md` showing methodical work

---

## Daily Habits

- **Commit often** with meaningful messages — your commit history is part of the portfolio story
- **Keep a `NOTES.md`** while working — captures decisions for the README
- **Re-test setup instructions** every Friday on a fresh clone or new directory
- **Don't shop for new tools mid-project** — the stack is locked

---

## Final Reminder

The thing that will set this project apart from every other RAG tutorial on GitHub is **evaluation rigor** and **honest README writing**. Most projects skip both. The technical wow comes from MCP integration; the credibility comes from numbers and clearly stated limitations.

Good luck — and ship it.
