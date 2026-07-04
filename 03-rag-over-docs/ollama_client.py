"""Thin, non-streaming client for a local Ollama server: one function for
chat completion, one for embeddings.
"""

import httpx

CHAT_URL = "http://localhost:11434/api/chat"
EMBED_URL = "http://localhost:11434/api/embeddings"

CHAT_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"


def chat(messages: list[dict], *, timeout: float = 60) -> str:
    payload = {"model": CHAT_MODEL, "messages": messages, "stream": False}
    response = httpx.post(CHAT_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()["message"]["content"]


def embed(text: str, *, timeout: float = 60) -> list[float]:
    payload = {"model": EMBED_MODEL, "prompt": text}
    response = httpx.post(EMBED_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()["embedding"]
