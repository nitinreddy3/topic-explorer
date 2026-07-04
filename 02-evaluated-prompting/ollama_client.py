"""Thin, non-streaming client for a local Ollama server.

Non-streaming (stream=False) on purpose: the eval harness needs the full
reply text before it can parse it as JSON, so there's nothing to gain from
streaming here, unlike Project 1.
"""

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"


def chat(messages: list[dict], *, json_mode: bool = False, timeout: float = 60) -> str:
    payload = {"model": MODEL, "messages": messages, "stream": False}
    if json_mode:
        payload["format"] = "json"
    response = httpx.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()["message"]["content"]
