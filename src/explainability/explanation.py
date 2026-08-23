import re


# --------------------------------------------------
# Human-readable profile descriptions
# --------------------------------------------------
STYLE_EXPLANATIONS = {
    "Fresh": "your preference for fresh and clean scents",
    "Citrus": "your interest in bright citrus fragrances",
    "Aquatic": "your preference for aquatic and marine scents",
    "Floral": "your interest in floral fragrances",
    "Fruity": "your preference for fruity scent profiles",
    "Green": "your interest in green and herbal scents",
    "Woody": "your preference for woody fragrances",
    "Spicy": "your interest in warm or aromatic spices",
    "Sweet": "your preference for sweet fragrances",
    "Vanilla": "your interest in vanilla-based scents",
    "Powdery": "your preference for soft powdery scents",
    "Amber": "your interest in warm amber fragrances",
}


OCCASION_EXPLANATIONS = {
    "University": (
        "you selected university use, where fresh and "
        "easy-to-wear profiles may be useful"
    ),
    "Office": (
        "you selected office use, where balanced and "
        "clean scent profiles may be useful"
    ),
    "Interview": (
        "you selected interview use, where subtle and "
        "polished profiles may be preferable"
    ),
    "Daily use": (
        "you selected daily use, so versatile scent "
        "characteristics were included"
    ),
    "Wedding": (
        "you selected a wedding, so elegant fragrance "
        "characteristics were included"
    ),
    "Evening event": (
        "you selected an evening event, so richer scent "
        "characteristics were considered"
    ),
    "Party": (
        "you selected party use, so stronger and more "
        "noticeable scent words were considered"
    ),
    "Special occasion": (
        "you selected a special occasion, so distinctive "
        "and elegant scent words were considered"
    ),
}


ENVIRONMENT_EXPLANATIONS = {
    "Hot and humid": (
        "you selected a hot and humid environment, so "
        "fresh, citrus and lighter scent words were considered"
    ),
    "Rainy": (
        "you selected a rainy environment, so green, woody "
        "and aromatic scent words were considered"
    ),
    "Cool": (
        "you selected a cool environment, so warm, amber "
        "and spicy scent words were considered"
    ),
    "Indoor air-conditioned": (
        "you selected an indoor air-conditioned environment, "
        "so balanced and softer scent words were considered"
    ),
    "Mostly outdoor": (
        "you selected mostly outdoor use, so fresh, green "
        "and woody scent words were considered"
    ),
    "A mixture of indoor and outdoor": (
        "you selected mixed indoor and outdoor use, so "
        "versatile scent words were considered"
    ),
}


STRENGTH_EXPLANATIONS = {
    "Light and subtle": (
        "you prefer a light and subtle fragrance character"
    ),
    "Moderate and balanced": (
        "you prefer a moderate and balanced fragrance character"
    ),
    "Strong and noticeable": (
        "you prefer a strong and noticeable fragrance character"
    ),
    "No strong preference": (
        "you did not select a specific fragrance-strength preference"
    ),
}


# --------------------------------------------------
# Text utilities
# --------------------------------------------------
def normalise_text(value):
    """Create clean lower-case text for matching."""

    if value is None:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9\s,-]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def split_notes(notes_text):
    """Convert the notes string into a clean list."""

    cleaned_notes = normalise_text(
        notes_text
    )

    if not cleaned_notes:
        return []

    notes = [
        note.strip()
        for note in cleaned_notes.split(",")
        if note.strip()
    ]

    return list(
        dict.fromkeys(notes)
    )


