# This file generates synthetic user ratings
# for Collaborative Filtering.
# Output:
# data/user_ratings.csv

import random
from pathlib import Path

import pandas as pd

from models.preprocessing import preprocess_data

RATINGS_PATH = Path(__file__).resolve().parents[1] / "data" / "user_ratings.csv"
RANDOM_SEED = 42


def generate_user_ratings():

    # Load cleaned Spotify dataset
    random.seed(RANDOM_SEED)

    songs = preprocess_data()

    # Remove duplicate song names
    songs = songs.drop_duplicates(
        subset="track_name"
    )

    songs = songs[
        [
            "track_name",
            "artists",
            "track_genre",
            "mood",
            "popularity",
        ]
    ]

    # Configuration

    number_of_users = 100

    minimum_ratings = 60

    maximum_ratings = 70

    profile_count = 5

    common_genres = (
        songs["track_genre"]
        .value_counts()
        .head(profile_count)
        .index
        .tolist()
    )

    common_moods = (
        songs["mood"]
        .value_counts()
        .index
        .tolist()
    )

    user_profiles = []

    for profile_index in range(profile_count):
        favourite_genre = common_genres[profile_index % len(common_genres)]
        favourite_mood = common_moods[profile_index % len(common_moods)]
        profile_songs = songs[
            (songs["track_genre"] == favourite_genre)
            | (songs["mood"] == favourite_mood)
        ].sort_values("popularity", ascending=False)

        user_profiles.append(
            {
                "genre": favourite_genre,
                "mood": favourite_mood,
                "shared_songs": profile_songs.head(55),
                "candidate_songs": profile_songs,
            }
        )


    ratings = []

    # Generate ratings for every user

    for user in range(1, number_of_users + 1):

        user_id = f"User{user:03d}"
        profile = user_profiles[(user - 1) % profile_count]


        # Randomly choose how many songs this
        # user has listened to.
        total_ratings = random.randint(
            minimum_ratings,
            maximum_ratings
        )


        shared_count = min(
            55,
            len(profile["shared_songs"]),
            total_ratings
        )

        selected_songs = profile["shared_songs"].head(shared_count)
        remaining_count = total_ratings - len(selected_songs)

        if remaining_count > 0:
            remaining_pool = profile["candidate_songs"][
                ~profile["candidate_songs"]["track_name"].isin(
                    selected_songs["track_name"]
                )
            ]

            if len(remaining_pool) >= remaining_count:
                extra_songs = remaining_pool.sample(
                    remaining_count,
                    random_state=RANDOM_SEED + user,
                )
            else:
                extra_songs = songs[
                    ~songs["track_name"].isin(selected_songs["track_name"])
                ].sample(
                    remaining_count,
                    random_state=RANDOM_SEED + user,
                )

            selected_songs = pd.concat(
                [selected_songs, extra_songs],
                ignore_index=True,
            )

        # Rate favourite-genre and favourite-mood songs higher so
        # collaborative filtering can learn clear user behaviour patterns.
        for _, song in selected_songs.iterrows():
            genre_match = song["track_genre"] == profile["genre"]
            mood_match = song["mood"] == profile["mood"]

            if genre_match and mood_match:
                rating = 5
            elif genre_match or mood_match:
                rating = random.choice([4, 5, 5])
            else:
                rating = random.choice([1, 2, 3])

            ratings.append({

                "user_id": user_id,

                "track_name": song["track_name"],

                "artist": song["artists"],

                "genre": song["track_genre"],

                "mood": song["mood"],

                "rating": rating

            })


    # Convert to DataFrame

    ratings_df = pd.DataFrame(ratings)

    # Save CSV

    ratings_df.to_csv(

        RATINGS_PATH,

        index=False,

        encoding="utf-8"

    )


    print()

    print("=================================")

    print("User Rating Dataset Generated")

    print()

    print("Total Users :", number_of_users)

    print("Total Ratings :", len(ratings_df))

    print()

    print("Saved to:")

    print(RATINGS_PATH)

    print("=================================")


# Run this file directly

if __name__ == "__main__":

    generate_user_ratings()
