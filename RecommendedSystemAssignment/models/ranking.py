import streamlit as st


MODULE_QUOTAS = {
    "content": 3,
    "collaborative": 3,
    "hybrid": 3,
}


def _module_score(song, module_name):
    if module_name == "content":
        return song.get("similarity", 0)

    if module_name == "collaborative":
        return song.get("rating", 0) / 5

    return song.get("score", 0)


def _add_candidate(final_scores, song, module_name):
    track = song["track_name"]
    score = _module_score(song, module_name)

    if track not in final_scores:
        final_scores[track] = {
            "track_name": track,
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "popularity": song.get("popularity", 0),
            "source_modules": [module_name],
            "score_total": score,
            "score_count": 1,
        }
        return

    if module_name not in final_scores[track]["source_modules"]:
        final_scores[track]["source_modules"].append(module_name)
        final_scores[track]["score_total"] += score
        final_scores[track]["score_count"] += 1


@st.cache_data
def generate_final_recommendations(

    content_results,

    collaborative_results,

    hybrid_results,

    top_n=10   
):

    final_scores = {}
    module_results = [
        ("content", content_results),
        ("collaborative", collaborative_results),
        ("hybrid", hybrid_results),
    ]

    for module_name, results in module_results:
        for song in results[:MODULE_QUOTAS[module_name]]:
            _add_candidate(final_scores, song, module_name)

    if len(final_scores) < top_n:
        for module_name, results in module_results:
            for song in results[MODULE_QUOTAS[module_name]:]:
                _add_candidate(final_scores, song, module_name)

                if len(final_scores) == top_n:
                    break

            if len(final_scores) == top_n:
                break

    ranked_songs = list(final_scores.values())

    for song in ranked_songs:
        song["final_score"] = (
            song["score_total"] / song["score_count"]
        )

    ranked_songs.sort(

        key=lambda x: (
            x["final_score"],
            x["score_count"],
            x["popularity"],
        ),

        reverse=True
    )

    # Add ranking position 
    for index, song in enumerate(ranked_songs, start=1):

        song["rank"] = index

        song["final_score"] = round(
            song["final_score"],
            3
        )

        del song["score_total"]
        del song["score_count"]

    return ranked_songs[:top_n]
# Test

if __name__ == "__main__":

    print("Ranking module loaded successfully.")
