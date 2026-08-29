
# REAL USER DATA
#
# Builds the User × Song rating matrix
# from real_user_ratings.csv.
#
# IMPORTANT:
# Missing ratings remain NaN.
# They are NOT converted to 0 because
# "not rated" does not mean "dislike".

import pandas as pd

from models.ratings import load_ratings


# CREATE UNIQUE SONG KEY
def create_song_key(
    track_name,
    artist
):
    """
    Create a unique identifier for a song.

    Track name alone is not enough because
    different artists may have songs with
    the same title.
    """

    return (
        f"{str(track_name).strip()}"
        f"|||"
        f"{str(artist).strip()}"
    )


# LOAD REAL RATINGS
def load_real_ratings():
    """
    Load real user ratings and
    prepare a unique song key.
    """

    ratings = (
        load_ratings()
    )


    if ratings.empty:

        return ratings


    ratings = (
        ratings.copy()
    )


    # CLEAN VALUES

    ratings[
        "user_id"
    ] = (

        ratings[
            "user_id"
        ]

        .astype(str)

        .str.strip()
    )


    ratings[
        "track_name"
    ] = (

        ratings[
            "track_name"
        ]

        .astype(str)

        .str.strip()
    )


    ratings[
        "artist"
    ] = (

        ratings[
            "artist"
        ]

        .astype(str)

        .str.strip()
    )


    ratings[
        "rating"
    ] = pd.to_numeric(

        ratings[
            "rating"
        ],

        errors="coerce"
    )


    # Remove invalid ratings
    ratings = (

        ratings

        .dropna(
            subset=[
                "user_id",
                "track_name",
                "artist",
                "rating",
            ]
        )

        .copy()
    )


    # Keep only ratings between 1 and 5
    ratings = ratings[

        ratings[
            "rating"
        ].between(
            1,
            5
        )

    ].copy()


    # CREATE UNIQUE SONG KEY
    ratings[
        "song_key"
    ] = ratings.apply(

        lambda row:

            create_song_key(

                row[
                    "track_name"
                ],

                row[
                    "artist"
                ]
            ),

        axis=1
    )


    return ratings


# BUILD USER × SONG MATRIX

def load_real_user_matrix():
    """
    Create the User × Song rating matrix.

    Rows:
        Users

    Columns:
        Songs

    Values:
        Ratings from 1 to 5

    Missing ratings:
        NaN
    """

    ratings = (
        load_real_ratings()
    )


    if ratings.empty:

        return pd.DataFrame()


    user_matrix = (

        ratings

        .pivot_table(

            index="user_id",

            columns="song_key",

            values="rating",

            aggfunc="mean"
        )

        .sort_index()
    )


    return user_matrix


# BUILD SONG METADATA TABLE
def load_song_metadata():
    """
    Create metadata lookup for every
    song appearing in the real ratings.
    """

    ratings = (
        load_real_ratings()
    )


    if ratings.empty:

        return pd.DataFrame(
            columns=[
                "song_key",
                "track_name",
                "artist",
                "genre",
                "mood",
            ]
        )


    metadata = (

        ratings[
            [
                "song_key",
                "track_name",
                "artist",
                "genre",
                "mood",
            ]
        ]

        .drop_duplicates(
            subset=[
                "song_key"
            ]
        )

        .reset_index(
            drop=True
        )
    )


    return metadata


# GET ONE USER'S RATINGS
def get_user_rating_series(
    user_id
):
    """
    Return one user's rating row
    from the User × Song matrix.
    """

    user_matrix = (
        load_real_user_matrix()
    )


    if user_matrix.empty:

        return None


    user_id = (
        str(
            user_id
        )
        .strip()
    )


    if (
        user_id
        not in user_matrix.index
    ):

        return None


    return (
        user_matrix.loc[
            user_id
        ]
    )


# GET SONG INFORMATION

def get_song_information(
    song_key
):
    """
    Find metadata for one song.
    """

    metadata = (
        load_song_metadata()
    )


    if metadata.empty:

        return None


    match = metadata[
        metadata[
            "song_key"
        ]
        ==
        song_key
    ]


    if match.empty:

        return None


    return (
        match.iloc[0]
        .to_dict()
    )


# TEST

if __name__ == "__main__":

    print()
    print(
        "========================================"
    )

    print(
        "REAL USER × SONG MATRIX"
    )

    print(
        "========================================"
    )


    user_matrix = (
        load_real_user_matrix()
    )


    if user_matrix.empty:

        print(
            "No real ratings found."
        )


    else:

        print()
        print(
            user_matrix
        )


        print()
        print(
            "========================================"
        )

        print(
            "MATRIX INFORMATION"
        )

        print(
            "========================================"
        )


        print(
            "Users:",
            len(
                user_matrix.index
            )
        )


        print(
            "Songs:",
            len(
                user_matrix.columns
            )
        )


        print()
        print(
            "Users in matrix:"
        )


        for user_id in user_matrix.index:

            rated_count = (
                user_matrix
                .loc[
                    user_id
                ]
                .notna()
                .sum()
            )


            print(
                f"{user_id}: "
                f"{rated_count} rated songs"
            )


        print()
        print(
            "========================================"
        )

        print(
            "COMMON RATINGS"
        )

        print(
            "========================================"
        )


        # Count how many users rated each song
        rating_counts = (

            user_matrix

            .notna()

            .sum(
                axis=0
            )

            .sort_values(
                ascending=False
            )
        )


        for (
            song_key,
            count
        ) in rating_counts.items():

            if count >= 2:

                song_info = (
                    get_song_information(
                        song_key
                    )
                )


                if song_info:

                    print(
                        f"{song_info['track_name']} "
                        f"— {song_info['artist']}: "
                        f"{count} users"
                    )