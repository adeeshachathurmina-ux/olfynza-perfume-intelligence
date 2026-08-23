from datetime import datetime, timezone
from pathlib import Path
import csv
import re
import uuid

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEEDBACK_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "feedback"
)

FEEDBACK_FILE = (
    FEEDBACK_DIRECTORY
    / "recommendation_feedback.csv"
)


# --------------------------------------------------
# Supported feedback options
# --------------------------------------------------
FEEDBACK_OPTIONS = [
    "Helpful",
    "Not for me",
    "Too sweet",
    "Too strong",
    "Too light",
    "Too floral",
    "Too spicy",
    "Possible disliked-note conflict",
    "I would sample this",
]


# --------------------------------------------------
# CSV structure
# --------------------------------------------------
FEEDBACK_COLUMNS = [
    "feedback_id",
    "submitted_at_utc",
    "session_id",
    "perfume_id",
    "perfume_name",
    "brand",
    "feedback_type",
    "ranking_score",
    "recommendation_position",
    "preferred_styles",
    "occasion",
    "environment",
    "strength",
    "budget",
    "disliked_notes",
    "comment",
]


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------
def clean_feedback_text(
    value,
    maximum_length=500,
):
    """
    Clean free-text feedback before local storage.

    This function removes control characters and limits
    the length of the stored comment.
    """

    if value is None:
        return ""

    cleaned_value = str(value)

    cleaned_value = cleaned_value.replace(
        "\n",
        " ",
    )

    cleaned_value = cleaned_value.replace(
        "\r",
        " ",
    )

    cleaned_value = cleaned_value.replace(
        "\t",
        " ",
    )

    cleaned_value = re.sub(
        r"\s+",
        " ",
        cleaned_value,
    )

    cleaned_value = cleaned_value.strip()

    return cleaned_value[
        :maximum_length
    ]


# --------------------------------------------------
# ID creation
# --------------------------------------------------
def create_feedback_id():
    """Create a unique anonymous feedback identifier."""

    return (
        "FB-"
        + uuid.uuid4().hex[:12].upper()
    )


def create_session_id():
    """
    Create an anonymous session identifier.

    The value does not include a user's name, email address,
    IP address or device information.
    """

    return (
        "SESSION-"
        + uuid.uuid4().hex[:12].upper()
    )


# --------------------------------------------------
# List formatting
# --------------------------------------------------
def serialise_list(values):
    """Convert a list into a consistent text value."""

    if not values:
        return ""

    cleaned_values = [
        clean_feedback_text(
            value,
            maximum_length=100,
        )
        for value in values
        if clean_feedback_text(
            value,
            maximum_length=100,
        )
    ]

    return " | ".join(
        cleaned_values
    )


# --------------------------------------------------
# Input validation
# --------------------------------------------------
def validate_feedback(
    perfume,
    feedback_type,
    profile=None,
):
    """Validate a feedback submission."""

    errors = []

    if not isinstance(
        perfume,
        dict,
    ):
        errors.append(
            "The perfume record is invalid."
        )

        return errors

    perfume_id = clean_feedback_text(
        perfume.get(
            "perfume_id",
            "",
        )
    )

    perfume_name = clean_feedback_text(
        perfume.get(
            "name",
            "",
        )
    )

    brand = clean_feedback_text(
        perfume.get(
            "brand",
            "",
        )
    )

    if not perfume_id:
        errors.append(
            "The perfume ID is missing."
        )

    if not perfume_name:
        errors.append(
            "The perfume name is missing."
        )

    if not brand:
        errors.append(
            "The perfume brand is missing."
        )

    if feedback_type not in FEEDBACK_OPTIONS:
        errors.append(
            "Please select a supported feedback option."
        )

    if (
        profile is not None
        and not isinstance(profile, dict)
    ):
        errors.append(
            "The scent profile is invalid."
        )

    return errors


# --------------------------------------------------
# Prepare storage
# --------------------------------------------------
def initialise_feedback_storage():
    """
    Create the feedback directory and CSV header
    when they do not already exist.
    """

    FEEDBACK_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not FEEDBACK_FILE.exists():
        with FEEDBACK_FILE.open(
            mode="w",
            newline="",
            encoding="utf-8",
        ) as feedback_file:
            writer = csv.DictWriter(
                feedback_file,
                fieldnames=FEEDBACK_COLUMNS,
            )

            writer.writeheader()

    return FEEDBACK_FILE


