import altair as alt
import pandas as pd
import streamlit as st

from evaluation.dashboard import get_evaluation_dashboard


# =========================================================
# PAGE CONFIGURATION
# =========================================================


# =========================================================
# LUXURY MUSIC APPLICATION UI
# =========================================================

def apply_luxury_ui():
    """
    Change only the Streamlit appearance.
    Recommendation logic, ratings, user data and algorithms stay unchanged.
    """

    st.markdown(
        """
        <style>
        :root {
            --bg: #080810;
            --panel: #151522;
            --panel-2: #1b1a2b;
            --purple: #8b5cf6;
            --purple-soft: #a78bfa;
            --gold: #d6b36a;
            --text: #f7f5ff;
            --muted: #9b98aa;
            --border: rgba(167, 139, 250, 0.18);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(139, 92, 246, 0.14), transparent 27%),
                radial-gradient(circle at 92% 12%, rgba(214, 179, 106, 0.08), transparent 25%),
                linear-gradient(135deg, #080810 0%, #0c0c16 45%, #11111d 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 4.25rem !important;
            padding-bottom: 2.5rem !important;
        }

        [data-testid="stHeader"] {
            background: rgba(8, 8, 16, 0.82);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(214, 179, 106, 0.10);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #121220 0%, #090910 100%);
            border-right: 1px solid rgba(214, 179, 106, 0.14);
        }

        [data-testid="stSidebar"] * {
            color: #f5f3ff;
        }

        h1 {
            font-weight: 850 !important;
            letter-spacing: -0.035em !important;
            background: linear-gradient(90deg, #ffffff, #d9ccff, #d6b36a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h2, h3, h4 {
            color: #f8f7ff !important;
            letter-spacing: -0.018em;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--muted) !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(
                145deg,
                rgba(27, 26, 43, 0.94),
                rgba(15, 15, 27, 0.94)
            );
            border: 1px solid var(--border) !important;
            border-radius: 18px !important;
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stMetric"] {
            background: linear-gradient(
                135deg,
                rgba(31, 29, 49, 0.96),
                rgba(17, 17, 30, 0.96)
            );
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
        }

        [data-testid="stMetricLabel"] {
            color: #aaa6b8 !important;
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            color: white !important;
            font-weight: 780 !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            min-height: 42px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: linear-gradient(135deg, #6e45d7, #8b5cf6);
            color: white;
            font-weight: 720;
            transition: 0.18s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(214, 179, 106, 0.50);
            background: linear-gradient(135deg, #8b5cf6, #ad7cf7);
            box-shadow: 0 10px 28px rgba(139, 92, 246, 0.28);
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background: rgba(24, 24, 40, 0.95) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }

        input {
            color: white !important;
        }

        input::placeholder {
            color: #777587 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 1.35rem;
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.09) !important;
            padding: 0 !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            color: #9694a5 !important;
            padding: 0.72rem 0.08rem !important;
            font-weight: 680;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #ddd1ff !important;
        }

        .stTabs [aria-selected="true"] {
            background: transparent !important;
            color: white !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            height: 3px !important;
            border-radius: 999px !important;
            background: linear-gradient(90deg, var(--purple), var(--gold)) !important;
        }

        [data-testid="stDataFrame"] {
            background: rgba(14, 14, 25, 0.93);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 13px;
            border: 1px solid rgba(167, 139, 250, 0.14);
        }

        details {
            background: rgba(20, 20, 34, 0.76) !important;
            border: 1px solid var(--border) !important;
            border-radius: 13px !important;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--purple), var(--gold));
        }

        hr {
            border-color: rgba(255, 255, 255, 0.08) !important;
        }

        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.03);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(90deg, #6e45d7, #d6b36a);
            border-radius: 999px;
        }

        @media (max-width: 800px) {
            .block-container {
                padding-top: 4rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="Evaluation",
    page_icon="📊",
    layout="wide",
)

# Apply the luxury music application appearance.
apply_luxury_ui()


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


# =========================================================
# LOAD EVALUATION RESULTS
# =========================================================

with st.spinner("Evaluating recommendation models..."):
    dashboard = get_evaluation_dashboard()

content = dashboard["content"]
collaborative = dashboard["collaborative"]
hybrid = dashboard["hybrid"]

evaluation_users = dashboard.get("evaluation_users", [])
user_count = len(evaluation_users)


# =========================================================
# HELPER - HOLD-OUT METRICS
# =========================================================

def show_metric_row(results):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Precision@10",
        f"{results.get('precision', 0):.3f}"
    )

    col2.metric(
        "Recall@10",
        f"{results.get('recall', 0):.3f}"
    )

    col3.metric(
        "F1 Score",
        f"{results.get('f1', 0):.3f}"
    )

    col4.metric(
        "Hit Rate@10",
        f"{results.get('hit_rate', 0):.3f}"
    )


# =========================================================
# HEADER
# =========================================================

st.title(
    "Recommendation System Evaluation",
    anchor=False
)

st.caption(
    "SoundScope evaluates each recommendation approach "
    "using evaluation methods suitable for its purpose."
)


# =========================================================
# TOP EVALUATION SUMMARY
# =========================================================

content_summary_col, evaluation_method_col = st.columns(
    [1, 1],
    vertical_alignment="top"
)


# =========================================================
# CONTENT-BASED EVALUATION SUMMARY
# =========================================================

with content_summary_col:

    st.subheader(
        "Content-Based Evaluation Summary",
        anchor=False
    )

    with st.container(border=True):

        st.metric(
            "Average Similarity Score",
            f"{content.get('similarity', 0):.3f}"
        )

        st.write(
            "The similarity score measures how closely the "
            "recommended songs match the selected seed song "
            "based on text and audio features."
        )

        st.info(
            "User questionnaire results can be added after "
            "5 to 10 users have evaluated the relevance of "
            "the Content-Based recommendations using the "
            "5-point Likert scale."
        )


# =========================================================
# EVALUATION METHOD
# =========================================================

with evaluation_method_col:

    st.subheader(
        "Evaluation Method",
        anchor=False
    )

    with st.container(border=True):

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Users Evaluated",
            user_count
        )

        col2.metric(
            "Recommendation Size",
            "Top 10"
        )

        col3.metric(
            "Relevant Rating",
            "4 - 5"
        )

        st.write(
            "Collaborative and Hybrid recommendations are "
            "evaluated using real-user hold-out testing. "
            "Songs that users rated 4 or 5 are temporarily "
            "hidden and used as relevant test songs."
        )

        st.write(
            "Content-Based Filtering is evaluated separately "
            "using the similarity of its recommendations and "
            "a user questionnaire because it recommends songs "
            "based on similarity to a selected seed song."
        )

        if evaluation_users:
            st.caption(
                "Evaluation users: "
                + ", ".join(evaluation_users)
            )


# =========================================================
# MODEL PERFORMANCE
# =========================================================

st.subheader(
    "Model Performance",
    anchor=False
)


# =========================================================
# CONTENT-BASED
# =========================================================

with st.container(border=True):

    st.markdown(
        "### Content-Based Filtering"
    )

    st.caption(
        "Uses TF-IDF text features and audio features "
        "with Cosine Similarity."
    )

    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # SIMILARITY SCORE
    # -----------------------------------------------------

    with col1:

        st.metric(
            "Average Similarity Score",
            f"{content.get('similarity', 0):.3f}"
        )

        st.caption(
            "Higher values indicate that the recommended "
            "songs are more similar to the selected song."
        )


    # -----------------------------------------------------
    # USER QUESTIONNAIRE
    # -----------------------------------------------------

    with col2:

        st.metric(
            "User Questionnaire",
            "5-Point Likert Scale"
        )

        st.caption(
            "Approximately 5 to 10 users will evaluate "
            "the relevance of the Content-Based "
            "recommendations."
        )


# =========================================================
# COLLABORATIVE
# =========================================================

with st.container(border=True):

    st.markdown(
        "### Collaborative Filtering"
    )

    st.caption(
        "Uses User-Based KNN and Item-Based KNN "
        "with Euclidean Distance."
    )

    show_metric_row(
        collaborative
    )

    st.divider()

    rmse_value = collaborative.get("rmse")

    if rmse_value is not None:
        rmse_display = f"{rmse_value:.3f}"
    else:
        rmse_display = "N/A"

    st.metric(
        "RMSE",
        rmse_display
    )

    st.caption(
        "Lower RMSE indicates better accuracy when "
        "predicting users' rating preferences."
    )


# =========================================================
# HYBRID
# =========================================================

with st.container(border=True):

    st.markdown(
        "### Hybrid Recommendation"
    )

    st.caption(
        "Uses 40% Content-Based allocation and "
        "60% Collaborative allocation. "
        "Final recommendations are ranked by Hybrid score."
    )

    show_metric_row(
        hybrid
    )


# =========================================================
# HOLD-OUT PERFORMANCE COMPARISON
# =========================================================

st.subheader(
    "Hold-Out Performance Comparison",
    anchor=False
)

st.caption(
    "Collaborative and Hybrid are compared using the "
    "same real-user hold-out evaluation."
)


comparison = pd.DataFrame({
    "Algorithm": [
        "Collaborative",
        "Hybrid",
    ],

    "Precision@10": [
        collaborative.get("precision", 0),
        hybrid.get("precision", 0),
    ],

    "Recall@10": [
        collaborative.get("recall", 0),
        hybrid.get("recall", 0),
    ],

    "F1 Score": [
        collaborative.get("f1", 0),
        hybrid.get("f1", 0),
    ],

    "Hit Rate@10": [
        collaborative.get("hit_rate", 0),
        hybrid.get("hit_rate", 0),
    ],
})


st.dataframe(
    comparison,
    width="stretch",
    hide_index=True
)


# =========================================================
# GROUPED EVALUATION CHART
# =========================================================

st.subheader(
    "Evaluation Chart",
    anchor=False
)


chart_data = comparison.melt(
    id_vars="Algorithm",
    var_name="Metric",
    value_name="Score"
)


chart = (
    alt.Chart(chart_data)

    .mark_bar()

    .encode(
        x=alt.X(
            "Algorithm:N",
            title="Recommendation Algorithm",
            axis=alt.Axis(
                labelAngle=0
            )
        ),

        xOffset="Metric:N",

        y=alt.Y(
            "Score:Q",
            title="Score",
            scale=alt.Scale(
                domain=[0, 1]
            )
        ),

        color=alt.Color(
            "Metric:N",
            title="Evaluation Metric"
        ),

        tooltip=[
            alt.Tooltip(
                "Algorithm:N",
                title="Algorithm"
            ),

            alt.Tooltip(
                "Metric:N",
                title="Metric"
            ),

            alt.Tooltip(
                "Score:Q",
                title="Score",
                format=".3f"
            ),
        ]
    )
)


st.altair_chart(
    chart,
    width="stretch"
)


# =========================================================
# BEST HOLD-OUT PERFORMANCE
# =========================================================

st.subheader(
    "Best Hold-Out Performance",
    anchor=False
)


scores = {
    "Collaborative": collaborative.get("f1", 0),
    "Hybrid": hybrid.get("f1", 0),
}


best_score = max(
    scores.values()
)


best_algorithms = [
    algorithm

    for algorithm, score
    in scores.items()

    if score == best_score
]


if len(best_algorithms) == 1:

    st.success(
        f"{best_algorithms[0]} achieved the highest "
        f"F1 Score of {best_score:.3f} in the "
        f"hold-out evaluation.",
        icon=":material/check_circle:"
    )

else:

    names = " and ".join(
        best_algorithms
    )

    st.success(
        f"{names} achieved the same highest "
        f"F1 Score of {best_score:.3f}.",
        icon=":material/check_circle:"
    )


# =========================================================
# METRIC EXPLANATIONS
# =========================================================

with st.expander(
    "What do the evaluation metrics mean?"
):

    st.markdown(
        """
**Similarity Score**  
Measures how similar the Content-Based recommendations
are to the selected seed song. Higher values indicate
greater similarity.

**User Questionnaire**  
Users rate the relevance of the recommendations using
a 5-point Likert scale, where a higher rating indicates
greater user satisfaction.

**Precision@10**  
Measures how many of the Top 10 recommendations are
relevant to the user.

**Recall@10**  
Measures how many of the relevant hidden songs were
successfully recovered in the Top 10 recommendations.

**F1 Score**  
Combines Precision and Recall into one performance score.

**Hit Rate@10**  
Measures whether at least one relevant hidden song
appears in the Top 10 recommendations.

**RMSE**  
Measures the difference between predicted ratings and
actual user ratings. Lower RMSE values indicate better
rating prediction accuracy.
        """
    )