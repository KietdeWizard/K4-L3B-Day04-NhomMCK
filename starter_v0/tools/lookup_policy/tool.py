from __future__ import annotations

from typing import Any


def lookup_policy(
    query: str = "",
    policy_area: str = "all",
    top_k: int = 3,
) -> dict[str, Any]:
    normalized_query = (query or "").strip()
    normalized_area = (policy_area or "all").strip().lower()
    results = [
        {
            "title": "Clinical escalation rule",
            "area": normalized_area or "all",
            "fact": "Severe symptoms such as breathing difficulty, chest pain, or collapse require clinician or emergency escalation.",
        },
        {
            "title": "Medication adherence safety",
            "area": "adherence",
            "fact": "AI may remind and log adherence but cannot change an approved medication order without clinician review.",
        },
    ]
    return {
        "tool": "lookup_policy",
        "query": normalized_query,
        "policy_area": normalized_area,
        "results": results[: max(1, int(top_k or 3))],
        "status": "ok",
    }
