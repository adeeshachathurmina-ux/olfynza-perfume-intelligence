from src.models.confidence import (
    calculate_confidence,
)


def test_strong_evidence_result():
    perfume = {
        "ranking_score": 0.24,
        "notes_score": 0.25,
        "matched_notes": [
            "fresh",
            "citrus",
            "bergamot",
        ],
        "has_verified_notes": True,
    }

    confidence = calculate_confidence(
        perfume
    )

    assert confidence["label"] == "Strong evidence"
    assert confidence["evidence_points"] >= 6


def test_limited_evidence_result():
    perfume = {
        "ranking_score": 0.03,
        "notes_score": 0.01,
        "matched_notes": [],
        "has_verified_notes": False,
    }

    confidence = calculate_confidence(
        perfume
    )

    assert confidence["label"] == "Limited evidence"
    assert confidence["evidence_points"] < 3


def test_confidence_has_user_guidance():
    perfume = {
        "ranking_score": 0.12,
        "notes_score": 0.10,
        "matched_notes": [
            "woody",
        ],
        "has_verified_notes": True,
    }

    confidence = calculate_confidence(
        perfume
    )

    assert confidence["guidance"]
    assert confidence["reasons"]