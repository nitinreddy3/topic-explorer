# topic-explorer

Learning journey: LLMs → prompt engineering → RAG → agentic AI → agentic
coding tools (Claude Code, MCP). Each phase is its own project directory,
runnable independently.

All projects run against a **local model via Ollama** — no API key or cost
required. See each project's README for how to port it to a hosted API later.

## Projects

1. [`01-raw-api-chatbot`](01-raw-api-chatbot) — chat with a local LLM
   directly over raw HTTP, no SDK, no framework. Message roles, history,
   streaming.
2. [`02-evaluated-prompting`](02-evaluated-prompting) — naive vs.
   well-specified prompts on the same task, scored against a labeled
   dataset, so "did this prompt change help?" has a real answer.
3. [`03-rag-over-docs`](03-rag-over-docs) — chat with this repo's own docs,
   built from scratch (chunking, embeddings, brute-force cosine similarity,
   no vector DB). Includes a retrieval-quality eval.
4. [`04-agent-with-tools`](04-agent-with-tools) — a hand-rolled agent loop
   (no LangChain/Agent SDK): calculator, sandboxed file reader, and doc
   search (reusing Project 3's index) as tools.
5. _(next: multi-agent / MCP integration)_
