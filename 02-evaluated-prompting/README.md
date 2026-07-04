# 02 — Evaluated Prompt Engineering

Phase 2 project: the same support-ticket triage task run through two prompt
variants, scored against a labeled dataset. The skill here isn't writing a
clever prompt — it's being able to say *objectively* whether a prompt change
helped, instead of eyeballing a few outputs and guessing.

## Setup

```bash
ollama serve &          # if not already running
uv run main.py
```

## What it does

- `dataset.py` — 12 hand-labeled support tickets (category + priority),
  including a few deliberately borderline cases.
- `prompts.py` — `naive_prompt` (zero-shot, no definitions) vs
  `improved_prompt` (category/priority definitions, few-shot examples,
  explicit "think, then output only JSON").
- `eval.py` — sends each ticket through a prompt variant, extracts JSON from
  the reply, scores it against the label.
- `main.py` — runs both variants, prints per-example pass/fail and a
  summary table.

## A real run's result (yours may vary slightly)

```
variant           category  priority     exact
naive prompt            0%        0%        0%
improved prompt        92%       75%       75%
```

**Why the naive prompt scored 0%, not just "worse":** it never told the model
what category/priority *vocabulary* to use, so it freely invented labels like
`"Account/Authentication"` and `"Urgent"` instead of `bug` and `high`. The
model wasn't necessarily wrong about the ticket's meaning — but with no
agreed-upon schema, nothing downstream (a script, a database column, another
LLM call) can reliably consume its output. This is the concrete case for
constrained/structured output, not just "nicer prompts."

## What to notice while reading the code

- `ollama_client.py` sets `"format": "json"` at the API level (JSON mode) —
  that alone guarantees valid JSON syntax, but not the *right keys or
  vocabulary*. Compare the naive prompt's output: valid JSON, wrong content.
- `eval.py`'s `extract_json` exists because even in JSON mode, smaller models
  occasionally add stray text — a real eval harness has to handle that
  instead of crashing.
- The dataset has ambiguous cases on purpose (e.g. ticket 4 "How do I export
  to CSV" scored `medium` instead of `low` even with the improved prompt) —
  100% accuracy on your own eval set is a warning sign of an eval that's too
  easy, not a prompt that's perfect.

## Ideas to extend (optional, before moving to Project 3)

- Add a third prompt variant using true few-shot *diversity* (one example per
  category) and see if it closes the remaining priority-accuracy gap.
- Swap in a bigger local model (`ollama pull qwen2.5:7b`) and compare —
  does prompt quality matter less as model capability goes up?
- Add a "self-consistency" variant: call the model 3x per ticket and take a
  majority vote, then compare cost (3x calls) vs accuracy gain.
