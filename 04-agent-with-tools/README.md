# 04 — Agent With Tools

Phase 4 project: a minimal agent loop, hand-rolled — no LangChain, no
LangGraph, no Agent SDK. The whole loop is in `agent.py`, about 30 lines.
The goal is to see exactly what "tool use" and "the agent loop" mean
mechanically, before reaching for a framework that automates it.

## Setup

```bash
ollama serve &      # if not already running
uv run demo.py      # canned prompts exercising all 3 tools, non-interactive
uv run main.py      # interactive chat
```

`search_docs` reuses the vector index built in Project 3
(`03-rag-over-docs/store.json`) — run `uv run ingest.py` there first if you
haven't.

## The loop, in one paragraph

Send the conversation + tool schemas to the model. If it responds with
`tool_calls` instead of plain text, run each tool locally, append the
results as `role: "tool"` messages, and send the whole thing back. Repeat
until the model responds with plain content, or a `MAX_ITERATIONS` safety
cap is hit. That's the entire ReAct pattern (`agent.py:run_agent`).

## The three tools

| Tool | What it does | Why it's here |
|---|---|---|
| `calculator` | Evaluates arithmetic via an AST whitelist (no `eval()`) | Models are bad at exact arithmetic — a classic case where a tool beats reasoning |
| `read_file` | Reads a file, sandboxed to the repo root | Any real "file access" tool needs a sandbox boundary, not just a path argument |
| `search_docs` | Semantic search over Project 3's index | Reuses earlier work — an agent with retrieval *is* RAG, just invoked on demand instead of always |

## A real run's output

```
you> What is 683 * 94, minus 100?
  [tool call] calculator({'expression': '683 * 94 - 100'})
  [tool result] 64102
assistant> The result of the calculation is: 64,102.

you> What's the capital of France?
  [tool call] search_docs({'query': 'capital of France'})
  [tool result] [01-raw-api-chatbot/main.py] ...
assistant> The capital of France is Paris.
```

**Notice the second one.** Nothing about "capital of France" needed a tool —
the model already knows the answer — but it called `search_docs` anyway,
got back an irrelevant chunk from `main.py`, and (fortunately) ignored it in
favor of its own knowledge. This is a real, common agentic-AI failure mode:
models over-triggering tools even when reasoning alone would do, and it's
not something the model always fails safely on — with different tools or
prompts, an irrelevant retrieved chunk can just as easily *mislead* the
final answer instead of being ignored.

## What to notice while reading the code

- `ollama_client.chat()` returns the raw message dict, not just text, so
  `agent.py` can inspect `tool_calls` and feed the exact same message back
  into history — that round-trip is what keeps the model's tool-call
  reasoning consistent across turns.
- `MAX_ITERATIONS` in `agent.py` exists because "call a tool, get a result,
  decide to call another tool" can loop indefinitely if the model gets
  stuck — this cap is a minimal example of the guardrails Phase 5 covers in
  more depth.
- `calculator` uses an `ast`-based whitelist instead of `eval()` on purpose:
  the input comes from the model, which is effectively untrusted input from
  a security standpoint, since a malicious or manipulated prompt could try
  to inject something like `__import__('os').system(...)`.

## Ideas to extend (optional, before moving to Project 5)

- Add a system-prompt instruction telling the model when *not* to use a
  tool, then re-run `demo.py`'s "capital of France" case — does it stop
  over-triggering `search_docs`?
- Add a `list_files` tool (sandboxed like `read_file`) so the agent can
  discover what's available instead of needing exact paths.
- Log every tool call with a timestamp to a file — the beginning of the
  "observability" theme from Phase 5.
- Try a deliberately ambiguous prompt (e.g. "check if this is faster: 12**5
  or reading main.py") and see whether the model picks the right tool(s).
