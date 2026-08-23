import html

import pandas as pd
import plotly.express as px
import streamlit as st

from src.features.feedback_manager import (
    calculate_feedback_summary,
    load_feedback,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Feedback Insights | OLFYNZA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
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
            margin-bottom: 1.6rem;
        }

        .section-title {
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 1.7rem;
            margin-bottom: 0.7rem;
        }

        .section-description {
            color: #bfaec8;
            font-size: 0.94rem;
            line-height: 1.65;
            margin-bottom: 1rem;
        }

        .empty-box {
            padding: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 1.2rem;
            border: 1px solid rgba(212, 175, 106, 0.38);
            border-radius: 18px;
            background: rgba(212, 175, 106, 0.075);
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.13);
        }

        .empty-title {
            color: #ffffff;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        .empty-text {
            color: #d7cadf;
            font-size: 0.98rem;
            line-height: 1.75;
        }

        .information-box {
            padding: 1.3rem 1.4rem;
            margin-top: 1.3rem;
            margin-bottom: 1.2rem;
            border: 1px solid rgba(212, 175, 106, 0.35);
            border-radius: 18px;
            background: rgba(212, 175, 106, 0.065);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        }

        .information-title {
            color: #e4c47e;
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.8rem;
        }

        .information-text {
            color: #d7cadf;
            font-size: 0.95rem;
            line-height: 1.75;
        }

        .privacy-list {
            margin-top: 0.6rem;
            margin-bottom: 0;
            padding-left: 1.25rem;
        }

        .privacy-list li {
            margin-bottom: 0.4rem;
        }

        [data-testid="stMetric"] {
            padding: 1.1rem;
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
# Load feedback safely
# --------------------------------------------------
try:
    feedback_data = load_feedback()

    feedback_summary = calculate_feedback_summary(
        feedback_data
    )

except (
    OSError,
    ValueError,
    KeyError,
    pd.errors.ParserError,
) as error:
    st.error(
        "OLFYNZA could not load the feedback data. "
        f"Details: {error}"
    )
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------
st.html(
    """
    <div class="mini-brand">
        OLFYNZA · FEEDBACK INTELLIGENCE
    </div>
    """
)

st.html(
    """
    <div class="page-title">
        Recommendation feedback insights
    </div>
    """
)

st.html(
    """
    <div class="page-description">
        This dashboard summarises anonymous feedback submitted
        through the OLFYNZA recommendation cards. It helps
        evaluate whether recommendations are useful and
        identifies common user concerns.
    </div>
    """
)


# --------------------------------------------------
# Empty feedback state
# --------------------------------------------------
if feedback_data.empty:
    st.html(
        """
        <div class="empty-box">
            <div class="empty-title">
                No feedback has been submitted yet
            </div>

            <div class="empty-text">
                Complete the scent-profile quiz, open the
                recommendation page and submit anonymous
                feedback for one of the recommended perfumes.
                The feedback summary will then appear on this
                dashboard.
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="information-box">
            <div class="information-title">
                Feedback privacy
            </div>

            <div class="information-text">
                OLFYNZA does not require a name, email address
                or phone number for recommendation feedback.

                <ul class="privacy-list">
                    <li>
                        Feedback uses an anonymous session ID.
                    </li>

                    <li>
                        Comments are limited to 500 characters.
                    </li>

                    <li>
                        Local feedback files are excluded from
                        the public GitHub repository.
                    </li>

                    <li>
                        Users should not include personal or
                        confidential information in comments.
                    </li>
                </ul>
            </div>
        </div>
        """
    )

    st.write("")

    profile_column, home_column = st.columns(
        2,
        gap="medium",
    )

    with profile_column:
        if st.button(
            "Create My Scent Profile →",
            use_container_width=True,
        ):
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

    st.stop()


# --------------------------------------------------
# Feedback metrics
# --------------------------------------------------
total_feedback = feedback_summary[
    "total_feedback"
]

unique_perfumes = feedback_summary[
    "unique_perfumes"
]

unique_sessions = feedback_summary[
    "unique_sessions"
]

helpful_percentage = feedback_summary[
    "helpful_percentage"
]


first_metric, second_metric, third_metric, fourth_metric = (
    st.columns(4)
)

with first_metric:
    st.metric(
        label="Feedback Records",
        value=f"{total_feedback:,}",
    )

with second_metric:
    st.metric(
        label="Reviewed Perfumes",
        value=f"{unique_perfumes:,}",
    )

with third_metric:
    st.metric(
        label="Anonymous Sessions",
        value=f"{unique_sessions:,}",
    )

with fourth_metric:
    st.metric(
        label="Helpful Responses",
        value=f"{helpful_percentage:.1f}%",
    )


# --------------------------------------------------
# Feedback type distribution
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Feedback response distribution
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        This chart shows how frequently each feedback option
        has been submitted.
    </div>
    """
)

feedback_type_counts = feedback_summary[
    "feedback_type_counts"
]

if feedback_type_counts:
    feedback_chart_data = pd.DataFrame(
        feedback_type_counts
    ).rename(
        columns={
            "feedback_type": "Feedback Type",
            "count": "Number of Responses",
        }
    )

    feedback_chart = px.bar(
        feedback_chart_data.sort_values(
            "Number of Responses"
        ),
        x="Number of Responses",
        y="Feedback Type",
        orientation="h",
        color="Number of Responses",
        color_continuous_scale=[
            "#56366D",
            "#E4C47E",
        ],
    )

    feedback_chart.update_layout(
        height=460,
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

    feedback_chart.update_xaxes(
        title="Number of Responses",
        gridcolor="rgba(255,255,255,0.08)",
    )

    feedback_chart.update_yaxes(
        title="",
        gridcolor="rgba(255,255,255,0)",
    )

    st.plotly_chart(
        feedback_chart,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

else:
    st.info(
        "No feedback categories are available "
        "for charting."
    )


# --------------------------------------------------
# Most reviewed perfumes
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Most reviewed perfumes
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        This table lists perfumes that have received the
        largest number of feedback submissions.
    </div>
    """
)

