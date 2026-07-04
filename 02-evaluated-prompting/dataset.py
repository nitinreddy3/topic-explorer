"""Small labeled eval set for the support-ticket triage task.

Deliberately includes a few borderline cases (e.g. a feature request from a
paying customer, a "question" that's really a disguised bug report) so that
prompt quality actually matters — a naive prompt and a well-specified one
should not score the same.
"""

DATASET = [
    {
        "ticket": "I can't log in, it says my password is wrong even though I just reset it twice.",
        "category": "bug",
        "priority": "high",
    },
    {
        "ticket": "Can you add a dark mode option to the dashboard?",
        "category": "feature_request",
        "priority": "low",
    },
    {
        "ticket": "I was charged twice for my subscription this month, please refund the duplicate.",
        "category": "billing",
        "priority": "high",
    },
    {
        "ticket": "How do I export my data to a CSV file?",
        "category": "question",
        "priority": "low",
    },
    {
        "ticket": "The export button does nothing when I click it, no download, no error.",
        "category": "bug",
        "priority": "medium",
    },
    {
        "ticket": "We're an enterprise customer and would love bulk-user CSV import for onboarding new hires.",
        "category": "feature_request",
        "priority": "medium",
    },
    {
        "ticket": "My invoice from last month shows the wrong tax amount, can someone check it?",
        "category": "billing",
        "priority": "medium",
    },
    {
        "ticket": "Is there a keyboard shortcut to duplicate a row?",
        "category": "question",
        "priority": "low",
    },
    {
        "ticket": "All of our team's data disappeared after the update this morning, this is urgent.",
        "category": "bug",
        "priority": "high",
    },
    {
        "ticket": "I want to cancel my subscription but the cancel button is greyed out.",
        "category": "bug",
        "priority": "high",
    },
    {
        "ticket": "It would be nice if the app remembered my last filter settings between sessions.",
        "category": "feature_request",
        "priority": "low",
    },
    {
        "ticket": "What plans include API access, and is there a rate limit?",
        "category": "question",
        "priority": "low",
    },
]
