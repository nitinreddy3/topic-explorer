"""A vector store, from scratch: a JSON file of {text, embedding} chunks and
brute-force cosine similarity for retrieval. No vector DB dependency.

This is deliberately the "naive" approach — at a few dozen chunks, comparing
against every embedding is instant. Once a real vector database (Chroma,
pgvector, ...) is doing this at scale with an index, this is the operation
it's approximating.
"""

import json
import math

STORE_PATH = "store.json"


def load_store(path: str = STORE_PATH) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(query_embedding: list[float], chunks: list[dict], top_k: int = 4) -> list[dict]:
    scored = [
        {**chunk, "score": cosine_similarity(query_embedding, chunk["embedding"])}
        for chunk in chunks
    ]
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:top_k]
