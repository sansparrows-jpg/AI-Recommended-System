# Collaborative Filtering
# User-Based Cosine Similarity

import numpy as np

from models.user_similarity import calculate_user_similarity
from models.preprocessing import preprocess_data


# Load Data Once

user_matrix, similarity_matrix = calculate_user_similarity()


# User ID Lookup

user_id_lookup = {
    str(user_id).casefold(): user_id
    for user_id in user_matrix.index
}


# Song Metadata

song_metadata = (
    preprocess_data()
    .drop_duplicates(subset="track_name")
    .set_index("track_name")
)


# Recommendation Function

def recommend_for_user(user_id, top_n=10):

    # Check whether the user exists
    canonical_user_id = user_id_lookup.get(
        str(user_id).strip().casefold()
    )

    if canonical_user_id is None:
        return []

    user_id = canonical_user_id

    # Get user index
    user_index = user_matrix.index.get_loc(user_id)

    # Get similarity scores
    similarity_scores = similarity_matrix[user_index]

    # Sort users by similarity
    similar_users = np.argsort(similarity_scores)[::-1]

    recommendations = {}

    # Songs already rated by current user
    current_user_ratings = user_matrix.loc[user_id]

    rated_songs = current_user_ratings[
        current_user_ratings > 0
    ].index

    # Look through similar users
    for index in similar_users[1:]:

        similar_user = user_matrix.index[index]

        similar_user_ratings = user_matrix.loc[similar_user]

        for song in similar_user_ratings.index:

            rating = similar_user_ratings[song]

            if rating >= 4 and song not in rated_songs:

                if song not in recommendations:

                    recommendations[song] = rating

        if len(recommendations) >= top_n:
            break

    # Sort recommendations
    recommendations = sorted(

        recommendations.items(),

        key=lambda x: x[1],

        reverse=True

    )

    # Convert to dictionary format
    result = []

    for song_name, rating in recommendations[:top_n]:

        if song_name in song_metadata.index:

            metadata = song_metadata.loc[song_name]

            artist = metadata["artists"]
            genre = metadata["track_genre"]
            mood = metadata["mood"]
            popularity = int(metadata["popularity"])

        else:

            artist = "Unknown Artist"
            genre = "Unknown Genre"
            mood = "Unknown"
            popularity = 0

        result.append({

            "track_name": song_name,

            "artist": artist,

            "genre": genre,

            "mood": mood,

            "popularity": popularity,

            "rating": round(float(rating), 1)

        })

    return result


# Test

if __name__ == "__main__":

    user = "User001"

    recommendations = recommend_for_user(user)

    print()

    print("==============================")
    print("Collaborative Filtering")
    print("==============================")
    print("User:", user)
    print()

    for song in recommendations:

        print(song)