import pandas as pd
import pytest

import src.features.feedback_manager as feedback_manager

from src.features.feedback_manager import (
    FEEDBACK_COLUMNS,
    FEEDBACK_OPTIONS,
    build_feedback_record,
    calculate_feedback_summary,
    clean_feedback_text,
    create_feedback_id,
    create_session_id,
    is_duplicate_feedback,
    load_feedback,
    save_feedback,
    serialise_list,
    validate_feedback,
)


# --------------------------------------------------
# Reusable test data
# --------------------------------------------------
SAMPLE_PERFUME = {
    "perfume_id": "OLF-TEST-001",
    "name": "Test Citrus",
    "brand": "Test Brand",
    "ranking_percentage": 24.5,
}

SAMPLE_PROFILE = {
    "preferred_styles": [
        "Fresh",
        "Citrus",
    ],
    "occasion": "University",
    "environment": "Hot and humid",
    "strength": "Moderate and balanced",
    "budget": "LKR 5,000 – 10,000",
    "disliked_notes": [
        "Tobacco",
    ],
}


# --------------------------------------------------
# Temporary feedback storage
# --------------------------------------------------
@pytest.fixture()
def temporary_feedback_storage(
    tmp_path,
    monkeypatch,
):
    """
    Redirect feedback storage to a temporary folder.

    This prevents automated tests from changing the
    real project feedback CSV file.
    """

    temporary_directory = (
        tmp_path
        / "feedback"
    )

    temporary_file = (
        temporary_directory
        / "recommendation_feedback.csv"
    )

    monkeypatch.setattr(
        feedback_manager,
        "FEEDBACK_DIRECTORY",
        temporary_directory,
    )

    monkeypatch.setattr(
        feedback_manager,
        "FEEDBACK_FILE",
        temporary_file,
    )

    return temporary_file


# --------------------------------------------------
# Text-cleaning tests
# --------------------------------------------------
def test_feedback_text_is_cleaned():
    result = clean_feedback_text(
        "  Useful\nrecommendation\tfor me.  "
    )

    assert result == (
        "Useful recommendation for me."
    )


def test_feedback_text_length_is_limited():
    result = clean_feedback_text(
        "A" * 1000,
        maximum_length=100,
    )

    assert len(result) == 100


def test_serialise_list():
    result = serialise_list(
        [
            "Fresh",
            "Citrus",
        ]
    )

    assert result == "Fresh | Citrus"


def test_serialise_empty_list():
    assert serialise_list([]) == ""


# --------------------------------------------------
# Anonymous ID tests
# --------------------------------------------------
def test_feedback_id_format():
    feedback_id = create_feedback_id()

    assert feedback_id.startswith(
        "FB-"
    )

    assert len(feedback_id) == 15


def test_session_id_format():
    session_id = create_session_id()

    assert session_id.startswith(
        "SESSION-"
    )

    assert len(session_id) == 20


def test_created_ids_are_unique():
    first_feedback_id = (
        create_feedback_id()
    )

    second_feedback_id = (
        create_feedback_id()
    )

    assert (
        first_feedback_id
        != second_feedback_id
    )


# --------------------------------------------------
# Validation tests
# --------------------------------------------------
def test_valid_feedback_has_no_errors():
    errors = validate_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        profile=SAMPLE_PROFILE,
    )

    assert errors == []


def test_invalid_feedback_type_is_rejected():
    errors = validate_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Unsupported option",
        profile=SAMPLE_PROFILE,
    )

    assert errors


def test_missing_perfume_details_are_rejected():
    errors = validate_feedback(
        perfume={
            "perfume_id": "",
            "name": "",
            "brand": "",
        },
        feedback_type="Helpful",
        profile=SAMPLE_PROFILE,
    )

    assert len(errors) == 3


def test_supported_options_are_available():
    assert "Helpful" in FEEDBACK_OPTIONS
    assert "Not for me" in FEEDBACK_OPTIONS
    assert "I would sample this" in FEEDBACK_OPTIONS


# --------------------------------------------------
# Feedback-record tests
# --------------------------------------------------
def test_feedback_record_contains_required_fields():
    record = build_feedback_record(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id="SESSION-TEST123456",
        profile=SAMPLE_PROFILE,
        comment="Useful result",
        recommendation_position=1,
    )

    assert set(
        FEEDBACK_COLUMNS
    ).issubset(
        set(record.keys())
    )

    assert record[
        "perfume_id"
    ] == "OLF-TEST-001"

    assert record[
        "feedback_type"
    ] == "Helpful"

    assert record[
        "recommendation_position"
    ] == 1

    assert record[
        "ranking_score"
    ] == 24.5


def test_feedback_record_does_not_store_identity_fields():
    record = build_feedback_record(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id="SESSION-TEST123456",
        profile=SAMPLE_PROFILE,
    )

    forbidden_fields = {
        "name_of_user",
        "email",
        "phone",
        "ip_address",
        "exact_location",
    }

    assert forbidden_fields.isdisjoint(
        set(record.keys())
    )


