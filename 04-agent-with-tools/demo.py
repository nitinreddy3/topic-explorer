"""
Runs a fixed set of prompts through the agent non-interactively, one per
tool (plus one needing no tool), so you can see each path exercised without
typing anything. Good smoke test after changing agent.py or tools.py.

Run:
    uv run demo.py
"""

from agent import run_agent
from main import SYSTEM_PROMPT

PROMPTS = [
    "What is 683 * 94, minus 100?",
    "Read 01-raw-api-chatbot/README.md and tell me in one sentence what that project teaches.",
    "Using the doc search tool, what does this repo's Project 2 README say caused the naive prompt to score 0 percent?",
    "What's the capital of France?",
]


def main() -> None:
    for prompt in PROMPTS:
        print(f"\n{'=' * 70}\nyou> {prompt}")
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        answer = run_agent(prompt, history)
        print(f"assistant> {answer}")


if __name__ == "__main__":
    main()
