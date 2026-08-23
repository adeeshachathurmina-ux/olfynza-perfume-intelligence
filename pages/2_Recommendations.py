import html

import streamlit as st

from src.models.recommender import (
    build_recommendation_model,
    load_perfume_data,
    recommend_perfumes,
)
from src.features.profile_mapper import build_profile_query
from src.explainability.explanation import generate_explanation
from src.models.confidence import calculate_confidence
# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Your Matches | OLFYNZA",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed",
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
            max-width: 1100px;
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
            margin-bottom: 0.7rem;
        }

        .page-description {
            color: #cfc2d7;
            font-size: 1rem;
            line-height: 1.65;
            max-width: 800px;
            margin-bottom: 1.5rem;
        }

        .profile-box {
            padding: 1rem 1.2rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(212, 175, 106, 0.35);
            border-radius: 18px;
            background: rgba(212, 175, 106, 0.07);
            color: #eadfef;
            line-height: 1.7;
        }

        .result-card {
            padding: 1.4rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.065);
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.16);
        }

        .rank-label {
            color: #e4c47e;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.1rem;
        }

        .perfume-name {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 0.35rem;
        }

        .brand-name {
            color: #cabbd2;
            margin-bottom: 1rem;
        }

        .score-chip {
            display: inline-block;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            background: rgba(212, 175, 106, 0.16);
            color: #f0d493;
            font-weight: 750;
            margin-bottom: 0.9rem;
        }

        .detail-label {
            color: #e4c47e;
            font-weight: 750;
        }

        .detail-text {
            color: #d7cadf;
            line-height: 1.65;
        }

        div.stButton > button {
            min-height: 3rem;
            border: none;
            border-radius: 14px;
            color: #211427;
            background: linear-gradient(90deg, #d4af6a, #efd79d);
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
# Cached model
# --------------------------------------------------
@st.cache_resource
def load_model():
    perfume_data = load_perfume_data()

    model = build_recommendation_model(
        perfume_data
    )

    return perfume_data, model


# --------------------------------------------------
# Profile validation
# --------------------------------------------------
profile = st.session_state.get(
    "scent_profile",
    {}
)

required_fields = [
    "preferred_styles",
    "occasion",
    "environment",
    "strength",
    "budget",
]

missing_fields = [
    field
    for field in required_fields
    if not profile.get(field)
]

if missing_fields:
    st.warning(
        "Please complete your scent profile before "
        "viewing recommendations."
    )

    if st.button(
        "Create My Scent Profile",
        use_container_width=True
    ):
        st.switch_page(
            "pages/1_Scent_Profile.py"
        )

    st.stop()


# --------------------------------------------------
# Build model query
# --------------------------------------------------
preferred_styles = profile.get(
    "preferred_styles",
    []
)

occasion = profile.get(
    "occasion",
    ""
)

environment = profile.get(
    "environment",
    ""
)

strength = profile.get(
    "strength",
    ""
)

budget = profile.get(
    "budget",
    ""
)

disliked_notes = profile.get(
    "disliked_notes",
    []
)

preference_query = build_profile_query(profile)

# --------------------------------------------------
# Generate results
# --------------------------------------------------
perfume_data, model = load_model()

recommendations = recommend_perfumes(
    query=preference_query,
    perfume_data=perfume_data,
    model=model,
    top_n=15,
)

if not recommendations.empty and disliked_notes:
    disliked_terms = [
        note.lower().strip()
        for note in disliked_notes
    ]

    def contains_disliked_note(notes_text):
        notes_text = str(notes_text).lower()

        return any(
            disliked_note in notes_text
            for disliked_note in disliked_terms
        )

    recommendations[
        "contains_disliked_note"
    ] = recommendations["notes"].apply(
        contains_disliked_note
    )

    preferred_results = recommendations[
        ~recommendations["contains_disliked_note"]
    ].copy()

    if len(preferred_results) >= 5:
        recommendations = preferred_results

recommendations = recommendations.head(5)


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="mini-brand">'
    'OLFYNZA · PERSONALISED MATCHES'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">'
    'Your fragrance matches are ready ✦'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        These results are ranked using fragrance-note and
        description similarity. They are decision-support
        suggestions, not guarantees of personal preference
        or product performance.
    </div>
    """,
    unsafe_allow_html=True,
)

styles_text = ", ".join(
    preferred_styles
)

avoid_text = (
    ", ".join(disliked_notes)
    if disliked_notes
    else "None selected"
)

st.markdown(
    f"""
    <div class="profile-box">
        <strong>Your profile:</strong><br>
        Preferred styles: {html.escape(styles_text)}<br>
        Occasion: {html.escape(occasion)}<br>
        Environment: {html.escape(environment)}<br>
        Strength: {html.escape(strength)}<br>
        Budget preference: {html.escape(budget)}<br>
        Notes to avoid: {html.escape(avoid_text)}
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Result cards
# --------------------------------------------------
if recommendations.empty:
    st.error(
        "OLFYNZA could not find a meaningful text match "
        "for this profile. Try editing your scent styles."
    )

else:
    for position, (_, perfume) in enumerate(
        recommendations.iterrows(),
        start=1,
    ):
        name = html.escape(
            str(perfume["name"])
        )

        brand = html.escape(
            str(perfume["brand"])
        )

        notes = str(perfume["notes"]).strip()

        notes_text = (
            html.escape(notes)
            if notes
            else "Verified notes are not available."
        )

        matched_notes = perfume[
            "matched_notes"
        ]

        matched_text = (
            ", ".join(matched_notes)
            if matched_notes
            else "General profile similarity"
        )

        matched_text = html.escape(
            matched_text
        )

        ranking_score = perfume[
            "ranking_percentage"
        ]
        explanation = generate_explanation(
        profile=profile,
        perfume=perfume.to_dict()
)
        confidence = calculate_confidence(
    perfume.to_dict()
)

confidence_label = html.escape(
    confidence["label"]
)

confidence_guidance = html.escape(
    confidence["guidance"]
)

reason_items = "".join(
    f"<li>{html.escape(reason)}</li>"
    for reason in explanation["reasons"]
)

caution_text = html.escape(
    explanation["caution"]
)

data_quality_text = html.escape(
    explanation["data_quality_note"]
)

st.markdown(
            f"""
            <div class="result-card">
                <div class="rank-label">
                    MATCH {position}
                </div>

                <div class="perfume-name">
                    {name}
                </div>

                <div class="brand-name">
                    by {brand}
                </div>

                <div class="score-chip">
                    Ranking score: {ranking_score}%
                </div>
                <div class="detail-text">
    <span class="detail-label">
        Recommendation evidence:
    </span>
    {confidence_label}
</div>

<div class="detail-text">
    {confidence_guidance}
</div>

<br>

                <div class="detail-text">
                    <span class="detail-label">
                        Direct matches:
                    </span>
                    {matched_text}
                </div>
                <br>

<div class="detail-text">
    <span class="detail-label">
        Why OLFYNZA selected this:
    </span>

    <ul>
        {reason_items}
    </ul>
</div>

<div class="detail-text">
    <span class="detail-label">
        Preference check:
    </span>
    {caution_text}
</div>

<br>

<div class="detail-text">
    <span class="detail-label">
        Data transparency:
    </span>
    {data_quality_text}
</div>

                <br>

                <div class="detail-text">
                    <span class="detail-label">
                        Fragrance notes:
                    </span>
                    {notes_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
        "The ranking score combines text similarities. "
        "It is not the probability that you will like "
        "a fragrance."
    )


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

edit_column, home_column = st.columns(2)

with edit_column:
    if st.button(
        "← Edit My Profile",
        use_container_width=True
    ):
        st.session_state.quiz_step = 1

        st.switch_page(
            "pages/1_Scent_Profile.py"
        )

with home_column:
    if st.button(
        "Return Home",
        use_container_width=True
    ):
        st.switch_page("app.py")