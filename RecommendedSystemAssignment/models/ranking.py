# Score Comparison % Ranking Module
# This module combines the recommendation
# results term:
# 1. Content-Based Filtering
# 2. Collaborative Filtering 
# 3. Hybrid Recommendation

# Ranking Factors:
# - Similarity Score
# - Predicted Rating 
# - Popularity
# - Dynamic Weight
import streamlit as st

@st.cache_data
def generate_final_recommendations(

    content_results,

    collaborative_results,

    hybrid_results,

    top_n=10   
):

    final_scores = {}

    # Dynamic Weight 
    if len(collaborative_results) == 0:
        weights = {
            "content": 0.60,
            "collaborative": 0.00,
            "hybrid": 0.25,
            "popularity": 0.15
        }

    elif len(collaborative_results) < 5:
        weights = {
            "content": 0.35,
            "collaborative": 0.15,
            "hybrid": 0.35,
            "popularity": 0.15
        }

    else: 
        weights = {
            "content": 0.25,
            "collaborative": 0.25,
            "hybrid": 0.35,
            "popularity": 0.15
        }

    # Content-Based Weight (30%)
    for song in content_results:

        track = song["track_name"]

        similarity = song.get("similarity", 0)

        popularity = song.get("popularity", 0) / 100

        final_scores[track] = {

            "track_name": track,

            "artist": song["artist"],

            "genre": song["genre"],

            "mood": song["mood"],

            "popularity": song.get("popularity", 0),

            "final_score": 
                similarity * weights["content"] +
                popularity * weights["popularity"]
        }

    # Collaborative Weight (30%)

    for song in collaborative_results:

        track = song["track_name"]

        rating = song.get("rating", 0) / 5

        popularity = song.get("popularity", 0) /100

        if track in final_scores:

            final_scores[track]["final_score"] += (
                rating * weights["collaborative"]
            )

        else:

            final_scores[track] = {

                "track_name": track,

                "artist": song["artist"],

                "genre": song["genre"],

                "mood": song["mood"],

                "popularity": song.get("popularity", 0),

                "final_score": 
                    rating * weights["collaborative"] +
                    popularity * weights["popularity"]

            }

    # Hybrid Weight (40%)

    for song in hybrid_results:

        track = song["track_name"]

        hybrid_score = song.get("score", 0)

        popularity = song.get("popularity", 0) / 100

        if track in final_scores:

            final_scores[track]["final_score"] += ( 
                hybrid_score * weights["hybrid"]
            )
        else:

            final_scores[track] = {

                "track_name": track,

                "artist": song["artist"],

                "genre": song["genre"],

                "mood": song["mood"],

                "popularity": song.get("popularity", 0),

                "final_score": 
                    hybrid_score * weights["hybrid"] +
                    popularity * weights["popularity"]

            }

    # Ranking
    # Convert Dictionary to List

    ranked_songs = list(final_scores.values())

    # Sort by Final Score

    ranked_songs.sort(

        key=lambda x: x["final_score"],

        reverse=True
    )

    # Add ranking position 
    for index, song in enumerate(ranked_songs, start=1):

        song["rank"] = index

        song["final_score"] = round(
            song["final_score"],
            3
        )

    return ranked_songs[:top_n]
# Test

if __name__ == "__main__":

    print("Ranking module loaded successfully.")