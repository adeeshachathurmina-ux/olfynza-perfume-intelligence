import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="OLFYNZA",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# Custom design
# --------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(120, 74, 142, 0.20),
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
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        .brand-badge {
            display: inline-block;
            padding: 0.45rem 0.9rem;
            border: 1px solid rgba(212, 175, 106, 0.55);
            border-radius: 999px;
            color: #e8c987;
            background: rgba(212, 175, 106, 0.08);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12rem;
        }

        .hero-title {
            color: #ffffff;
            font-size: clamp(3.4rem, 8vw, 6.3rem);
            line-height: 0.95;
            font-weight: 850;
            letter-spacing: 0.18rem;
            margin-top: 1.4rem;
            margin-bottom: 1rem;
        }

        .hero-tagline {
            color: #e4c47e;
            font-size: clamp(1.25rem, 2.6vw, 2rem);
            font-weight: 650;
            margin-bottom: 1.1rem;
        }

        .hero-description {
            color: #d9cedf;
            font-size: 1.08rem;
            line-height: 1.8;
            max-width: 720px;
        }

        .feature-card {
            min-height: 180px;
            padding: 1.45rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.065);
            backdrop-filter: blur(12px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.18);
        }

        .feature-icon {
            font-size: 1.7rem;
            margin-bottom: 0.6rem;
        }

        .feature-title {
            color: #ffffff;
            font-size: 1.08rem;
            font-weight: 750;
            margin-bottom: 0.5rem;
        }

        .feature-text {
            color: #cfc2d7;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .trust-line {
            color: #bcaec5;
            font-size: 0.9rem;
            margin-top: 1rem;
        }

        div.stButton > button {
            width: 100%;
            min-height: 3.25rem;
            border: none;
            border-radius: 14px;
            color: #211427;
            background: linear-gradient(90deg, #d4af6a, #efd79d);
            font-size: 1rem;
            font-weight: 800;
        }

        div.stButton > button:hover {
            color: #211427;
            border: none;
            background: linear-gradient(90deg, #e0bd75, #f7e3ad);
            transform: translateY(-1px);
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Hero section
# --------------------------------------------------
left_column, right_column = st.columns([1.55, 0.45], gap="large")

with left_column:
    st.markdown(
        '<div class="brand-badge">PERFUME INTELLIGENCE PLATFORM</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title">OLFYNZA</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-tagline">'
        'Find Your Scent. Know Why It Fits.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-description">
            Discover fragrances based on your scent preferences,
            occasion, environment and budget. OLFYNZA does more
            than suggest a perfume. It clearly explains the main
            reasons behind every match.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    button_column, empty_column = st.columns([0.42, 0.58])

    with button_column:
        start_button = st.button(
            "Create My Scent Profile  →",
            use_container_width=True
        )

    st.markdown(
        """
        <div class="trust-line">
            ✓ Understandable results &nbsp;&nbsp;
            ✓ Budget-aware choices &nbsp;&nbsp;
            ✓ Honest confidence guidance
        </div>
        """,
        unsafe_allow_html=True
    )

with right_column:
    st.write("")
    st.write("")
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">✦</div>
            <div class="feature-title">Personal to You</div>
            <div class="feature-text">
                Recommendations begin with the preferences and
                context you choose, not a one-size-fits-all list.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Feature section
# --------------------------------------------------
st.write("")
st.write("")

first, second, third = st.columns(3, gap="large")

with first:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🌿</div>
            <div class="feature-title">Preference Matching</div>
            <div class="feature-text">
                Match fragrance families and notes with your
                personal likes, dislikes and preferred strength.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with second:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Clear Explanations</div>
            <div class="feature-text">
                Understand which preferences influenced each
                result and where a possible mismatch may exist.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with third:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Smarter Value</div>
            <div class="feature-text">
                Consider budget fit and explore similar options
                before committing to a full bottle.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Temporary button action
# --------------------------------------------------
if start_button:
    st.switch_page("pages/1_Scent_Profile.py")