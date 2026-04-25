"""Unit tests for the deterministic safety validation module (Phase 3.3)."""
from src.brain.safety import validate_safety


# ---------------------------------------------------------------------------
# Fail-closed baseline: None / non-list / empty plans must always be rejected.
# ---------------------------------------------------------------------------

def test_none_plan_is_unsafe() -> None:
    result = validate_safety(None)
    assert result.safe is False
    assert any("plan_is_none" in v for v in result.violations)


def test_non_list_plan_is_unsafe() -> None:
    result = validate_safety("pick the cup")  # type: ignore[arg-type]
    assert result.safe is False
    assert any("plan_not_a_list" in v for v in result.violations)


def test_empty_list_plan_is_unsafe() -> None:
    result = validate_safety([])
    assert result.safe is False
    assert any("empty_plan" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Non-dict action in list
# ---------------------------------------------------------------------------

def test_non_dict_action_is_unsafe() -> None:
    result = validate_safety(["not a dict"])
    assert result.safe is False
    assert any("not_a_dict" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Unknown / missing action name
# ---------------------------------------------------------------------------

def test_unknown_action_is_unsafe() -> None:
    result = validate_safety([{"action": "fly_to_moon"}])
    assert result.safe is False
    assert any("unknown_action" in v for v in result.violations)


def test_missing_action_field_is_unsafe() -> None:
    result = validate_safety([{"object": "medicine_cup"}])
    assert result.safe is False
    assert any("missing_or_invalid_action_field" in v for v in result.violations)


# ---------------------------------------------------------------------------
# pick
# ---------------------------------------------------------------------------

def test_pick_known_object_is_safe() -> None:
    result = validate_safety([{"action": "pick", "object": "medicine_cup"}])
    assert result.safe is True
    assert result.violations == []
    assert result.safe_actions == [{"action": "pick", "object": "medicine_cup"}]


def test_pick_all_known_objects_are_safe() -> None:
    for obj in ("medicine_cup", "pill_box", "gauze_pack", "tray"):
        result = validate_safety([{"action": "pick", "object": obj}])
        assert result.safe is True, f"Expected safe for object={obj}"


def test_pick_unknown_object_is_unsafe() -> None:
    result = validate_safety([{"action": "pick", "object": "chainsaw"}])
    assert result.safe is False
    assert any("unsafe_object" in v for v in result.violations)


def test_pick_missing_object_is_unsafe() -> None:
    result = validate_safety([{"action": "pick"}])
    assert result.safe is False
    assert any("unsafe_object" in v for v in result.violations)


# ---------------------------------------------------------------------------
# place
# ---------------------------------------------------------------------------

def test_place_known_zone_is_safe() -> None:
    result = validate_safety([{"action": "place", "target": "handover_zone"}])
    assert result.safe is True


def test_place_all_known_zones_are_safe() -> None:
    for zone in ("left_zone", "right_zone", "handover_zone", "safe_area"):
        result = validate_safety([{"action": "place", "target": zone}])
        assert result.safe is True, f"Expected safe for zone={zone}"


def test_place_unknown_target_is_unsafe() -> None:
    result = validate_safety([{"action": "place", "target": "trash_bin"}])
    assert result.safe is False
    assert any("unsafe_target" in v for v in result.violations)


def test_place_missing_target_is_unsafe() -> None:
    result = validate_safety([{"action": "place"}])
    assert result.safe is False
    assert any("unsafe_target" in v for v in result.violations)


# ---------------------------------------------------------------------------
# moveee
# ---------------------------------------------------------------------------

def test_moveee_known_zone_target_is_safe() -> None:
    result = validate_safety([{"action": "moveee", "target": "left_zone"}])
    assert result.safe is True


def test_moveee_in_bounds_xyz_is_safe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [0.1, 0.2, 0.3]}])
    assert result.safe is True


def test_moveee_zero_xyz_is_safe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [0.0, 0.0, 0.0]}])
    assert result.safe is True


def test_moveee_boundary_xyz_is_safe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [-2.0, 2.0, 0.0]}])
    assert result.safe is True


def test_moveee_missing_both_target_and_xyz_is_unsafe() -> None:
    result = validate_safety([{"action": "moveee"}])
    assert result.safe is False
    assert any("missing_target_and_target_xyz" in v for v in result.violations)


def test_moveee_out_of_bounds_xyz_is_unsafe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [999.0, 0.0, 0.0]}])
    assert result.safe is False
    assert any("out_of_bounds" in v for v in result.violations)


