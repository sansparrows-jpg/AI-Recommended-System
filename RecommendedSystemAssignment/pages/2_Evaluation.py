import altair as alt
import pandas as pd
import streamlit as st

from evaluation.dashboard import get_evaluation_dashboard


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Evaluation",
    page_icon="📊",
    layout="wide",
)


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

evaluation_users = dashboard.get(
    "evaluation_users",
    [],
)

user_count = len(evaluation_users)


# =========================================================
# HELPER - HOLD-OUT METRICS
# =========================================================

def show_metric_row(results):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Precision@10",
        f"{results.get('precision', 0):.3f}",
    )

    col2.metric(
        "Recall@10",
        f"{results.get('recall', 0):.3f}",
    )

    col3.metric(
        "F1 Score",
        f"{results.get('f1', 0):.3f}",
    )

    col4.metric(
        "Hit Rate@10",
        f"{results.get('hit_rate', 0):.3f}",
    )


# =========================================================
# HEADER
# =========================================================

st.title(
    "Recommendation System Evaluation",
    anchor=False,
)

st.caption(
    "SoundScope evaluates each recommendation approach "
    "using evaluation methods suitable for its purpose."
)


# =========================================================
# EVALUATION METHODS
# =========================================================

st.subheader(
    "Evaluation Methods",
    anchor=False,
)

col1, col2 = st.columns(2)


# =========================================================
# CONTENT-BASED EVALUATION METHOD
# =========================================================

with col1:

    with st.container(border=True):

        st.markdown(
            "### Content-Based Evaluation"
        )

        st.write(
            "Content-Based Filtering is evaluated using "
            "the average similarity score of its Top 10 "
            "recommended songs."
        )

        st.metric(
            "Evaluation Metric",
            "Similarity Score",
        )

        st.caption(
            "A higher score indicates that the recommended "
            "songs are more similar to the selected seed song."
        )


# =========================================================
# HOLD-OUT EVALUATION METHOD
# =========================================================

with col2:

    with st.container(border=True):

        st.markdown(
            "### Real-User Hold-Out Evaluation"
        )

        col_a, col_b, col_c = st.columns(3)

        col_a.metric(
            "Users",
            user_count,
        )

        col_b.metric(
            "Size",
            "Top 10",
        )

        col_c.metric(
            "Relevant",
            "4 - 5",
        )

        st.write(
            "Songs that users rated 4 or 5 are temporarily "
            "hidden. Collaborative and Hybrid recommendations "
            "are tested on whether they can recover these songs."
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
    anchor=False,
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

    st.metric(
        "Average Similarity Score",
        f"{content.get('similarity', 0):.3f}",
    )

    st.caption(
        "Higher values indicate that the Top 10 "
        "recommended songs are more similar to "
        "the selected seed songs."
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

    rmse_display = (
        f"{rmse_value:.3f}"
        if rmse_value is not None
        else "N/A"
    )

    st.metric(
        "RMSE",
        rmse_display,
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
    anchor=False,
)

st.caption(
    "Collaborative and Hybrid are compared using "
    "the same real-user hold-out evaluation."
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
    hide_index=True,
)


# =========================================================
# EVALUATION CHART
# =========================================================

st.subheader(
    "Evaluation Chart",
    anchor=False,
)

chart_data = comparison.melt(
    id_vars="Algorithm",
    var_name="Metric",
    value_name="Score",
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
            ),
        ),

        xOffset="Metric:N",

        y=alt.Y(
            "Score:Q",
            title="Score",
            scale=alt.Scale(
                domain=[0, 1]
            ),
        ),

        color=alt.Color(
            "Metric:N",
            title="Evaluation Metric",
        ),

        tooltip=[
            alt.Tooltip(
                "Algorithm:N",
                title="Algorithm",
            ),

            alt.Tooltip(
                "Metric:N",
                title="Metric",
            ),

            alt.Tooltip(
                "Score:Q",
                title="Score",
                format=".3f",
            ),
        ],
    )
)

st.altair_chart(
    chart,
    width="stretch",
)


# =========================================================
# BEST HOLD-OUT PERFORMANCE
# =========================================================

st.subheader(
    "Best Hold-Out Performance",
    anchor=False,
)

scores = {
    "Collaborative":
        collaborative.get("f1", 0),

    "Hybrid":
        hybrid.get("f1", 0),
}

best_score = max(
    scores.values()
)

best_algorithms = [
    algorithm
    for algorithm, score in scores.items()
    if score == best_score
]

if len(best_algorithms) == 1:

    st.success(
        f"{best_algorithms[0]} achieved the highest "
        f"F1 Score of {best_score:.3f} in the "
        f"hold-out evaluation.",
        icon=":material/check_circle:",
    )

else:

    names = " and ".join(
        best_algorithms
    )

    st.success(
        f"{names} achieved the same highest "
        f"F1 Score of {best_score:.3f}.",
        icon=":material/check_circle:",
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