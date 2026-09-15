from __future__ import annotations

from typing import Any


def record_side_effect(
    patient_id: str = "",
    medication_name: str = "",
    symptom: str = "",
    severity: str = "moderate",
    confirmed: bool = False,
) -> dict[str, Any]:
    return {
        "tool": "record_side_effect",
        "patient_id": (patient_id or "").strip(),
        "medication_name": (medication_name or "").strip(),
        "symptom": (symptom or "").strip(),
        "severity": (severity or "moderate").strip().lower(),
        "confirmed": bool(confirmed),
        "status": "logged",
    }
