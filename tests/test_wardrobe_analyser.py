from src.features.wardrobe_analyser import (
    analyse_wardrobe,
    calculate_data_coverage,
    calculate_diversity_score,
    calculate_note_frequencies,
    calculate_pairwise_similarities,
    extract_collection_notes,
    identify_possible_duplicates,
    validate_perfume_record,
)


# --------------------------------------------------
# Reusable test collection
# --------------------------------------------------
SAMPLE_PERFUMES = [
    {
        "name": "Fresh One",
        "brand": "Brand A",
        "notes": "bergamot, lemon, cedar",
    },
    {
        "name": "Fresh Two",
        "brand": "Brand B",
        "notes": "bergamot, lemon, musk",
    },
    {
        "name": "Warm One",
        "brand": "Brand C",
        "notes": "vanilla, amber, cinnamon",
    },
]


# --------------------------------------------------
# Record-validation tests
# --------------------------------------------------
def test_valid_perfume_record():
    perfume = {
        "name": "Test Perfume",
        "brand": "Test Brand",
        "notes": "bergamot",
    }

    assert validate_perfume_record(
        perfume
    ) is True


def test_invalid_perfume_record():
    assert validate_perfume_record(
        None
    ) is False

    assert validate_perfume_record(
        {}
    ) is False

    assert validate_perfume_record(
        {
            "name": "",
            "brand": "Brand A",
        }
    ) is False

    assert validate_perfume_record(
        {
            "name": "Perfume A",
            "brand": "",
        }
    ) is False


# --------------------------------------------------
# Note-extraction tests
# --------------------------------------------------
def test_extract_collection_notes():
    notes = extract_collection_notes(
        SAMPLE_PERFUMES
    )

    assert len(notes) == 9

    assert notes.count(
        "bergamot"
    ) == 2

    assert notes.count(
        "lemon"
    ) == 2


def test_note_frequency_order():
    frequencies = calculate_note_frequencies(
        SAMPLE_PERFUMES
    )

    frequency_dictionary = {
        item["note"]: item["count"]
        for item in frequencies
    }

    assert frequency_dictionary[
        "bergamot"
    ] == 2

    assert frequency_dictionary[
        "lemon"
    ] == 2

    assert frequency_dictionary[
        "vanilla"
    ] == 1


# --------------------------------------------------
# Pairwise-similarity tests
# --------------------------------------------------
def test_pairwise_comparison_count():
    comparisons = calculate_pairwise_similarities(
        SAMPLE_PERFUMES
    )

    # Three perfumes create three possible pairs:
    # AB, AC and BC
    assert len(comparisons) == 3


def test_most_similar_pair_is_first():
    comparisons = calculate_pairwise_similarities(
        SAMPLE_PERFUMES
    )

    first_result = comparisons[0]

    assert first_result[
        "first_name"
    ] == "Fresh One"

    assert first_result[
        "second_name"
    ] == "Fresh Two"

    assert first_result[
        "similarity_percentage"
    ] == 50.0

    assert first_result[
        "shared_notes"
    ] == [
        "bergamot",
        "lemon",
    ]


# --------------------------------------------------
# Duplicate-indicator tests
# --------------------------------------------------
def test_possible_duplicate_is_detected():
    comparisons = calculate_pairwise_similarities(
        SAMPLE_PERFUMES
    )

    possible_duplicates = (
        identify_possible_duplicates(
            comparisons,
            threshold=40.0,
        )
    )

    assert len(
        possible_duplicates
    ) == 1

    assert possible_duplicates[0][
        "similarity_percentage"
    ] == 50.0


def test_high_threshold_removes_duplicate():
    comparisons = calculate_pairwise_similarities(
        SAMPLE_PERFUMES
    )

    possible_duplicates = (
        identify_possible_duplicates(
            comparisons,
            threshold=60.0,
        )
    )

    assert possible_duplicates == []


# --------------------------------------------------
# Diversity tests
# --------------------------------------------------
def test_diversity_score_is_bounded():
    comparisons = calculate_pairwise_similarities(
        SAMPLE_PERFUMES
    )

    diversity = calculate_diversity_score(
        perfumes=SAMPLE_PERFUMES,
        similarity_results=comparisons,
    )

    assert (
        0.0
        <= diversity["score"]
        <= 100.0
    )

    assert (
        0.0
        <= diversity["average_similarity"]
        <= 100.0
    )

    assert diversity["label"]
    assert diversity["guidance"]


def test_single_perfume_has_no_diversity_score():
    one_perfume = [
        SAMPLE_PERFUMES[0]
    ]

    diversity = calculate_diversity_score(
        perfumes=one_perfume,
        similarity_results=[],
    )

    assert diversity[
        "score"
    ] == 0.0

    assert diversity[
        "label"
    ] == "Not enough perfumes"


# --------------------------------------------------
# Data-coverage tests
# --------------------------------------------------
def test_complete_note_coverage():
    coverage = calculate_data_coverage(
        SAMPLE_PERFUMES
    )

    assert coverage[
        "total_perfumes"
    ] == 3

    assert coverage[
        "perfumes_with_notes"
    ] == 3

    assert coverage[
        "perfumes_without_notes"
    ] == 0

    assert coverage[
        "coverage_percentage"
    ] == 100.0


def test_partial_note_coverage():
    perfumes = [
        {
            "name": "Perfume A",
            "brand": "Brand A",
            "notes": "bergamot, lemon",
        },
        {
            "name": "Perfume B",
            "brand": "Brand B",
            "notes": "",
        },
    ]

    coverage = calculate_data_coverage(
        perfumes
    )

    assert coverage[
        "total_perfumes"
    ] == 2

    assert coverage[
        "perfumes_with_notes"
    ] == 1

    assert coverage[
        "perfumes_without_notes"
    ] == 1

    assert coverage[
        "coverage_percentage"
    ] == 50.0


# --------------------------------------------------
# Complete analysis tests
# --------------------------------------------------
def test_complete_wardrobe_analysis():
    analysis = analyse_wardrobe(
        SAMPLE_PERFUMES
    )

    assert analysis[
        "collection_size"
    ] == 3

    assert analysis[
        "unique_note_count"
    ] == 7

    assert analysis[
        "possible_duplicate_count"
    ] == 1

    assert len(
        analysis[
            "pairwise_similarities"
        ]
    ) == 3

    assert analysis[
        "data_coverage"
    ][
        "coverage_percentage"
    ] == 100.0


def test_empty_wardrobe_is_handled():
    analysis = analyse_wardrobe(
        []
    )

    assert analysis[
        "collection_size"
    ] == 0

    assert analysis[
        "unique_note_count"
    ] == 0

    assert analysis[
        "possible_duplicate_count"
    ] == 0

    assert analysis[
        "dominant_notes"
    ] == []

    assert analysis[
        "pairwise_similarities"
    ] == []