from src.features.perfume_comparison import (
    calculate_note_similarity,
    compare_perfumes,
    find_preference_conflicts,
    normalise_note,
    split_notes,
)


# --------------------------------------------------
# Note cleaning tests
# --------------------------------------------------
def test_normalise_note():
    result = normalise_note(
        "  Pink Pepper!  "
    )

    assert result == "pink pepper"


def test_split_notes_removes_duplicates():
    result = split_notes(
        "Bergamot, Vanilla, Bergamot, Cedar"
    )

    assert result == {
        "bergamot",
        "vanilla",
        "cedar",
    }


def test_split_notes_handles_empty_value():
    assert split_notes("") == set()
    assert split_notes(None) == set()


# --------------------------------------------------
# Similarity tests
# --------------------------------------------------
def test_note_similarity_is_correct():
    first_notes = (
        "bergamot, lemon, cedar"
    )

    second_notes = (
        "bergamot, vanilla, cedar"
    )

    result = calculate_note_similarity(
        first_notes,
        second_notes,
    )

    assert result == 50.0


def test_similarity_is_zero_without_shared_notes():
    result = calculate_note_similarity(
        "lemon, cedar",
        "vanilla, rose",
    )

    assert result == 0.0


def test_similarity_is_zero_when_notes_are_missing():
    result = calculate_note_similarity(
        "",
        "",
    )

    assert result == 0.0


# --------------------------------------------------
# Preference conflict tests
# --------------------------------------------------
def test_disliked_note_conflict_is_found():
    conflicts = find_preference_conflicts(
        perfume_notes=(
            "bergamot, vanilla, cedar"
        ),
        disliked_notes=[
            "Vanilla",
            "Tobacco",
        ],
    )

    assert "Vanilla" in conflicts
    assert "Tobacco" not in conflicts


def test_no_conflict_returns_empty_list():
    conflicts = find_preference_conflicts(
        perfume_notes=(
            "bergamot, lemon, cedar"
        ),
        disliked_notes=[
            "Vanilla",
            "Tobacco",
        ],
    )

    assert conflicts == []


# --------------------------------------------------
# Complete comparison tests
# --------------------------------------------------
def test_complete_perfume_comparison():
    first_perfume = {
        "name": "Perfume A",
        "brand": "Brand A",
        "notes": (
            "bergamot, lemon, cedar"
        ),
    }

    second_perfume = {
        "name": "Perfume B",
        "brand": "Brand B",
        "notes": (
            "bergamot, vanilla, cedar"
        ),
    }

    comparison = compare_perfumes(
        first_perfume=first_perfume,
        second_perfume=second_perfume,
        disliked_notes=[
            "Vanilla",
        ],
    )

    assert comparison[
        "similarity_percentage"
    ] == 50.0

    assert comparison[
        "total_shared_notes"
    ] == 2

    assert comparison[
        "shared_notes"
    ] == [
        "bergamot",
        "cedar",
    ]

    assert comparison[
        "first_perfume"
    ]["unique_notes"] == [
        "lemon",
    ]

    assert comparison[
        "second_perfume"
    ]["unique_notes"] == [
        "vanilla",
    ]

    assert comparison[
        "first_perfume"
    ]["conflicts"] == []

    assert comparison[
        "second_perfume"
    ]["conflicts"] == [
        "Vanilla",
    ]


def test_comparison_handles_missing_notes():
    first_perfume = {
        "name": "Perfume A",
        "brand": "Brand A",
        "notes": "",
    }

    second_perfume = {
        "name": "Perfume B",
        "brand": "Brand B",
        "notes": "vanilla",
    }

    comparison = compare_perfumes(
        first_perfume=first_perfume,
        second_perfume=second_perfume,
    )

    assert comparison[
        "similarity_percentage"
    ] == 0.0

    assert comparison[
        "first_perfume"
    ]["has_notes"] is False

    assert comparison[
        "second_perfume"
    ]["has_notes"] is True