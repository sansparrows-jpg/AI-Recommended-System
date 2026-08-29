
# REAL USER RATING MANAGEMENT
#
# This file stores ratings entered by
# real registered users.
#
# Rating scale:
# 1 = Strongly dislike
# 2 = Dislike
# 3 = Neutral
# 4 = Like
# 5 = Strongly like

from datetime import datetime
from pathlib import Path

import pandas as pd


# RATINGS FILE
RATINGS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "real_user_ratings.csv"
)


RATING_COLUMNS = [
    "user_id",
    "track_name",
    "artist",
    "genre",
    "mood",
    "rating",
    "rated_at",
]


# LOAD RATINGS
def load_ratings():
    """
    Load all real user ratings.

    If the file does not exist,
    create an empty ratings file.
    """

    if not RATINGS_PATH.exists():

        empty_ratings = pd.DataFrame(
            columns=RATING_COLUMNS
        )

        empty_ratings.to_csv(
            RATINGS_PATH,
            index=False
        )

        return empty_ratings


    ratings = pd.read_csv(
        RATINGS_PATH
    )


    # Make sure required columns exist
    for column in RATING_COLUMNS:

        if column not in ratings.columns:

            ratings[column] = ""


    # Convert rating into numeric values
    if not ratings.empty:

        ratings["rating"] = pd.to_numeric(
            ratings["rating"],
            errors="coerce"
        )


    return ratings


# SAVE / UPDATE RATING
def save_rating(
    user_id,
    song,
    rating
):
    """
    Save a new rating or update
    an existing rating.

    A unique rating is identified using:

    User ID
    + Track Name
    + Artist
    """

    # VALIDATE RATING
    try:

        rating = int(
            rating
        )

    except (TypeError, ValueError):

        return (
            False,
            "Rating must be between 1 and 5."
        )


    if rating < 1 or rating > 5:

        return (
            False,
            "Rating must be between 1 and 5."
        )


    ratings = (
        load_ratings()
    )


    track_name = str(
        song[
            "track_name"
        ]
    ).strip()


    artist = str(
        song[
            "artists"
        ]
    ).strip()


    genre = str(
        song[
            "track_genre"
        ]
    ).strip()


    mood = str(
        song[
            "mood"
        ]
    ).strip()


    # FIND EXISTING RATING

    if not ratings.empty:

        existing_rating = (

            (
                ratings[
                    "user_id"
                ]
                .astype(str)
                .str.strip()
                ==
                str(user_id).strip()
            )

            &

            (
                ratings[
                    "track_name"
                ]
                .astype(str)
                .str.strip()
                .str.casefold()
                ==
                track_name.casefold()
            )

            &

            (
                ratings[
                    "artist"
                ]
                .astype(str)
                .str.strip()
                .str.casefold()
                ==
                artist.casefold()
            )
        )


    else:

        existing_rating = pd.Series(
            False,
            index=ratings.index
        )


    # UPDATE EXISTING RATING
    if existing_rating.any():

        ratings.loc[
            existing_rating,
            "rating"
        ] = rating


        ratings.loc[
            existing_rating,
            "rated_at"
        ] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        ratings.to_csv(
            RATINGS_PATH,
            index=False
        )


        return (
            True,
            "Rating updated successfully."
        )


    # CREATE NEW RATING
    new_rating = pd.DataFrame(
        [
            {
                "user_id":
                    user_id,

                "track_name":
                    track_name,

                "artist":
                    artist,

                "genre":
                    genre,

                "mood":
                    mood,

                "rating":
                    rating,

                "rated_at":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
            }
        ]
    )


    ratings = pd.concat(
        [
            ratings,
            new_rating,
        ],
        ignore_index=True
    )


    ratings.to_csv(
        RATINGS_PATH,
        index=False
    )


    return (
        True,
        "Rating saved successfully."
    )


# GET CURRENT USER RATINGS
def get_user_ratings(
    user_id
):
    """
    Return ratings belonging only
    to one user.
    """

    ratings = (
        load_ratings()
    )


    if ratings.empty:

        return []


    user_ratings = ratings[
        ratings[
            "user_id"
        ]
        .astype(str)
        .str.strip()
        ==
        str(user_id).strip()
    ].copy()


    if user_ratings.empty:

        return []


    user_ratings = (
        user_ratings

        .sort_values(
            "rated_at",
            ascending=False
        )
    )


    return user_ratings.to_dict(
        "records"
    )


# GET ONE SONG RATING

def get_song_rating(
    user_id,
    track_name,
    artist
):
    """
    Find the rating the current user
    previously gave to one song.

    Returns None if not rated.
    """

    ratings = (
        load_ratings()
    )


    if ratings.empty:

        return None


    match = ratings[

        (
            ratings[
                "user_id"
            ]
            .astype(str)
            .str.strip()
            ==
            str(user_id).strip()
        )

        &

        (
            ratings[
                "track_name"
            ]
            .astype(str)
            .str.strip()
            .str.casefold()
            ==
            str(track_name)
            .strip()
            .casefold()
        )

        &

        (
            ratings[
                "artist"
            ]
            .astype(str)
            .str.strip()
            .str.casefold()
            ==
            str(artist)
            .strip()
            .casefold()
        )
    ]


    if match.empty:

        return None


    return int(
        match.iloc[0][
            "rating"
        ]
    )


# COUNT USER RATINGS

def get_rating_count(
    user_id
):
    """
    Count how many songs one user
    has rated.
    """

    return len(
        get_user_ratings(
            user_id
        )
    )


# CHECK COLLABORATIVE READINESS

def has_enough_ratings(
    user_id,
    minimum=10
):
    """
    Check whether the user has enough
    ratings for Collaborative Filtering.
    """

    return (
        get_rating_count(
            user_id
        )
        >=
        minimum
    )


# TEST
if __name__ == "__main__":

    print()
    print("==============================")
    print("Real User Ratings")
    print("==============================")

    ratings = load_ratings()

    print(ratings)

    print()
    print(
        "Total ratings:",
        len(ratings)
    )