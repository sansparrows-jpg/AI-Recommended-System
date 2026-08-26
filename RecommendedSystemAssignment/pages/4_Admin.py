# SoundScope - Admin User Data

from pathlib import Path

import pandas as pd
import streamlit as st

from models.auth import load_users


# =========================================================
# ADMIN ACCESS CHECK
# =========================================================

if not st.session_state.get("logged_in"):
    st.error("Please login first.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()


# =========================================================
# FILE PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RATINGS_PATH = (
    PROJECT_ROOT
    / "data"
    / "real_user_ratings.csv"
)

HISTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "search_history.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

def load_csv(path):
    """
    Safely load a CSV file.
    """

    if not path.exists():
        return pd.DataFrame()

    return (
        pd.read_csv(
            path,
            dtype=str
        )
        .fillna("")
    )


users = load_users()
ratings = load_csv(RATINGS_PATH)
history = load_csv(HISTORY_PATH)


# =========================================================
# NORMAL USERS ONLY
# =========================================================

if "role" in users.columns:

    normal_users = users[
        users["role"]
        .astype(str)
        .str.strip()
        .str.casefold()
        ==
        "user"
    ].copy()

else:

    normal_users = users.copy()


# =========================================================
# PAGE HEADER
# =========================================================

st.title(
    "Admin User Data",
    anchor=False
)

st.caption(
    "View registered users, ratings, "
    "and search activity."
)


# =========================================================
# SUMMARY METRICS
# =========================================================

total_users = len(normal_users)

total_ratings = len(ratings)

total_searches = len(history)