# --------------------------------------------------
# Load feedback
# --------------------------------------------------
def load_feedback():
    """Load locally stored feedback records."""

    initialise_feedback_storage()

    try:
        feedback_data = pd.read_csv(
            FEEDBACK_FILE,
            encoding="utf-8",
        )

    except pd.errors.EmptyDataError:
        feedback_data = pd.DataFrame(
            columns=FEEDBACK_COLUMNS
        )

    for column in FEEDBACK_COLUMNS:
        if column not in feedback_data.columns:
            feedback_data[column] = ""

    return feedback_data[
        FEEDBACK_COLUMNS
    ]


# --------------------------------------------------
# Duplicate checking
# --------------------------------------------------
def is_duplicate_feedback(
    feedback_data,
    session_id,
    perfume_id,
    feedback_type,
):
    """
    Check whether the same anonymous session has already
    submitted the same feedback for the same perfume.
    """

    if feedback_data.empty:
        return False

    duplicate_rows = feedback_data[
        feedback_data["session_id"]
        .fillna("")
        .astype(str)
        .eq(str(session_id))
        & feedback_data["perfume_id"]
        .fillna("")
        .astype(str)
        .eq(str(perfume_id))
        & feedback_data["feedback_type"]
        .fillna("")
        .astype(str)
        .eq(str(feedback_type))
    ]

    return not duplicate_rows.empty


# --------------------------------------------------
# Build feedback record
# --------------------------------------------------
def build_feedback_record(
    perfume,
    feedback_type,
    session_id,
    profile=None,
    comment="",
    recommendation_position=None,
):
    """Create a clean feedback record."""

    if profile is None:
        profile = {}

    ranking_score = perfume.get(
        "ranking_percentage",
        0,
    )

    try:
        ranking_score = round(
            float(ranking_score),
            2,
        )

    except (TypeError, ValueError):
        ranking_score = 0.0

    try:
        recommendation_position = int(
            recommendation_position
        )

    except (TypeError, ValueError):
        recommendation_position = 0

    submitted_at = datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )

    return {
        "feedback_id": create_feedback_id(),
        "submitted_at_utc": submitted_at,
        "session_id": clean_feedback_text(
            session_id,
            maximum_length=40,
        ),
        "perfume_id": clean_feedback_text(
            perfume.get(
                "perfume_id",
                "",
            ),
            maximum_length=50,
        ),
        "perfume_name": clean_feedback_text(
            perfume.get(
                "name",
                "",
            ),
            maximum_length=200,
        ),
        "brand": clean_feedback_text(
            perfume.get(
                "brand",
                "",
            ),
            maximum_length=150,
        ),
        "feedback_type": feedback_type,
        "ranking_score": ranking_score,
        "recommendation_position": (
            recommendation_position
        ),
        "preferred_styles": serialise_list(
            profile.get(
                "preferred_styles",
                [],
            )
        ),
        "occasion": clean_feedback_text(
            profile.get(
                "occasion",
                "",
            ),
            maximum_length=100,
        ),
        "environment": clean_feedback_text(
            profile.get(
                "environment",
                "",
            ),
            maximum_length=100,
        ),
        "strength": clean_feedback_text(
            profile.get(
                "strength",
                "",
            ),
            maximum_length=100,
        ),
        "budget": clean_feedback_text(
            profile.get(
                "budget",
                "",
            ),
            maximum_length=100,
        ),
        "disliked_notes": serialise_list(
            profile.get(
                "disliked_notes",
                [],
            )
        ),
        "comment": clean_feedback_text(
            comment,
            maximum_length=500,
        ),
    }


