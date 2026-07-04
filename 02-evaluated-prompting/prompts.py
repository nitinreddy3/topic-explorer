"""Two prompt variants for the same task, so the eval can quantify the gap.

naive_prompt:    zero-shot, no definitions, no examples — what most people
                 write on their first try.
improved_prompt: category/priority definitions + few-shot examples +
                 an explicit "think step by step, then output only JSON"
                 instruction.
"""


def naive_prompt(ticket: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": (
                f"Classify this support ticket:\n\n{ticket}\n\n"
                "Respond in JSON with 'category' and 'priority' fields."
            ),
        }
    ]


IMPROVED_SYSTEM_PROMPT = """You are a support ticket triage assistant.

Classify each ticket into exactly one category:
- bug: something in the product is broken or not working as expected
- billing: questions or issues about payments, invoices, subscriptions, refunds
- feature_request: the customer is asking for new functionality that doesn't exist today
- question: a how-to or informational question with no bug or billing issue

Assign a priority:
- high: the customer is blocked, losing money, or facing data loss/security risk
- medium: an inconvenience with a workaround, or a paying/enterprise customer's request
- low: a minor annoyance, cosmetic issue, or a nice-to-have request

Think step by step about which category and priority fit best, then respond
with ONLY a JSON object of the form: {"category": "...", "priority": "..."}

Examples:
Ticket: "I can't log in, it says my password is wrong even though I just reset it."
{"category": "bug", "priority": "high"}

Ticket: "Can you add dark mode to the dashboard?"
{"category": "feature_request", "priority": "low"}

Ticket: "I was charged twice for my subscription this month."
{"category": "billing", "priority": "high"}
"""


def improved_prompt(ticket: str) -> list[dict]:
    return [
        {"role": "system", "content": IMPROVED_SYSTEM_PROMPT},
        {"role": "user", "content": f'Ticket: "{ticket}"'},
    ]
