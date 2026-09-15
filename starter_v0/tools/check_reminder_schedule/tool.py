from __future__ import annotations

from typing import Any


def check_reminder_schedule(
    patient_id: str = "",
    medication_name: str = "",
    day: str = "today",
) -> dict[str, Any]:
    normalized_patient = (patient_id or "").strip()
    normalized_med = (medication_name or "").strip() or "Metformin"
    normalized_day = (day or "today").strip().lower()
    return {
        "tool": "check_reminder_schedule",
        "patient_id": normalized_patient,
        "medication_name": normalized_med,
        "day": normalized_day,
        "next_reminder": "08:00",
        "missed_doses": 0,
        "status": "ok",
    }