rated_users = (
    ratings["user_id"].nunique()
    if (
        not ratings.empty
        and "user_id" in ratings.columns
    )
    else 0
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    with st.container(border=True):

        st.metric(
            "Registered Users",
            total_users
        )


with col2:

    with st.container(border=True):

        st.metric(
            "Total Ratings",
            total_ratings
        )


with col3:

    with st.container(border=True):

        st.metric(
            "Users With Ratings",
            rated_users
        )


with col4:

    with st.container(border=True):

        st.metric(
            "Search Records",
            total_searches
        )


st.space("small")


# =========================================================
# TABS
# =========================================================

(
    users_tab,
    summary_tab,
    ratings_tab,
    history_tab,
) = st.tabs(
    [
        "Registered Users",
        "User Summary",
        "All Ratings",
        "Search History",
    ]
)


# =========================================================
# REGISTERED USERS
# =========================================================

with users_tab:

    st.subheader(
        "Registered Users"
    )

    st.caption(
        "Normal user accounts registered in SoundScope."
    )


    if normal_users.empty:

        st.info(
            "No registered users found."
        )

    else:

        # Do not display passwords.
        user_columns = [
            column
            for column in [
                "user_id",
                "username",
                "role",
            ]
            if column in normal_users.columns
        ]


        display_users = (
            normal_users[
                user_columns
            ]
            .reset_index(
                drop=True
            )
        )


        st.dataframe(
            display_users,
            width="stretch",
            hide_index=True
        )


# =========================================================
# USER SUMMARY
# =========================================================

with summary_tab:

    st.subheader(
        "User Activity Summary"
    )

    st.caption(
        "Summary of ratings and search activity "
        "for each registered user."
    )


    if normal_users.empty:

        st.info(
            "No user data available."
        )

    else:

        summary = (
            normal_users[
                [
                    "user_id",
                    "username",
                ]
            ]
            .copy()
        )


        # -------------------------------------------------
        # RATING SUMMARY
        # -------------------------------------------------

        if (
            not ratings.empty
            and
            "user_id" in ratings.columns
        ):

            ratings_copy = (
                ratings.copy()
            )


            if "rating" in ratings_copy.columns:

                ratings_copy[
                    "rating"
                ] = pd.to_numeric(
                    ratings_copy[
                        "rating"
                    ],
                    errors="coerce"
                )


                rating_summary = (

                    ratings_copy

                    .groupby(
                        "user_id"
                    )

                    .agg(
                        rating_count=(
                            "rating",
                            "count"
                        ),

                        average_rating=(
                            "rating",
                            "mean"
                        ),
                    )

                    .reset_index()
                )


                rating_summary[
                    "average_rating"
                ] = (

                    rating_summary[
                        "average_rating"
                    ]

                    .round(2)
                )


                summary = summary.merge(
                    rating_summary,
                    on="user_id",
                    how="left"
                )


        # -------------------------------------------------
        # SEARCH SUMMARY
        # -------------------------------------------------

        if (
            not history.empty
            and
            "user_id" in history.columns
        ):

            search_summary = (

                history

                .groupby(
                    "user_id"
                )

                .size()

                .reset_index(
                    name="search_count"
                )
            )


            summary = summary.merge(
                search_summary,
                on="user_id",
                how="left"
            )


        # -------------------------------------------------
        # MISSING VALUES
        # -------------------------------------------------

        if "rating_count" not in summary.columns:

            summary[
                "rating_count"
            ] = 0


        if "average_rating" not in summary.columns:

            summary[
                "average_rating"
            ] = 0.0


        if "search_count" not in summary.columns:

            summary[
                "search_count"
            ] = 0


        summary[
            "rating_count"
        ] = (

            summary[
                "rating_count"
            ]

            .fillna(0)

            .astype(int)
        )


        summary[
            "average_rating"
        ] = (

            summary[
                "average_rating"
            ]

            .fillna(0.0)
        )


        summary[
            "search_count"
        ] = (

            summary[
                "search_count"
            ]

            .fillna(0)

            .astype(int)
        )


        summary = (
            summary
            .sort_values(
                "user_id"
            )
            .reset_index(
                drop=True
            )
        )


        st.dataframe(
            summary,
            width="stretch",
            hide_index=True
        )


# =========================================================
# ALL RATINGS
# =========================================================

with ratings_tab:

    st.subheader(
        "All User Ratings"
    )

    st.caption(
        "Ratings submitted by SoundScope users."
    )


    if ratings.empty:

        st.info(
            "No rating data available."
        )

    else:

        rating_users = sorted(
            ratings[
                "user_id"
            ]
            .dropna()
            .unique()
        )


        selected_rating_user = (
            st.selectbox(
                "Filter by User",
                [
                    "All Users",
                    *rating_users,
                ],
                key="admin_rating_user"
            )
        )


        filtered_ratings = (
            ratings.copy()
        )


        if (
            selected_rating_user
            !=
            "All Users"
        ):

            filtered_ratings = (
                filtered_ratings[
                    filtered_ratings[
                        "user_id"
                    ]
                    ==
                    selected_rating_user
                ]
            )


        preferred_columns = [
            "user_id",
            "track_name",
            "artist",
            "genre",
            "mood",
            "rating",
            "rated_at",
        ]


        visible_columns = [
            column
            for column
            in preferred_columns
            if column
            in filtered_ratings.columns
        ]


        st.caption(
            f"{len(filtered_ratings)} "
            f"rating record(s)"
        )


        st.dataframe(
            filtered_ratings[
                visible_columns
            ],
            width="stretch",
            hide_index=True
        )


# =========================================================
# SEARCH HISTORY
# =========================================================

with history_tab:

    st.subheader(
        "All User Search History"
    )

    st.caption(
        "Songs selected by each user."
    )


    if history.empty:

        st.info(
            "No search history available."
        )

    else:

        history_users = sorted(
            history[
                "user_id"
            ]
            .dropna()
            .unique()
        )


        selected_history_user = (
            st.selectbox(
                "Filter by User",
                [
                    "All Users",
                    *history_users,
                ],
                key="admin_history_user"
            )
        )


        filtered_history = (
            history.copy()
        )


        if (
            selected_history_user
            !=
            "All Users"
        ):

            filtered_history = (
                filtered_history[
                    filtered_history[
                        "user_id"
                    ]
                    ==
                    selected_history_user
                ]
            )


        preferred_columns = [
            "user_id",
            "track_name",
            "artist",
            "genre",
            "mood",
            "searched_at",
            "search_time",
            "timestamp",
        ]


        visible_columns = [
            column
            for column
            in preferred_columns
            if column
            in filtered_history.columns
        ]


        # If the history file has a different
        # timestamp column, show the remaining
        # existing columns as well.
        if not visible_columns:

            visible_columns = list(
                filtered_history.columns
            )


        st.caption(
            f"{len(filtered_history)} "
            f"search record(s)"
        )


        st.dataframe(
            filtered_history[
                visible_columns
            ],
            width="stretch",
            hide_index=True
        )