most_reviewed_perfumes = feedback_summary[
    "most_reviewed_perfumes"
]

if most_reviewed_perfumes:
    reviewed_perfume_data = pd.DataFrame(
        most_reviewed_perfumes
    ).rename(
        columns={
            "perfume_id": "Perfume ID",
            "perfume_name": "Perfume Name",
            "brand": "Brand",
            "feedback_count": "Feedback Count",
        }
    )

    st.dataframe(
        reviewed_perfume_data[
            [
                "Perfume ID",
                "Perfume Name",
                "Brand",
                "Feedback Count",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "No reviewed-perfume summary is available."
    )


# --------------------------------------------------
# Feedback record preview
# --------------------------------------------------
st.html(
    """
    <div class="section-title">
        Anonymous feedback records
    </div>
    """
)

st.html(
    """
    <div class="section-description">
        The table displays non-comment feedback fields for
        local project evaluation. Free-text comments are not
        displayed on this dashboard.
    </div>
    """
)

preview_columns = [
    "submitted_at_utc",
    "perfume_name",
    "brand",
    "feedback_type",
    "ranking_score",
    "recommendation_position",
]

available_preview_columns = [
    column
    for column in preview_columns
    if column in feedback_data.columns
]

feedback_preview = (
    feedback_data[
        available_preview_columns
    ]
    .copy()
    .tail(100)
)

feedback_preview = feedback_preview.rename(
    columns={
        "submitted_at_utc": "Submitted At UTC",
        "perfume_name": "Perfume Name",
        "brand": "Brand",
        "feedback_type": "Feedback Type",
        "ranking_score": "Ranking Score",
        "recommendation_position": (
            "Recommendation Position"
        ),
    }
)

st.dataframe(
    feedback_preview,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Interpretation note
# --------------------------------------------------
st.html(
    f"""
    <div class="information-box">
        <div class="information-title">
            How to interpret these results
        </div>

        <div class="information-text">
            OLFYNZA currently contains
            <strong>{total_feedback:,}</strong>
            locally stored feedback record(s) from
            <strong>{unique_sessions:,}</strong>
            anonymous session(s).

            <br><br>

            The helpful-response percentage divides responses
            labelled <strong>Helpful</strong> by all submitted
            feedback records. It is not a scientifically
            validated model-accuracy score.

            <br><br>

            Feedback totals may include different feedback
            categories for different perfumes. Larger and more
            varied feedback data would be required before
            drawing broad conclusions about recommendation
            quality.
        </div>
    </div>
    """
)


# --------------------------------------------------
# Privacy note
# --------------------------------------------------
st.html(
    """
    <div class="information-box">
        <div class="information-title">
            Privacy and storage
        </div>

        <div class="information-text">
            Feedback is stored locally with an anonymous
            session identifier. The system does not request a
            name, email address or phone number.

            <br><br>

            The feedback CSV file is excluded from the public
            GitHub repository through the project
            <strong>.gitignore</strong> configuration.
        </div>
    </div>
    """
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.write("")

recommendation_column, home_column = st.columns(
    2,
    gap="medium",
)

with recommendation_column:
    if st.button(
        "← View Recommendations",
        use_container_width=True,
    ):
        if st.session_state.get(
            "scent_profile"
        ):
            st.switch_page(
                "pages/2_Recommendations.py"
            )

        else:
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