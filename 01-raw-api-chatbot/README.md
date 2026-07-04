# 01 — Raw-API Chatbot

Phase 1 project: a terminal chatbot built directly against an LLM's chat API
with no SDK and no agent framework in between — plain `httpx` and JSON. The
point is to see the actual mechanics — message roles, conversation history,
streaming — before anything abstracts them away.

Runs against a **local model via Ollama**, so it costs nothing and needs no
API key.

## Setup

```bash
brew install --cask ollama
ollama serve &          # or just launch the Ollama app once
ollama pull llama3.2    # ~2GB, one-time download

uv run main.py
```

## What to notice while reading `main.py`

- The API has no memory of its own — `history` is a plain Python list that
  gets resent in full on every call. Try commenting out `history.append(...)`
  for the assistant reply and see the model "forget" what it just said.
- The response is streamed as newline-delimited JSON (`{"message": {"content": "..."},
  "done": false}` per chunk) — this is what SDKs like the Anthropic or OpenAI
  clients are doing under the hood when you call `.stream(...)`.
- There's no retry/backoff logic here on purpose — see how the app behaves
  when Ollama isn't running or the model name is wrong, then decide for
  yourself whether that's worth adding.

## Moving to a hosted model later

Once you have an API key (Anthropic, OpenAI, etc.), the concepts transfer
directly — same `system` / `user` / `assistant` roles, same "resend full
history every turn" pattern, same idea of streaming chunks. Only the
transport changes: swap the `httpx` call to the vendor's endpoint (or their
SDK) and the auth header/key. Worth doing later as a comparison exercise.

## Ideas to extend (optional, before moving to Project 2)

- Add a `--system` CLI flag to swap the system prompt at launch.
- Persist `history` to a JSON file so conversations survive restarts.
- Try swapping `MODEL` to another pulled model (`ollama pull qwen2.5:7b`,
  etc.) and compare response quality/speed.