def test_moveee_malformed_xyz_wrong_length_is_unsafe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [0.1, 0.2]}])
    assert result.safe is False
    assert any("malformed_target_xyz" in v for v in result.violations)


def test_moveee_malformed_xyz_non_numeric_is_unsafe() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": ["a", "b", "c"]}])
    assert result.safe is False
    assert any("malformed_target_xyz" in v for v in result.violations)


def test_moveee_unknown_string_target_is_unsafe() -> None:
    result = validate_safety([{"action": "moveee", "target": "danger_zone"}])
    assert result.safe is False
    assert any("unsafe_target" in v for v in result.violations)


# ---------------------------------------------------------------------------
# opengripper
# ---------------------------------------------------------------------------

def test_opengripper_no_params_is_safe() -> None:
    result = validate_safety([{"action": "opengripper"}])
    assert result.safe is True


def test_opengripper_safe_width_is_safe() -> None:
    result = validate_safety([{"action": "opengripper", "width": 0.10}])
    assert result.safe is True


def test_opengripper_zero_width_is_safe() -> None:
    result = validate_safety([{"action": "opengripper", "width": 0.0}])
    assert result.safe is True


def test_opengripper_max_width_boundary_is_safe() -> None:
    result = validate_safety([{"action": "opengripper", "width": 0.20}])
    assert result.safe is True


def test_opengripper_excessive_width_is_unsafe() -> None:
    result = validate_safety([{"action": "opengripper", "width": 0.50}])
    assert result.safe is False
    assert any("unsafe_width" in v for v in result.violations)


def test_opengripper_non_numeric_width_is_unsafe() -> None:
    result = validate_safety([{"action": "opengripper", "width": "wide_open"}])
    assert result.safe is False
    assert any("non_numeric_width" in v for v in result.violations)


# ---------------------------------------------------------------------------
# closegripper
# ---------------------------------------------------------------------------

def test_closegripper_no_params_is_safe() -> None:
    result = validate_safety([{"action": "closegripper"}])
    assert result.safe is True


def test_closegripper_safe_force_is_safe() -> None:
    result = validate_safety([{"action": "closegripper", "force": 5.0}])
    assert result.safe is True


def test_closegripper_zero_force_is_safe() -> None:
    result = validate_safety([{"action": "closegripper", "force": 0.0}])
    assert result.safe is True


def test_closegripper_max_force_boundary_is_safe() -> None:
    result = validate_safety([{"action": "closegripper", "force": 50.0}])
    assert result.safe is True


def test_closegripper_excessive_force_is_unsafe() -> None:
    result = validate_safety([{"action": "closegripper", "force": 200.0}])
    assert result.safe is False
    assert any("unsafe_force" in v for v in result.violations)


def test_closegripper_non_numeric_force_is_unsafe() -> None:
    result = validate_safety([{"action": "closegripper", "force": "max"}])
    assert result.safe is False
    assert any("non_numeric_force" in v for v in result.violations)


# ---------------------------------------------------------------------------
# reset / describescene (parameterless — always safe when action name is valid)
# ---------------------------------------------------------------------------

def test_reset_is_safe() -> None:
    result = validate_safety([{"action": "reset"}])
    assert result.safe is True


def test_describescene_is_safe() -> None:
    result = validate_safety([{"action": "describescene"}])
    assert result.safe is True


# ---------------------------------------------------------------------------
# Multi-action plans
# ---------------------------------------------------------------------------

def test_multi_action_all_safe() -> None:
    result = validate_safety([
        {"action": "pick", "object": "medicine_cup"},
        {"action": "place", "target": "handover_zone"},
    ])
    assert result.safe is True
    assert len(result.safe_actions) == 2


def test_multi_action_one_unsafe_fails_whole_plan() -> None:
    result = validate_safety([
        {"action": "pick", "object": "medicine_cup"},
        {"action": "moveee", "target_xyz": [999.0, 0.0, 0.0]},
    ])
    assert result.safe is False
    assert any("out_of_bounds" in v for v in result.violations)
    assert result.safe_actions is None


# ---------------------------------------------------------------------------
# Immutability guarantee: validator must not mutate the original actions
# ---------------------------------------------------------------------------

def test_validator_does_not_mutate_input() -> None:
    original = [{"action": "pick", "object": "medicine_cup"}]
    original_copy = [dict(original[0])]
    validate_safety(original)
    assert original == original_copy
