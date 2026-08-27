# =========================================================
# ADMIN RECOMMENDATION REVIEW SERVICE
# =========================================================

from pathlib import Path

import pandas as pd

from models.auth import load_users
from models.ratings import get_rating_count


# =========================================================
# PATH
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SEARCH_HISTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "search_history.csv"
)


# =========================================================
# LOAD SEARCH HISTORY
# =========================================================

def load_search_history():
    """
    Load the existing search_history.csv.

    No new dataset is created.
    """

    if not SEARCH_HISTORY_PATH.exists():

        return pd.DataFrame()


    try:

        history = pd.read_csv(
            SEARCH_HISTORY_PATH,
            dtype=str,
        ).fillna("")

    except pd.errors.EmptyDataError:

        return pd.DataFrame()


    return history


# =========================================================
# GET NORMAL USERS
# =========================================================

def get_reviewable_users():
    """
    Return normal registered users only.

    Admin accounts are excluded.

    Passwords are not returned.
    """

    users = load_users().copy()


    if users.empty:

        return pd.DataFrame(
            columns=[
                "user_id",
                "username",
            ]
        )


    required_columns = {
        "user_id",
        "username",
    }


    if not required_columns.issubset(
        users.columns
    ):

        return pd.DataFrame(
            columns=[
                "user_id",
                "username",
            ]
        )


    # =====================================================
    # ROLE FILTER
    # =====================================================

    if "role" in users.columns:

        role_value = (
            users["role"]
            .astype(str)
            .str.strip()
            .str.casefold()
        )


        user_id_value = (
            users["user_id"]
            .astype(str)
            .str.strip()
        )


        users = users[
            (
                role_value.eq("user")
            )
            |
            (
                role_value.eq("")
                &
                user_id_value.str.startswith(
                    "User"
                )
            )
        ].copy()


    else:

        # Old users.csv without role column
        users = users[
            users["user_id"]
            .astype(str)
            .str.startswith("User")
        ].copy()


    # =====================================================
    # RETURN SAFE COLUMNS ONLY
    # =====================================================

    return (
        users[
            [
                "user_id",
                "username",
            ]
        ]
        .drop_duplicates(
            subset=[
                "user_id"
            ]
        )
        .sort_values(
            "user_id"
        )
        .reset_index(
            drop=True
        )
    )


# =========================================================
# GET USERNAME
# =========================================================

