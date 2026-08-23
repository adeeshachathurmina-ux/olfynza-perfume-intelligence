from pathlib import Path
import html

import pandas as pd
import streamlit as st

from src.features.perfume_comparison import (
    compare_perfumes,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Perfume Comparison | OLFYNZA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Dataset path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perfumes_clean.csv"
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.html(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(120, 74, 142, 0.22),
                    transparent 35%
                ),
                linear-gradient(
                    135deg,
                    #160f1d 0%,
                    #24152e 48%,
                    #35203f 100%
                );
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        .mini-brand {
            color: #e4c47e;
            font-size: 0.92rem;
            font-weight: 800;
            letter-spacing: 0.15rem;
            margin-bottom: 1rem;
        }

        .page-title {
            color: #ffffff;
            font-size: clamp(2.2rem, 5vw, 3.2rem);
            font-weight: 850;
            line-height: 1.15;
            margin-bottom: 0.7rem;
        }

        .page-description {
            color: #cfc2d7;
            font-size: 1rem;
            line-height: 1.7;
            max-width: 850px;
            margin-bottom: 1.7rem;
        }

        .comparison-card {
            min-height: 410px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.065);
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.16);
        }

        .perfume-name {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 0.25rem;
        }

        .brand-name {
            color: #cabbd2;
            font-size: 0.98rem;
            margin-bottom: 1.35rem;
        }

        .detail-label {
            color: #e4c47e;
            font-weight: 800;
        }

        .detail-text {
            color: #d7cadf;
            font-size: 0.95rem;
            line-height: 1.7;
            margin-bottom: 1.1rem;
            overflow-wrap: anywhere;
        }

        .similarity-box {
            padding: 1.35rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
            border: 1px solid rgba(212, 175, 106, 0.42);
            border-radius: 20px;
            background: rgba(212, 175, 106, 0.09);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.14);
        }

        .similarity-number {
            color: #ffffff;
            font-size: 2.35rem;
            font-weight: 850;
            line-height: 1.2;
        }

        .similarity-label {
            color: #e4c47e;
            font-size: 1.05rem;
            font-weight: 800;
            margin-top: 0.3rem;
        }

        .similarity-description {
            color: #d7cadf;
            font-size: 0.92rem;
            margin-top: 0.5rem;
        }

        .information-box {
            padding: 1.25rem 1.35rem;
            margin-top: 1.1rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 17px;
            color: #d7cadf;
            background: rgba(255, 255, 255, 0.05);
            line-height: 1.7;
        }

        .information-title {
            color: #e4c47e;
            font-size: 1rem;
            font-weight: 800;
        }

        .warning-text {
            color: #f2c572;
            font-size: 1rem;
            font-weight: 800;
        }

        .safe-text {
            color: #a9dfbf;
            font-weight: 750;
        }

        [data-testid="stSelectbox"] {
            background: rgba(255, 255, 255, 0.025);
            border-radius: 14px;
        }

        div.stButton > button {
            width: 100%;
            min-height: 3rem;
            border: none;
            border-radius: 14px;
            color: #211427;
            background: linear-gradient(
                90deg,
                #d4af6a,
                #efd79d
            );
            font-weight: 800;
        }

        div.stButton > button:hover {
            color: #211427;
            border: none;
            background: linear-gradient(
                90deg,
                #e0bd75,
                #f7e3ad
            );
            transform: translateY(-1px);
        }

        #MainMenu,
        footer,
        header {
            visibility: hidden;
        }

        @media (max-width: 768px) {
            .comparison-card {
                min-height: auto;
            }

            .block-container {
                padding-top: 1.5rem;
            }

            .page-title {
                font-size: 2rem;
            }
        }
    </style>
    """
)


# --------------------------------------------------
# Load and validate the dataset
# --------------------------------------------------
@st.cache_data
def load_perfume_data():
    """Load the cleaned OLFYNZA perfume catalogue."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "The cleaned perfume dataset was not found. "
            "Run src/data/clean_data.py first."
        )

    perfume_data = pd.read_csv(
        DATASET_PATH,
        encoding="utf-8",
    )

    required_columns = {
        "name",
        "brand",
        "notes",
        "description",
    }

    missing_columns = (
        required_columns
        - set(perfume_data.columns)
    )

    if missing_columns:
        raise ValueError(
            "The dataset is missing these required columns: "
            + ", ".join(sorted(missing_columns))
        )

    text_columns = [
        "name",
        "brand",
        "notes",
        "description",
    ]

    for column in text_columns:
        perfume_data[column] = (
            perfume_data[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    perfume_data = perfume_data[
        perfume_data["name"].ne("")
        & perfume_data["brand"].ne("")
    ].copy()

    perfume_data["display_name"] = (
        perfume_data["name"]
        + " · "
        + perfume_data["brand"]
    )

    perfume_data = (
        perfume_data
        .sort_values(
            by=["name", "brand"],
            key=lambda series: series.str.lower(),
        )
        .reset_index(drop=True)
    )

    return perfume_data


try:
    perfume_data = load_perfume_data()

except (
    FileNotFoundError,
    ValueError,
    pd.errors.ParserError,
) as error:
    st.error(str(error))
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------
st.html(
    """
    <div class="mini-brand">
        OLFYNZA · PERFUME COMPARISON
    </div>
    """
)

st.html(
    """
    <div class="page-title">
        Compare two fragrances
    </div>
    """
)

st.html(
    """
    <div class="page-description">
        Select two perfumes to compare their fragrance notes,
        shared characteristics, unique notes and direct
        conflicts with the notes selected in your scent profile.
    </div>
    """
)


# --------------------------------------------------
# Perfume selectors
# --------------------------------------------------
display_options = perfume_data[
    "display_name"
].tolist()

if len(display_options) < 2:
    st.error(
        "At least two perfume records are required "
        "to create a comparison."
    )
    st.stop()


first_selector, second_selector = st.columns(
    2,
    gap="medium",
)

with first_selector:
    first_selection = st.selectbox(
        "Select the first perfume",
        options=display_options,
        index=0,
        key="comparison_first_perfume",
    )

with second_selector:
    second_selection = st.selectbox(
        "Select the second perfume",
        options=display_options,
        index=1,
        key="comparison_second_perfume",
    )


if first_selection == second_selection:
    st.warning(
        "Please select two different perfumes "
        "to create a meaningful comparison."
    )
    st.stop()


# --------------------------------------------------
# Retrieve selected perfume records
# --------------------------------------------------
first_matches = perfume_data[
    perfume_data["display_name"]
    == first_selection
]

second_matches = perfume_data[
    perfume_data["display_name"]
    == second_selection
]

if first_matches.empty or second_matches.empty:
    st.error(
        "One of the selected perfumes could not "
        "be found in the catalogue."
    )
    st.stop()


first_perfume = (
    first_matches
    .iloc[0]
    .to_dict()
)

second_perfume = (
    second_matches
    .iloc[0]
    .to_dict()
)


# --------------------------------------------------
# Retrieve the user's scent profile
# --------------------------------------------------
profile = st.session_state.get(
    "scent_profile",
    {},
)

disliked_notes = profile.get(
    "disliked_notes",
    [],
)


# --------------------------------------------------
# Compare the selected perfumes
# --------------------------------------------------
comparison = compare_perfumes(
    first_perfume=first_perfume,
    second_perfume=second_perfume,
    disliked_notes=disliked_notes,
)


# --------------------------------------------------
# Safe display helpers
# --------------------------------------------------
def format_list(items, empty_message):
    """Convert a list into safe user-facing text."""

    if not items:
        return html.escape(
            empty_message
        )

    return ", ".join(
        html.escape(str(item))
        for item in items
    )


shared_notes_text = format_list(
    comparison["shared_notes"],
    "No directly shared notes were found.",
)

first_unique_text = format_list(
    comparison["first_perfume"]["unique_notes"],
    "No unique notes were identified.",
)

second_unique_text = format_list(
    comparison["second_perfume"]["unique_notes"],
    "No unique notes were identified.",
)

first_notes_text = format_list(
    comparison["first_perfume"]["notes"],
    "Verified notes are not available.",
)

second_notes_text = format_list(
    comparison["second_perfume"]["notes"],
    "Verified notes are not available.",
)

first_conflict_text = format_list(
    comparison["first_perfume"]["conflicts"],
    "No direct conflict detected.",
)

second_conflict_text = format_list(
    comparison["second_perfume"]["conflicts"],
    "No direct conflict detected.",
)

first_name = html.escape(
    comparison["first_perfume"]["name"]
)

first_brand = html.escape(
    comparison["first_perfume"]["brand"]
)

second_name = html.escape(
    comparison["second_perfume"]["name"]
)

second_brand = html.escape(
    comparison["second_perfume"]["brand"]
)


# --------------------------------------------------
# Similarity summary
# --------------------------------------------------
similarity_percentage = comparison[
    "similarity_percentage"
]

total_shared_notes = comparison[
    "total_shared_notes"
]

st.html(
    f"""
    <div class="similarity-box">
        <div class="similarity-number">
            {similarity_percentage}%
        </div>

        <div class="similarity-label">
            Fragrance-note similarity
        </div>

        <div class="similarity-description">
            {total_shared_notes} directly shared note(s)
        </div>
    </div>
    """
)


# --------------------------------------------------
# Build the first perfume card
# --------------------------------------------------
first_card_html = f"""
<div class="comparison-card">
    <div class="perfume-name">
        {first_name}
    </div>

    <div class="brand-name">
        by {first_brand}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            All available notes
        </span>

        <br>

        {first_notes_text}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            Notes unique to this perfume
        </span>

        <br>

        {first_unique_text}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            Selected-note conflicts
        </span>

        <br>

        {first_conflict_text}
    </div>
</div>
"""


# --------------------------------------------------
# Build the second perfume card
# --------------------------------------------------
second_card_html = f"""
<div class="comparison-card">
    <div class="perfume-name">
        {second_name}
    </div>

    <div class="brand-name">
        by {second_brand}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            All available notes
        </span>

        <br>

        {second_notes_text}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            Notes unique to this perfume
        </span>

        <br>

        {second_unique_text}
    </div>

    <div class="detail-text">
        <span class="detail-label">
            Selected-note conflicts
        </span>

        <br>

        {second_conflict_text}
    </div>
</div>
"""


# --------------------------------------------------
# Display side-by-side cards
# --------------------------------------------------
first_column, second_column = st.columns(
    2,
    gap="large",
)

with first_column:
    st.html(
        first_card_html
    )

with second_column:
    st.html(
        second_card_html
    )


# --------------------------------------------------
# Shared fragrance notes
# --------------------------------------------------
st.html(
    f"""
    <div class="information-box">
        <span class="information-title">
            Shared fragrance notes
        </span>

        <br><br>

        {shared_notes_text}
    </div>
    """
)


# --------------------------------------------------
# Personal preference conflict summary
# --------------------------------------------------
first_conflicts = comparison[
    "first_perfume"
]["conflicts"]

second_conflicts = comparison[
    "second_perfume"
]["conflicts"]

if disliked_notes:
    if first_conflicts or second_conflicts:
        st.html(
            """
            <div class="information-box">
                <span class="warning-text">
                    Preference caution
                </span>

                <br><br>

                At least one selected perfume contains a
                fragrance note that appears in the notes
                selected in the scent profile. Review the
                conflict information in both comparison cards
                before making a decision.
            </div>
            """
        )

    else:
        st.html(
            """
            <div class="information-box">
                <span class="safe-text">
                    No direct preference conflicts detected
                </span>

                <br><br>

                No direct conflict was found between the
                available perfume notes and the notes selected
                to avoid.
            </div>
            """
        )

else:
    st.info(
        "Complete the scent-profile quiz and select notes "
        "to avoid if you want personalised conflict checks."
    )


# --------------------------------------------------
# Method transparency
# --------------------------------------------------
st.html(
    """
    <div class="information-box">
        <span class="information-title">
            How this comparison works
        </span>

        <br><br>

        The fragrance-note similarity is calculated using
        Jaccard similarity. The number of directly shared
        notes is divided by the total number of unique notes
        across both perfumes.

        <br><br>

        This percentage describes note-list overlap only.
        It does not measure fragrance quality, longevity,
        safety, market value or the probability that a user
        will prefer one perfume.
    </div>
    """
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

home_column, profile_column = st.columns(
    2,
    gap="medium",
)

with home_column:
    if st.button(
        "← Return Home",
        use_container_width=True,
    ):
        st.switch_page(
            "app.py"
        )

with profile_column:
    if st.button(
        "Edit My Scent Profile →",
        use_container_width=True,
    ):
        st.session_state.quiz_step = 1

        st.switch_page(
            "pages/1_Scent_Profile.py"
        )