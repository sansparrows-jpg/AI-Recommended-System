from datetime import datetime
from pathlib import Path

import pandas as pd


# =========================================================
# SEARCH HISTORY FILE
# =========================================================

HISTORY_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "search_history.csv"
)


# =========================================================
# LOAD SEARCH HISTORY
# =========================================================

def load_search_history():
    """
    Load search history from CSV.

    If the file does not exist,
    create an empty search history file.
    """

    if not HISTORY_PATH.exists():

        empty_history = pd.DataFrame(
            columns=[
                "user_id",
                "track_name",
                "artist",
                "genre",
                "mood",
                "searched_at",
            ]
        )

        empty_history.to_csv(
            HISTORY_PATH,
            index=False
        )

        return empty_history


    history = pd.read_csv(
        HISTORY_PATH
    )

    return history


# =========================================================
# GET RECENT SEARCHES
# =========================================================

def get_recent_searches(
    user_id,
    limit=8
):
    """
    Get recent searches belonging
    only to the logged-in user.

    A unique song is identified using:

    track_name + artist
    """

    history = load_search_history()


    # No history available
    if history.empty:

        return []


    # =====================================================
    # FILTER CURRENT USER
    # =====================================================

    user_history = history[
        history["user_id"].astype(str)
        ==
        str(user_id)
    ].copy()


    if user_history.empty:

        return []


    # =====================================================
    # SORT NEWEST FIRST
    # =====================================================

    user_history = (
        user_history

        .sort_values(
            "searched_at",
            ascending=False
        )

        # IMPORTANT:
        # Same song name from different
        # artists is allowed.
        .drop_duplicates(
            subset=[
                "track_name",
                "artist",
            ],
            keep="first"
        )

        .head(
            limit
        )
    )


    return user_history.to_dict(
        "records"
    )


# =========================================================
# ADD SEARCH HISTORY
# =========================================================

def add_search_history(
    user_id,
    song
):
    """
    Save a selected song to the
    logged-in user's search history.

    If the same user searches the
    same song + same artist again,
    the old record is removed and
    the new search moves to the top.
    """

    history = load_search_history()


    # =====================================================
    # REMOVE OLD COPY OF SAME SONG
    # =====================================================

    if not history.empty:

        duplicate = (

            # Same user
            (
                history[
                    "user_id"
                ].astype(str)
                ==
                str(user_id)
            )

            &

            # Same track name
            (
                history[
                    "track_name"
                ].astype(str)
                .str.strip()
                .str.casefold()
                ==
                str(
                    song["track_name"]
                )
                .strip()
                .casefold()
            )

            &

            # Same artist
            (
                history[
                    "artist"
                ].astype(str)
                .str.strip()
                .str.casefold()
                ==
                str(
                    song["artists"]
                )
                .strip()
                .casefold()
            )
        )


        # Remove previous occurrence
        # so the newest search moves
        # to the top.
        history = history[
            ~duplicate
        ]


    # =====================================================
    # CREATE NEW SEARCH RECORD
    # =====================================================

    new_search = pd.DataFrame(
        [
            {
                "user_id":
                    user_id,

                "track_name":
                    song[
                        "track_name"
                    ],

                "artist":
                    song[
                        "artists"
                    ],

                "genre":
                    song[
                        "track_genre"
                    ],

                "mood":
                    song[
                        "mood"
                    ],

                "searched_at":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
            }
        ]
    )


    # =====================================================
    # ADD NEW SEARCH
    # =====================================================

    history = pd.concat(
        [
            history,
            new_search,
        ],
        ignore_index=True
    )


    # =====================================================
    # SAVE SEARCH HISTORY
    # =====================================================

    history.to_csv(
        HISTORY_PATH,
        index=False
    )


# =========================================================
# CLEAR SEARCH HISTORY
# =========================================================

def clear_search_history(
    user_id
):
    """
    Delete search history only for
    the selected logged-in user.

    Other users' search histories
    are not affected.
    """

    history = load_search_history()


    if history.empty:

        return


    # Keep all history except
    # the current user's records.
    history = history[
        history[
            "user_id"
        ].astype(str)
        !=
        str(user_id)
    ]


    history.to_csv(
        HISTORY_PATH,
        index=False
    )