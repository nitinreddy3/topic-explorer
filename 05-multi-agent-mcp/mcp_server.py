"""
An MCP server exposing three tools: calculator, read_file, search_docs.

Same tool logic as Project 4, but instead of being Python functions living
inside the agent's own process, they're served over the Model Context
Protocol — the same mechanism Claude Code itself uses to talk to external
tool servers. Any MCP-compatible client (this project's agent, Claude Code,
Claude Desktop, ...) can discover and call these tools without knowing how
they're implemented.

Run standalone to sanity-check it starts:
    uv run mcp_server.py
(it will then wait on stdio for a client — Ctrl+C to stop)
"""

import ast
import json
import operator
import os

import httpx
from mcp.server.fastmcp import FastMCP

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_STORE_PATH = os.path.join(REPO_ROOT, "03-rag-over-docs", "store.json")

EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

mcp = FastMCP("topic-explorer-tools")


# ---- calculator ----

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")


@mcp.tool()
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression (+, -, *, /, **) and return the numeric result."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        return f"error: could not evaluate {expression!r}: {e}"


# ---- read_file ----


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file's contents by path, relative to the topic-explorer repo root."""
    full_path = os.path.abspath(os.path.join(REPO_ROOT, path))
    if not (full_path == REPO_ROOT or full_path.startswith(REPO_ROOT + os.sep)):
        return f"error: access denied, {path!r} is outside the repo"
    if not os.path.isfile(full_path):
        return f"error: no such file: {path!r}"
    with open(full_path) as f:
        return f.read()[:4000]


# ---- search_docs (reuses Project 3's index) ----


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


@mcp.tool()
def search_docs(query: str) -> str:
    """Semantic search over this repo's indexed docs/code (built in Project 3) for a natural-language query."""
    if not os.path.exists(RAG_STORE_PATH):
        return "error: no doc index found — run `uv run ingest.py` in 03-rag-over-docs first"

    with open(RAG_STORE_PATH) as f:
        chunks = json.load(f)

    response = httpx.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": query}, timeout=60)
    response.raise_for_status()
    query_embedding = response.json()["embedding"]

    scored = sorted(chunks, key=lambda c: _cosine_similarity(query_embedding, c["embedding"]), reverse=True)
    top = scored[:3]
    return "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in top)


if __name__ == "__main__":
    mcp.run()
