import pytest

from src.schema.action_schema import validate_action_plan


# ---------------------------------------------------------------------------
# Valid cases
# ---------------------------------------------------------------------------

def test_pick_with_object() -> None:
    result = validate_action_plan([{"action": "pick", "object": "medicine_cup"}])
    assert result.valid is True
    assert result.errors == []
    assert result.normalized_actions == [{"action": "pick", "object": "medicine_cup"}]


def test_place_with_target() -> None:
    result = validate_action_plan([{"action": "place", "target": "handover_zone"}])
    assert result.valid is True
    assert result.errors == []


def test_moveee_with_target() -> None:
    result = validate_action_plan([{"action": "moveee", "target": "left_zone"}])
    assert result.valid is True
    assert result.errors == []


def test_moveee_with_target_xyz() -> None:
    result = validate_action_plan([{"action": "moveee", "target_xyz": [0.1, 0.2, 0.3]}])
    assert result.valid is True
    assert result.errors == []


def test_opengripper_empty() -> None:
    result = validate_action_plan([{"action": "opengripper"}])
    assert result.valid is True


def test_opengripper_with_numeric_width() -> None:
    result = validate_action_plan([{"action": "opengripper", "width": 0.05}])
    assert result.valid is True


def test_closegripper_empty() -> None:
    result = validate_action_plan([{"action": "closegripper"}])
    assert result.valid is True


def test_closegripper_with_numeric_force() -> None:
    result = validate_action_plan([{"action": "closegripper", "force": 10}])
    assert result.valid is True


def test_reset_empty() -> None:
    result = validate_action_plan([{"action": "reset"}])
    assert result.valid is True


def test_describescene_empty() -> None:
    result = validate_action_plan([{"action": "describescene"}])
    assert result.valid is True


def test_dict_with_actions_list() -> None:
    result = validate_action_plan({"actions": [{"action": "pick", "object": "pill_box"}]})
    assert result.valid is True
    assert result.normalized_actions == [{"action": "pick", "object": "pill_box"}]


# ---------------------------------------------------------------------------
# Invalid cases
# ---------------------------------------------------------------------------

def test_top_level_string_is_invalid() -> None:
    result = validate_action_plan("pick the cup")
    assert result.valid is False
    assert any("top_level" in e for e in result.errors)


def test_top_level_dict_without_actions_key_is_invalid() -> None:
    result = validate_action_plan({"action": "pick"})
    assert result.valid is False
    assert any("missing_actions_key" in e or "dict_missing" in e for e in result.errors)


def test_unknown_action_is_invalid() -> None:
    result = validate_action_plan([{"action": "fly"}])
    assert result.valid is False
    assert any("unknown_action" in e for e in result.errors)


def test_missing_action_field_is_invalid() -> None:
    result = validate_action_plan([{"object": "medicine_cup"}])
    assert result.valid is False
    assert any("missing_action_field" in e for e in result.errors)


def test_pick_missing_object_is_invalid() -> None:
    result = validate_action_plan([{"action": "pick"}])
    assert result.valid is False
    assert any("missing_object" in e for e in result.errors)


def test_place_missing_target_is_invalid() -> None:
    result = validate_action_plan([{"action": "place"}])
    assert result.valid is False
    assert any("missing_target" in e for e in result.errors)


def test_moveee_missing_both_target_and_target_xyz_is_invalid() -> None:
    result = validate_action_plan([{"action": "moveee"}])
    assert result.valid is False
    assert any("missing_target_and_target_xyz" in e for e in result.errors)


def test_moveee_target_xyz_wrong_length_is_invalid() -> None:
    result = validate_action_plan([{"action": "moveee", "target_xyz": [0.1, 0.2]}])
    assert result.valid is False
    assert any("invalid_target_xyz" in e for e in result.errors)


def test_moveee_target_xyz_non_numeric_is_invalid() -> None:
    result = validate_action_plan([{"action": "moveee", "target_xyz": ["a", "b", "c"]}])
    assert result.valid is False
    assert any("invalid_target_xyz" in e for e in result.errors)


def test_opengripper_non_numeric_width_is_invalid() -> None:
    result = validate_action_plan([{"action": "opengripper", "width": "wide"}])
    assert result.valid is False
    assert any("invalid_width" in e for e in result.errors)


def test_closegripper_non_numeric_force_is_invalid() -> None:
    result = validate_action_plan([{"action": "closegripper", "force": "max"}])
    assert result.valid is False
    assert any("invalid_force" in e for e in result.errors)


def test_pick_with_extra_confidence_key_is_invalid() -> None:
    result = validate_action_plan(
        [{"action": "pick", "object": "medicine_cup", "confidence": 0.9}]
    )
    assert result.valid is False
    assert "action[0].unexpected_key:confidence" in result.errors


def test_place_with_extra_reasoning_key_is_invalid() -> None:
    result = validate_action_plan(
        [{"action": "place", "target": "handover_zone", "reasoning": "best guess"}]
    )
    assert result.valid is False
    assert "action[0].unexpected_key:reasoning" in result.errors


def test_moveee_with_both_target_and_target_xyz_is_invalid() -> None:
    result = validate_action_plan(
        [{"action": "moveee", "target": "left_zone", "target_xyz": [0.1, 0.2, 0.3]}]
    )
    assert result.valid is False
    assert any("mutually_exclusive" in e for e in result.errors)


def test_reset_with_extra_notes_key_is_invalid() -> None:
    result = validate_action_plan([{"action": "reset", "notes": "please do this"}])
    assert result.valid is False
    assert "action[0].unexpected_key:notes" in result.errors
