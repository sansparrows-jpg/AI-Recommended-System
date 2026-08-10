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

    # Select useful columns only

    songs = songs[
        [
            "track_name",
            "artists",
            "track_genre"
        ]
    ]

    # Configuration

    number_of_users = 100

    minimum_ratings = 30

    maximum_ratings = 50


    ratings = []

    # Generate ratings for every user

    for user in range(1, number_of_users + 1):

        user_id = f"User{user:03d}"


        # Randomly choose how many songs this
        # user has listened to.
        total_ratings = random.randint(
            minimum_ratings,
            maximum_ratings
        )


        # Randomly choose songs
        selected_songs = songs.sample(
            total_ratings,
            random_state=RANDOM_SEED + user
        )


        # Give each selected song
        # a random rating from 1-5
        for _, song in selected_songs.iterrows():

            ratings.append({

                "user_id": user_id,

                "track_name": song["track_name"],

                "artist": song["artists"],

                "genre": song["track_genre"],

                "rating": random.randint(1, 5)

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
