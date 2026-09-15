from __future__ import annotations

from typing import Any


def search_medical_guide(
    query: str = "",
    category: str = "all",
    top_k: int = 3,
) -> dict[str, Any]:
    normalized_query = (query or "").strip()
    normalized_category = (category or "all").strip().lower()
    return {
        "tool": "search_medical_guide",
        "query": normalized_query,
        "category": normalized_category,
        "results": [
            {
                "title": "Medication reminder best practice",
                "category": normalized_category or "all",
                "content": "Use reminders and confirmation only; do not change dose without clinician approval.",
            }
        ][: max(1, int(top_k or 3))],
        "status": "ok",
    }
