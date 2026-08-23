from pathlib import Path
import html

import pandas as pd
import plotly.express as px
import streamlit as st

from src.features.wardrobe_analyser import (
    analyse_wardrobe,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="My Wardrobe | OLFYNZA",
    page_icon="🧴",
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
            font-size: clamp(2.1rem, 5vw, 3rem);
            font-weight: 850;
            line-height: 1.15;
            margin-bottom: 0.7rem;
        }

        .page-description {
            color: #cfc2d7;
            font-size: 1rem;
            line-height: 1.7;
            max-width: 850px;
            margin-bottom: 1.5rem;
        }

        .analysis-box {
            padding: 1.3rem 1.4rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.06);
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.14);
        }

        .analysis-title {
            color: #e4c47e;
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        .analysis-value {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 850;
            margin-bottom: 0.3rem;
        }

        .analysis-text {
            color: #d7cadf;
            font-size: 0.96rem;
            line-height: 1.7;
        }

        .section-title {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 1.5rem;
            margin-bottom: 0.7rem;
        }

        .section-description {
            color: #bfaec8;
            font-size: 0.94rem;
            line-height: 1.65;
            margin-bottom: 1rem;
        }

        .duplicate-card {
            padding: 1.15rem 1.25rem;
            margin-bottom: 0.9rem;
            border-left: 4px solid #d4af6a;
            border-radius: 0 16px 16px 0;
            background: rgba(212, 175, 106, 0.075);
        }

        .pair-name {
            color: #ffffff;
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.5;
        }

        .pair-score {
            color: #e4c47e;
            font-size: 0.94rem;
            font-weight: 800;
            margin-top: 0.35rem;
        }

        .pair-notes {
            color: #d7cadf;
            font-size: 0.92rem;
            line-height: 1.65;
            margin-top: 0.35rem;
        }

        .information-box {
            padding: 1.25rem 1.35rem;
            margin-top: 1rem;
            border: 1px solid rgba(212, 175, 106, 0.34);
            border-radius: 17px;
            color: #d7cadf;
            background: rgba(212, 175, 106, 0.065);
            line-height: 1.7;
        }

        .information-title {
            color: #e4c47e;
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.065);
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
# Load perfume catalogue
# --------------------------------------------------
@st.cache_data
def load_perfume_data():
    """Load and validate the cleaned perfume catalogue."""

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
        "perfume_id",
        "name",
        "brand",
        "notes",
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

    for column in [
        "perfume_id",
        "name",
        "brand",
        "notes",
    ]:
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
        OLFYNZA · WARDROBE INTELLIGENCE
    </div>
    """
)

st.html(
    """
    <div class="page-title">
        Analyse your perfume wardrobe
    </div>
    """
)

st.html(
    """
    <div class="page-description">
        Select the perfumes you currently own. OLFYNZA will
        analyse note variety, identify highly similar pairs,
        highlight dominant notes and provide a transparent
        collection-diversity indicator.
    </div>
    """
)


# --------------------------------------------------
# Perfume selection
# --------------------------------------------------
display_options = perfume_data[
    "display_name"
].tolist()

selected_perfumes = st.multiselect(
    "Select the perfumes in your collection",
    options=display_options,
    placeholder=(
        "Search and select at least two perfumes"
    ),
)

st.caption(
    "Choose perfumes from the cleaned OLFYNZA catalogue. "
    "Select at least two perfumes for similarity analysis."
)


# --------------------------------------------------
# Empty and single-selection states
# --------------------------------------------------
if not selected_perfumes:
    st.info(
        "Select perfumes from the list above to create "
        "your wardrobe analysis."
    )

    st.stop()


selected_records = perfume_data[
    perfume_data["display_name"].isin(
        selected_perfumes
    )
].copy()

wardrobe_records = (
    selected_records[
        [
            "perfume_id",
            "name",
            "brand",
            "notes",
        ]
    ]
    .to_dict(
        orient="records"
    )
)

analysis = analyse_wardrobe(
    wardrobe_records
)


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------
collection_size = analysis[
    "collection_size"
]

unique_note_count = analysis[
    "unique_note_count"
]

possible_duplicate_count = analysis[
    "possible_duplicate_count"
]

diversity = analysis[
    "diversity"
]

data_coverage = analysis[
    "data_coverage"
]

first_metric, second_metric, third_metric, fourth_metric = (
    st.columns(4)
)

with first_metric:
    st.metric(
        "Selected Perfumes",
        collection_size,
    )

with second_metric:
    st.metric(
        "Unique Notes",
        unique_note_count,
    )

with third_metric:
    st.metric(
        "Similar Pairs",
        possible_duplicate_count,
    )

with fourth_metric:
    st.metric(
        "Notes Coverage",
        (
            f"{data_coverage['coverage_percentage']:.1f}%"
        ),
    )


# --------------------------------------------------
# Diversity indicator
# --------------------------------------------------
diversity_score = diversity[
    "score"
]

diversity_label = html.escape(
    str(
        diversity["label"]
    )
)

diversity_guidance = html.escape(
    str(
        diversity["guidance"]
    )
)

average_similarity = diversity[
    "average_similarity"
]

st.html(
    f"""
    <div class="analysis-box">
        <div class="analysis-title">
            Collection diversity
        </div>

        <div class="analysis-value">
            {diversity_score:.1f}/100
        </div>

        <div class="analysis-text">
            <strong>{diversity_label}</strong>
            <br>
            {diversity_guidance}
            <br><br>
            Average pairwise note similarity:
            <strong>{average_similarity:.1f}%</strong>
        </div>
    </div>
    """
)


# --------------------------------------------------
# Not enough perfumes
# --------------------------------------------------
if collection_size < 2:
    st.warning(
        "Select at least two perfumes to calculate "
        "pairwise similarity and collection diversity."
    )


# --------------------------------------------------
# Dominant fragrance notes
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Dominant fragrance notes
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        These are the notes that appear most often across
        the selected perfume collection.
    </div>
    """
)

