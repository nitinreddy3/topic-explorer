"""Tool implementations plus the JSON-schema descriptions the model sees.

The agent loop never calls a tool by name directly — it looks up whatever
name the model requested in TOOLS. This is the same pattern MCP formalizes:
a name, a schema, and a function to run.
"""

import ast
import json
import operator
import os

import httpx

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_STORE_PATH = os.path.join(REPO_ROOT, "03-rag-over-docs", "store.json")

EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


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


def calculator(expression: str) -> str:
    """Evaluate arithmetic via an AST whitelist — no eval(), so no arbitrary
    code execution even though the model's input is untrusted."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        return f"error: could not evaluate {expression!r}: {e}"


# ---- read_file ----


def read_file(path: str) -> str:
    """Read a file's contents, sandboxed to this repo's directory."""
    full_path = os.path.abspath(os.path.join(REPO_ROOT, path))
    if not (full_path == REPO_ROOT or full_path.startswith(REPO_ROOT + os.sep)):
        return f"error: access denied, {path!r} is outside the repo"
    if not os.path.isfile(full_path):
        return f"error: no such file: {path!r}"
    with open(full_path) as f:
        content = f.read()
    return content[:4000]  # cap so one tool call can't blow the context window


# ---- search_docs (reuses Project 3's index) ----


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def search_docs(query: str) -> str:
    """Semantic search over Project 3's doc index, if it's been built."""
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


TOOLS = {
    "calculator": calculator,
    "read_file": read_file,
    "search_docs": search_docs,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression (+, -, *, /, **) and return the numeric result.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": 'e.g. "47 * 89"'}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file's contents by path, relative to the topic-explorer repo root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": 'e.g. "01-raw-api-chatbot/README.md"'}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Semantic search over this repo's indexed docs/code (built in Project 3) for a natural-language query.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
]
