from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .check_reminder_schedule.tool import check_reminder_schedule
from .confirm_dose_taken.tool import confirm_dose_taken
from .escalate_to_clinician.tool import escalate_to_clinician
from .lookup_policy.tool import lookup_policy
from .notify_caregiver.tool import notify_caregiver
from .record_side_effect.tool import record_side_effect
from .search_medical_guide.tool import search_medical_guide
from .view_medication_plan.tool import view_medication_plan


# Medication adherence version: registry must match tools.yaml and eval datasets.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "view_medication_plan": view_medication_plan,
    "check_reminder_schedule": check_reminder_schedule,
    "confirm_dose_taken": confirm_dose_taken,
    "record_side_effect": record_side_effect,
    "lookup_policy": lookup_policy,
    "notify_caregiver": notify_caregiver,
    "escalate_to_clinician": escalate_to_clinician,
    "search_medical_guide": search_medical_guide,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]
