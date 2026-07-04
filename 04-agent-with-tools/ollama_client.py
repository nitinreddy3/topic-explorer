"""Thin, non-streaming chat client that supports tool calling.

Returns the raw assistant *message* dict (not just text) so the caller can
inspect `tool_calls` and feed the message straight back into history
unmodified — that round-trip is what makes the agent loop work.
"""

import httpx

CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"


def chat(messages: list[dict], *, tools: list[dict] | None = None, timeout: float = 60) -> dict:
    payload = {"model": MODEL, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    response = httpx.post(CHAT_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()["message"]
