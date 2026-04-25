from __future__ import annotations

from dataclasses import dataclass

from src.brain.uncertainty import UncertaintyResult


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
            return SemanticScore(1.0, True, "none", "Correct uncertainty rejection")
        if not planned:
            return SemanticScore(0.5, True, "none", "Rejected without uncertainty evidence")
        reason = "ambiguous_reference"
        if uncertainty_result and "underspecified_motion" in uncertainty_result.reasons:
            reason = "underspecified_motion"
        return SemanticScore(0.0, False, reason, "Forced execution for uncertain command")

    if label == "REJECT_UNSUPPORTED":
        if not planned:
            return SemanticScore(1.0, True, "none", "Correct unsupported-intent rejection")
        return SemanticScore(0.0, False, "unsupported_intent", "Forced execution of unsupported intent")

    if label == "EXECUTE_EXACT":
        if not planned:
            return SemanticScore(0.0, False, "over_rejection", "Expected execution but rejected")

        if len(planned) != len(gold_actions):
            return SemanticScore(0.0, False, "semantic_mismatch", "Action count mismatch")

        for gold, got in zip(gold_actions, planned):
            if not _action_matches_exact(gold, got):
                return SemanticScore(0.0, False, "semantic_mismatch", "Exact action semantics mismatch")

        return SemanticScore(1.0, True, "none", "Exact semantic match")

    if label == "EXECUTE_FLEXIBLE":
        if not planned:
            return SemanticScore(0.0, False, "over_rejection", "Expected flexible execution but rejected")

        if planned == gold_actions:
            return SemanticScore(1.0, True, "none", "Flexible command matched exactly")

        if gold_actions and planned:
            gold_primary = gold_actions[0]
            got_primary = planned[0]
            if got_primary.get("object") == gold_primary.get("object"):
                return SemanticScore(
                    0.5,
                    True,
                    "semantic_mismatch",
                    "Partial semantic match with correct object",
                )

        return SemanticScore(0.0, False, "semantic_mismatch", "Flexible semantic mismatch")

    return SemanticScore(0.0, False, "parse_error", "Unknown benchmark label")
