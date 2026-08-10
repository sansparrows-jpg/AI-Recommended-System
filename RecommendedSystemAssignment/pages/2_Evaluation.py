import pandas as pd
import streamlit as st

from evaluation.dashboard import get_evaluation_dashboard


st.set_page_config(
    page_title="Evaluation",
    page_icon="chart",
    layout="wide",
)


def metric_card(label, value):
    with st.container(border=True):
        st.metric(label, value)


dashboard = get_evaluation_dashboard()
content = dashboard["content"]
collaborative = dashboard["collaborative"]
hybrid = dashboard["hybrid"]

st.title("Recommendation system evaluation", anchor=False)
st.caption(
    "Precision, recall, F1 score, similarity score, and accuracy are calculated across the three recommendation modules."
)

st.subheader("Content-Based Filtering")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Precision", content["precision"])
with col2:
    metric_card("Recall", content["recall"])
with col3:
    metric_card("F1 score", content["f1"])
col1, col2 = st.columns(2)
with col1:
    metric_card("Similarity", content["similarity"])
with col2:
    metric_card("Accuracy", content["accuracy"])

st.space("small")
st.subheader("Collaborative Filtering")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Precision", collaborative["precision"])
with col2:
    metric_card("Recall", collaborative["recall"])
with col3:
    metric_card("F1 score", collaborative["f1"])
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Similarity", collaborative["similarity"])
with col2:
    metric_card("Accuracy", collaborative["accuracy"])
with col3:
    metric_card("RMSE", collaborative["rmse"])

st.space("small")
st.subheader("Hybrid Recommendation")
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Precision", hybrid["precision"])
with col2:
    metric_card("Recall", hybrid["recall"])
with col3:
    metric_card("F1 score", hybrid["f1"])
col1, col2 = st.columns(2)
with col1:
    metric_card("Similarity", hybrid["similarity"])
with col2:
    metric_card("Accuracy", hybrid["accuracy"])

st.space("small")
st.subheader("Performance comparison")

comparison = pd.DataFrame(
    {
        "Algorithm": [
            "Content-Based",
            "Collaborative",
            "Hybrid",
        ],
        "Precision": [
            content["precision"],
            collaborative["precision"],
            hybrid["precision"],
        ],
        "Recall": [
            content["recall"],
            collaborative["recall"],
            hybrid["recall"],
        ],
        "F1 score": [
            content["f1"],
            collaborative["f1"],
            hybrid["f1"],
        ],
        "Similarity": [
            content["similarity"],
            collaborative["similarity"],
            hybrid["similarity"],
        ],
        "Accuracy": [
            content["accuracy"],
            collaborative["accuracy"],
            hybrid["accuracy"],
        ],
        "RMSE": [
            "-",
            collaborative["rmse"],
            "-",
        ],
    }
)

st.dataframe(comparison, width="stretch", hide_index=True)

st.space("small")
st.subheader("Evaluation chart")

chart_data = comparison.set_index("Algorithm")[
    ["Precision", "Recall", "F1 score", "Similarity", "Accuracy"]
].astype(float)

st.bar_chart(chart_data)

st.space("small")
st.subheader("Best performing algorithm")

scores = {
    "Content-Based": content["accuracy"],
    "Collaborative": collaborative["accuracy"],
    "Hybrid": hybrid["accuracy"],
}
best_algorithm = max(scores, key=scores.get)

st.success(f"{best_algorithm} achieved the highest accuracy score.", icon=":material/check_circle:")
st.caption(
    "RMSE is shown only for Collaborative Filtering because it measures rating prediction error."
)
