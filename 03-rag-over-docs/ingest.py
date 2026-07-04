"""
Ingestion pipeline: read source files -> chunk -> embed -> save to store.json.

Indexes this repo's own docs and code from Projects 1 and 2 — meta on
purpose, so you can ask the RAG system questions about the very concepts
you just built.

Chunking here is a plain character-based sliding window, applied the same
way to markdown and Python alike. It's the simplest thing that works, not
the best — see the README for smarter alternatives to try as an exercise.

Run:
    uv run ingest.py
"""

import os

from ollama_client import embed

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
STORE_PATH = "store.json"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_FILES = [
    "README.md",
    "01-raw-api-chatbot/README.md",
    "01-raw-api-chatbot/main.py",
    "02-evaluated-prompting/README.md",
    "02-evaluated-prompting/ollama_client.py",
    "02-evaluated-prompting/dataset.py",
    "02-evaluated-prompting/prompts.py",
    "02-evaluated-prompting/eval.py",
    "02-evaluated-prompting/main.py",
]


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def main() -> None:
    import json

    chunks = []
    for relpath in SOURCE_FILES:
        with open(os.path.join(REPO_ROOT, relpath)) as f:
            text = f.read()

        for i, piece in enumerate(chunk_text(text)):
            if not piece.strip():
                continue
            print(f"embedding {relpath} chunk {i}...")
            chunks.append(
                {
                    "id": len(chunks),
                    "source": relpath,
                    "chunk_index": i,
                    "text": piece,
                    "embedding": embed(piece),
                }
            )

    with open(STORE_PATH, "w") as f:
        json.dump(chunks, f)

    print(f"\nIngested {len(chunks)} chunks from {len(SOURCE_FILES)} files into {STORE_PATH}")


if __name__ == "__main__":
    main()
