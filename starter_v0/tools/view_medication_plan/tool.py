from __future__ import annotations

from typing import Any


def view_medication_plan(
    patient_id: str = "",
    medication_name: str = "",
    time_window: str = "today",
) -> dict[str, Any]:
    normalized_time = (time_window or "today").strip().lower()
    normalized_patient = (patient_id or "").strip()
    normalized_med = (medication_name or "").strip()
    plan = [
        {
            "medication": normalized_med or "Metformin",
            "dose": "500mg",
            "time": "08:00",
            "status": "scheduled",
        },
        {
            "medication": normalized_med or "Amlodipine",
            "dose": "5mg",
            "time": "20:00",
            "status": "scheduled",
        },
    ]
    if normalized_patient:
        return {
            "tool": "view_medication_plan",
            "patient_id": normalized_patient,
            "medication_name": normalized_med,
            "time_window": normalized_time,
            "plan": plan,
            "status": "ok",
        }
    return {
        "tool": "view_medication_plan",
        "patient_id": normalized_patient,
        "medication_name": normalized_med,
        "time_window": normalized_time,
        "plan": plan,
        "status": "ok",
    }
