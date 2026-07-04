"""
Project 3: chat with your own docs (RAG).

Embeds the question, retrieves the most similar chunks from store.json,
stuffs them into the prompt as context, and asks the model to answer using
only that context. Prints which chunks were retrieved so you can see
retrieval and generation as two separate, inspectable steps.

Run (after `uv run ingest.py` has produced store.json):
    uv run main.py
"""

import sys

from ollama_client import chat, embed
from store import load_store, retrieve

STORE_PATH = "store.json"
TOP_K = 4

SYSTEM_PROMPT = """You are a helpful assistant answering questions about the \
topic-explorer learning repo. Use ONLY the provided context to answer — if \
the context doesn't contain the answer, say you don't know. Cite the source \
file(s) you used."""


def build_prompt(question: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n".join(
        f"[Source: {c['source']} chunk {c['chunk_index']}]\n{c['text']}" for c in chunks
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]


def main() -> None:
    try:
        chunks = load_store(STORE_PATH)
    except FileNotFoundError:
        print("No store.json found — run `uv run ingest.py` first.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(chunks)} chunks. Ask a question ('exit' to quit).\n")

    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() == "exit":
            break

        query_embedding = embed(question)
        top_chunks = retrieve(query_embedding, chunks, top_k=TOP_K)

        print("\n[retrieved]")
        for c in top_chunks:
            print(f"  {c['score']:.3f}  {c['source']} (chunk {c['chunk_index']})")

        answer = chat(build_prompt(question, top_chunks))
        print(f"\nassistant> {answer}\n")


if __name__ == "__main__":
    main()
