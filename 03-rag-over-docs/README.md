# 03 — RAG Over Your Own Docs

Phase 3 project: "chat with your docs," built from scratch — no vector DB,
no RAG framework (LangChain, LlamaIndex, ...). Indexes this repo's own
READMEs and code from Projects 1 and 2, so you can ask questions about the
concepts you already built.

## Setup

```bash
ollama serve &                    # if not already running
ollama pull nomic-embed-text      # ~270MB, one-time

uv run ingest.py                  # build store.json (do this once, or after editing docs)
uv run main.py                    # ask questions
uv run eval_retrieval.py          # check retrieval quality
```

## The pipeline, and where each piece lives

1. **Chunk** — `ingest.py` splits each source file into ~800-character
   overlapping windows.
2. **Embed** — each chunk is turned into a vector via `nomic-embed-text`
   (`ollama_client.embed`).
3. **Store** — chunks + embeddings are saved as plain JSON (`store.py`) —
   a vector store is fundamentally just "vectors + a similarity search,"
   and at a few dozen chunks, brute-force cosine similarity is instant.
4. **Retrieve** — `main.py` embeds the question, ranks all chunks by cosine
   similarity, takes the top 4 (`store.retrieve`).
5. **Generate** — the retrieved chunks are stuffed into the prompt as
   context, with an instruction to answer only from that context and cite
   sources (`main.py:build_prompt`).

## Result: retrieval eval

```
retrieval hit rate: 6/6 (100%)
```

`eval_retrieval.py` checks a different thing than Project 2's eval did:
not "is the final answer right," but "does the chunk containing the answer
even get retrieved." This distinction matters — if retrieval misses the
right chunk, no amount of prompt tuning on the generation side can recover
it. Evaluating retrieval and generation separately is how you debug *where*
a RAG system is actually failing.

## What to notice while reading the code

- `store.py`'s `cosine_similarity` and `retrieve` are the entire "vector
  database" here — maybe 15 lines. Chroma/pgvector/Pinecone do the same
  math, just with an index (HNSW, IVF, ...) so it doesn't degrade to
  brute-force `O(n)` at millions of vectors.
- `ingest.py` uses one fixed chunking strategy for both markdown and Python
  — simple, but naive: it can split a function or a code block mid-way.
  Compare the retrieved chunks for a code-specific question against a
  prose-specific one and see if you can tell.
- The system prompt in `main.py` explicitly says "use ONLY the provided
  context... if it doesn't contain the answer, say you don't know" — try
  asking something unrelated to this repo and see whether the model
  actually admits it doesn't know, or hallucinates anyway.

## Ideas to extend (optional, before moving to Project 4)

- Re-run `ingest.py` after adding a new file to `SOURCE_FILES` (try your own
  notes or a different codebase) and see how retrieval quality holds up.
- Try AST-aware chunking for `.py` files (split on `def`/`class` boundaries)
  and see if it changes the eval hit rate or answer quality.
- Add hybrid search: combine cosine similarity with a simple keyword/BM25
  score and compare retrieval quality against embeddings alone.
- Add a generation-quality eval (like Project 2's) on top of the retrieval
  eval — now you'd have both halves of a full RAG eval.
