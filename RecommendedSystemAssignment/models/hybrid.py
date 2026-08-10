# Hybrid Recommendation System
# Combines:
# 1. Content-Based Filtering
# 2. Collaborative Filtering

import streamlit as st

from models.content_based import recommend_song
from models.collaborative import recommend_for_user


@st.cache_data
def hybrid_recommend(song_name, user_id=None, top_n=10):
    """
    Generate Hybrid Recommendations.

    Parameters
    ----------
    song_name : str
        Song selected by the user.

    user_id : str, optional
        User ID for collaborative filtering.
        If omitted, only Content-Based recommendations are used.

    top_n : int
        Number of recommendations to return.
    """

    # ---------------------------------
    # Generate Recommendations
    # ---------------------------------

    content_results = recommend_song(song_name)

    if user_id:
        collaborative_results = recommend_for_user(user_id)
    else:
        collaborative_results = []

    # ---------------------------------
    # Combine Recommendation Scores
    # ---------------------------------

    hybrid_scores = {}

    # Content-Based Weight (60%)

    for song in content_results:

        hybrid_scores[song["track_name"]] = {

            "track_name": song["track_name"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "popularity": song.get("popularity", 0),

            "score": song["similarity"] * 0.6

        }

    # Collaborative Weight (40%)

    for song in collaborative_results:

        collaborative_score = song["rating"] / 5

        if song["track_name"] in hybrid_scores:

            hybrid_scores[song["track_name"]]["score"] += (
                collaborative_score * 0.4
            )

        else:

            hybrid_scores[song["track_name"]] = {

                "track_name": song["track_name"],
                "artist": song["artist"],
                "genre": song["genre"],
                "mood": song["mood"],
                "popularity": song.get("popularity", 0),

                "score": collaborative_score * 0.4

            }

    # ---------------------------------
    # Convert Dictionary to List
    # ---------------------------------

    final_results = list(hybrid_scores.values())

    # ---------------------------------
    # Sort by Hybrid Score
    # ---------------------------------

    final_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return final_results[:top_n]


# ---------------------------------
# Test
# ---------------------------------

if __name__ == "__main__":

    results = hybrid_recommend(
        "Perfect",
        "User001"
    )

    print("\n==============================")
    print("Hybrid Recommendation")
    print("==============================")

    for song in results:
        print(song)
