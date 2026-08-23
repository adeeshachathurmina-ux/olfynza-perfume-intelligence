def calculate_confidence(perfume):
    """
    Estimate the amount of supporting evidence available
    for a recommendation.

    This is an evidence label, not a probability that the
    user will like the perfume.
    """

    ranking_score = float(
        perfume.get("ranking_score", 0)
    )

    notes_score = float(
        perfume.get("notes_score", 0)
    )

    matched_notes = perfume.get(
        "matched_notes",
        []
    )

    has_verified_notes = bool(
        perfume.get("has_verified_notes", False)
    )

    evidence_points = 0
    reasons = []

    if ranking_score >= 0.18:
        evidence_points += 2
        reasons.append(
            "The overall text-ranking evidence is relatively strong."
        )

    elif ranking_score >= 0.10:
        evidence_points += 1
        reasons.append(
            "The overall text-ranking evidence is moderate."
        )

    else:
        reasons.append(
            "The overall text-ranking evidence is limited."
        )

    if notes_score >= 0.18:
        evidence_points += 2
        reasons.append(
            "The perfume has strong note-level similarity."
        )

    elif notes_score >= 0.08:
        evidence_points += 1
        reasons.append(
            "The perfume has some note-level similarity."
        )

    else:
        reasons.append(
            "Direct note-level similarity is limited."
        )

    if len(matched_notes) >= 3:
        evidence_points += 2
        reasons.append(
            "At least three direct preference terms were matched."
        )

    elif len(matched_notes) >= 1:
        evidence_points += 1
        reasons.append(
            "At least one direct preference term was matched."
        )

    else:
        reasons.append(
            "No direct preference term was found in the notes."
        )

    if has_verified_notes:
        evidence_points += 1
        reasons.append(
            "Verified fragrance-note information is available."
        )

    else:
        reasons.append(
            "Verified fragrance-note information is unavailable."
        )

    if evidence_points >= 6:
        label = "Strong evidence"
        guidance = (
            "This result has comparatively strong matching "
            "evidence within the current dataset."
        )

    elif evidence_points >= 3:
        label = "Moderate evidence"
        guidance = (
            "This result has useful matching evidence, but "
            "sampling is still recommended before purchase."
        )

    else:
        label = "Limited evidence"
        guidance = (
            "This result has limited matching evidence. "
            "Consider testing a sample before purchasing."
        )

    return {
        "label": label,
        "evidence_points": evidence_points,
        "reasons": reasons,
        "guidance": guidance,
    }