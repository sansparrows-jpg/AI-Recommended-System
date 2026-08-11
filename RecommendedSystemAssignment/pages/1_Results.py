import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Recommendation Results",
    page_icon="music",
    layout="wide",
)


def show_table(rows, columns=None):
    if not rows:
        st.info("No recommendations available.")
        return

    df = pd.DataFrame(rows)

    if columns:
        columns = [column for column in columns if column in df.columns]
        df = df[columns]

    st.dataframe(df, width="stretch", hide_index=True)


def show_final_table(rows):
    if not rows:
        st.info("No recommendations available.")
        return

    df = (
        pd.DataFrame(rows)
        .sort_values("final_score", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    df["rank"] = df.index + 1
    columns = [
        "rank",
        "track_name",
        "artist",
        "genre",
        "mood",
        "popularity",
        "final_score",
    ]
    st.dataframe(df[columns], width="stretch", hide_index=True)


st.title("Recommendation results", anchor=False)
st.caption(
    "Final ranking first, then the individual model outputs for comparison."
)

if "content_results" not in st.session_state:
    st.warning("No recommendation has been generated yet.")
    st.info("Please return to the Discover page and generate recommendations first.")
    st.stop()

selected_song = st.session_state.get("selected_song", "")
selected_user = st.session_state.get("selected_user", "")
content_results = st.session_state.get("content_results", [])
collaborative_results = st.session_state.get("collaborative_results", [])
hybrid_results = st.session_state.get("hybrid_results", [])
final_results = st.session_state.get("final_results", [])

with st.container(border=True):
    st.subheader("Input information")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Selected song", selected_song)

    with col2:
        st.metric("User ID", selected_user or "Not provided")

st.space("small")

with st.container(border=True):
    st.subheader("Recommendation summary")
    summary1, summary2, summary3 = st.columns(3)

    with summary1:
        st.metric("Content-Based", len(content_results))

    with summary2:
        st.metric("Collaborative", len(collaborative_results))

    with summary3:
        st.metric("Hybrid", len(hybrid_results))

st.space("small")

with st.container(border=True):
    st.subheader("Final Top 10 recommended songs")
    st.caption(
        "Final recommendation generated from the best 3 results in each module, then sorted from highest to lowest score."
    )
    show_final_table(final_results)

st.space("small")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("Content-Based")
        st.caption("Recommendations based on song features and similarity.")
        show_table(content_results)

with col2:
    with st.container(border=True):
        st.subheader("Collaborative")
        st.caption("Recommendations based on users with similar listening preferences.")
        show_table(collaborative_results)

with col3:
    with st.container(border=True):
        st.subheader("Hybrid")
        st.caption("Recommendations generated with 60% Content-Based and 40% Collaborative Filtering.")
        show_table(hybrid_results)
