import html

import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Scent Profile | OLFYNZA",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Session state
# --------------------------------------------------
if "quiz_step" not in st.session_state:
    st.session_state.quiz_step = 1

if "scent_profile" not in st.session_state:
    st.session_state.scent_profile = {}


# --------------------------------------------------
# Navigation functions
# --------------------------------------------------
def go_to_next_step():
    """Move to the next quiz step."""

    if st.session_state.quiz_step < 7:
        st.session_state.quiz_step += 1


def go_to_previous_step():
    """Move to the previous quiz step."""

    if st.session_state.quiz_step > 1:
        st.session_state.quiz_step -= 1


def reset_quiz():
    """Clear all profile answers and restart the quiz."""

    st.session_state.quiz_step = 1
    st.session_state.scent_profile = {}


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
            max-width: 920px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        .mini-brand {
            color: #e4c47e;
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.15rem;
            margin-bottom: 1.2rem;
        }

        .step-text {
            color: #c4b4cc;
            font-size: 0.9rem;
            font-weight: 650;
            margin-bottom: 0.4rem;
        }

        .question-title {
            color: #ffffff;
            font-size: clamp(1.9rem, 5vw, 2.5rem);
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.7rem;
        }

        .question-help {
            color: #cfc2d7;
            font-size: 1rem;
            line-height: 1.65;
            margin-bottom: 1.5rem;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
        }

        .summary-card {
            padding: 1.4rem;
            border: 1px solid rgba(255, 255, 255, 0.11);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.065);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
        }

        .summary-label {
            color: #e4c47e;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .summary-value {
            color: #ffffff;
            font-size: 1.05rem;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }

        .completion-box {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(212, 175, 106, 0.4);
            border-radius: 20px;
            background: rgba(212, 175, 106, 0.08);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.14);
        }

        .completion-title {
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 0.55rem;
        }

        .completion-text {
            color: #d8cce0;
            font-size: 1rem;
            line-height: 1.65;
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

        [data-testid="stMultiSelect"],
        [data-testid="stSelectbox"],
        [data-testid="stRadio"] {
            background: rgba(255, 255, 255, 0.035);
            border-radius: 14px;
        }

        #MainMenu,
        footer,
        header {
            visibility: hidden;
        }

        @media (min-width: 800px) {
            .summary-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1.5rem;
            }

            .question-title {
                font-size: 1.9rem;
            }
        }
    </style>
    """
)


# --------------------------------------------------
# Common header
# --------------------------------------------------
st.html(
    """
    <div class="mini-brand">
        OLFYNZA · SCENT PROFILE
    </div>
    """
)

current_step = st.session_state.quiz_step

if current_step <= 6:
    st.html(
        f"""
        <div class="step-text">
            STEP {current_step} OF 6
        </div>
        """
    )

    st.progress(
        current_step / 6
    )

    st.write("")


# --------------------------------------------------
# Step 1: Preferred scent styles
# --------------------------------------------------
if current_step == 1:
    st.html(
        """
        <div class="question-title">
            Which scent styles do you enjoy?
        </div>

        <div class="question-help">
            Select all the fragrance styles that usually appeal
            to you. If you are unsure, choose the words that
            sound most pleasant.
        </div>
        """
    )

    scent_styles = [
        "Fresh",
        "Citrus",
        "Aquatic",
        "Floral",
        "Fruity",
        "Green",
        "Woody",
        "Spicy",
        "Sweet",
        "Vanilla",
        "Powdery",
        "Amber",
    ]

    selected_styles = st.multiselect(
        "Preferred scent styles",
        options=scent_styles,
        default=st.session_state.scent_profile.get(
            "preferred_styles",
            [],
        ),
        placeholder="Select your preferred scent styles",
        label_visibility="collapsed",
    )

    st.caption(
        "You can select several options. "
        "There is no correct or incorrect answer."
    )

    st.write("")

    home_column, space_column, next_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with home_column:
        if st.button(
            "← Home",
            use_container_width=True,
        ):
            st.switch_page(
                "app.py"
            )

    with next_column:
        if st.button(
            "Continue →",
            use_container_width=True,
        ):
            if not selected_styles:
                st.warning(
                    "Please select at least one scent style."
                )

            else:
                st.session_state.scent_profile[
                    "preferred_styles"
                ] = selected_styles

                go_to_next_step()
                st.rerun()


# --------------------------------------------------
# Step 2: Main occasion
# --------------------------------------------------
elif current_step == 2:
    st.html(
        """
        <div class="question-title">
            Where do you plan to wear it?
        </div>

        <div class="question-help">
            Choose the main occasion. OLFYNZA will use this
            context when building the recommendation query.
        </div>
        """
    )

    occasions = [
        "University",
        "Office",
        "Interview",
        "Daily use",
        "Wedding",
        "Evening event",
        "Party",
        "Special occasion",
    ]

    saved_occasion = (
        st.session_state
        .scent_profile
        .get("occasion")
    )

    occasion_index = (
        occasions.index(saved_occasion)
        if saved_occasion in occasions
        else None
    )

    selected_occasion = st.radio(
        "Main occasion",
        options=occasions,
        index=occasion_index,
        label_visibility="collapsed",
    )

    st.write("")

    back_column, space_column, next_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
        ):
            go_to_previous_step()
            st.rerun()

    with next_column:
        if st.button(
            "Continue →",
            use_container_width=True,
        ):
            if selected_occasion is None:
                st.warning(
                    "Please select your main occasion."
                )

            else:
                st.session_state.scent_profile[
                    "occasion"
                ] = selected_occasion

                go_to_next_step()
                st.rerun()


# --------------------------------------------------
# Step 3: Usage environment
# --------------------------------------------------
elif current_step == 3:
    st.html(
        """
        <div class="question-title">
            What environment will you use it in?
        </div>

        <div class="question-help">
            Select the environment that best represents where
            you expect to wear the fragrance most often.
        </div>
        """
    )

    environments = [
        "Hot and humid",
        "Rainy",
        "Cool",
        "Indoor air-conditioned",
        "Mostly outdoor",
        "A mixture of indoor and outdoor",
    ]

    saved_environment = (
        st.session_state
        .scent_profile
        .get("environment")
    )

    environment_index = (
        environments.index(saved_environment)
        if saved_environment in environments
        else None
    )

    selected_environment = st.radio(
        "Usage environment",
        options=environments,
        index=environment_index,
        label_visibility="collapsed",
    )

    st.write("")

    back_column, space_column, next_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
        ):
            go_to_previous_step()
            st.rerun()

    with next_column:
        if st.button(
            "Continue →",
            use_container_width=True,
        ):
            if selected_environment is None:
                st.warning(
                    "Please select a usage environment."
                )

            else:
                st.session_state.scent_profile[
                    "environment"
                ] = selected_environment

                go_to_next_step()
                st.rerun()


# --------------------------------------------------
# Step 4: Preferred strength
# --------------------------------------------------
elif current_step == 4:
    st.html(
        """
        <div class="question-title">
            How noticeable should the fragrance feel?
        </div>

        <div class="question-help">
            Choose your preferred scent strength. This describes
            a personal preference, not a guaranteed product
            performance level.
        </div>
        """
    )

    strengths = [
        "Light and subtle",
        "Moderate and balanced",
        "Strong and noticeable",
        "No strong preference",
    ]

    saved_strength = (
        st.session_state
        .scent_profile
        .get("strength")
    )

    strength_index = (
        strengths.index(saved_strength)
        if saved_strength in strengths
        else None
    )

    selected_strength = st.radio(
        "Preferred strength",
        options=strengths,
        index=strength_index,
        label_visibility="collapsed",
    )

    st.write("")

    back_column, space_column, next_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
        ):
            go_to_previous_step()
            st.rerun()

    with next_column:
        if st.button(
            "Continue →",
            use_container_width=True,
        ):
            if selected_strength is None:
                st.warning(
                    "Please select your preferred strength."
                )

            else:
                st.session_state.scent_profile[
                    "strength"
                ] = selected_strength

                go_to_next_step()
                st.rerun()


# --------------------------------------------------
# Step 5: Budget preference
# --------------------------------------------------
elif current_step == 5:
    st.html(
        """
        <div class="question-title">
            What is your preferred budget range?
        </div>

        <div class="question-help">
            Choose a broad range in Sri Lankan rupees. Prices
            can change, so this answer is stored as a general
            preference rather than a fixed price promise.
        </div>
        """
    )

    budget_ranges = [
        "Below LKR 5,000",
        "LKR 5,000 – 10,000",
        "LKR 10,000 – 20,000",
        "LKR 20,000 – 40,000",
        "Above LKR 40,000",
        "Show options from every range",
    ]

    saved_budget = (
        st.session_state
        .scent_profile
        .get("budget")
    )

    budget_index = (
        budget_ranges.index(saved_budget)
        if saved_budget in budget_ranges
        else None
    )

    selected_budget = st.radio(
        "Budget range",
        options=budget_ranges,
        index=budget_index,
        label_visibility="collapsed",
    )

    st.write("")

    back_column, space_column, next_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
        ):
            go_to_previous_step()
            st.rerun()

    with next_column:
        if st.button(
            "Continue →",
            use_container_width=True,
        ):
            if selected_budget is None:
                st.warning(
                    "Please select a preferred budget range."
                )

            else:
                st.session_state.scent_profile[
                    "budget"
                ] = selected_budget

                go_to_next_step()
                st.rerun()


# --------------------------------------------------
# Step 6: Notes to avoid
# --------------------------------------------------
elif current_step == 6:
    st.html(
        """
        <div class="question-title">
            Are there any scent notes you prefer to avoid?
        </div>

        <div class="question-help">
            This helps OLFYNZA reduce recommendations containing
            notes you usually dislike. You may leave this empty.
        </div>
        """
    )

    note_options = [
        "Vanilla",
        "Rose",
        "Jasmine",
        "Patchouli",
        "Musk",
        "Leather",
        "Tobacco",
        "Oud",
        "Cinnamon",
        "Coconut",
        "Caramel",
        "Strong florals",
        "Heavy spices",
        "Powdery notes",
    ]

    disliked_notes = st.multiselect(
        "Disliked scent notes",
        options=note_options,
        default=st.session_state.scent_profile.get(
            "disliked_notes",
            [],
        ),
        placeholder="Select notes to avoid, if any",
        label_visibility="collapsed",
    )

    st.caption(
        "This is a preference filter only. "
        "It does not provide medical or allergy advice."
    )

    st.write("")

    back_column, space_column, finish_column = st.columns(
        [0.24, 0.44, 0.32]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
        ):
            go_to_previous_step()
            st.rerun()

    with finish_column:
        if st.button(
            "Create My Profile",
            use_container_width=True,
        ):
            st.session_state.scent_profile[
                "disliked_notes"
            ] = disliked_notes

            go_to_next_step()
            st.rerun()


# --------------------------------------------------
# Step 7: Profile summary
# --------------------------------------------------
elif current_step == 7:
    profile = st.session_state.scent_profile

    preferred_styles = ", ".join(
        profile.get(
            "preferred_styles",
            [],
        )
    )

    if not preferred_styles:
        preferred_styles = "Not selected"

    disliked_notes_list = profile.get(
        "disliked_notes",
        [],
    )

    disliked_notes_text = (
        ", ".join(disliked_notes_list)
        if disliked_notes_list
        else "No disliked notes selected"
    )

    occasion_text = str(
        profile.get(
            "occasion",
            "Not selected",
        )
    )

    environment_text = str(
        profile.get(
            "environment",
            "Not selected",
        )
    )

    strength_text = str(
        profile.get(
            "strength",
            "Not selected",
        )
    )

    budget_text = str(
        profile.get(
            "budget",
            "Not selected",
        )
    )

    preferred_styles_safe = html.escape(
        preferred_styles
    )

    occasion_safe = html.escape(
        occasion_text
    )

    environment_safe = html.escape(
        environment_text
    )

    strength_safe = html.escape(
        strength_text
    )

    budget_safe = html.escape(
        budget_text
    )

    disliked_notes_safe = html.escape(
        disliked_notes_text
    )

    st.html(
        """
        <div class="completion-box">
            <div class="completion-title">
                Your scent profile is ready ✦
            </div>

            <div class="completion-text">
                OLFYNZA has saved the preferences selected
                during this session. Review the profile before
                moving to the recommendation stage.
            </div>
        </div>
        """
    )

    st.html(
        f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">
                    Preferred scent styles
                </div>

                <div class="summary-value">
                    {preferred_styles_safe}
                </div>
            </div>

            <div class="summary-card">
                <div class="summary-label">
                    Main occasion
                </div>

                <div class="summary-value">
                    {occasion_safe}
                </div>
            </div>

            <div class="summary-card">
                <div class="summary-label">
                    Usage environment
                </div>

                <div class="summary-value">
                    {environment_safe}
                </div>
            </div>

            <div class="summary-card">
                <div class="summary-label">
                    Preferred strength
                </div>

                <div class="summary-value">
                    {strength_safe}
                </div>
            </div>

            <div class="summary-card">
                <div class="summary-label">
                    Budget preference
                </div>

                <div class="summary-value">
                    {budget_safe}
                </div>
            </div>

            <div class="summary-card">
                <div class="summary-label">
                    Notes to avoid
                </div>

                <div class="summary-value">
                    {disliked_notes_safe}
                </div>
            </div>
        </div>
        """
    )

    st.write("")

    edit_column, reset_column, continue_column = st.columns(
        [0.30, 0.30, 0.40]
    )

    with edit_column:
        if st.button(
            "← Edit Answers",
            use_container_width=True,
        ):
            st.session_state.quiz_step = 1
            st.rerun()

    with reset_column:
        if st.button(
            "Reset Profile",
            use_container_width=True,
        ):
            reset_quiz()
            st.rerun()

    with continue_column:
        if st.button(
            "Find My Matches →",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/2_Recommendations.py"
            )