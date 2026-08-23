from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Data Insights | OLFYNZA",
    page_icon="📊",
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
            margin-bottom: 1.7rem;
        }

        .section-title {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 1.6rem;
            margin-bottom: 0.9rem;
        }

        .section-description {
            color: #bfaec8;
            font-size: 0.94rem;
            line-height: 1.65;
            margin-top: -0.35rem;
            margin-bottom: 1rem;
        }

        .information-box {
            padding: 1.35rem 1.45rem;
            margin-top: 1.4rem;
            margin-bottom: 1.2rem;
            border: 1px solid rgba(212, 175, 106, 0.38);
            border-radius: 18px;
            background: rgba(212, 175, 106, 0.075);
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.13);
        }

        .information-title {
            color: #e4c47e;
            font-size: 1.12rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }

        .information-text {
            color: #d7cadf;
            font-size: 0.98rem;
            line-height: 1.75;
            margin-bottom: 0.85rem;
        }

        .information-text:last-child {
            margin-bottom: 0;
        }

        .information-number {
            color: #ffffff;
            font-weight: 800;
        }

        .coverage-highlight {
            display: inline-block;
            padding: 0.18rem 0.48rem;
            border-radius: 999px;
            color: #f1d894;
            background: rgba(212, 175, 106, 0.15);
            font-weight: 800;
        }

        [data-testid="stMetric"] {
            padding: 1.15rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.065);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
        }

        [data-testid="stMetricLabel"] {
            color: #cdbfd3;
            font-weight: 700;
        }

        [data-testid="stMetricValue"] {
            color: #ffffff;
            font-weight: 850;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 16px;
            overflow: hidden;
        }

        [data-testid="stTextInput"] {
            margin-bottom: 0.4rem;
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

            .information-box {
                padding: 1.15rem;
            }
        }
    </style>
    """
)


# --------------------------------------------------
# Load and validate dataset
# --------------------------------------------------
@st.cache_data
def load_data():
    """Load the cleaned OLFYNZA perfume dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "The cleaned perfume dataset was not found. "
            "Run src/data/clean_data.py first."
        )

    data = pd.read_csv(
        DATASET_PATH,
        encoding="utf-8",
    )

    required_columns = {
        "perfume_id",
        "name",
        "brand",
        "notes",
        "description",
        "has_notes",
    }

    missing_columns = (
        required_columns
        - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "The dataset is missing these required columns: "
            + ", ".join(sorted(missing_columns))
        )

    text_columns = [
        "perfume_id",
        "name",
        "brand",
        "notes",
        "description",
    ]

    for column in text_columns:
        data[column] = (
            data[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    data = data[
        data["name"].ne("")
        & data["brand"].ne("")
    ].copy()

    data["has_notes"] = (
        data["notes"]
        .str.strip()
        .ne("")
    )

    return data


# --------------------------------------------------
# Calculate fragrance-note frequencies
# --------------------------------------------------
@st.cache_data
def calculate_note_frequencies(data):
    """Count the comma-separated fragrance notes."""

    all_notes = []

    for notes_text in data["notes"]:
        notes = [
            note.strip().lower()
            for note in str(notes_text).split(",")
            if note.strip()
        ]

        all_notes.extend(notes)

    note_counts = Counter(
        all_notes
    )

    note_data = pd.DataFrame(
        note_counts.most_common(20),
        columns=[
            "Fragrance Note",
            "Number of Perfumes",
        ],
    )

    return note_data


# --------------------------------------------------
# Load and prepare dataset
# --------------------------------------------------
try:
    perfume_data = load_data()

except (
    FileNotFoundError,
    ValueError,
    pd.errors.ParserError,
    UnicodeDecodeError,
) as error:
    st.error(
        str(error)
    )
    st.stop()


# --------------------------------------------------
# Dataset statistics
# --------------------------------------------------
total_perfumes = len(
    perfume_data
)

total_brands = perfume_data[
    "brand"
].nunique()

records_with_notes = int(
    perfume_data[
        "has_notes"
    ].sum()
)

records_without_notes = (
    total_perfumes
    - records_with_notes
)

notes_coverage = (
    records_with_notes
    / total_perfumes
    * 100
    if total_perfumes
    else 0
)


# --------------------------------------------------
# Header
# --------------------------------------------------
st.html(
    """
    <div class="mini-brand">
        OLFYNZA · DATA INTELLIGENCE
    </div>
    """
)

st.html(
    """
    <div class="page-title">
        Explore the fragrance dataset
    </div>
    """
)

st.html(
    """
    <div class="page-description">
        This dashboard summarises the cleaned perfume records
        used by the OLFYNZA recommendation engine. Explore
        catalogue coverage, represented brands, frequently
        occurring fragrance notes and current data limitations.
    </div>
    """
)


# --------------------------------------------------
# Dataset metrics
# --------------------------------------------------
first_metric, second_metric, third_metric, fourth_metric = (
    st.columns(4)
)

with first_metric:
    st.metric(
        label="Perfume Records",
        value=f"{total_perfumes:,}",
    )

with second_metric:
    st.metric(
        label="Unique Brands",
        value=f"{total_brands:,}",
    )

with third_metric:
    st.metric(
        label="Records with Notes",
        value=f"{records_with_notes:,}",
    )

with fourth_metric:
    st.metric(
        label="Notes Coverage",
        value=f"{notes_coverage:.1f}%",
    )


# --------------------------------------------------
# Brand analysis
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Most Represented Brands
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        The chart shows the fifteen brands with the largest
        number of perfume records in the cleaned catalogue.
    </div>
    """
)

top_brands = (
    perfume_data["brand"]
    .value_counts()
    .head(15)
    .rename_axis("Brand")
    .reset_index(
        name="Number of Perfumes"
    )
)

brand_chart = px.bar(
    top_brands.sort_values(
        "Number of Perfumes"
    ),
    x="Number of Perfumes",
    y="Brand",
    orientation="h",
    title=None,
    color="Number of Perfumes",
    color_continuous_scale=[
        "#56366D",
        "#D4AF6A",
    ],
)

brand_chart.update_layout(
    height=520,
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
    hoverlabel=dict(
        bgcolor="#24152E",
        font_color="#FFFFFF",
        bordercolor="#D4AF6A",
    ),
)

brand_chart.update_xaxes(
    title="Number of Perfumes",
    gridcolor="rgba(255,255,255,0.08)",
    zerolinecolor="rgba(255,255,255,0.10)",
)

brand_chart.update_yaxes(
    title="",
    gridcolor="rgba(255,255,255,0)",
)

st.plotly_chart(
    brand_chart,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
    },
)


# --------------------------------------------------
# Fragrance-note analysis
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Most Common Fragrance Notes
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        The chart counts individual comma-separated notes
        appearing in the available fragrance-note lists.
    </div>
    """
)

note_frequency_data = (
    calculate_note_frequencies(
        perfume_data
    )
)

if note_frequency_data.empty:
    st.warning(
        "No fragrance-note information is available "
        "for frequency analysis."
    )

else:
    note_chart = px.bar(
        note_frequency_data.sort_values(
            "Number of Perfumes"
        ),
        x="Number of Perfumes",
        y="Fragrance Note",
        orientation="h",
        title=None,
        color="Number of Perfumes",
        color_continuous_scale=[
            "#56366D",
            "#E4C47E",
        ],
    )

    note_chart.update_layout(
        height=620,
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
        hoverlabel=dict(
            bgcolor="#24152E",
            font_color="#FFFFFF",
            bordercolor="#D4AF6A",
        ),
    )

    note_chart.update_xaxes(
        title="Number of Perfumes",
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.10)",
    )

    note_chart.update_yaxes(
        title="",
        gridcolor="rgba(255,255,255,0)",
    )

    st.plotly_chart(
        note_chart,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# --------------------------------------------------
# Searchable catalogue
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Search the Catalogue
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        Search the cleaned catalogue using a perfume name,
        brand name or fragrance note.
    </div>
    """
)

search_term = st.text_input(
    "Search by perfume, brand or fragrance note",
    placeholder=(
        "Example: bergamot, vanilla or Xerjoff"
    ),
    label_visibility="collapsed",
)

if search_term.strip():
    search_text = (
        search_term
        .strip()
        .lower()
    )

    name_matches = (
        perfume_data["name"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
            na=False,
        )
    )

    brand_matches = (
        perfume_data["brand"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
            na=False,
        )
    )

    note_matches = (
        perfume_data["notes"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
            na=False,
        )
    )

    filtered_data = perfume_data[
        name_matches
        | brand_matches
        | note_matches
    ].copy()

else:
    filtered_data = (
        perfume_data
        .copy()
    )


st.caption(
    f"Showing {len(filtered_data):,} matching record(s). "
    "The table displays a maximum of 100 records."
)

catalogue_columns = [
    "perfume_id",
    "name",
    "brand",
    "notes",
    "has_notes",
]

catalogue_preview = (
    filtered_data[
        catalogue_columns
    ]
    .head(100)
    .rename(
        columns={
            "perfume_id": "Perfume ID",
            "name": "Perfume Name",
            "brand": "Brand",
            "notes": "Fragrance Notes",
            "has_notes": "Notes Available",
        }
    )
)

st.dataframe(
    catalogue_preview,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Perfume ID": st.column_config.TextColumn(
            width="small",
        ),
        "Perfume Name": st.column_config.TextColumn(
            width="medium",
        ),
        "Brand": st.column_config.TextColumn(
            width="medium",
        ),
        "Fragrance Notes": st.column_config.TextColumn(
            width="large",
        ),
        "Notes Available": st.column_config.CheckboxColumn(
            width="small",
        ),
    },
)


# --------------------------------------------------
# Data transparency
# --------------------------------------------------
data_quality_html = f"""
<div class="information-box">
    <div class="information-title">
        Data-quality note
    </div>

    <div class="information-text">
        The cleaned catalogue contains
        <span class="information-number">
            {total_perfumes:,}
        </span>
        perfume records from
        <span class="information-number">
            {total_brands:,}
        </span>
        represented brands.
    </div>

    <div class="information-text">
        Fragrance-note information is available for
        <span class="information-number">
            {records_with_notes:,}
        </span>
        records. This represents
        <span class="coverage-highlight">
            {notes_coverage:.1f}% notes coverage
        </span>
        in the current cleaned catalogue.
    </div>

    <div class="information-text">
        A total of
        <span class="information-number">
            {records_without_notes:,}
        </span>
        records do not contain verified fragrance-note lists
        in the source dataset.
    </div>

    <div class="information-text">
        OLFYNZA keeps those records because their descriptions
        may still support text comparisons. The recommendation
        interface clearly indicates when verified fragrance
        notes are unavailable.
    </div>
</div>
"""

st.html(
    data_quality_html
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
        "Create My Scent Profile →",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/1_Scent_Profile.py"
)