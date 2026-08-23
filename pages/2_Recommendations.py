import html

import streamlit as st

from src.explainability.explanation import (
    generate_explanation,
)
from src.features.profile_mapper import (
    build_profile_query,
)
from src.models.confidence import (
    calculate_confidence,
)
from src.models.recommender import (
    build_recommendation_model,
    load_perfume_data,
    recommend_perfumes,
)
from src.features.feedback_manager import (
    FEEDBACK_OPTIONS,
    create_session_id,
    save_feedback,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Your Matches | OLFYNZA",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)
# --------------------------------------------------
# Anonymous feedback session
# --------------------------------------------------
if "feedback_session_id" not in st.session_state:
    st.session_state.feedback_session_id = (
        create_session_id()
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
            max-width: 1100px;
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
            max-width: 820px;
            margin-bottom: 1.5rem;
        }

        .profile-box {
            padding: 1.25rem 1.35rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(212, 175, 106, 0.35);
            border-radius: 18px;
            background: rgba(212, 175, 106, 0.07);
            color: #eadfef;
            font-size: 0.96rem;
            line-height: 1.8;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        }

        .profile-title {
            color: #e4c47e;
            font-size: 1rem;
            font-weight: 800;
        }

        .profile-label {
            color: #e4c47e;
            font-weight: 750;
        }

        .result-card {
            padding: 1.5rem;
            margin-bottom: 1.35rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.065);
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.16);
        }

        .rank-label {
            color: #e4c47e;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.1rem;
            margin-bottom: 0.45rem;
        }

        .perfume-name {
            color: #ffffff;
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 0.2rem;
        }

        .brand-name {
            color: #cabbd2;
            font-size: 0.98rem;
            margin-bottom: 1rem;
        }

        .score-chip {
            display: inline-block;
            padding: 0.48rem 0.8rem;
            margin-bottom: 1.1rem;
            border: 1px solid rgba(212, 175, 106, 0.24);
            border-radius: 999px;
            background: rgba(212, 175, 106, 0.16);
            color: #f0d493;
            font-size: 0.9rem;
            font-weight: 800;
        }

        .evidence-box {
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            border-radius: 15px;
            background: rgba(86, 54, 109, 0.32);
            border: 1px solid rgba(255, 255, 255, 0.09);
        }

        .detail-section {
            padding-top: 0.35rem;
            padding-bottom: 0.85rem;
        }

        .detail-label {
            color: #e4c47e;
            font-size: 0.95rem;
            font-weight: 800;
        }

        .detail-text {
            color: #d7cadf;
            font-size: 0.95rem;
            line-height: 1.7;
            overflow-wrap: anywhere;
        }

        .detail-text ul {
            padding-left: 1.3rem;
            margin-top: 0.55rem;
            margin-bottom: 0;
        }

        .detail-text li {
            margin-bottom: 0.45rem;
        }

        .data-note {
            padding: 0.9rem 1rem;
            margin-top: 0.35rem;
            border-left: 3px solid #d4af6a;
            border-radius: 0 12px 12px 0;
            background: rgba(212, 175, 106, 0.055);
        }

        .page-caption {
            color: #aa9bb3;
            font-size: 0.86rem;
            line-height: 1.55;
            margin-top: 0.3rem;
            margin-bottom: 1rem;
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

            .result-card {
                padding: 1.2rem;
            }

            .perfume-name {
                font-size: 1.3rem;
            }
            .feedback-heading {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 800;
    margin-top: 0.4rem;
    margin-bottom: 0.2rem;
}

.feedback-help {
    color: #bfaec8;
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 0.7rem;
}

.feedback-privacy {
    padding: 0.8rem 0.95rem;
    margin-top: 0.7rem;
    margin-bottom: 0.7rem;
    border-radius: 12px;
    color: #beafc7;
    background: rgba(255, 255, 255, 0.035);
    font-size: 0.84rem;
    line-height: 1.55;
}

[data-testid="stForm"] {
    padding: 1rem;
    margin-top: -0.45rem;
    margin-bottom: 1.4rem;
    border: 1px solid rgba(212, 175, 106, 0.22);
    border-radius: 0 0 20px 20px;
    background: rgba(255, 255, 255, 0.035);
}

[data-testid="stTextArea"] textarea {
    min-height: 90px;
}

        }
    </style>
    """
)


# --------------------------------------------------
# Cached recommendation model
# --------------------------------------------------
@st.cache_resource
def load_model():
    """Load the perfume catalogue and recommendation model."""

    perfume_data = load_perfume_data()

    model = build_recommendation_model(
        perfume_data
    )

    return perfume_data, model


# --------------------------------------------------
# Retrieve and validate the scent profile
# --------------------------------------------------
profile = st.session_state.get(
    "scent_profile",
    {},
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
        use_container_width=True,
    ):
        st.switch_page(
            "pages/1_Scent_Profile.py"
        )

    st.stop()


# --------------------------------------------------
# Profile values
# --------------------------------------------------
preferred_styles = profile.get(
    "preferred_styles",
    [],
)

occasion = str(
    profile.get(
        "occasion",
        "",
    )
)

environment = str(
    profile.get(
        "environment",
        "",
    )
)

strength = str(
    profile.get(
        "strength",
        "",
    )
)

budget = str(
    profile.get(
        "budget",
        "",
    )
)

disliked_notes = profile.get(
    "disliked_notes",
    [],
)


# --------------------------------------------------
# Build recommendation query
# --------------------------------------------------
preference_query = build_profile_query(
    profile
)

if not preference_query.strip():
    st.error(
        "OLFYNZA could not build a recommendation query "
        "from the selected profile."
    )
    st.stop()


# --------------------------------------------------
# Generate recommendations
# --------------------------------------------------
perfume_data, model = load_model()

recommendations = recommend_perfumes(
    query=preference_query,
    perfume_data=perfume_data,
    model=model,
    top_n=15,
)


# --------------------------------------------------
# Apply disliked-note filtering
# --------------------------------------------------
if (
    not recommendations.empty
    and disliked_notes
):
    disliked_terms = [
        str(note).lower().strip()
        for note in disliked_notes
        if str(note).strip()
    ]

    def contains_disliked_note(notes_text):
        """Identify direct disliked-note matches."""

        normalised_notes = str(
            notes_text
        ).lower()

        return any(
            disliked_note in normalised_notes
            for disliked_note in disliked_terms
        )

    recommendations[
        "contains_disliked_note"
    ] = recommendations["notes"].apply(
        contains_disliked_note
    )

    preferred_results = recommendations[
        ~recommendations[
            "contains_disliked_note"
        ]
    ].copy()

    if len(preferred_results) >= 5:
        recommendations = preferred_results


recommendations = (
    recommendations
    .head(5)
    .reset_index(drop=True)
)


# --------------------------------------------------
# Header
# --------------------------------------------------
st.html(
    """
    <div class="mini-brand">
        OLFYNZA · PERSONALISED MATCHES
    </div>
    """
)

st.html(
    """
    <div class="page-title">
        Your fragrance matches are ready ✦
    </div>
    """
)

st.html(
    """
    <div class="page-description">
        These results are ranked using fragrance-note and
        description similarity. They are decision-support
        suggestions, not guarantees of personal preference
        or product performance.
    </div>
    """
)


# --------------------------------------------------
# Safe profile display values
# --------------------------------------------------
styles_text = (
    ", ".join(preferred_styles)
    if preferred_styles
    else "Not selected"
)

avoid_text = (
    ", ".join(disliked_notes)
    if disliked_notes
    else "None selected"
)

styles_safe = html.escape(
    styles_text
)

occasion_safe = html.escape(
    occasion
)

environment_safe = html.escape(
    environment
)

strength_safe = html.escape(
    strength
)

budget_safe = html.escape(
    budget
)

avoid_safe = html.escape(
    avoid_text
)


# --------------------------------------------------
# Profile summary
# --------------------------------------------------
profile_html = f"""
<div class="profile-box">
    <div class="profile-title">
        Your selected profile
    </div>

    <br>

    <span class="profile-label">
        Preferred styles:
    </span>
    {styles_safe}

    <br>

    <span class="profile-label">
        Occasion:
    </span>
    {occasion_safe}

    <br>

    <span class="profile-label">
        Environment:
    </span>
    {environment_safe}

    <br>

    <span class="profile-label">
        Strength:
    </span>
    {strength_safe}

    <br>

    <span class="profile-label">
        Budget preference:
    </span>
    {budget_safe}

    <br>

    <span class="profile-label">
        Notes to avoid:
    </span>
    {avoid_safe}
