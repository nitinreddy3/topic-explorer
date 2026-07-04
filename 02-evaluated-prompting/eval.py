"""Eval harness: run a prompt variant over the dataset and score it.

This is the skill Phase 2 is really about — not writing a clever prompt, but
being able to say *objectively* whether one prompt is better than another.
"""

import json
from typing import Callable

from ollama_client import chat


def extract_json(text: str) -> dict | None:
    """Best-effort extraction of a JSON object from a model reply.

    Models (especially smaller local ones) sometimes wrap JSON in prose or
    markdown fences even when asked not to — this pulls out the outermost
    {...} block rather than crashing on the first stray character.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def run_eval(name: str, prompt_fn: Callable[[str], list[dict]], dataset: list[dict]) -> dict:
    results = []
    for example in dataset:
        messages = prompt_fn(example["ticket"])
        raw = chat(messages, json_mode=True)
        parsed = extract_json(raw)

        category_ok = bool(parsed) and parsed.get("category") == example["category"]
        priority_ok = bool(parsed) and parsed.get("priority") == example["priority"]

        results.append(
            {
                "ticket": example["ticket"],
                "expected": {"category": example["category"], "priority": example["priority"]},
                "predicted": parsed,
                "category_ok": category_ok,
                "priority_ok": priority_ok,
                "parse_failed": parsed is None,
            }
        )

    n = len(results)
    return {
        "name": name,
        "results": results,
        "category_accuracy": sum(r["category_ok"] for r in results) / n,
        "priority_accuracy": sum(r["priority_ok"] for r in results) / n,
        "exact_match_accuracy": sum(r["category_ok"] and r["priority_ok"] for r in results) / n,
        "parse_failures": sum(r["parse_failed"] for r in results),
    }
