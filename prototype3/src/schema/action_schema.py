from __future__ import annotations

from dataclasses import dataclass, field

SUPPORTED_ACTIONS = {
    "pick",
    "place",
    "moveee",
    "opengripper",
    "closegripper",
    "reset",
    "describescene",
}


@dataclass
class SchemaValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    normalized_actions: list[dict] | None = None


def _validate_single_action(action: object, idx: int) -> list[str]:
    errors: list[str] = []

    if not isinstance(action, dict):
        return [f"action[{idx}].not_an_object"]

    action_name = action.get("action")
    if action_name is None:
        return [f"action[{idx}].missing_action_field"]

    if action_name not in SUPPORTED_ACTIONS:
        return [f"action[{idx}].unknown_action:{action_name}"]

    if action_name == "pick":
        obj = action.get("object")
        if not isinstance(obj, str):
            errors.append(f"action[{idx}].missing_object")

    elif action_name == "place":
        target = action.get("target")
        if not isinstance(target, str):
            errors.append(f"action[{idx}].missing_target")

    elif action_name == "moveee":
        target = action.get("target")
        target_xyz = action.get("target_xyz")
        if target is None and target_xyz is None:
            errors.append(f"action[{idx}].missing_target_and_target_xyz")
        if target_xyz is not None:
            if (
                not isinstance(target_xyz, list)
                or len(target_xyz) != 3
                or not all(isinstance(v, (int, float)) for v in target_xyz)
            ):
                errors.append(f"action[{idx}].invalid_target_xyz")

    elif action_name == "opengripper":
        width = action.get("width")
        if width is not None and not isinstance(width, (int, float)):
            errors.append(f"action[{idx}].invalid_width")

    elif action_name == "closegripper":
        force = action.get("force")
        if force is not None and not isinstance(force, (int, float)):
            errors.append(f"action[{idx}].invalid_force")

    return errors


def validate_action_plan(parsed: object) -> SchemaValidationResult:
    """Validate a parsed model output against the Prototype 3 action schema.

    Returns SchemaValidationResult with valid=True only when the entire plan
    satisfies the schema. Never raises on invalid input.
    """
    if isinstance(parsed, dict):
        if "actions" not in parsed:
            return SchemaValidationResult(
                valid=False,
                errors=["top_level_dict_missing_actions_key"],
            )
        actions_raw = parsed["actions"]
        if not isinstance(actions_raw, list):
            return SchemaValidationResult(
                valid=False,
                errors=["actions_field_not_list"],
            )
        action_list = actions_raw
    elif isinstance(parsed, list):
        action_list = parsed
    else:
        return SchemaValidationResult(
            valid=False,
            errors=["top_level_not_list_or_dict"],
        )

    all_errors: list[str] = []
    normalized: list[dict] = []
    for idx, action in enumerate(action_list):
        errs = _validate_single_action(action, idx)
        if errs:
            all_errors.extend(errs)
        else:
            normalized.append(dict(action))

    if all_errors:
        return SchemaValidationResult(valid=False, errors=all_errors)

    return SchemaValidationResult(
        valid=True,
        errors=[],
        normalized_actions=normalized,
    )
