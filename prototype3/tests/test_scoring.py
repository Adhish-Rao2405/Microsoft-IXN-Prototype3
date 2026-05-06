from src.brain.uncertainty import UncertaintyResult
from src.eval.scoring import score_semantics


def test_score_execute_exact_success() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "pick", "object": "medicine_cup"}])
    assert result.score == 1.0
    assert result.passed is True
    assert result.failure_mode == "exact_match"


def test_score_execute_exact_wrong_object_fails() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "pick", "object": "pill_box"}])
    assert result.score == 0.0
    assert result.failure_mode == "wrong_object"


def test_score_reject_uncertain_success() -> None:
    item = {"gold_label": "REJECT_UNCERTAIN", "gold_intent": {"actions": []}}
    uncertainty = UncertaintyResult(
        uncertain=True, reasons=["ambiguous_reference"], score=0.7
    )
    result = score_semantics(item, [], uncertainty)
    assert result.score == 1.0
    assert result.passed is True


def test_score_reject_unsupported_success() -> None:
    item = {"gold_label": "REJECT_UNSUPPORTED", "gold_intent": {"actions": []}}
    result = score_semantics(item, [])
    assert result.score == 1.0
    assert result.passed is True


def test_score_execute_flexible_partial_credit() -> None:
    item = {
        "gold_label": "EXECUTE_FLEXIBLE",
        "gold_intent": {
            "actions": [
                {"action": "place", "object": "medicine_cup", "target": "handover_zone"}
            ]
        },
    }
    result = score_semantics(
        item, [{"action": "place", "object": "medicine_cup", "target": "right_zone"}]
    )
    assert result.score == 0.5
    assert result.passed is True


def test_score_execute_exact_wrong_target() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "place", "target": "tray"}]},
    }
    result = score_semantics(item, [{"action": "place", "target": "left_zone"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "wrong_target"


def test_score_execute_exact_wrong_action() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "place", "target": "tray"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "wrong_action"


def test_score_execute_exact_extra_action() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(
        item,
        [
            {"action": "pick", "object": "medicine_cup"},
            {"action": "place", "target": "tray"},
        ],
    )
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "unnecessary_extra_action"


def test_score_execute_exact_missing_action() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {
            "actions": [
                {"action": "pick", "object": "medicine_cup"},
                {"action": "place", "target": "tray"},
            ]
        },
    }
    result = score_semantics(item, [{"action": "pick", "object": "medicine_cup"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "missing_action"


def test_score_execute_exact_false_reject() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "false_reject"


def test_score_execute_exact_malformed_none() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, None)
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "malformed_or_unparseable_output"


def test_score_execute_exact_malformed_not_list() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, "not a list")  # type: ignore[arg-type]
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "malformed_or_unparseable_output"


def test_score_execute_exact_unsupported_action() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "grab", "object": "medicine_cup"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "unsupported_action"


def test_score_reject_uncertain_false_accept() -> None:
    item = {"gold_label": "REJECT_UNCERTAIN", "gold_intent": {"actions": []}}
    result = score_semantics(item, [{"action": "pick", "object": "something"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "false_accept"


def test_score_reject_unsupported_false_accept() -> None:
    item = {"gold_label": "REJECT_UNSUPPORTED", "gold_intent": {"actions": []}}
    result = score_semantics(item, [{"action": "pick", "object": "something"}])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "false_accept"


def test_score_execute_exact_wrong_object_uses_correct_mode() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "pick", "object": "gauze_pack"}])
    assert result.failure_mode == "wrong_object"
    assert result.failure_mode != "semantic_mismatch"


def test_score_execute_exact_multi_step_exact() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {
            "actions": [
                {"action": "pick", "object": "medicine_cup"},
                {"action": "place", "target": "tray"},
            ]
        },
    }
    result = score_semantics(
        item,
        [
            {"action": "pick", "object": "medicine_cup"},
            {"action": "place", "target": "tray"},
        ],
    )
    assert result.score == 1.0
    assert result.passed is True
    assert result.failure_mode == "exact_match"


def test_score_execute_flexible_malformed_none() -> None:
    item = {
        "gold_label": "EXECUTE_FLEXIBLE",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, None)
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "malformed_or_unparseable_output"


def test_score_execute_flexible_false_reject() -> None:
    item = {
        "gold_label": "EXECUTE_FLEXIBLE",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [])
    assert result.score == 0.0
    assert result.passed is False
    assert result.failure_mode == "false_reject"


def test_score_execute_flexible_partial_credit_uses_acceptable_equivalent() -> None:
    item = {
        "gold_label": "EXECUTE_FLEXIBLE",
        "gold_intent": {
            "actions": [
                {"action": "pick", "object": "medicine_cup"},
                {"action": "place", "target": "tray"},
            ]
        },
    }
    result = score_semantics(
        item,
        [
            {"action": "pick", "object": "medicine_cup"},
            {"action": "place", "target": "left_zone"},
        ],
    )
    assert result.score == 0.5
    assert result.passed is True
    assert result.failure_mode == "acceptable_equivalent"
