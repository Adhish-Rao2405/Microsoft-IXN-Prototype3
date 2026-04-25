from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Safety bounds for the constrained clinical manipulation workspace.
# These values are intentionally conservative and deterministic.
# ---------------------------------------------------------------------------
_COORD_MIN: float = -2.0        # metres — minimum per-axis workspace bound
_COORD_MAX: float = 2.0         # metres — maximum per-axis workspace bound
_GRIPPER_WIDTH_MAX: float = 0.20  # metres — maximum safe gripper opening
_GRIPPER_WIDTH_MIN: float = 0.0
_GRIPPER_FORCE_MAX: float = 50.0  # newtons — maximum safe gripping force
_GRIPPER_FORCE_MIN: float = 0.0

# Known clinical-scene objects that may be manipulated.
KNOWN_SAFE_OBJECTS: frozenset[str] = frozenset({
    "medicine_cup",
    "pill_box",
    "gauze_pack",
    "tray",
})

# Known clinical-scene placement zones.
KNOWN_SAFE_ZONES: frozenset[str] = frozenset({
    "left_zone",
    "right_zone",
    "handover_zone",
    "safe_area",
})

# All targets accepted by place / moveee with a string target.
KNOWN_SAFE_TARGETS: frozenset[str] = KNOWN_SAFE_ZONES | KNOWN_SAFE_OBJECTS

# Action names that this validator understands.  Any name outside this set
# is rejected — fail-closed by design.
_ALLOWED_ACTIONS: frozenset[str] = frozenset({
    "pick",
    "place",
    "moveee",
    "opengripper",
    "closegripper",
    "reset",
    "describescene",
})


@dataclass
class SafetyValidationResult:
    """Structured result of deterministic safety validation.

    Attributes:
        safe:             True only when every action in the plan passes all
                          safety rules without exception.
        violations:       Explicit, testable strings describing each failure.
        safe_actions:     The original action list echoed back when safe=True,
                          otherwise None.  The validator never mutates actions.
    """
    safe: bool
    violations: list[str] = field(default_factory=list)
    safe_actions: list[dict] | None = None


# ---------------------------------------------------------------------------
# Per-action safety rules
# ---------------------------------------------------------------------------

def _check_pick(action: dict, idx: int) -> list[str]:
    violations: list[str] = []
    obj = action.get("object")
    if not isinstance(obj, str) or obj not in KNOWN_SAFE_OBJECTS:
        violations.append(
            f"action[{idx}].unsafe_object:{obj!r}"
        )
    return violations


def _check_place(action: dict, idx: int) -> list[str]:
    violations: list[str] = []
    target = action.get("target")
    if not isinstance(target, str) or target not in KNOWN_SAFE_TARGETS:
        violations.append(
            f"action[{idx}].unsafe_target:{target!r}"
        )
    return violations


def _check_moveee(action: dict, idx: int) -> list[str]:
    violations: list[str] = []

    target = action.get("target")
    target_xyz = action.get("target_xyz")

    if target is None and target_xyz is None:
        violations.append(f"action[{idx}].missing_target_and_target_xyz")
        return violations

    if target is not None:
        if not isinstance(target, str) or target not in KNOWN_SAFE_TARGETS:
            violations.append(f"action[{idx}].unsafe_target:{target!r}")

    if target_xyz is not None:
        if (
            not isinstance(target_xyz, list)
            or len(target_xyz) != 3
            or not all(isinstance(v, (int, float)) for v in target_xyz)
        ):
            violations.append(f"action[{idx}].malformed_target_xyz")
        else:
            for axis_idx, coord in enumerate(target_xyz):
                if not (_COORD_MIN <= coord <= _COORD_MAX):
                    violations.append(
                        f"action[{idx}].target_xyz[{axis_idx}]"
                        f"_out_of_bounds:{coord}"
                    )

    return violations


def _check_opengripper(action: dict, idx: int) -> list[str]:
    violations: list[str] = []
    width = action.get("width")
    if width is not None:
        if not isinstance(width, (int, float)):
            violations.append(f"action[{idx}].non_numeric_width:{width!r}")
        elif not (_GRIPPER_WIDTH_MIN <= width <= _GRIPPER_WIDTH_MAX):
            violations.append(
                f"action[{idx}].unsafe_width:{width}"
                f" (allowed 0.0–{_GRIPPER_WIDTH_MAX})"
            )
    return violations


def _check_closegripper(action: dict, idx: int) -> list[str]:
    violations: list[str] = []
    force = action.get("force")
    if force is not None:
        if not isinstance(force, (int, float)):
            violations.append(f"action[{idx}].non_numeric_force:{force!r}")
        elif not (_GRIPPER_FORCE_MIN <= force <= _GRIPPER_FORCE_MAX):
            violations.append(
                f"action[{idx}].unsafe_force:{force}"
                f" (allowed 0.0–{_GRIPPER_FORCE_MAX})"
            )
    return violations


# reset and describescene have no mutable parameters — always safe if the
# action name itself is known.
_PARAMETERLESS_SAFE_ACTIONS: frozenset[str] = frozenset({"reset", "describescene"})

_ACTION_CHECKERS = {
    "pick": _check_pick,
    "place": _check_place,
    "moveee": _check_moveee,
    "opengripper": _check_opengripper,
    "closegripper": _check_closegripper,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_safety(
    actions: list[dict] | None,
) -> SafetyValidationResult:
    """Deterministically validate a list of actions against clinical safety rules.

    Fail-closed: None, non-list, or empty plans are always unsafe.
    Does not raise; returns structured result for all failure modes.
    Does not mutate the supplied actions.
    """
    if actions is None:
        return SafetyValidationResult(safe=False, violations=["plan_is_none"])

    if not isinstance(actions, list):
        return SafetyValidationResult(safe=False, violations=["plan_not_a_list"])

    if len(actions) == 0:
        return SafetyValidationResult(safe=False, violations=["empty_plan"])

    all_violations: list[str] = []

    for idx, action in enumerate(actions):
        if not isinstance(action, dict):
            all_violations.append(f"action[{idx}].not_a_dict")
            continue

        action_name = action.get("action")

        if not isinstance(action_name, str):
            all_violations.append(f"action[{idx}].missing_or_invalid_action_field")
            continue

        if action_name not in _ALLOWED_ACTIONS:
            all_violations.append(
                f"action[{idx}].unknown_action:{action_name!r}"
            )
            continue

        if action_name in _PARAMETERLESS_SAFE_ACTIONS:
            continue  # no parameter rules for these

        checker = _ACTION_CHECKERS.get(action_name)
        if checker:
            all_violations.extend(checker(action, idx))

    if all_violations:
        return SafetyValidationResult(safe=False, violations=all_violations)

    return SafetyValidationResult(
        safe=True,
        violations=[],
        safe_actions=list(actions),  # shallow copy — never mutates original
    )
