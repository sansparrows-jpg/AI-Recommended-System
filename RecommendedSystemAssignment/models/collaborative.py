# Collaborative Filtering using real user ratings.
# User-Based KNN + Item-Based KNN, K = 5.
# Euclidean Distance is converted to similarity.
# Final score = 50% User-Based + 50% Item-Based.

import math

import pandas as pd

from models.preprocessing import preprocess_data
from models.real_user_data import (
    load_real_user_matrix,
    load_song_metadata,
)
from models.ratings import get_rating_count


# Configuration values used by both KNN methods.

K_NEIGHBORS = 5
MIN_RECOMMEND_RATING = 4
MIN_USER_RATINGS = 10

USER_WEIGHT = 0.5
ITEM_WEIGHT = 0.5


# Build a lookup for Spotify popularity values.

spotify_songs = preprocess_data()

popularity_lookup = {}

for _, row in spotify_songs.iterrows():
    key = (
        str(row["track_name"]).strip().casefold(),
        str(row["artists"]).strip().casefold(),
    )

    # Same behaviour as before:
    # keep the first exact matching record.
    if key not in popularity_lookup:
        popularity_lookup[key] = int(
            row.get("popularity", 0)
        )


# Helper functions for IDs, similarity and song metadata.

def distance_to_similarity(distance):
    """Convert Euclidean Distance to similarity."""

    return 1 / (1 + distance)


def get_canonical_user_id(user_id, user_matrix):
    """Match User ID without case sensitivity."""

    requested = str(user_id).strip().casefold()

    for existing_user in user_matrix.index:
        if (
            str(existing_user)
            .strip()
            .casefold()
            == requested
        ):
            return existing_user

    return None


def get_song_popularity(track_name, artist):
    """Get popularity using track name + artist."""

    key = (
        str(track_name).strip().casefold(),
        str(artist).strip().casefold(),
    )

    return popularity_lookup.get(key, 0)