</div>
"""

st.html(
    profile_html
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
        # ------------------------------------------
        # Safe perfume information
        # ------------------------------------------
        name = html.escape(
            str(
                perfume.get(
                    "name",
                    "Unknown perfume",
                )
            )
        )

        brand = html.escape(
            str(
                perfume.get(
                    "brand",
                    "Unknown brand",
                )
            )
        )

        notes = str(
            perfume.get(
                "notes",
                "",
            )
        ).strip()

        notes_text = (
            html.escape(notes)
            if notes
            else "Verified notes are not available."
        )

        matched_notes = perfume.get(
            "matched_notes",
            [],
        )

        if not isinstance(
            matched_notes,
            (list, tuple, set),
        ):
            matched_notes = []

        matched_text = (
            ", ".join(
                str(term)
                for term in matched_notes
            )
            if matched_notes
            else "General profile similarity"
        )

        matched_text = html.escape(
            matched_text
        )

        ranking_score = float(
            perfume.get(
                "ranking_percentage",
                0,
            )
        )

        ranking_score_text = (
            f"{ranking_score:.1f}"
        )

        # ------------------------------------------
        # Explainability
        # ------------------------------------------
        perfume_dictionary = (
            perfume.to_dict()
        )

        explanation = generate_explanation(
            profile=profile,
            perfume=perfume_dictionary,
        )

        confidence = calculate_confidence(
            perfume_dictionary
        )

        confidence_label = html.escape(
            str(
                confidence.get(
                    "label",
                    "Limited evidence",
                )
            )
        )

        confidence_guidance = html.escape(
            str(
                confidence.get(
                    "guidance",
                    "Consider testing a sample "
                    "before purchasing.",
                )
            )
        )

        caution_text = html.escape(
            str(
                explanation.get(
                    "caution",
                    "No preference check is available.",
                )
            )
        )

        data_quality_text = html.escape(
            str(
                explanation.get(
                    "data_quality_note",
                    "No data-quality information is available.",
                )
            )
        )

        explanation_reasons = explanation.get(
            "reasons",
            [],
        )

        reason_items = "".join(
            (
                "<li>"
                + html.escape(str(reason))
                + "</li>"
            )
            for reason in explanation_reasons
        )

        if not reason_items:
            reason_items = (
                "<li>"
                "This result has general text similarity "
                "with the profile provided."
                "</li>"
            )

        # ------------------------------------------
        # Result card HTML
        # ------------------------------------------
        result_card_html = f"""
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
                Ranking score: {ranking_score_text}%
            </div>

            <div class="evidence-box">
                <div class="detail-label">
                    Recommendation evidence
                </div>

                <div class="detail-text">
                    <strong>{confidence_label}</strong>
                    <br>
                    {confidence_guidance}
                </div>
            </div>

            <div class="detail-section">
                <div class="detail-label">
                    Direct matches
                </div>

                <div class="detail-text">
                    {matched_text}
                </div>
            </div>

            <div class="detail-section">
                <div class="detail-label">
                    Why OLFYNZA selected this
                </div>

                <div class="detail-text">
                    <ul>
                        {reason_items}
                    </ul>
                </div>
            </div>

            <div class="detail-section">
                <div class="detail-label">
                    Preference check
                </div>

                <div class="detail-text">
                    {caution_text}
                </div>
            </div>

            <div class="data-note">
                <div class="detail-label">
                    Data transparency
                </div>

                <div class="detail-text">
                    {data_quality_text}
                </div>
            </div>

            <div class="detail-section">
                <div class="detail-label">
                    Fragrance notes
                </div>

                <div class="detail-text">
                    {notes_text}
                </div>
            </div>
        </div>
        """

        st.html(
            result_card_html
        )
                # ------------------------------------------
        # Recommendation feedback form
        # ------------------------------------------
        st.html(
            """
            <div class="feedback-heading">
                Help OLFYNZA improve this recommendation
            </div>

            <div class="feedback-help">
                Select the response that best describes
                this result. An optional short comment may
                also be added.
            </div>
            """
        )

        feedback_form_key = (
            f"feedback_form_"
            f"{perfume.get('perfume_id', position)}_"
            f"{position}"
        )

        feedback_type_key = (
            f"feedback_type_"
            f"{perfume.get('perfume_id', position)}_"
            f"{position}"
        )

        feedback_comment_key = (
            f"feedback_comment_"
            f"{perfume.get('perfume_id', position)}_"
            f"{position}"
        )

        with st.form(
            key=feedback_form_key,
            clear_on_submit=True,
        ):
            selected_feedback_type = st.selectbox(
                "How useful was this recommendation?",
                options=FEEDBACK_OPTIONS,
                index=None,
                placeholder="Select one feedback option",
                key=feedback_type_key,
            )

            feedback_comment = st.text_area(
                "Optional comment",
                placeholder=(
                    "Add a short comment without including "
                    "personal or confidential information."
                ),
                max_chars=500,
                key=feedback_comment_key,
            )

            st.html(
                """
                <div class="feedback-privacy">
                    Feedback is stored using an anonymous
                    session identifier. Do not include names,
                    email addresses, phone numbers or other
                    personal information in the comment.
                </div>
                """
            )

            submit_feedback = st.form_submit_button(
                "Submit Anonymous Feedback",
                use_container_width=True,
            )

        if submit_feedback:
            if selected_feedback_type is None:
                st.warning(
                    "Please select a feedback option "
                    "before submitting."
                )

            else:
                feedback_result = save_feedback(
                    perfume=perfume_dictionary,
                    feedback_type=selected_feedback_type,
                    session_id=(
                        st.session_state
                        .feedback_session_id
                    ),
                    profile=profile,
                    comment=feedback_comment,
                    recommendation_position=position,
                )

                if feedback_result["success"]:
                    st.success(
                        feedback_result["message"]
                    )

                elif feedback_result["duplicate"]:
                    st.info(
                        feedback_result["message"]
                    )

                else:
                    st.error(
                        feedback_result["message"]
                    )


# --------------------------------------------------
# Ranking disclaimer
# --------------------------------------------------
st.html(
    """
    <div class="page-caption">
        The ranking score combines text similarities.
        It is not the probability that a user will like
        a fragrance. Sampling is recommended before making
        a full-bottle purchase.
    </div>
    """
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

edit_column, home_column = st.columns(
    2,
    gap="medium",
)

with edit_column:
    if st.button(
        "← Edit My Profile",
        use_container_width=True,
    ):
        st.session_state.quiz_step = 1

        st.switch_page(
            "pages/1_Scent_Profile.py"
        )

with home_column:
    if st.button(
        "Return Home",
        use_container_width=True,
    ):
        st.switch_page(
            "app.py"
        )