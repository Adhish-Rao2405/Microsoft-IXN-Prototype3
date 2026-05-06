from __future__ import annotations

from dataclasses import dataclass

from src.brain.uncertainty import UncertaintyResult
from src.schema.action_schema import SUPPORTED_ACTIONS


@dataclass
class SemanticScore:
    score: float
    passed: bool
    failure_mode: str | None
    notes: str


def _normalize_actions(actions: list[dict] | None) -> list[dict]:
    if not actions:
        return []
    if not isinstance(actions, list):
        return []
    return [a for a in actions if isinstance(a, dict)]


def _action_matches_exact(gold_action: dict, planned_action: dict) -> bool:
    # Require semantic key/value agreement and no extra keys for strict exact mode.
    return gold_action == planned_action


def _first_failure_mode(gold_actions: list[dict], planned_actions: list[dict]) -> str:
    """Walk paired (gold, planned) actions and return the first distinguishable
    failure_mode, or 'semantic_mismatch' as catch-all.

    Called only when lengths are equal and at least one pair does not match exactly.
    """
    for gold, got in zip(gold_actions, planned_actions):
        got_action = got.get("action")
        if got_action not in SUPPORTED_ACTIONS:
            return "unsupported_action"
        if gold.get("action") != got_action:
            return "wrong_action"
        if "object" in gold and gold.get("object") != got.get("object"):
            return "wrong_object"
        if "target" in gold and gold.get("target") != got.get("target"):
            return "wrong_target"
        if gold != got:
            return "semantic_mismatch"
    return "semantic_mismatch"


def score_semantics(
    benchmark_item: dict,
    planned_actions: list[dict] | None,
    uncertainty_result: UncertaintyResult | None = None,
) -> SemanticScore:
    label = benchmark_item.get("gold_label")
    gold_actions = _normalize_actions(
        benchmark_item.get("gold_intent", {}).get("actions")
    )
    planned = _normalize_actions(planned_actions)

    if label == "REJECT_UNCERTAIN":
        if uncertainty_result and uncertainty_result.uncertain and not planned:
            return SemanticScore(1.0, True, "correct_reject", "Correct uncertainty rejection")
        if not planned:
            return SemanticScore(0.5, True, "correct_reject", "Rejected without uncertainty evidence")
        return SemanticScore(0.0, False, "false_accept", "Forced execution for uncertain command")

    if label == "REJECT_UNSUPPORTED":
        if not planned:
            return SemanticScore(1.0, True, "correct_reject", "Correct unsupported-intent rejection")
        return SemanticScore(0.0, False, "false_accept", "Forced execution of unsupported intent")

    if label == "EXECUTE_EXACT":
        if planned_actions is None or not isinstance(planned_actions, list):
            return SemanticScore(0.0, False, "malformed_or_unparseable_output", "Planner output is not a list")
        if len(planned) == 0:
            return SemanticScore(0.0, False, "false_reject", "Expected execution but plan is empty")
        if len(planned) > len(gold_actions):
            return SemanticScore(0.0, False, "unnecessary_extra_action", "More actions planned than gold")
        if len(planned) < len(gold_actions):
            return SemanticScore(0.0, False, "missing_action", "Fewer actions planned than gold")

        all_match = all(_action_matches_exact(g, p) for g, p in zip(gold_actions, planned))
        if all_match:
            return SemanticScore(1.0, True, "exact_match", "Exact semantic match")

        failure = _first_failure_mode(gold_actions, planned)
        return SemanticScore(0.0, False, failure, "Action semantics mismatch")

    if label == "EXECUTE_FLEXIBLE":
        if planned_actions is None or not isinstance(planned_actions, list):
            return SemanticScore(0.0, False, "malformed_or_unparseable_output", "Planner output is not a list")
        if len(planned) == 0:
            return SemanticScore(0.0, False, "false_reject", "Expected flexible execution but plan is empty")

        if planned == gold_actions:
            return SemanticScore(1.0, True, "exact_match", "Flexible command matched exactly")

        if gold_actions and planned:
            gold_primary = gold_actions[0]
            got_primary = planned[0]
            if got_primary.get("object") is not None and got_primary.get("object") == gold_primary.get("object"):
                return SemanticScore(
                    0.5,
                    True,
                    "acceptable_equivalent",
                    "Partial semantic match with correct object",
                )

        return SemanticScore(0.0, False, "semantic_mismatch", "Flexible semantic mismatch")

    return SemanticScore(0.0, False, "parse_error", "Unknown benchmark label")
