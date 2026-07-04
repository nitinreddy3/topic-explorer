# 01 — Raw-API Chatbot

Phase 1 project: a terminal chatbot built directly against the Anthropic API,
with no agent framework in between. The point is to see the actual mechanics —
message roles, conversation history, streaming — before anything abstracts
them away.

## Setup

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run main.py
```

## What to notice while reading `main.py`

- The API has no memory of its own — `history` is a plain Python list that
  gets resent in full on every call. Try commenting out `history.append(...)`
  for the assistant reply and see the model "forget" what it just said.
- `client.messages.stream(...)` yields text incrementally instead of blocking
  until the whole reply is done.
- There's no retry/backoff logic here on purpose — see how the app behaves
  when the network drops or the key is invalid, then decide for yourself
  whether that's worth adding.

## Ideas to extend (optional, before moving to Project 2)

- Add a `--system` CLI flag to swap the system prompt at launch.
- Persist `history` to a JSON file so conversations survive restarts.
- Add a token/cost counter using the `usage` field on the response.
