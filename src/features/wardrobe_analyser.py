from collections import Counter
from itertools import combinations

from src.features.perfume_comparison import (
    calculate_note_similarity,
    split_notes,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------
HIGH_SIMILARITY_THRESHOLD = 40.0
MODERATE_SIMILARITY_THRESHOLD = 20.0


# --------------------------------------------------
# Data validation
# --------------------------------------------------
def validate_perfume_record(perfume):
    """Check whether a perfume record can be analysed."""

    if not isinstance(perfume, dict):
        return False

    name = str(
        perfume.get("name", "")
    ).strip()

    brand = str(
        perfume.get("brand", "")
    ).strip()

    return bool(name and brand)


# --------------------------------------------------
# Extract collection notes
# --------------------------------------------------
def extract_collection_notes(perfumes):
    """
    Extract all available fragrance notes from a
    perfume collection.
    """

    all_notes = []

    for perfume in perfumes:
        if not validate_perfume_record(perfume):
            continue

        perfume_notes = split_notes(
            perfume.get("notes", "")
        )

        all_notes.extend(
            perfume_notes
        )

    return all_notes


# --------------------------------------------------
# Note frequency analysis
# --------------------------------------------------
def calculate_note_frequencies(perfumes):
    """Count how frequently each note appears."""

    all_notes = extract_collection_notes(
        perfumes
    )

    note_counter = Counter(
        all_notes
    )

    return [
        {
            "note": note,
            "count": count,
        }
        for note, count in note_counter.most_common()
    ]


# --------------------------------------------------
# Pairwise similarity
# --------------------------------------------------
def calculate_pairwise_similarities(perfumes):
    """
    Compare every possible pair of perfumes in the
    selected wardrobe.
    """

    valid_perfumes = [
        perfume
        for perfume in perfumes
        if validate_perfume_record(perfume)
    ]

    similarity_results = []

    for first_perfume, second_perfume in combinations(
        valid_perfumes,
        2,
    ):
        similarity_percentage = (
            calculate_note_similarity(
                first_perfume.get("notes", ""),
                second_perfume.get("notes", ""),
            )
        )

        first_notes = split_notes(
            first_perfume.get("notes", "")
        )

        second_notes = split_notes(
            second_perfume.get("notes", "")
        )

        shared_notes = sorted(
            first_notes
            & second_notes
        )

        similarity_results.append(
            {
                "first_name": first_perfume.get(
                    "name",
                    "Unknown perfume",
                ),
                "first_brand": first_perfume.get(
                    "brand",
                    "Unknown brand",
                ),
                "second_name": second_perfume.get(
                    "name",
                    "Unknown perfume",
                ),
                "second_brand": second_perfume.get(
                    "brand",
                    "Unknown brand",
                ),
                "similarity_percentage": (
                    similarity_percentage
                ),
                "shared_notes": shared_notes,
                "shared_note_count": len(
                    shared_notes
                ),
            }
        )

    return sorted(
        similarity_results,
        key=lambda item: item[
            "similarity_percentage"
        ],
        reverse=True,
    )


# --------------------------------------------------
# Identify possible duplicates
# --------------------------------------------------
def identify_possible_duplicates(
    similarity_results,
    threshold=HIGH_SIMILARITY_THRESHOLD,
):
    """
    Identify perfume pairs with comparatively high
    fragrance-note overlap.

    These results indicate similarity only. They do not
    prove that two perfumes smell identical.
    """

    return [
        comparison
        for comparison in similarity_results
        if comparison[
            "similarity_percentage"
        ] >= threshold
    ]


# --------------------------------------------------
# Diversity calculation
# --------------------------------------------------
def calculate_diversity_score(
    perfumes,
    similarity_results,
):
    """
    Create a simple collection-diversity indicator.

    Higher average similarity produces a lower diversity
    score. This is a project heuristic, not a scientific
    measure of fragrance diversity.
    """

    valid_perfumes = [
        perfume
        for perfume in perfumes
        if validate_perfume_record(perfume)
    ]

    if len(valid_perfumes) <= 1:
        return {
            "score": 0.0,
            "label": "Not enough perfumes",
            "average_similarity": 0.0,
            "guidance": (
                "Select at least two perfumes to measure "
                "collection diversity."
            ),
        }

    if not similarity_results:
        return {
            "score": 0.0,
            "label": "Insufficient note data",
            "average_similarity": 0.0,
            "guidance": (
                "The selected perfumes do not contain enough "
                "note information for diversity analysis."
            ),
        }

    similarity_values = [
        comparison[
            "similarity_percentage"
        ]
        for comparison in similarity_results
    ]

    average_similarity = (
        sum(similarity_values)
        / len(similarity_values)
    )

    diversity_score = max(
        0.0,
        min(
            100.0,
            100.0 - average_similarity,
        ),
    )

    diversity_score = round(
        diversity_score,
        1,
    )

    average_similarity = round(
        average_similarity,
        1,
    )

    if diversity_score >= 80:
        label = "Highly varied"

        guidance = (
            "The selected collection contains relatively "
            "low note overlap across its perfumes."
        )

    elif diversity_score >= 60:
        label = "Balanced variety"

        guidance = (
            "The collection contains a useful mixture of "
            "shared and different fragrance notes."
        )

    elif diversity_score >= 40:
        label = "Moderately similar"

        guidance = (
            "Several perfumes share noticeable note patterns."
        )

    else:
        label = "Highly similar"

        guidance = (
            "The selected collection contains substantial "
            "note overlap. Review similar pairs before adding "
            "another perfume with the same profile."
        )

    return {
        "score": diversity_score,
        "label": label,
        "average_similarity": (
            average_similarity
        ),
        "guidance": guidance,
    }


# --------------------------------------------------
# Data coverage
# --------------------------------------------------
def calculate_data_coverage(perfumes):
    """Measure available note information in the collection."""

    valid_perfumes = [
        perfume
        for perfume in perfumes
        if validate_perfume_record(perfume)
    ]

    total_perfumes = len(
        valid_perfumes
    )

    perfumes_with_notes = sum(
        bool(
            split_notes(
                perfume.get("notes", "")
            )
        )
        for perfume in valid_perfumes
    )

    perfumes_without_notes = (
        total_perfumes
        - perfumes_with_notes
    )

    coverage_percentage = (
        perfumes_with_notes
        / total_perfumes
        * 100
        if total_perfumes
        else 0.0
    )

    return {
        "total_perfumes": total_perfumes,
        "perfumes_with_notes": (
            perfumes_with_notes
        ),
        "perfumes_without_notes": (
            perfumes_without_notes
        ),
        "coverage_percentage": round(
            coverage_percentage,
            1,
        ),
    }


# --------------------------------------------------
# Dominant note summary
# --------------------------------------------------
def get_dominant_notes(
    note_frequencies,
    limit=10,
):
    """Return the most common collection notes."""

    return note_frequencies[
        :limit
    ]


# --------------------------------------------------
# Main wardrobe analyser
# --------------------------------------------------
def analyse_wardrobe(perfumes):
    """
    Produce a complete OLFYNZA wardrobe analysis.
    """

    valid_perfumes = [
        perfume
        for perfume in perfumes
        if validate_perfume_record(perfume)
    ]

    note_frequencies = (
        calculate_note_frequencies(
            valid_perfumes
        )
    )

    pairwise_similarities = (
        calculate_pairwise_similarities(
            valid_perfumes
        )
    )

    possible_duplicates = (
        identify_possible_duplicates(
            pairwise_similarities
        )
    )

    diversity = calculate_diversity_score(
        perfumes=valid_perfumes,
        similarity_results=pairwise_similarities,
    )

    data_coverage = calculate_data_coverage(
        valid_perfumes
    )

    unique_notes = {
        item["note"]
        for item in note_frequencies
    }

    return {
        "collection_size": len(
            valid_perfumes
        ),
        "unique_note_count": len(
            unique_notes
        ),
        "dominant_notes": get_dominant_notes(
            note_frequencies
        ),
        "all_note_frequencies": (
            note_frequencies
        ),
        "pairwise_similarities": (
            pairwise_similarities
        ),
        "possible_duplicates": (
            possible_duplicates
        ),
        "possible_duplicate_count": len(
            possible_duplicates
        ),
        "diversity": diversity,
        "data_coverage": data_coverage,
    }