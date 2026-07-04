"""
Project 4: a hand-rolled agent with tools.

No LangChain/LangGraph — the entire agent loop lives in agent.py, in about
30 lines. This project exists to demystify what those frameworks automate.

Run:
    uv run main.py
"""

from agent import run_agent

SYSTEM_PROMPT = """You are a helpful assistant with access to tools: a \
calculator, a file reader (sandboxed to the topic-explorer repo), and a doc \
search over this repo's own indexed content. Use a tool whenever it would \
give a more reliable answer than reasoning alone — don't guess at arithmetic \
or file contents you haven't actually read."""


def main() -> None:
    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Agent with tools (calculator, read_file, search_docs). Type 'exit' to quit.\n")

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

        answer = run_agent(user_input, history)
        print(f"\nassistant> {answer}\n")


if __name__ == "__main__":
    main()