def get_username(
    user_id
):
    users = get_reviewable_users()


    if users.empty:

        return ""


    target_user = (
        str(user_id)
        .strip()
        .casefold()
    )


    match = users[
        users["user_id"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq(
            target_user
        )
    ]


    if match.empty:

        return ""


    return str(
        match.iloc[0][
            "username"
        ]
    )


# =========================================================
# GET LATEST SEARCH
# =========================================================

def get_latest_user_search(
    user_id
):
    """
    Get one user's most recent searched/selected song.

    Preferred timestamp columns:

    searched_at
    search_time
    timestamp
    created_at

    If no timestamp exists, the final CSV row for
    that user is treated as the newest search.
    """

    history = (
        load_search_history()
    )


    if (
        history.empty
        or
        "user_id"
        not in history.columns
    ):

        return None


    target_user = (
        str(user_id)
        .strip()
        .casefold()
    )


    user_history = history[
        history["user_id"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq(
            target_user
        )
    ].copy()


    if user_history.empty:

        return None


    # =====================================================
    # KEEP ORIGINAL CSV ORDER
    # =====================================================

    user_history[
        "_row_order"
    ] = range(
        len(user_history)
    )


    # =====================================================
    # FIND TIME COLUMN
    # =====================================================

    timestamp_candidates = [
        "searched_at",
        "search_time",
        "timestamp",
        "created_at",
    ]


    timestamp_column = next(
        (
            column
            for column
            in timestamp_candidates
            if column
            in user_history.columns
        ),
        None,
    )


    # =====================================================
    # FIND NEWEST RECORD
    # =====================================================

    if timestamp_column:

        user_history[
            "_parsed_time"
        ] = pd.to_datetime(
            user_history[
                timestamp_column
            ],
            errors="coerce",
        )


        valid_rows = user_history[
            user_history[
                "_parsed_time"
            ].notna()
        ]


        if not valid_rows.empty:

            latest = (
                valid_rows
                .sort_values(
                    [
                        "_parsed_time",
                        "_row_order",
                    ]
                )
                .iloc[-1]
            )


        else:

            latest = (
                user_history
                .sort_values(
                    "_row_order"
                )
                .iloc[-1]
            )


    else:

        latest = (
            user_history
            .sort_values(
                "_row_order"
            )
            .iloc[-1]
        )


    # =====================================================
    # COLUMN SUPPORT
    # =====================================================

    if "artist" in user_history.columns:

        artist_column = "artist"

    elif "artists" in user_history.columns:

        artist_column = "artists"

    else:

        artist_column = None


    if "genre" in user_history.columns:

        genre_column = "genre"

    elif "track_genre" in user_history.columns:

        genre_column = "track_genre"

    else:

        genre_column = None


    # =====================================================
    # VALUES
    # =====================================================

    track_name = str(
        latest.get(
            "track_name",
            "",
        )
    ).strip()


    artist = (
        str(
            latest.get(
                artist_column,
                "",
            )
        ).strip()

        if artist_column

        else ""
    )


    genre = (
        str(
            latest.get(
                genre_column,
                "",
            )
        ).strip()

        if genre_column

        else ""
    )


    mood = str(
        latest.get(
            "mood",
            "",
        )
    ).strip()


    searched_at = (
        str(
            latest.get(
                timestamp_column,
                "",
            )
        ).strip()

        if timestamp_column

        else ""
    )


    if not track_name:

        return None


    return {

        "user_id":
            str(user_id),

        "track_name":
            track_name,

        "artist":
            artist,

        "genre":
            genre,

        "mood":
            mood,

        "searched_at":
            searched_at,
    }


# =========================================================
# GENERATE ADMIN REVIEW
# =========================================================

def generate_user_review(
    user_id
):
    """
    Re-generate recommendations for Admin.

    Uses:

    - User's latest searched song
    - User's CURRENT ratings

    Does NOT save recommendation results
    into any CSV.
    """

    # Import only when Admin generates review.
    from models.collaborative import (
        recommend_for_user,
    )

    from models.content_based import (
        recommend_song,
    )

    from models.hybrid import (
        hybrid_recommend,
    )


    # =====================================================
    # GET LATEST SEARCH
    # =====================================================

    latest_search = (
        get_latest_user_search(
            user_id
        )
    )


    if latest_search is None:

        return None


    song_name = (
        latest_search[
            "track_name"
        ]
    )


    artist = (
        latest_search[
            "artist"
        ]
    )


    # =====================================================
    # CONTENT-BASED
    # =====================================================

    content_results = recommend_song(
        song_name,
        artist,
    )


    # =====================================================
    # COLLABORATIVE
    # =====================================================

    collaborative_results = (
        recommend_for_user(
            user_id,
            top_n=10,
        )
    )


    # =====================================================
    # HYBRID
    # =====================================================

    hybrid_results = hybrid_recommend(
        song_name,
        artist,
        user_id,
    )


    # =====================================================
    # FINAL TOP 10
    # =====================================================

    final_results = []


    for song in hybrid_results:

        item = song.copy()


        item["final_score"] = float(
            song.get(
                "score",
                0.0,
            )
            or 0.0
        )


        final_results.append(
            item
        )


    final_results.sort(
        key=lambda row:
            row.get(
                "final_score",
                0.0,
            ),
        reverse=True,
    )


    final_results = (
        final_results[:10]
    )


    # =====================================================
    # RETURN TEMPORARY RESULT
    # =====================================================

    return {

        "user_id":
            str(user_id),

        "username":
            get_username(
                user_id
            ),

        "selected_song":
            song_name,

        "selected_artist":
            artist,

        "latest_search":
            latest_search,

        "rating_count":
            get_rating_count(
                user_id
            ),

        "content_results":
            content_results,

        "collaborative_results":
            collaborative_results,

        "hybrid_results":
            hybrid_results,

        "final_results":
            final_results,
    }