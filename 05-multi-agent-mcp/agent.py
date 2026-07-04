"""
The same ReAct loop as Project 4 (chat -> tool_calls? -> execute -> repeat),
except tools now come from an MCP server instead of local Python functions.
The agent doesn't know or care how a tool is implemented — only its name,
schema, and how to call it over the MCP session.

`allowed_tools` is what makes this a *specialist*: even though the MCP
server exposes all three tools, a given agent only sees (and is permitted
to call) the subset relevant to its job. Scoping tool access per agent is
a real guardrail, not just an implementation detail — see orchestrator.py.
"""

from mcp import ClientSession

from mcp_tool_client import call_tool, list_tool_schemas
from ollama_client import chat

MAX_ITERATIONS = 6


async def run_agent(
    user_message: str,
    history: list[dict],
    session: ClientSession,
    *,
    allowed_tools: set[str] | None = None,
    verbose: bool = True,
) -> str:
    history.append({"role": "user", "content": user_message})
    tool_schemas = await list_tool_schemas(session, allowed_tools)

    for _ in range(MAX_ITERATIONS):
        message = chat(history, tools=tool_schemas)
        history.append(message)

        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content", "")

        for call in tool_calls:
            name = call["function"]["name"]
            arguments = call["function"]["arguments"]

            if verbose:
                print(f"  [tool call] {name}({arguments})")

            if allowed_tools is not None and name not in allowed_tools:
                result = f"error: tool {name!r} not permitted for this agent"
            else:
                result = await call_tool(session, name, arguments)

            if verbose:
                preview = result if len(result) < 200 else result[:200] + "..."
                print(f"  [tool result] {preview}")

            history.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", name),
                    "content": result,
                }
            )

    return "[agent hit the max-iteration safety cap without producing a final answer]"