# --------------------------------------------------
# Save feedback
# --------------------------------------------------
def save_feedback(
    perfume,
    feedback_type,
    session_id,
    profile=None,
    comment="",
    recommendation_position=None,
):
    """
    Validate and save one anonymous feedback submission.

    Returns a result dictionary used by the Streamlit page.
    """

    validation_errors = validate_feedback(
        perfume=perfume,
        feedback_type=feedback_type,
        profile=profile,
    )

    if validation_errors:
        return {
            "success": False,
            "duplicate": False,
            "message": " ".join(
                validation_errors
            ),
            "feedback_id": "",
        }

    clean_session_id = clean_feedback_text(
        session_id,
        maximum_length=40,
    )

    if not clean_session_id:
        return {
            "success": False,
            "duplicate": False,
            "message": (
                "An anonymous session ID is required."
            ),
            "feedback_id": "",
        }

    feedback_data = load_feedback()

    perfume_id = clean_feedback_text(
        perfume.get(
            "perfume_id",
            "",
        )
    )

    if is_duplicate_feedback(
        feedback_data=feedback_data,
        session_id=clean_session_id,
        perfume_id=perfume_id,
        feedback_type=feedback_type,
    ):
        return {
            "success": False,
            "duplicate": True,
            "message": (
                "This feedback was already recorded for "
                "the selected perfume in this session."
            ),
            "feedback_id": "",
        }

    feedback_record = build_feedback_record(
        perfume=perfume,
        feedback_type=feedback_type,
        session_id=clean_session_id,
        profile=profile,
        comment=comment,
        recommendation_position=(
            recommendation_position
        ),
    )

    initialise_feedback_storage()

    with FEEDBACK_FILE.open(
        mode="a",
        newline="",
        encoding="utf-8",
    ) as feedback_file:
        writer = csv.DictWriter(
            feedback_file,
            fieldnames=FEEDBACK_COLUMNS,
        )

        writer.writerow(
            feedback_record
        )

    return {
        "success": True,
        "duplicate": False,
        "message": (
            "Thank you. Your anonymous feedback "
            "was saved locally."
        ),
        "feedback_id": feedback_record[
            "feedback_id"
        ],
    }


# --------------------------------------------------
# Feedback statistics
# --------------------------------------------------
def calculate_feedback_summary(
    feedback_data=None,
):
    """Calculate aggregate feedback statistics."""

    if feedback_data is None:
        feedback_data = load_feedback()

    if feedback_data.empty:
        return {
            "total_feedback": 0,
            "unique_perfumes": 0,
            "unique_sessions": 0,
            "helpful_count": 0,
            "not_for_me_count": 0,
            "helpful_percentage": 0.0,
            "feedback_type_counts": [],
            "most_reviewed_perfumes": [],
        }

    total_feedback = len(
        feedback_data
    )

    unique_perfumes = feedback_data[
        "perfume_id"
    ].nunique(
        dropna=True
    )

    unique_sessions = feedback_data[
        "session_id"
    ].nunique(
        dropna=True
    )

    helpful_count = int(
        feedback_data[
            "feedback_type"
        ].eq(
            "Helpful"
        ).sum()
    )

    not_for_me_count = int(
        feedback_data[
            "feedback_type"
        ].eq(
            "Not for me"
        ).sum()
    )

    helpful_percentage = (
        helpful_count
        / total_feedback
        * 100
        if total_feedback
        else 0.0
    )

    feedback_type_counts = (
        feedback_data[
            "feedback_type"
        ]
        .value_counts()
        .rename_axis(
            "feedback_type"
        )
        .reset_index(
            name="count"
        )
        .to_dict(
            orient="records"
        )
    )

    reviewed_perfumes = (
        feedback_data
        .groupby(
            [
                "perfume_id",
                "perfume_name",
                "brand",
            ],
            dropna=False,
        )
        .size()
        .reset_index(
            name="feedback_count"
        )
        .sort_values(
            by="feedback_count",
            ascending=False,
        )
        .head(10)
        .to_dict(
            orient="records"
        )
    )

    return {
        "total_feedback": int(
            total_feedback
        ),
        "unique_perfumes": int(
            unique_perfumes
        ),
        "unique_sessions": int(
            unique_sessions
        ),
        "helpful_count": helpful_count,
        "not_for_me_count": (
            not_for_me_count
        ),
        "helpful_percentage": round(
            helpful_percentage,
            1,
        ),
        "feedback_type_counts": (
            feedback_type_counts
        ),
        "most_reviewed_perfumes": (
            reviewed_perfumes
        ),
    }