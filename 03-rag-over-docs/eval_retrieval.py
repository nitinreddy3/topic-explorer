"""
Evaluate retrieval quality — the half of RAG that's easiest to get wrong
silently. For each question, check whether the chunk containing the actual
answer shows up in the top-k retrieved results at all. If retrieval misses
it, no amount of prompt engineering on the generation side will help.

(Evaluating the final generated *answer* is left as an extension — see
README.)

Run:
    uv run eval_retrieval.py
"""

from ollama_client import embed
from store import load_store, retrieve

TOP_K = 4

EVAL_SET = [
    {
        "question": "How do I run the raw API chatbot project?",
        "expected_source": "01-raw-api-chatbot/README.md",
    },
    {
        "question": "Why did the naive prompt score 0 percent in the evaluated prompting project?",
        "expected_source": "02-evaluated-prompting/README.md",
    },
    {
        "question": "How does the eval harness handle a model reply that isn't valid JSON?",
        "expected_source": "02-evaluated-prompting/eval.py",
    },
    {
        "question": "What five projects make up this learning repo?",
        "expected_source": "README.md",
    },
    {
        "question": "What categories can a support ticket be classified into?",
        "expected_source": "02-evaluated-prompting/prompts.py",
    },
    {
        "question": "What happens if Ollama isn't running when the chatbot starts?",
        "expected_source": "01-raw-api-chatbot/main.py",
    },
]


def main() -> None:
    chunks = load_store()
    hits = 0

    for case in EVAL_SET:
        query_embedding = embed(case["question"])
        top_chunks = retrieve(query_embedding, chunks, top_k=TOP_K)
        retrieved_sources = {c["source"] for c in top_chunks}
        hit = case["expected_source"] in retrieved_sources
        hits += hit

        mark = "PASS" if hit else "FAIL"
        print(f"[{mark}] {case['question']!r}")
        print(f"       expected:  {case['expected_source']}")
        print(f"       retrieved: {sorted(retrieved_sources)}")

    print(f"\nretrieval hit rate: {hits}/{len(EVAL_SET)} ({hits / len(EVAL_SET):.0%})")


if __name__ == "__main__":
    main()
