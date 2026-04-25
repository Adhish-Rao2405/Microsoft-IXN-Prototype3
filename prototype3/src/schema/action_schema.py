from __future__ import annotations

from dataclasses import dataclass

ALLOWED_ACTIONS = {
    "pick",
    "place",
    "move",
    "open_gripper",
    "reset_robot",
}
ALLOWED_OBJECTS = {
    "medicine_cup",
    "pill_box",
    "gauze_pack",
    "tray",
}
ALLOWED_ZONES = {
    "left_zone",
    "right_zone",
    "handover_zone",
    "safe_area",
}


@dataclass
class SchemaValidationResult:
    valid: bool
    reasons: list[str]


def validate_actions(planned_actions: list[dict] | None) -> SchemaValidationResult:
    # Reject-by-default: missing or malformed plans are invalid until proven valid.
    if not planned_actions:
        return SchemaValidationResult(valid=False, reasons=["empty_plan"])

    reasons: list[str] = []
    for idx, action in enumerate(planned_actions):
        if not isinstance(action, dict):
            reasons.append(f"action_{idx}_not_object")
            continue

        action_name = action.get("action")
        if action_name not in ALLOWED_ACTIONS:
            reasons.append(f"action_{idx}_unsupported_action")
            continue

        if action_name in {"pick", "place", "move"}:
            obj = action.get("object")
            if obj not in ALLOWED_OBJECTS:
                reasons.append(f"action_{idx}_invalid_object")

        if action_name in {"place", "move"}:
            target = action.get("target")
            if target not in ALLOWED_ZONES and target not in ALLOWED_OBJECTS:
                reasons.append(f"action_{idx}_invalid_target")

    return SchemaValidationResult(valid=len(reasons) == 0, reasons=reasons)


def validate_safety(planned_actions: list[dict] | None) -> bool:
    # Minimal local safety concept: reject unknown actions and any explicit unsafe target.
    if not planned_actions:
        return False

    for action in planned_actions:
        if not isinstance(action, dict):
            return False
        if action.get("action") not in ALLOWED_ACTIONS:
            return False
        if action.get("target") == "unsafe_area":
            return False
    return True