# --------------------------------------------------
# Preference matching
# --------------------------------------------------
def find_style_evidence(
    preferred_styles,
    perfume_notes,
    matched_terms
):
    """
    Identify scent-style evidence found in the perfume result.
    """

    notes_text = " ".join(
        split_notes(perfume_notes)
    )

    matched_terms_text = " ".join(
        str(term).lower()
        for term in matched_terms
    )

    searchable_text = (
        notes_text
        + " "
        + matched_terms_text
    )

    evidence = []

    style_terms = {
        "Fresh": [
            "fresh",
            "clean",
            "bright"
        ],
        "Citrus": [
            "citrus",
            "bergamot",
            "lemon",
            "orange",
            "grapefruit",
            "mandarin",
            "lime",
            "yuzu"
        ],
        "Aquatic": [
            "aquatic",
            "marine",
            "sea",
            "water",
            "ozonic"
        ],
        "Floral": [
            "floral",
            "jasmine",
            "rose",
            "peony",
            "lily",
            "violet",
            "iris",
            "tuberose"
        ],
        "Fruity": [
            "fruity",
            "apple",
            "peach",
            "pear",
            "berry",
            "berries",
            "plum"
        ],
        "Green": [
            "green",
            "herbal",
            "grass",
            "leaf",
            "vetiver"
        ],
        "Woody": [
            "woody",
            "wood",
            "cedar",
            "sandalwood",
            "vetiver"
        ],
        "Spicy": [
            "spicy",
            "pepper",
            "cardamom",
            "cinnamon",
            "clove",
            "saffron"
        ],
        "Sweet": [
            "sweet",
            "gourmand",
            "caramel",
            "honey",
            "toffee"
        ],
        "Vanilla": [
            "vanilla",
            "tonka",
            "creamy"
        ],
        "Powdery": [
            "powdery",
            "powder",
            "iris",
            "violet",
            "musk"
        ],
        "Amber": [
            "amber",
            "benzoin",
            "labdanum",
            "resin"
        ],
    }

    for style in preferred_styles:
        keywords = style_terms.get(
            style,
            []
        )

        found_keywords = [
            keyword
            for keyword in keywords
            if keyword in searchable_text
        ]

        if found_keywords:
            evidence.append(
                {
                    "style": style,
                    "keywords": list(
                        dict.fromkeys(
                            found_keywords
                        )
                    )[:4]
                }
            )

    return evidence


# --------------------------------------------------
# Disliked-note check
# --------------------------------------------------
def find_disliked_note_conflicts(
    disliked_notes,
    perfume_notes
):
    """Find explicitly selected disliked notes in the result."""

    notes_text = normalise_text(
        perfume_notes
    )

    conflicts = []

    for disliked_note in disliked_notes:
        cleaned_disliked_note = normalise_text(
            disliked_note
        )

        if (
            cleaned_disliked_note
            and cleaned_disliked_note in notes_text
        ):
            conflicts.append(
                disliked_note
            )

    return conflicts


# --------------------------------------------------
# Main explanation generator
# --------------------------------------------------
def generate_explanation(
    profile,
    perfume
):
    """
    Create an explanation using visible profile choices
    and perfume information.

    The explanation describes matching text evidence.
    It does not claim scientific suitability.
    """

    preferred_styles = profile.get(
        "preferred_styles",
        []
    )

    disliked_notes = profile.get(
        "disliked_notes",
        []
    )

    perfume_notes = perfume.get(
        "notes",
        ""
    )

    matched_terms = perfume.get(
        "matched_notes",
        []
    )

    style_evidence = find_style_evidence(
        preferred_styles=preferred_styles,
        perfume_notes=perfume_notes,
        matched_terms=matched_terms
    )

    conflicts = find_disliked_note_conflicts(
        disliked_notes=disliked_notes,
        perfume_notes=perfume_notes
    )

    reasons = []

    for item in style_evidence[:3]:
        style = item["style"]

        keywords_text = ", ".join(
            item["keywords"]
        )

        style_description = STYLE_EXPLANATIONS.get(
            style,
            f"your preference for {style.lower()} scents"
        )

        reasons.append(
            f"It supports {style_description}; "
            f"matching evidence includes {keywords_text}."
        )

    occasion = profile.get(
        "occasion",
        ""
    )

    if occasion in OCCASION_EXPLANATIONS:
        reasons.append(
            OCCASION_EXPLANATIONS[occasion].capitalize()
            + "."
        )

    environment = profile.get(
        "environment",
        ""
    )

    if environment in ENVIRONMENT_EXPLANATIONS:
        reasons.append(
            ENVIRONMENT_EXPLANATIONS[
                environment
            ].capitalize()
            + "."
        )

    strength = profile.get(
        "strength",
        ""
    )

    if strength in STRENGTH_EXPLANATIONS:
        reasons.append(
            STRENGTH_EXPLANATIONS[
                strength
            ].capitalize()
            + "."
        )

    if not reasons:
        reasons.append(
            "This result has general text similarity with "
            "the scent profile you provided."
        )

    if conflicts:
        caution = (
            "This perfume lists a note you selected to avoid: "
            + ", ".join(conflicts)
            + ". Consider testing a sample before purchasing."
        )
    else:
        caution = (
            "No direct conflict was detected between the "
            "available notes and your selected notes to avoid."
        )

    if not str(perfume_notes).strip():
        data_quality_note = (
            "Verified fragrance notes were not available for "
            "this record, so the result relies more heavily "
            "on its name and description."
        )
    else:
        data_quality_note = (
            "This explanation uses the fragrance notes and "
            "description available in the project dataset."
        )

    return {
        "reasons": reasons[:4],
        "conflicts": conflicts,
        "caution": caution,
        "data_quality_note": data_quality_note,
    }