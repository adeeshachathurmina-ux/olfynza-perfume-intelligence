# --------------------------------------------------
# OLFYNZA profile-to-query mappings
# --------------------------------------------------

STYLE_KEYWORDS = {
    "Fresh": ["fresh", "clean", "bright"],
    "Citrus": [
        "citrus",
        "bergamot",
        "lemon",
        "orange",
        "grapefruit"
    ],
    "Aquatic": [
        "aquatic",
        "marine",
        "water",
        "sea",
        "ozonic"
    ],
    "Floral": [
        "floral",
        "jasmine",
        "rose",
        "peony",
        "lily"
    ],
    "Fruity": [
        "fruity",
        "apple",
        "peach",
        "pear",
        "berries"
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
        "cedar",
        "sandalwood",
        "vetiver"
    ],
    "Spicy": [
        "spicy",
        "pepper",
        "cardamom",
        "cinnamon",
        "clove"
    ],
    "Sweet": [
        "sweet",
        "gourmand",
        "caramel",
        "honey"
    ],
    "Vanilla": [
        "vanilla",
        "tonka",
        "creamy",
        "sweet"
    ],
    "Powdery": [
        "powdery",
        "iris",
        "violet",
        "musk"
    ],
    "Amber": [
        "amber",
        "resin",
        "benzoin",
        "labdanum"
    ]
}


OCCASION_KEYWORDS = {
    "University": [
        "fresh",
        "clean",
        "light",
        "daytime"
    ],
    "Office": [
        "clean",
        "balanced",
        "elegant",
        "daytime"
    ],
    "Interview": [
        "clean",
        "subtle",
        "professional",
        "elegant"
    ],
    "Daily use": [
        "versatile",
        "fresh",
        "comfortable",
        "daytime"
    ],
    "Wedding": [
        "elegant",
        "floral",
        "luxurious",
        "special"
    ],
    "Evening event": [
        "warm",
        "rich",
        "elegant",
        "evening"
    ],
    "Party": [
        "bold",
        "sweet",
        "spicy",
        "strong"
    ],
    "Special occasion": [
        "luxurious",
        "elegant",
        "memorable",
        "rich"
    ]
}


ENVIRONMENT_KEYWORDS = {
    "Hot and humid": [
        "fresh",
        "citrus",
        "aquatic",
        "light"
    ],
    "Rainy": [
        "woody",
        "green",
        "aromatic",
        "fresh"
    ],
    "Cool": [
        "warm",
        "amber",
        "spicy",
        "vanilla"
    ],
    "Indoor air-conditioned": [
        "balanced",
        "clean",
        "moderate",
        "soft"
    ],
    "Mostly outdoor": [
        "fresh",
        "citrus",
        "green",
        "woody"
    ],
    "A mixture of indoor and outdoor": [
        "versatile",
        "balanced",
        "fresh",
        "woody"
    ]
}


STRENGTH_KEYWORDS = {
    "Light and subtle": [
        "light",
        "soft",
        "subtle",
        "delicate"
    ],
    "Moderate and balanced": [
        "moderate",
        "balanced",
        "smooth",
        "versatile"
    ],
    "Strong and noticeable": [
        "strong",
        "intense",
        "bold",
        "powerful"
    ],
    "No strong preference": []
}


# --------------------------------------------------
# Query builder
# --------------------------------------------------
def build_profile_query(profile):
    """
    Convert quiz answers into perfume-related search terms.

    These mappings are product-design heuristics.
    They are not scientific or medical classifications.
    """

    query_terms = []

    preferred_styles = profile.get(
        "preferred_styles",
        []
    )

    for style in preferred_styles:
        query_terms.extend(
            STYLE_KEYWORDS.get(style, [style.lower()])
        )

    occasion = profile.get("occasion", "")

    query_terms.extend(
        OCCASION_KEYWORDS.get(
            occasion,
            [occasion.lower()] if occasion else []
        )
    )

    environment = profile.get("environment", "")

    query_terms.extend(
        ENVIRONMENT_KEYWORDS.get(
            environment,
            [environment.lower()]
            if environment
            else []
        )
    )

    strength = profile.get("strength", "")

    query_terms.extend(
        STRENGTH_KEYWORDS.get(
            strength,
            [strength.lower()] if strength else []
        )
    )

    # Remove duplicates while preserving order
    unique_terms = list(
        dict.fromkeys(
            term.strip().lower()
            for term in query_terms
            if term and term.strip()
        )
    )

    return " ".join(unique_terms)