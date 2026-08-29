from datetime import datetime, timezone
from pathlib import Path
import csv
import re
import uuid

import pandas as pd


# --------------------------------------------------
# Storage configuration
# --------------------------------------------------
# The current stable portfolio release uses local CSV
# feedback storage.
#
# Cloud feedback persistence can be added as a future
# improvement without affecting the current application.
CLOUD_FEEDBACK_ENABLED = False


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
    Clean feedback text before local storage.

    Control characters are removed and the stored text
    is limited to the specified maximum length.
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

    try:
        maximum_length = int(
            maximum_length
        )

    except (TypeError, ValueError):
        maximum_length = 500

    maximum_length = max(
        0,
        maximum_length,
    )

    return cleaned_value[
        :maximum_length
    ]


# --------------------------------------------------
# Anonymous ID creation
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

    The identifier does not contain a name, email address,
    phone number, IP address or device information.
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

    cleaned_values = []

    for value in values:
        cleaned_value = clean_feedback_text(
            value,
            maximum_length=100,
        )

        if cleaned_value:
            cleaned_values.append(
                cleaned_value
            )

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
    """Validate one feedback submission."""

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
# Prepare local storage
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
# Load locally stored feedback
# --------------------------------------------------
def load_feedback():
    """
    Load feedback from the local CSV file.

    Local CSV storage is used by the current stable
    portfolio release.
    """

    initialise_feedback_storage()

    try:
        feedback_data = pd.read_csv(
            FEEDBACK_FILE,
            encoding="utf-8",
        )

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ):
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
    submitted the same feedback type for the same perfume.
    """

    if feedback_data is None:
        return False

    if not isinstance(
        feedback_data,
        pd.DataFrame,
    ):
        return False

    if feedback_data.empty:
        return False

    required_columns = {
        "session_id",
        "perfume_id",
        "feedback_type",
    }

    if not required_columns.issubset(
        set(feedback_data.columns)
    ):
        return False

    session_matches = (
        feedback_data["session_id"]
        .fillna("")
        .astype(str)
        .eq(str(session_id))
    )

    perfume_matches = (
        feedback_data["perfume_id"]
        .fillna("")
        .astype(str)
        .eq(str(perfume_id))
    )

    feedback_type_matches = (
        feedback_data["feedback_type"]
        .fillna("")
        .astype(str)
        .eq(str(feedback_type))
    )

    duplicate_rows = feedback_data[
        session_matches
        & perfume_matches
        & feedback_type_matches
    ]

    return not duplicate_rows.empty


# --------------------------------------------------
# Build a feedback record
# --------------------------------------------------
def build_feedback_record(
    perfume,
    feedback_type,
    session_id,
    profile=None,
    comment="",
    recommendation_position=None,
):
    """Create a clean anonymous feedback record."""

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
        "feedback_type": clean_feedback_text(
            feedback_type,
            maximum_length=100,
        ),
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
# Save feedback locally
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
    Validate and save anonymous recommendation feedback.

    The current stable portfolio release stores feedback
    in a local CSV file.
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
            "storage": "",
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
            "storage": "",
        }

    perfume_id = clean_feedback_text(
        perfume.get(
            "perfume_id",
            "",
        ),
        maximum_length=50,
    )

    feedback_data = load_feedback()

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
            "storage": "local",
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

    try:
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

    except OSError:
        return {
            "success": False,
            "duplicate": False,
            "message": (
                "The feedback could not be saved. "
                "Please try again."
            ),
            "feedback_id": "",
            "storage": "local",
        }

    return {
        "success": True,
        "duplicate": False,
        "message": (
            "Thank you. Your anonymous feedback "
            "was recorded for this demo session."
        ),
        "feedback_id": feedback_record[
            "feedback_id"
        ],
        "storage": "local",
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

    if (
        feedback_data is None
        or not isinstance(
            feedback_data,
            pd.DataFrame,
        )
        or feedback_data.empty
    ):
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

    for column in FEEDBACK_COLUMNS:
        if column not in feedback_data.columns:
            feedback_data[column] = ""

    total_feedback = len(
        feedback_data
    )

    unique_perfumes = feedback_data[
        "perfume_id"
    ].replace(
        "",
        pd.NA,
    ).nunique(
        dropna=True
    )

    unique_sessions = feedback_data[
        "session_id"
    ].replace(
        "",
        pd.NA,
    ).nunique(
        dropna=True
    )

    helpful_count = int(
        feedback_data[
            "feedback_type"
        ]
        .fillna("")
        .astype(str)
        .eq("Helpful")
        .sum()
    )

    not_for_me_count = int(
        feedback_data[
            "feedback_type"
        ]
        .fillna("")
        .astype(str)
        .eq("Not for me")
        .sum()
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
        .fillna("")
        .astype(str)
        .loc[
            lambda series: series.str.strip().ne("")
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

    reviewed_source = feedback_data.copy()

    reviewed_source = reviewed_source[
        reviewed_source["perfume_id"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
    ]

    if reviewed_source.empty:
        reviewed_perfumes = []

    else:
        reviewed_perfumes = (
            reviewed_source
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
                by=[
                    "feedback_count",
                    "perfume_name",
                ],
                ascending=[
                    False,
                    True,
                ],
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