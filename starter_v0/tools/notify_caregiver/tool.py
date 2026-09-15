from __future__ import annotations

from typing import Any


def notify_caregiver(
    patient_id: str = "",
    caregiver_id: str = "",
    message: str = "",
    confirmed: bool = False,
) -> dict[str, Any]:
    return {
        "tool": "notify_caregiver",
        "patient_id": (patient_id or "").strip(),
        "caregiver_id": (caregiver_id or "").strip(),
        "message": (message or "").strip(),
        "confirmed": bool(confirmed),
        "status": "notified",
    }
