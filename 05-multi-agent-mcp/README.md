# 05 — Multi-Agent Orchestration Over MCP

Phase 5 (capstone) project: two things combined, since they compound well —
(1) tools served over a real **MCP server** instead of living in the
agent's own process, and (2) a lightweight **orchestrator** that routes each
request to a scoped specialist agent.

## Setup

```bash
ollama serve &      # if not already running
uv run demo.py      # canned prompts: one routes to "math", one to "research"
uv run main.py      # interactive
```

`search_docs` reuses Project 3's index (`03-rag-over-docs/store.json`) —
build it there first if you haven't.

## Architecture

- **`mcp_server.py`** — the same three tools from Project 4 (`calculator`,
  `read_file`, `search_docs`), now served over the Model Context Protocol
  via `FastMCP`, in their own process. This is the same protocol Claude
  Code itself uses to talk to external tool servers — nothing here is
  MCP-flavored pseudocode, it's the real thing.
- **`mcp_tool_client.py`** — spawns the server over stdio, lists its tools,
  calls them. The agent only ever sees tool name + JSON schema; it has no
  idea `calculator` is implemented with an AST-based evaluator.
- **`agent.py`** — the same ReAct loop as Project 4, adapted to pull tool
  schemas and execute calls through the MCP session instead of local
  functions. `allowed_tools` restricts which of the server's tools a given
  agent is permitted to call — that's what makes a "specialist."
- **`orchestrator.py`** — one small LLM call classifies the request as
  `math` or `research`, then hands off to that specialist with only its
  relevant tools visible. This is the orchestrator/worker pattern: one
  coordinating decision, tightly scoped workers.

## Two real bugs found while building this (kept, not papered over)

**1. An em-dash broke tool calling entirely.** The first version of the
`math` specialist's system prompt used `"...arithmetic — never compute it
yourself."` (an em-dash, `—`). With that character present, `llama3.2`
stopped emitting structured `tool_calls` and instead wrote the tool call
*as text*: `{"name":"calculator",""parameters":{}}` — malformed JSON, as
plain assistant content. Swapping the em-dash for a period fixed it
immediately and reproducibly. Confirmed directly against the raw Ollama API
via `curl`, independent of any of this project's code — it's a genuine
quirk of this model's chat template, not a bug in `agent.py` or
`mcp_tool_client.py`. **Lesson:** small local models can be far more
sensitive to prompt formatting/punctuation than hosted frontier models;
don't assume a prompt that works on one model works unchanged on another.

**2. The calculator tool call itself is unreliable for compound questions.**
Asking "What is 683 * 94, minus 100?" gets `llama3.2` to emit a malformed
`expression` argument (`"* 683 94 - 100"`, prefix notation; or `"*92-100"`,
missing an operand) roughly 1 in 3 tries — even with correct tool calling
mechanics. When that happens, `calculator` returns an `error: ...` string,
which does get fed back to the model as a `tool` message — but the model
doesn't reliably retry the tool with a corrected expression; it sometimes
just estimates the answer itself and gets it wrong. **Lesson:** the agent
loop *supports* self-correction (the error is visible for the next
iteration), but whether the model actually uses that opportunity is a
capability gap, not something the harness can force. This is exactly the
kind of silent failure Phase 5's "observability" and "guardrails" themes
exist for — you'd want to log tool errors and flag answers that followed
one, rather than trust the model noticed.

## What to notice while reading the code

- `mcp_server.py`'s tool docstrings *are* the schema descriptions sent to
  the model (`FastMCP` reads them via the `@mcp.tool()` decorator) — compare
  this to Project 4's `tools.py`, where the description was a separate,
  hand-written string. MCP pushes you toward a single source of truth.
- `orchestrator.py`'s `route()` is a full extra LLM call before any real
  work happens — for a two-specialist system this routing overhead is
  arguably not worth it over a simpler heuristic; it starts paying for
  itself once there are enough specialists (or tools) that no single agent
  should see all of them at once (smaller tool lists → more reliable tool
  calls, as tool count grows).
- `agent.py`'s `allowed_tools` filtering happens in two places: once when
  building the schema list sent to the model (so it can't even see
  disallowed tools), and again when executing a call (so a model that
  hallucinates a tool name outside its schema still can't run it). Defense
  in depth, not redundancy.

## Ideas to extend

- Make the agent loop retry-aware: on a tool error, explicitly instruct the
  model "the last call failed, try a corrected expression" instead of
  hoping it notices — then see if that closes the reliability gap from bug #2.
- Add a third specialist and a real multi-tool task that needs routing
  *and* a handoff between specialists (e.g., "look up X in the docs, then
  compute Y based on it") — that's where orchestration earns its cost.
- Swap `llama3.2` for a larger local model (`qwen2.5:7b` or similar) and
  re-run `demo.py` — does the malformed-expression rate drop?
- Point Claude Code itself at `mcp_server.py` as an MCP server (via
  `claude mcp add`) and call these same tools from inside a real Claude
  Code session — the same server, a different client.
