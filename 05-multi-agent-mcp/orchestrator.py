"""
Orchestrator/worker multi-agent pattern: one lightweight LLM call routes a
request to the right specialist, which then runs its own agent loop with
only the tools relevant to its job.

This is the simplest version of "multi-agent" that's actually worth the
added complexity — routing plus scoped tool access, not a swarm of
identical agents talking to each other. See the README for when this
pattern stops paying for itself.
"""

from agent import run_agent
from mcp_tool_client import mcp_session
from ollama_client import chat

SPECIALISTS = {
    "math": {
        "tools": {"calculator"},
        "system_prompt": "You are a math specialist. Use the calculator tool for any arithmetic. Never compute it yourself.",
    },
    "research": {
        "tools": {"read_file", "search_docs"},
        "system_prompt": (
            "You are a research specialist over the topic-explorer repo. "
            "Use read_file and search_docs to answer from real content. Don't guess at file contents."
        ),
    },
}

ROUTER_SYSTEM_PROMPT = (
    'You route user requests to the right specialist. Respond with ONLY one word: "math" or "research".'
)


def route(user_message: str) -> str:
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    reply = chat(messages).get("content", "").strip().lower()
    return "math" if "math" in reply else "research"


async def handle(user_message: str, *, verbose: bool = True) -> str:
    specialist_name = route(user_message)
    specialist = SPECIALISTS[specialist_name]

    if verbose:
        print(f"  [orchestrator] routed to: {specialist_name}")

    async with mcp_session() as session:
        history = [{"role": "system", "content": specialist["system_prompt"]}]
        return await run_agent(
            user_message,
            history,
            session,
            allowed_tools=specialist["tools"],
            verbose=verbose,
        )
