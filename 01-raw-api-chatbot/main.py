"""
Project 1: Raw-API chatbot.

Goal: understand what a "chat" actually is at the API level, with zero framework
(and zero vendor SDK) in the way. This is the foundation every RAG/agent system
in later projects builds on top of.

Runs against a local Ollama server, so it needs no API key or cost. Swapping
this to a hosted model later (Anthropic, OpenAI, ...) is a small change: same
message-role structure, different endpoint/auth.

Concepts this demonstrates:
- message roles (system / user / assistant) and why history must be resent every turn
- streaming a response token-by-token over raw HTTP (NDJSON), no SDK
- basic error handling around a network API

Setup (once):
    brew install --cask ollama
    ollama serve &          # or launch the Ollama app
    ollama pull llama3.2

Run:
    uv run main.py
"""

import json
import sys

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"
SYSTEM_PROMPT = "You are a concise, helpful assistant."


def stream_reply(client: httpx.Client, history: list[dict]) -> str:
    """Send the full conversation history and stream back the assistant's reply.

    The API is stateless: there is no server-side session, so every request
    resends the entire message history. This is *the* thing to internalize
    before touching any agent framework. Ollama streams newline-delimited JSON
    objects, each holding one incremental chunk of the reply.
    """
    full_text = ""
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *history],
        "stream": True,
    }
    with client.stream("POST", OLLAMA_URL, json=payload, timeout=60) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            content = chunk.get("message", {}).get("content", "")
            if content:
                print(content, end="", flush=True)
                full_text += content
            if chunk.get("done"):
                break
    print()
    return full_text


def main() -> None:
    client = httpx.Client()
    try:
        client.get("http://localhost:11434", timeout=2)
    except httpx.ConnectError:
        print(
            "Can't reach Ollama at localhost:11434 — is it running? "
            "Start it with `ollama serve` or the Ollama app.",
            file=sys.stderr,
        )
        sys.exit(1)

    history: list[dict] = []

    print("Raw-API chatbot. Type 'exit' to quit, 'reset' to clear history.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "reset":
            history.clear()
            print("(history cleared)")
            continue

        history.append({"role": "user", "content": user_input})

        print("assistant> ", end="")
        try:
            reply = stream_reply(client, history)
        except Exception as e:
            print(f"\n[error] {e}", file=sys.stderr)
            history.pop()  # drop the unanswered user turn so history stays valid
            continue

        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
