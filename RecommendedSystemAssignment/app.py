# AI Music Recommendation System
# Streamlit Main Application

import pandas as pd
import streamlit as st

from models.preprocessing import preprocess_data
from models.user_data import load_user_matrix


st.set_page_config(
    page_title="SoundScope",
    page_icon="music",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(show_spinner=False)
def get_song_options():
    songs = preprocess_data()
    search_songs = (
        songs[
            [
                "track_name",
                "artists",
                "track_genre",
                "mood",
            ]
        ]
        .drop_duplicates(subset="track_name")
        .sort_values("track_name")
        .reset_index(drop=True)
    )
    search_songs["search_text"] = (
        search_songs["track_name"].astype(str)
        + " "
        + search_songs["artists"].astype(str)
        + " "
        + search_songs["track_genre"].astype(str)
        + " "
        + search_songs["mood"].astype(str)
    ).str.casefold()
    search_songs["search_fold"] = search_songs["search_text"].map(fold_search_text)
    return songs, search_songs


@st.cache_data(show_spinner=False)
def get_user_count():
    return len(load_user_matrix().index)


def render_top_10(final_results):
    st.subheader("Top 10 recommended songs")
    st.caption(
        "Final ranking generated from the best 3 results in each module, then sorted from highest to lowest score."
    )

    if not final_results:
        st.info("No final recommendation available yet.")
        return

    top_10 = (
        pd.DataFrame(final_results)
        .sort_values("final_score", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_10["rank"] = top_10.index + 1
    preferred_columns = [
        "rank",
        "track_name",
        "artist",
        "genre",
        "mood",
        "popularity",
        "final_score",
    ]
    visible_columns = [column for column in preferred_columns if column in top_10.columns]
    st.dataframe(top_10[visible_columns], width="stretch", hide_index=True)


def fold_search_text(text):
    return "".join(
        character
        for character in str(text).casefold()
        if character.isalnum() and character not in "aeiou"
    )


def format_song_option(song):
    return (
        f"{song['track_name']} - {song['artists']} · "
        f"{song['track_genre']} · {song['mood']}"
    )


def filter_song_options(query, search_songs, limit=40):
    query = query.strip().casefold()

    if not query:
        return search_songs.head(limit).to_dict("records")

    track_starts = search_songs["track_name"].astype(str).str.casefold().str.startswith(query)
    artist_starts = search_songs["artists"].astype(str).str.casefold().str.startswith(query)
    contains = search_songs["search_text"].str.contains(query, regex=False)
    folded_contains = search_songs["search_fold"].str.contains(
        fold_search_text(query),
        regex=False,
    )

    ranked_matches = pd.concat(
        [
            search_songs[track_starts],
            search_songs[artist_starts & ~track_starts],
            search_songs[contains & ~track_starts & ~artist_starts],
            search_songs[
                folded_contains
                & ~track_starts
                & ~artist_starts
                & ~contains
            ],
        ]
    ).drop_duplicates(subset="track_name")

    return ranked_matches.head(limit).to_dict("records")


songs, search_songs = get_song_options()

st.title("SoundScope", anchor=False)
st.caption(
    "AI-powered music recommendations with Content-Based, Collaborative, and Hybrid ranking."
)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric("Tracks", f"{len(songs):,}")

with col2:
    with st.container(border=True):
        st.metric("Users", f"{get_user_count():,}")

with col3:
    with st.container(border=True):
        st.metric("Models", 3)

st.space("small")
st.subheader("Discover music")

song_query = st.text_input(
    "Search songs, artists, categories, or emotions",
    placeholder="Try The Weeknd, pop, acoustic, Happy, or Perfect",
    key="song_search_query",
)
filtered_song_options = filter_song_options(song_query, search_songs)

with st.container(border=True):
    with st.form("recommendation_form", border=False):
        if filtered_song_options:
            selected_song = st.selectbox(
                "Select a matching song",
                filtered_song_options,
                format_func=format_song_option,
                key="selected_song_option",
            )
            song_name = selected_song["track_name"]
            st.caption(f"Showing {len(filtered_song_options)} matching songs.")
        else:
            song_name = ""
            st.warning("No matching song found. Try another keyword.", icon=":material/search_off:")

        user_id = st.text_input("User ID", placeholder="Example: User001")
        generate = st.form_submit_button(
            "Generate recommendations",
            icon=":material/headphones:",
            width="stretch",
        )

st.caption(
    "Enter a song and a user ID to generate recommendations using all three modules."
)

if generate:
    with st.spinner("Generating recommendations..."):
        from models.collaborative import recommend_for_user
        from models.content_based import recommend_song
        from models.hybrid import hybrid_recommend
        from models.ranking import generate_final_recommendations

        content_results = recommend_song(song_name) if song_name else []
        collaborative_results = recommend_for_user(user_id) if user_id else []
        hybrid_results = hybrid_recommend(song_name, user_id if user_id else None) if song_name else []

        final_results = generate_final_recommendations(
            content_results,
            collaborative_results,
            hybrid_results,
        )

    st.session_state["selected_song"] = song_name
    st.session_state["selected_user"] = user_id
    st.session_state["content_results"] = content_results
    st.session_state["collaborative_results"] = collaborative_results
    st.session_state["hybrid_results"] = hybrid_results
    st.session_state["final_results"] = final_results

    st.success("Recommendations generated successfully.")

final_results = st.session_state.get("final_results", [])
if final_results:
    st.space("small")
    render_top_10(final_results)
    st.caption("Open the Results page from the sidebar to compare all three recommendation methods.")
