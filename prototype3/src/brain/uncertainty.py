from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UncertaintyResult:
    uncertain: bool
    reasons: list[str]
    score: float


_AMBIGUOUS_REFERENCES = (
    "it",
    "that",
    "this",
    "there",
    "over there",
    "somewhere",
    "correct one",
    "nearby",
)
_UNDERSPECIFIED_MOTION = (
    "move slightly",
    "move a bit",
    "move over",
    "move there",
)
_ABSTRACT_UNSUPPORTED = (
    "sort this out",
    "get this ready",
    "properly",
    "usual",
)


def _contains_word(text: str, word: str) -> bool:
    padded = f" {text} "
    return f" {word} " in padded


def assess_uncertainty(
    command: str, scene_context: dict | None = None
) -> UncertaintyResult:
    normalized = " ".join(command.lower().strip().split())
    reasons: list[str] = []

    if any(phrase in normalized for phrase in _UNDERSPECIFIED_MOTION):
        reasons.append("underspecified_motion")

    ambiguous_hit = any(
        phrase in normalized
        if " " in phrase
        else _contains_word(normalized, phrase)
        for phrase in _AMBIGUOUS_REFERENCES
    )
    if ambiguous_hit:
        reasons.append("ambiguous_reference")

    if any(phrase in normalized for phrase in _ABSTRACT_UNSUPPORTED):
        reasons.append("unsupported_abstract_goal")

    if "safe area" in normalized or "safe_area" in normalized:
        known_zones = set((scene_context or {}).get("known_zones", []))
        if "safe_area" not in known_zones:
            reasons.append("ambiguous_reference")

    unique_reasons = sorted(set(reasons))
    if not unique_reasons:
        return UncertaintyResult(uncertain=False, reasons=[], score=0.0)

    score = min(1.0, 0.4 * len(unique_reasons))
    return UncertaintyResult(uncertain=True, reasons=unique_reasons, score=score)
