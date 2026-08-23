import re


# --------------------------------------------------
# Note cleaning
# --------------------------------------------------
def normalise_note(note):
    """Clean a fragrance note for reliable comparison."""

    if note is None:
        return ""

    cleaned_note = str(note).lower().strip()

    cleaned_note = re.sub(
        r"[^a-z0-9\s-]",
        "",
        cleaned_note,
    )

    cleaned_note = re.sub(
        r"\s+",
        " ",
        cleaned_note,
    )

    return cleaned_note.strip()


def split_notes(notes_text):
    """Convert comma-separated notes into a unique set."""

    if notes_text is None:
        return set()

    raw_notes = str(notes_text).split(",")

    cleaned_notes = {
        normalise_note(note)
        for note in raw_notes
        if normalise_note(note)
    }

    return cleaned_notes


# --------------------------------------------------
# Jaccard note similarity
# --------------------------------------------------
def calculate_note_similarity(
    first_notes,
    second_notes,
):
    """
    Calculate similarity using shared and total unique notes.

    Jaccard similarity =
    shared notes / all unique notes
    """

    first_note_set = split_notes(
        first_notes
    )

    second_note_set = split_notes(
        second_notes
    )

    all_notes = (
        first_note_set
        | second_note_set
    )

    shared_notes = (
        first_note_set
        & second_note_set
    )

    if not all_notes:
        return 0.0

    similarity = (
        len(shared_notes)
        / len(all_notes)
    )

    return round(
        similarity * 100,
        1,
    )


# --------------------------------------------------
# Disliked-note conflicts
# --------------------------------------------------
def find_preference_conflicts(
    perfume_notes,
    disliked_notes,
):
    """Find selected disliked notes in a perfume."""

    perfume_note_set = split_notes(
        perfume_notes
    )

    conflicts = []

    for disliked_note in disliked_notes:
        cleaned_disliked_note = normalise_note(
            disliked_note
        )

        if not cleaned_disliked_note:
            continue

        direct_match = (
            cleaned_disliked_note
            in perfume_note_set
        )

        partial_match = any(
            cleaned_disliked_note in perfume_note
            for perfume_note in perfume_note_set
        )

        if direct_match or partial_match:
            conflicts.append(
                disliked_note
            )

    return list(
        dict.fromkeys(conflicts)
    )


# --------------------------------------------------
# Main comparison
# --------------------------------------------------
def compare_perfumes(
    first_perfume,
    second_perfume,
    disliked_notes=None,
):
    """Compare two perfume records."""

    if disliked_notes is None:
        disliked_notes = []

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

    first_unique_notes = sorted(
        first_notes
        - second_notes
    )

    second_unique_notes = sorted(
        second_notes
        - first_notes
    )

    similarity_percentage = (
        calculate_note_similarity(
            first_perfume.get(
                "notes",
                "",
            ),
            second_perfume.get(
                "notes",
                "",
            ),
        )
    )

    first_conflicts = (
        find_preference_conflicts(
            first_perfume.get(
                "notes",
                "",
            ),
            disliked_notes,
        )
    )

    second_conflicts = (
        find_preference_conflicts(
            second_perfume.get(
                "notes",
                "",
            ),
            disliked_notes,
        )
    )

    return {
        "first_perfume": {
            "name": first_perfume.get(
                "name",
                "Unknown perfume",
            ),
            "brand": first_perfume.get(
                "brand",
                "Unknown brand",
            ),
            "notes": sorted(first_notes),
            "unique_notes": first_unique_notes,
            "conflicts": first_conflicts,
            "has_notes": bool(first_notes),
        },
        "second_perfume": {
            "name": second_perfume.get(
                "name",
                "Unknown perfume",
            ),
            "brand": second_perfume.get(
                "brand",
                "Unknown brand",
            ),
            "notes": sorted(second_notes),
            "unique_notes": second_unique_notes,
            "conflicts": second_conflicts,
            "has_notes": bool(second_notes),
        },
        "shared_notes": shared_notes,
        "similarity_percentage": (
            similarity_percentage
        ),
        "total_shared_notes": len(
            shared_notes
        ),
    }