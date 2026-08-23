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
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# File path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perfumes_clean.csv"
)


# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
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
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.15rem;
            margin-bottom: 1rem;
        }

        .page-title {
            color: #ffffff;
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 850;
            line-height: 1.15;
            margin-bottom: 0.6rem;
        }

        .page-description {
            color: #cfc2d7;
            font-size: 1rem;
            line-height: 1.65;
            max-width: 850px;
            margin-bottom: 1.5rem;
        }

        .section-title {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 1.4rem;
            margin-bottom: 0.8rem;
        }

        .information-box {
            padding: 1rem 1.2rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(212, 175, 106, 0.35);
            border-radius: 16px;
            color: #ded3e3;
            background: rgba(212, 175, 106, 0.07);
            line-height: 1.6;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.065);
        }

        [data-testid="stMetricLabel"] {
            color: #cdbfd3;
        }

        [data-testid="stMetricValue"] {
            color: #ffffff;
        }

        div.stButton > button {
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

        #MainMenu, footer, header {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Load dataset
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

    text_columns = [
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
        )

    return data


# --------------------------------------------------
# Note-frequency calculation
# --------------------------------------------------
@st.cache_data
def calculate_note_frequencies(data):
    """Count comma-separated fragrance notes."""

    all_notes = []

    for notes_text in data["notes"]:
        notes = [
            note.strip().lower()
            for note in notes_text.split(",")
            if note.strip()
        ]

        all_notes.extend(notes)

    note_counts = Counter(all_notes)

    note_data = pd.DataFrame(
        note_counts.most_common(20),
        columns=[
            "Fragrance Note",
            "Number of Perfumes",
        ],
    )

    return note_data


# --------------------------------------------------
# Load and prepare data
# --------------------------------------------------
try:
    perfume_data = load_data()

except (FileNotFoundError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()


total_perfumes = len(perfume_data)

total_brands = perfume_data[
    "brand"
].nunique()

records_with_notes = int(
    perfume_data["notes"]
    .str.strip()
    .ne("")
    .sum()
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
st.markdown(
    """
    <div class="mini-brand">
        OLFYNZA · DATA INTELLIGENCE
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-title">
        Explore the fragrance dataset
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        This dashboard summarises the cleaned perfume records
        used by the OLFYNZA recommendation engine. It provides
        transparent information about catalogue coverage,
        frequently occurring notes and current data limitations.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Dataset metrics
# --------------------------------------------------
first, second, third, fourth = st.columns(4)

with first:
    st.metric(
        "Perfume Records",
        f"{total_perfumes:,}",
    )

with second:
    st.metric(
        "Unique Brands",
        f"{total_brands:,}",
    )

with third:
    st.metric(
        "Records with Notes",
        f"{records_with_notes:,}",
    )

with fourth:
    st.metric(
        "Notes Coverage",
        f"{notes_coverage:.1f}%",
    )


# --------------------------------------------------
# Brand analysis
# --------------------------------------------------
st.markdown(
    """
    <div class="section-title">
        Most Represented Brands
    </div>
    """,
    unsafe_allow_html=True,
)

top_brands = (
    perfume_data["brand"]
    .value_counts()
    .head(15)
    .rename_axis("Brand")
    .reset_index(name="Number of Perfumes")
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
    font_color="#E7DDEB",
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20,
    ),
)

brand_chart.update_xaxes(
    gridcolor="rgba(255,255,255,0.08)"
)

brand_chart.update_yaxes(
    gridcolor="rgba(255,255,255,0)"
)

st.plotly_chart(
    brand_chart,
    use_container_width=True,
)


# --------------------------------------------------
# Note analysis
# --------------------------------------------------
st.markdown(
    """
    <div class="section-title">
        Most Common Fragrance Notes
    </div>
    """,
    unsafe_allow_html=True,
)

note_frequency_data = calculate_note_frequencies(
    perfume_data
)

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
    font_color="#E7DDEB",
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20,
    ),
)

note_chart.update_xaxes(
    gridcolor="rgba(255,255,255,0.08)"
)

note_chart.update_yaxes(
    gridcolor="rgba(255,255,255,0)"
)

st.plotly_chart(
    note_chart,
    use_container_width=True,
)


# --------------------------------------------------
# Searchable catalogue
# --------------------------------------------------
st.markdown(
    """
    <div class="section-title">
        Search the Catalogue
    </div>
    """,
    unsafe_allow_html=True,
)

search_term = st.text_input(
    "Search by perfume, brand or fragrance note",
    placeholder=(
        "Example: bergamot, vanilla, Xerjoff..."
    ),
)

if search_term.strip():
    search_text = search_term.strip().lower()

    filtered_data = perfume_data[
        perfume_data["name"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
        )
        | perfume_data["brand"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
        )
        | perfume_data["notes"]
        .str.lower()
        .str.contains(
            search_text,
            regex=False,
        )
    ].copy()

else:
    filtered_data = perfume_data.copy()


st.caption(
    f"Showing {len(filtered_data):,} matching records"
)

st.dataframe(
    filtered_data[
        [
            "perfume_id",
            "name",
            "brand",
            "notes",
            "has_notes",
        ]
    ].head(100),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Data transparency
# --------------------------------------------------
st.markdown(
    f"""
    <div class="information-box">
        <strong>Data-quality note</strong><br><br>

        The cleaned catalogue contains
        <strong>{total_perfumes:,}</strong> records.
        Fragrance-note information is available for
        <strong>{records_with_notes:,}</strong> records,
        while <strong>{records_without_notes:,}</strong>
        records do not contain verified note lists in the
        source dataset.

        OLFYNZA keeps those records because descriptions may
        still support text comparisons, but the recommendation
        interface discloses when verified notes are unavailable.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

home_column, profile_column = st.columns(2)

with home_column:
    if st.button(
        "← Return Home",
        use_container_width=True,
    ):
        st.switch_page("app.py")

with profile_column:
    if st.button(
        "Create My Scent Profile →",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/1_Scent_Profile.py"
        )
