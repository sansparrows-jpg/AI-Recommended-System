from sklearn.metrics.pairwise import cosine_similarity

from models.similarity import prepare_similarity

# Load everything once when the program starts
songs, text_matrix, audio_matrix = prepare_similarity()

# Song lookup without mutating the cached dataframe.
song_lookup = {
    str(track_name).casefold(): index
    for index, track_name in songs["track_name"].items()
}

def recommend_song(song_name):

    # Convert user input to lowercase
    song_key = str(song_name).strip().casefold()

    # Check if the song exist 
    if song_key not in song_lookup:
        return []
    
    # Get selected song index
    song_index = song_lookup[song_key]

    # Calculate Text Similarity
    text_scores = cosine_similarity(
        text_matrix[song_index],
        text_matrix
    ).flatten()

    # Calculate Audio Similarity
    audio_scores = cosine_similarity(
        audio_matrix[song_index].reshape(1, -1),
        audio_matrix
    ).flatten()

    # Final Weighted Similarity
    final_scores = (
        0.6 * text_scores +
        0.4 * audio_scores
    )

    # Pair song index with similarity score 
    similarity_scores = list(enumerate(final_scores))

    # Sort by similarity
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Skip the selected song itself
    similarity_scores = similarity_scores[1:11]

    recommendations = []
    recommended_tracks = set()

    # Build recommendation list
    for index, score in similarity_scores:

        track_name = songs.iloc[index]["track_name"]

        # Skip duplicate track names
        if track_name in recommended_tracks:
            continue

        recommended_tracks.add(track_name)

        recommendations.append({

            "track_name": track_name,

            "artist": songs.iloc[index]["artists"],

            "genre": songs.iloc[index]["track_genre"],

            "mood": songs.iloc[index]["mood"],

            "popularity": int(songs.iloc[index]["popularity"]),

            "similarity": round(float(score), 3)
        })

        # Stop after 10 unqiue songs 
        if len(recommendations) == 10:
            break

    return recommendations
