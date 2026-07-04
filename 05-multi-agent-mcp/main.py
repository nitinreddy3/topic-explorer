"""
Project 5: multi-agent orchestration over an MCP server.

Tools (calculator, read_file, search_docs) are served by a standalone MCP
server (mcp_server.py) instead of living inside the agent's own process. An
orchestrator routes each request to a scoped specialist agent — "math" or
"research" — that only sees the tools relevant to its job.

Run:
    uv run main.py
"""

import asyncio

from orchestrator import handle


async def main() -> None:
    print("Multi-agent orchestrator (math / research specialists via MCP). Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            break

        answer = await handle(user_input)
        print(f"\nassistant> {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
