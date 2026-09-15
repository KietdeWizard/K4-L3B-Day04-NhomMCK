from __future__ import annotations

from typing import Any


def escalate_to_clinician(
    patient_id: str = "",
    urgency: str = "urgent",
    reason: str = "",
) -> dict[str, Any]:
    return {
        "tool": "escalate_to_clinician",
        "patient_id": (patient_id or "").strip(),
        "urgency": (urgency or "urgent").strip().lower(),
        "reason": (reason or "").strip(),
        "status": "escalated",
    }
