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
    assert result.failure_mode == "none"


def test_score_execute_exact_wrong_object_fails() -> None:
    item = {
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": [{"action": "pick", "object": "medicine_cup"}]},
    }
    result = score_semantics(item, [{"action": "pick", "object": "pill_box"}])
    assert result.score == 0.0
    assert result.failure_mode == "semantic_mismatch"


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