dominant_notes = analysis[
    "dominant_notes"
]

if not dominant_notes:
    st.warning(
        "The selected perfumes do not contain enough "
        "verified note information for note analysis."
    )

else:
    dominant_note_data = pd.DataFrame(
        dominant_notes
    ).rename(
        columns={
            "note": "Fragrance Note",
            "count": "Number of Perfumes",
        }
    )

    dominant_chart = px.bar(
        dominant_note_data.sort_values(
            "Number of Perfumes"
        ),
        x="Number of Perfumes",
        y="Fragrance Note",
        orientation="h",
        color="Number of Perfumes",
        color_continuous_scale=[
            "#56366D",
            "#E4C47E",
        ],
    )

    dominant_chart.update_layout(
        height=440,
        showlegend=False,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#E7DDEB",
            size=13,
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    dominant_chart.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)"
    )

    dominant_chart.update_yaxes(
        title="",
        gridcolor="rgba(255,255,255,0)"
    )

    st.plotly_chart(
        dominant_chart,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# --------------------------------------------------
# Possible duplicate pairs
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Highly similar perfume pairs
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        Pairs with at least 40% direct note overlap are flagged
        for review. A flagged pair does not mean the perfumes
        smell identical.
    </div>
    """
)

possible_duplicates = analysis[
    "possible_duplicates"
]

if not possible_duplicates:
    st.success(
        "No perfume pairs reached the current 40% "
        "note-overlap threshold."
    )

else:
    for comparison in possible_duplicates:
        first_name = html.escape(
            str(
                comparison["first_name"]
            )
        )

        first_brand = html.escape(
            str(
                comparison["first_brand"]
            )
        )

        second_name = html.escape(
            str(
                comparison["second_name"]
            )
        )

        second_brand = html.escape(
            str(
                comparison["second_brand"]
            )
        )

        similarity = comparison[
            "similarity_percentage"
        ]

        shared_notes = comparison[
            "shared_notes"
        ]

        shared_notes_text = (
            ", ".join(
                html.escape(
                    str(note)
                )
                for note in shared_notes
            )
            if shared_notes
            else "No shared notes available"
        )

        st.html(
            f"""
            <div class="duplicate-card">
                <div class="pair-name">
                    {first_name} by {first_brand}
                    <br>
                    and
                    <br>
                    {second_name} by {second_brand}
                </div>

                <div class="pair-score">
                    Note similarity: {similarity:.1f}%
                </div>

                <div class="pair-notes">
                    Shared notes: {shared_notes_text}
                </div>
            </div>
            """
        )


# --------------------------------------------------
# Selected collection table
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Selected collection
    </div>
    """
)

collection_table = selected_records[
    [
        "perfume_id",
        "name",
        "brand",
        "notes",
    ]
].rename(
    columns={
        "perfume_id": "Perfume ID",
        "name": "Perfume Name",
        "brand": "Brand",
        "notes": "Fragrance Notes",
    }
)

st.dataframe(
    collection_table,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Method transparency
# --------------------------------------------------
st.html(
    """
    <div class="information-box">
        <div class="information-title">
            How wardrobe analysis works
        </div>

        OLFYNZA compares each possible perfume pair using
        Jaccard note similarity. The diversity indicator is
        calculated as 100 minus the average pairwise note
        similarity.

        <br><br>

        The diversity score and 40% similarity threshold are
        documented project heuristics. They do not measure
        fragrance quality, performance or whether two perfumes
        smell identical.
    </div>
    """
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

home_column, comparison_column = st.columns(
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

with comparison_column:
    if st.button(
        "Compare Two Perfumes →",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/4_Perfume_Comparison.py"
        )