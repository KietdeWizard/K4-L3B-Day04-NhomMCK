from __future__ import annotations

from typing import Any


def confirm_dose_taken(
    patient_id: str = "",
    medication_name: str = "",
    time_taken: str = "",
    confirmed_by: str = "patient",
) -> dict[str, Any]:
    return {
        "tool": "confirm_dose_taken",
        "patient_id": (patient_id or "").strip(),
        "medication_name": (medication_name or "").strip(),
        "time_taken": (time_taken or "").strip(),
        "confirmed_by": (confirmed_by or "patient").strip().lower(),
        "status": "logged",
    }
