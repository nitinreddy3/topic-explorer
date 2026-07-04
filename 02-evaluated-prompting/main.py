"""
Project 2: evaluated prompt engineering.

Runs the same ticket-triage task through a naive prompt and an improved
prompt, scores both against a labeled dataset, and prints a side-by-side
comparison. The point isn't the task itself — it's having a repeatable way
to answer "did my prompt change actually help?" instead of eyeballing it.

Run:
    uv run main.py
"""

from dataset import DATASET
from eval import run_eval
from prompts import improved_prompt, naive_prompt


def print_report(report: dict) -> None:
    print(f"\n=== {report['name']} ===")
    print(f"category accuracy:    {report['category_accuracy']:.0%}")
    print(f"priority accuracy:    {report['priority_accuracy']:.0%}")
    print(f"exact match accuracy: {report['exact_match_accuracy']:.0%}")
    print(f"parse failures:       {report['parse_failures']}/{len(report['results'])}")
    for r in report["results"]:
        mark = "PASS" if r["category_ok"] and r["priority_ok"] else "FAIL"
        ticket_preview = r["ticket"][:55]
        print(f"  [{mark}] {ticket_preview!r:58} expected={r['expected']} got={r['predicted']}")


def main() -> None:
    naive_report = run_eval("naive prompt", naive_prompt, DATASET)
    improved_report = run_eval("improved prompt", improved_prompt, DATASET)

    print_report(naive_report)
    print_report(improved_report)

    print("\n=== Summary ===")
    print(f"{'variant':<16}{'category':>10}{'priority':>10}{'exact':>10}")
    for r in (naive_report, improved_report):
        print(
            f"{r['name']:<16}"
            f"{r['category_accuracy']:>10.0%}"
            f"{r['priority_accuracy']:>10.0%}"
            f"{r['exact_match_accuracy']:>10.0%}"
        )


if __name__ == "__main__":
    main()
