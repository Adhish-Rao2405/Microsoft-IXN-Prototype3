from src.brain.uncertainty import assess_uncertainty


def test_uncertainty_flags_ambiguous_reference() -> None:
    result = assess_uncertainty("Pick that")
    assert result.uncertain is True
    assert "ambiguous_reference" in result.reasons


def test_uncertainty_flags_underspecified_motion() -> None:
    result = assess_uncertainty("Move a bit to the left")
    assert result.uncertain is True
    assert "underspecified_motion" in result.reasons


def test_uncertainty_clear_command_not_over_rejected() -> None:
    result = assess_uncertainty("Pick up the medicine cup")
    assert result.uncertain is False
    assert result.reasons == []
    assert result.score == 0.0


def test_uncertainty_safe_area_needs_context() -> None:
    result = assess_uncertainty("Move to safe area")
    assert result.uncertain is True
    assert "ambiguous_reference" in result.reasons


def test_uncertainty_safe_area_resolved_by_scene_context() -> None:
    result = assess_uncertainty(
        "Move to safe area", scene_context={"known_zones": ["safe_area"]}
    )
    assert result.uncertain is False
