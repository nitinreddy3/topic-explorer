"""
The agent loop itself — the part every agent framework wraps in an
abstraction. Written out in full here so none of it is a black box.

Loop:
  1. Send the conversation + tool schemas to the model.
  2. If the model asks for tool calls, execute them locally and append the
     results as "tool" messages.
  3. Repeat until the model responds with plain content instead of tool
     calls, or a safety cap on iterations is hit.

The iteration cap is not decoration — an agent that keeps calling tools and
never converges on an answer is a real failure mode, not a hypothetical one.
"""

from ollama_client import chat
from tools import TOOL_SCHEMAS, TOOLS

MAX_ITERATIONS = 6


def run_agent(user_message: str, history: list[dict], *, verbose: bool = True) -> str:
    history.append({"role": "user", "content": user_message})

    for _ in range(MAX_ITERATIONS):
        message = chat(history, tools=TOOL_SCHEMAS)
        history.append(message)

        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content", "")

        for call in tool_calls:
            name = call["function"]["name"]
            arguments = call["function"]["arguments"]
            tool_fn = TOOLS.get(name)

            if verbose:
                print(f"  [tool call] {name}({arguments})")

            result = f"error: unknown tool {name!r}" if tool_fn is None else tool_fn(**arguments)

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