# --------------------------------------------------
# Storage tests
# --------------------------------------------------
def test_empty_feedback_file_is_created(
    temporary_feedback_storage,
):
    feedback_data = load_feedback()

    assert temporary_feedback_storage.exists()

    assert feedback_data.empty

    assert list(
        feedback_data.columns
    ) == FEEDBACK_COLUMNS


def test_feedback_is_saved(
    temporary_feedback_storage,
):
    session_id = create_session_id()

    result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id=session_id,
        profile=SAMPLE_PROFILE,
        comment="Easy to understand",
        recommendation_position=1,
    )

    assert result["success"] is True
    assert result["duplicate"] is False
    assert result["feedback_id"]

    feedback_data = load_feedback()

    assert len(feedback_data) == 1

    assert feedback_data.iloc[0][
        "feedback_type"
    ] == "Helpful"


def test_duplicate_feedback_is_blocked(
    temporary_feedback_storage,
):
    session_id = create_session_id()

    first_result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id=session_id,
        profile=SAMPLE_PROFILE,
        recommendation_position=1,
    )

    second_result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id=session_id,
        profile=SAMPLE_PROFILE,
        recommendation_position=1,
    )

    assert first_result[
        "success"
    ] is True

    assert second_result[
        "success"
    ] is False

    assert second_result[
        "duplicate"
    ] is True

    feedback_data = load_feedback()

    assert len(feedback_data) == 1


def test_different_feedback_type_is_allowed(
    temporary_feedback_storage,
):
    session_id = create_session_id()

    helpful_result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id=session_id,
        profile=SAMPLE_PROFILE,
    )

    sample_result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="I would sample this",
        session_id=session_id,
        profile=SAMPLE_PROFILE,
    )

    assert helpful_result[
        "success"
    ] is True

    assert sample_result[
        "success"
    ] is True

    feedback_data = load_feedback()

    assert len(feedback_data) == 2


def test_missing_session_id_is_rejected(
    temporary_feedback_storage,
):
    result = save_feedback(
        perfume=SAMPLE_PERFUME,
        feedback_type="Helpful",
        session_id="",
        profile=SAMPLE_PROFILE,
    )

    assert result["success"] is False
    assert result["duplicate"] is False


# --------------------------------------------------
# Duplicate-check helper test
# --------------------------------------------------
def test_duplicate_check():
    feedback_data = pd.DataFrame(
        [
            {
                "session_id": "SESSION-001",
                "perfume_id": "OLF-001",
                "feedback_type": "Helpful",
            }
        ]
    )

    duplicate_found = is_duplicate_feedback(
        feedback_data=feedback_data,
        session_id="SESSION-001",
        perfume_id="OLF-001",
        feedback_type="Helpful",
    )

    different_feedback = is_duplicate_feedback(
        feedback_data=feedback_data,
        session_id="SESSION-001",
        perfume_id="OLF-001",
        feedback_type="Not for me",
    )

    assert duplicate_found is True
    assert different_feedback is False


# --------------------------------------------------
# Summary tests
# --------------------------------------------------
def test_empty_feedback_summary():
    empty_feedback = pd.DataFrame(
        columns=FEEDBACK_COLUMNS
    )

    summary = calculate_feedback_summary(
        empty_feedback
    )

    assert summary[
        "total_feedback"
    ] == 0

    assert summary[
        "helpful_percentage"
    ] == 0.0

    assert summary[
        "feedback_type_counts"
    ] == []


def test_feedback_summary_calculation():
    feedback_data = pd.DataFrame(
        [
            {
                "session_id": "SESSION-001",
                "perfume_id": "OLF-001",
                "perfume_name": "Perfume A",
                "brand": "Brand A",
                "feedback_type": "Helpful",
            },
            {
                "session_id": "SESSION-002",
                "perfume_id": "OLF-001",
                "perfume_name": "Perfume A",
                "brand": "Brand A",
                "feedback_type": "Helpful",
            },
            {
                "session_id": "SESSION-003",
                "perfume_id": "OLF-002",
                "perfume_name": "Perfume B",
                "brand": "Brand B",
                "feedback_type": "Not for me",
            },
        ]
    )

    summary = calculate_feedback_summary(
        feedback_data
    )

    assert summary[
        "total_feedback"
    ] == 3

    assert summary[
        "unique_perfumes"
    ] == 2

    assert summary[
        "unique_sessions"
    ] == 3

    assert summary[
        "helpful_count"
    ] == 2

    assert summary[
        "not_for_me_count"
    ] == 1

    assert summary[
        "helpful_percentage"
    ] == 66.7

    assert summary[
        "most_reviewed_perfumes"
    ][0][
        "perfume_name"
    ] == "Perfume A"