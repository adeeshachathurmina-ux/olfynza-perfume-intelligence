from src.explainability.explanation import (
    find_disliked_note_conflicts,
    generate_explanation,
)


def test_disliked_note_conflict_is_detected():
    """A selected disliked note must be identified."""

    conflicts = find_disliked_note_conflicts(
        disliked_notes=[
            "Vanilla",
            "Tobacco",
        ],
        perfume_notes=(
            "bergamot, vanilla, cedarwood, musk"
        ),
    )

    assert "Vanilla" in conflicts
    assert "Tobacco" not in conflicts


def test_explanation_returns_required_sections():
    """An explanation must contain all user-facing sections."""

    profile = {
        "preferred_styles": [
            "Fresh",
            "Citrus",
        ],
        "occasion": "University",
        "environment": "Hot and humid",
        "strength": "Moderate and balanced",
        "disliked_notes": [
            "Tobacco",
        ],
    }

    perfume = {
        "notes": (
            "fresh citrus, bergamot, lemon, "
            "cedarwood"
        ),
        "matched_notes": [
            "fresh",
            "citrus",
            "bergamot",
        ],
    }

    explanation = generate_explanation(
        profile=profile,
        perfume=perfume,
    )

    assert "reasons" in explanation
    assert "conflicts" in explanation
    assert "caution" in explanation
    assert "data_quality_note" in explanation

    assert len(
        explanation["reasons"]
    ) > 0


def test_missing_notes_are_disclosed():
    """Missing verified notes must be transparently reported."""

    profile = {
        "preferred_styles": [
            "Woody",
        ],
        "occasion": "Daily use",
        "environment": "Mostly outdoor",
        "strength": "No strong preference",
        "disliked_notes": [],
    }

    perfume = {
        "notes": "",
        "matched_notes": [],
    }

    explanation = generate_explanation(
        profile=profile,
        perfume=perfume,
    )

    assert (
        "not available"
        in explanation[
            "data_quality_note"
        ].lower()
    )