def find_song_key(track_name, artist):
    """Find rating song_key using track + artist."""

    metadata = load_song_metadata()

    if metadata.empty:
        return None

    track_key = str(track_name).strip().casefold()
    artist_key = str(artist).strip().casefold()

    matches = metadata[
        (
            metadata["track_name"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == track_key
        )
        &
        (
            metadata["artist"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == artist_key
        )
    ]

    if matches.empty:
        return None

    return matches.iloc[0]["song_key"]


def get_song_metadata(song_key, metadata):
    """Return metadata row for one song_key."""

    matches = metadata[
        metadata["song_key"] == song_key
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


def get_recommendation_source(
    user_knn_score,
    item_knn_score,
):
    """Show which KNN method supports the song."""

    user_score = float(user_knn_score or 0)
    item_score = float(item_knn_score or 0)

    if user_score > 0 and item_score > 0:
        return "Both"

    if user_score > 0:
        return "User-Based"

    if item_score > 0:
        return "Item-Based"

    return "None"


# User-Based KNN: compare users with common song ratings.
def calculate_user_distance(
    user_a,
    user_b,
    user_matrix,
):
    """
    Euclidean Distance between two users.

    Only songs rated by BOTH users are used.
    """

    if (
        user_a not in user_matrix.index
        or user_b not in user_matrix.index
    ):
        return None, 0

    ratings_a = user_matrix.loc[user_a]
    ratings_b = user_matrix.loc[user_b]

    common_mask = (
        ratings_a.notna()
        &
        ratings_b.notna()
    )

    common_songs = user_matrix.columns[
        common_mask
    ]

    if len(common_songs) == 0:
        return None, 0

    distance = math.sqrt(
        (
            (
                ratings_a[common_songs]
                -
                ratings_b[common_songs]
            )
            ** 2
        ).sum()
    )

    return float(distance), len(common_songs)


def find_nearest_users(
    user_id,
    k=K_NEIGHBORS,
):
    """Find K nearest users using Euclidean Distance."""

    user_matrix = load_real_user_matrix()

    if user_matrix.empty:
        return []

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return []

    neighbours = []

    for other_user in user_matrix.index:

        if other_user == user_id:
            continue

        distance, common_count = (
            calculate_user_distance(
                user_id,
                other_user,
                user_matrix,
            )
        )

        if distance is None:
            continue

        neighbours.append({
            "user_id": other_user,
            "distance": float(distance),
            "similarity": float(
                distance_to_similarity(distance)
            ),
            "common_ratings": common_count,
        })

    # Stable ranking:
    # lowest distance first.
    neighbours.sort(
        key=lambda user: (
            user["distance"],
            str(user["user_id"]),
        )
    )

    return neighbours[:k]


def user_based_recommendations(
    user_id,
    top_n=10,
    k=K_NEIGHBORS,
):
    """
    Recommend unseen songs liked by nearest users.

    Only ratings >= 4 are considered positive.
    """

    user_matrix = load_real_user_matrix()
    metadata = load_song_metadata()

    if user_matrix.empty or metadata.empty:
        return []

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return []

    neighbours = find_nearest_users(
        user_id,
        k,
    )

    if not neighbours:
        return []

    target_ratings = user_matrix.loc[user_id]

    rated_songs = set(
        target_ratings[
            target_ratings.notna()
        ].index
    )

    candidate_scores = {}

    for neighbour in neighbours:

        neighbour_ratings = user_matrix.loc[
            neighbour["user_id"]
        ]

        similarity = neighbour["similarity"]

        for song_key, rating in neighbour_ratings.items():

            if song_key in rated_songs:
                continue

            if pd.isna(rating):
                continue

            if rating < MIN_RECOMMEND_RATING:
                continue

            values = candidate_scores.setdefault(
                song_key,
                {
                    "weighted_score": 0.0,
                    "similarity_total": 0.0,
                    "neighbour_count": 0,
                },
            )

            normalized_rating = float(rating) / 5.0

            values["weighted_score"] += (
                similarity * normalized_rating
            )

            values["similarity_total"] += similarity
            values["neighbour_count"] += 1

    results = []

    for song_key, values in candidate_scores.items():

        if values["similarity_total"] <= 0:
            continue

        score = (
            values["weighted_score"]
            /
            values["similarity_total"]
        )

        song = get_song_metadata(
            song_key,
            metadata,
        )

        if song is None:
            continue

        results.append({
            "song_key": song_key,
            "track_name": song["track_name"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "user_knn_score": float(score),
            "neighbour_count":
                values["neighbour_count"],
        })

    results.sort(
        key=lambda song: (
            -song["user_knn_score"],
            str(song["track_name"]).casefold(),
            str(song["artist"]).casefold(),
        )
    )

    return results[:top_n]


# Item-Based KNN: compare songs using common user ratings.

def calculate_item_distance(
    song_a,
    song_b,
    user_matrix,
):
    """
    Euclidean Distance between two songs.

    Only users who rated BOTH songs are used.
    """

    if (
        song_a not in user_matrix.columns
        or song_b not in user_matrix.columns
    ):
        return None, 0

    ratings_a = user_matrix[song_a]
    ratings_b = user_matrix[song_b]

    common_mask = (
        ratings_a.notna()
        &
        ratings_b.notna()
    )

    common_users = user_matrix.index[
        common_mask
    ]

    if len(common_users) == 0:
        return None, 0

    distance = math.sqrt(
        (
            (
                ratings_a[common_users]
                -
                ratings_b[common_users]
            )
            ** 2
        ).sum()
    )

    return float(distance), len(common_users)


def item_based_recommendations(
    user_id,
    top_n=10,
    k=K_NEIGHBORS,
):
    """
    Recommend unseen songs similar to songs
    the target user previously rated 4 or 5.
    """

    user_matrix = load_real_user_matrix()
    metadata = load_song_metadata()

    if user_matrix.empty or metadata.empty:
        return []

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return []

    target_ratings = user_matrix.loc[user_id]

    liked_songs = target_ratings[
        target_ratings
        >=
        MIN_RECOMMEND_RATING
    ]

    if liked_songs.empty:
        return []

    unseen_songs = target_ratings[
        target_ratings.isna()
    ].index

    results = []

    for candidate_song in unseen_songs:

        similarities = []

        for liked_song, user_rating in liked_songs.items():

            distance, common_users = (
                calculate_item_distance(
                    candidate_song,
                    liked_song,
                    user_matrix,
                )
            )

            if distance is None:
                continue

            similarities.append({
                "similarity":
                    distance_to_similarity(distance),

                "rating":
                    float(user_rating),

                "common_users":
                    common_users,
            })

        if not similarities:
            continue

        similarities.sort(
            key=lambda item:
                item["similarity"],
            reverse=True,
        )

        nearest_items = similarities[:k]

        weighted_score = sum(
            item["similarity"]
            *
            (item["rating"] / 5.0)
            for item in nearest_items
        )

        similarity_total = sum(
            item["similarity"]
            for item in nearest_items
        )

        if similarity_total <= 0:
            continue

        score = (
            weighted_score
            /
            similarity_total
        )

        song = get_song_metadata(
            candidate_song,
            metadata,
        )

        if song is None:
            continue

        results.append({
            "song_key": candidate_song,
            "track_name": song["track_name"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "item_knn_score": float(score),
            "similar_items": len(nearest_items),
        })

    results.sort(
        key=lambda song: (
            -song["item_knn_score"],
            str(song["track_name"]).casefold(),
            str(song["artist"]).casefold(),
        )
    )

    return results[:top_n]


# Explain why two users are considered similar.

def get_user_similarity_details(
    user_id,
    neighbour_id,
):
    """Explain why two users are considered similar."""

    user_matrix = load_real_user_matrix()
    metadata = load_song_metadata()

    if user_matrix.empty:
        return None

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    neighbour_id = get_canonical_user_id(
        neighbour_id,
        user_matrix,
    )

    if user_id is None or neighbour_id is None:
        return None

    user_ratings = user_matrix.loc[user_id]
    neighbour_ratings = user_matrix.loc[
        neighbour_id
    ]

    common_mask = (
        user_ratings.notna()
        &
        neighbour_ratings.notna()
    )

    common_songs = user_matrix.columns[
        common_mask
    ]

    if len(common_songs) == 0:
        return None

    distance, common_count = (
        calculate_user_distance(
            user_id,
            neighbour_id,
            user_matrix,
        )
    )

    comparison = []
    exact_matches = 0
    close_matches = 0
    total_difference = 0.0

    for song_key in common_songs:

        target_rating = float(
            user_ratings[song_key]
        )

        neighbour_rating = float(
            neighbour_ratings[song_key]
        )

        difference = abs(
            target_rating
            -
            neighbour_rating
        )

        total_difference += difference

        if difference == 0:
            exact_matches += 1

        if difference <= 1:
            close_matches += 1

        song = get_song_metadata(
            song_key,
            metadata,
        )

        if song is not None:
            track_name = song["track_name"]
            artist = song["artist"]
        else:
            track_name = str(song_key)
            artist = "Unknown Artist"

        comparison.append({
            "track_name": track_name,
            "artist": artist,
            "target_rating": int(target_rating),
            "neighbour_rating":
                int(neighbour_rating),
            "difference": int(difference),
            "squared_difference":
                int(difference ** 2),
        })

    comparison.sort(
        key=lambda row:
            row["difference"]
    )

    return {
        "user_id": user_id,
        "neighbour_id": neighbour_id,
        "distance": float(distance),
        "similarity": float(
            distance_to_similarity(distance)
        ),
        "common_ratings": common_count,
        "exact_matches": exact_matches,
        "close_matches": close_matches,
        "average_difference": float(
            total_difference / common_count
        ),
        "comparison": comparison,
    }


def get_nearest_users_explanation(
    user_id,
    k=K_NEIGHBORS,
):
    """Detailed explanation for the K nearest users."""

    explanations = []

    for neighbour in find_nearest_users(
        user_id,
        k,
    ):
        details = get_user_similarity_details(
            user_id,
            neighbour["user_id"],
        )

        if details is not None:
            explanations.append(details)

    return explanations


# Explain which similar users support a recommendation.

def get_recommendation_support(
    user_id,
    track_name,
    artist,
    k=K_NEIGHBORS,
):
    """Show which nearby users support a recommendation."""

    user_matrix = load_real_user_matrix()

    if user_matrix.empty:
        return None

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return None

    song_key = find_song_key(
        track_name,
        artist,
    )

    if song_key is None:
        return None

    if song_key not in user_matrix.columns:
        return None

    target_rating = user_matrix.loc[
        user_id,
        song_key,
    ]

    if pd.isna(target_rating):
        target_rating = None

    supporters = []

    for neighbour in find_nearest_users(
        user_id,
        k,
    ):

        neighbour_rating = user_matrix.loc[
            neighbour["user_id"],
            song_key,
        ]

        if pd.isna(neighbour_rating):
            continue

        supporters.append({
            "user_id": neighbour["user_id"],
            "distance": float(
                neighbour["distance"]
            ),
            "similarity": float(
                neighbour["similarity"]
            ),
            "rating": int(neighbour_rating),
            "liked": bool(
                neighbour_rating
                >=
                MIN_RECOMMEND_RATING
            ),
        })

    liked_supporters = [
        supporter
        for supporter in supporters
        if supporter["liked"]
    ]

    return {
        "user_id": user_id,
        "track_name": track_name,
        "artist": artist,
        "target_rating": target_rating,
        "target_has_rated":
            target_rating is not None,
        "supporting_users": supporters,
        "liked_supporters": liked_supporters,
        "liked_support_count":
            len(liked_supporters),
    }


# Explain which liked songs support an Item-Based recommendation.

def get_item_recommendation_support(
    user_id,
    track_name,
    artist,
    k=K_NEIGHBORS,
):
    """
    Explain Item-Based score by comparing
    a recommendation with songs the user likes.
    """

    user_matrix = load_real_user_matrix()
    metadata = load_song_metadata()

    if user_matrix.empty:
        return None

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return None

    candidate_song = find_song_key(
        track_name,
        artist,
    )

    if (
        candidate_song is None
        or candidate_song
        not in user_matrix.columns
    ):
        return None

    target_ratings = user_matrix.loc[user_id]

    liked_songs = target_ratings[
        target_ratings
        >=
        MIN_RECOMMEND_RATING
    ]

    supporting_items = []

    for liked_song, user_rating in liked_songs.items():

        distance, common_users = (
            calculate_item_distance(
                candidate_song,
                liked_song,
                user_matrix,
            )
        )

        if distance is None:
            continue

        song = get_song_metadata(
            liked_song,
            metadata,
        )

        supporting_items.append({
            "song_key": liked_song,

            "track_name":
                song["track_name"]
                if song is not None
                else str(liked_song),

            "artist":
                song["artist"]
                if song is not None
                else "Unknown Artist",

            "user_rating":
                int(user_rating),

            "distance":
                float(distance),

            "similarity":
                float(
                    distance_to_similarity(
                        distance
                    )
                ),

            "common_users":
                common_users,
        })

    supporting_items.sort(
        key=lambda item:
            item["similarity"],
        reverse=True,
    )

    nearest_items = supporting_items[:k]

    similarity_total = sum(
        item["similarity"]
        for item in nearest_items
    )

    if similarity_total > 0:

        item_knn_score = (
            sum(
                item["similarity"]
                *
                (item["user_rating"] / 5.0)
                for item in nearest_items
            )
            /
            similarity_total
        )

    else:
        item_knn_score = 0.0

    return {
        "user_id": user_id,
        "track_name": track_name,
        "artist": artist,
        "supporting_items": nearest_items,
        "item_knn_score":
            float(item_knn_score),
    }


# Combine User-Based and Item-Based KNN into the final score.

def recommend_for_user(
    user_id,
    top_n=10,
):
    """
    Final Collaborative recommendation:

    50% User-Based KNN
    +
    50% Item-Based KNN
    """

    # Cold start
    if (
        get_rating_count(user_id)
        <
        MIN_USER_RATINGS
    ):
        return []

    user_matrix = load_real_user_matrix()

    if user_matrix.empty:
        return []

    user_id = get_canonical_user_id(
        user_id,
        user_matrix,
    )

    if user_id is None:
        return []

    user_results = user_based_recommendations(
        user_id,
        top_n=50,
    )

    item_results = item_based_recommendations(
        user_id,
        top_n=50,
    )

    combined = {}

    # Add User-Based recommendation scores.

    for song in user_results:

        combined[song["song_key"]] = {
            "track_name": song["track_name"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "user_knn_score":
                song["user_knn_score"],
            "item_knn_score": 0.0,
            "neighbour_count":
                song.get(
                    "neighbour_count",
                    0,
                ),
        }

    # Merge Item-Based recommendation scores.

    for song in item_results:

        song_key = song["song_key"]

        if song_key not in combined:

            combined[song_key] = {
                "track_name": song["track_name"],
                "artist": song["artist"],
                "genre": song["genre"],
                "mood": song["mood"],
                "user_knn_score": 0.0,
                "item_knn_score":
                    song["item_knn_score"],
                "neighbour_count": 0,
            }

        else:

            combined[
                song_key
            ][
                "item_knn_score"
            ] = song["item_knn_score"]

    # Calculate the final 50/50 Collaborative score.

    results = []

    for values in combined.values():

        user_score = float(
            values["user_knn_score"]
        )

        item_score = float(
            values["item_knn_score"]
        )

        collaborative_score = (
            USER_WEIGHT * user_score
            +
            ITEM_WEIGHT * item_score
        )

        results.append({
            "track_name":
                values["track_name"],

            "artist":
                values["artist"],

            "genre":
                values["genre"],

            "mood":
                values["mood"],

            "popularity":
                get_song_popularity(
                    values["track_name"],
                    values["artist"],
                ),

            "source":
                get_recommendation_source(
                    user_score,
                    item_score,
                ),

            "user_knn_score":
                round(user_score, 3),

            "item_knn_score":
                round(item_score, 3),

            "collaborative_score":
                round(
                    collaborative_score,
                    3,
                ),

            "neighbour_count":
                values["neighbour_count"],

            # Predicted preference on 1–5 scale
            "rating":
                round(
                    collaborative_score * 5,
                    1,
                ),
        })

    # Sort recommendations consistently when scores are tied.

    results.sort(
        key=lambda song: (
            -song["collaborative_score"],
            -song["user_knn_score"],
            -song["item_knn_score"],
            str(song["track_name"]).casefold(),
            str(song["artist"]).casefold(),
        )
    )

    return results[:top_n]


# Simple command-line test for the Collaborative Filtering module.

if __name__ == "__main__":

    TEST_USER = "User101"

    print()
    print("=" * 55)
    print("COLLABORATIVE FILTERING - REAL KNN")
    print("=" * 55)

    print(
        "User:",
        TEST_USER
    )

    print(
        "Ratings:",
        get_rating_count(TEST_USER)
    )

    # Display the nearest users for testing.

    print()
    print("=" * 55)
    print("NEAREST USERS")
    print("=" * 55)

    neighbours = find_nearest_users(
        TEST_USER
    )

    for neighbour in neighbours:

        print(
            f"{neighbour['user_id']} | "
            f"Distance: {neighbour['distance']:.3f} | "
            f"Similarity: {neighbour['similarity']:.3f} | "
            f"Common: {neighbour['common_ratings']}"
        )

    # Display the final Collaborative recommendations for testing.

    print()
    print("=" * 55)
    print("FINAL COLLABORATIVE RECOMMENDATIONS")
    print("=" * 55)

    recommendations = recommend_for_user(
        TEST_USER
    )

    for rank, song in enumerate(
        recommendations,
        start=1,
    ):

        print(
            f"{rank}. "
            f"{song['track_name']} — "
            f"{song['artist']}"
        )

        print(
            f"   Source: {song['source']} | "
            f"User: {song['user_knn_score']:.3f} | "
            f"Item: {song['item_knn_score']:.3f} | "
            f"Collaborative: "
            f"{song['collaborative_score']:.3f}"
        )