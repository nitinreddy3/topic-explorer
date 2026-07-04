"""
Runs a fixed set of prompts through the orchestrator non-interactively —
one that should route to "math", one to "research" — so both specialists
and the MCP round-trip get exercised without typing anything.

Run:
    uv run demo.py
"""

import asyncio

from orchestrator import handle

PROMPTS = [
    "What is 683 * 94, minus 100?",
    "Using the doc search tool, what does this repo's Project 2 README say caused the naive prompt to score 0 percent?",
]


async def main() -> None:
    for prompt in PROMPTS:
        print(f"\n{'=' * 70}\nyou> {prompt}")
        answer = await handle(prompt)
        print(f"assistant> {answer}")


if __name__ == "__main__":
    asyncio.run(main())
