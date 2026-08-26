# =========================================================
# SOUND SCOPE
# ADMIN USER RATING MANAGEMENT PAGE
# =========================================================

from pathlib import Path

import pandas as pd
import streamlit as st

from models.preprocessing import preprocess_data

from models.ratings import (
    get_rating_count,
    get_song_rating,
    get_user_ratings,
    save_rating,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Rate Music - SoundScope",
    page_icon="⭐",
    layout="wide",
)


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.get(
    "logged_in",
    False
):

    st.warning(
        "Please login from the Home page first."
    )

    st.stop()


# =========================================================
# CURRENT LOGGED-IN ACCOUNT
# =========================================================

current_user_id = (
    st.session_state.get(
        "user_id",
        ""
    )
)

current_username = (
    st.session_state.get(
        "username",
        ""
    )
)

current_role = (
    str(
        st.session_state.get(
            "role",
            ""
        )
    )
    .strip()
)


# =========================================================
# ADMIN ACCESS ONLY
# =========================================================

if (
    current_role.casefold()
    !=
    "admin"
):

    st.error(
        "Access denied. "
        "Only administrators can manage "
        "Collaborative Filtering ratings."
    )

    st.stop()


# =========================================================
# CONFIGURATION
# =========================================================

MINIMUM_RATINGS = 10

USER_RATINGS_FILE = (
    Path("data/user_ratings.csv")
)

USERS_FILE = (
    Path("data/users.csv")
)


# =========================================================
# COMMON SONGS
#
# Every selected user should have ratings for these songs.
# This creates overlapping rating data for KNN.
# =========================================================

COMMON_RATING_TARGETS = [

    (
        "Perfect",
        "Ed Sheeran"
    ),

    (
        "Shape of You",
        "Ed Sheeran"
    ),

    (
        "Believer",
        "Imagine Dragons"
    ),

    (
        "Baby",
        "Justin Bieber"
    ),

    (
        "Happier",
        "Marshmello"
    ),

    (
        "Bad Habits",
        "Ed Sheeran"
    ),

    (
        "Photograph",
        "Ed Sheeran"
    ),

    (
        "Don't Blame Me",
        "Taylor Swift"
    ),

    (
        "I Feel It Coming",
        "The Weeknd"
    ),

    (
        "STAY",
        "Justin Bieber"
    ),
]


# =========================================================
# LOAD AVAILABLE USERS
# =========================================================

def load_available_users():
    """
    Load users that the administrator can manage.

    First try to get users from data/users.csv.

    If data/users.csv is not available,
    user IDs are loaded from data/user_ratings.csv.
    """

    user_ids = set()


    # =====================================================
    # TRY USERS FILE
    # =====================================================

    if USERS_FILE.exists():

        try:

            users_dataframe = (
                pd.read_csv(
                    USERS_FILE
                )
            )


            if (
                "user_id"
                in users_dataframe.columns
            ):

                # =========================================
                # EXCLUDE ADMIN ACCOUNTS IF ROLE EXISTS
                # =========================================

                if (
                    "role"
                    in users_dataframe.columns
                ):

                    normal_users = (

                        users_dataframe[

                            users_dataframe[
                                "role"
                            ]

                            .astype(str)

                            .str.strip()

                            .str.casefold()

                            !=
                            "admin"
                        ]
                    )


                else:

                    normal_users = (
                        users_dataframe
                    )


                for user_id in (
                    normal_users[
                        "user_id"
                    ]
                    .dropna()
                    .astype(str)
                    .str.strip()
                ):

                    if user_id:

                        user_ids.add(
                            user_id
                        )


        except Exception:

            pass


    # =====================================================
    # LOAD USERS FROM RATING DATA
    # =====================================================

    if USER_RATINGS_FILE.exists():

        try:

            ratings_dataframe = (
                pd.read_csv(
                    USER_RATINGS_FILE
                )
            )


            if (
                "user_id"
                in ratings_dataframe.columns
            ):

                for user_id in (
                    ratings_dataframe[
                        "user_id"
                    ]
                    .dropna()
                    .astype(str)
                    .str.strip()
                ):

                    if user_id:

                        user_ids.add(
                            user_id
                        )


        except Exception:

            pass


    # =====================================================
    # REMOVE CURRENT ADMIN FROM LIST
    # =====================================================

    user_ids = [

        user_id

        for user_id
        in user_ids

        if (
            user_id.casefold()
            !=
            str(
                current_user_id
            )
            .strip()
            .casefold()
        )
    ]


    # =====================================================
    # SORT USER IDS
    # =====================================================

    return sorted(
        user_ids
    )


# =========================================================
# LOAD COMMON SONGS
# =========================================================

@st.cache_data(
    show_spinner=False
)
def load_common_songs():
    """
    Find the common rating songs
    inside the Spotify dataset.

    Song title + artist keyword
    are used so we select the
    correct version of each song.
    """

    songs = (
        preprocess_data()
    )


    common_songs = []


    for (
        track_name,
        artist_keyword
    ) in COMMON_RATING_TARGETS:


        # =================================================
        # MATCH TRACK NAME
        # =================================================

        track_match = (

            songs[
                "track_name"
            ]

            .astype(str)

            .str.strip()

            .str.casefold()

            ==
            track_name
            .strip()
            .casefold()
        )


        # =================================================
        # MATCH ARTIST
        # =================================================

        artist_match = (

            songs[
                "artists"
            ]

            .astype(str)

            .str.contains(
                artist_keyword,
                case=False,
                regex=False,
                na=False
            )
        )


        matches = (
            songs[
                track_match
                &
                artist_match
            ]
        )


        # =================================================
        # SONG EXISTS
        # =================================================

        if not matches.empty:

            # If duplicate versions exist,
            # use the most popular one.

            if (
                "popularity"
                in matches.columns
            ):

                matches = (
                    matches.sort_values(
                        "popularity",
                        ascending=False
                    )
                )


            song = (
                matches.iloc[0]
            )


            common_songs.append(
                {

                    "track_name":
                        song[
                            "track_name"
                        ],

                    "artists":
                        song[
                            "artists"
                        ],

                    "track_genre":
                        song[
                            "track_genre"
                        ],

                    "mood":
                        song[
                            "mood"
                        ],
                }
            )


    return common_songs


# =========================================================
# FLASH MESSAGE
# =========================================================

if (
    "rating_message"
    in st.session_state
):

    st.success(
        st.session_state.pop(
            "rating_message"
        )
    )


# =========================================================
# PAGE HEADER
# =========================================================

st.title(
    "Rate Music",
    anchor=False
)


st.caption(
    f"Logged in as "
    f"{current_username} "
    f"({current_role})"
)


st.write(
    "Select a user and manage their song ratings "
    "from **1 to 5**. These ratings are used to "
    "build user preference profiles for "
    "**Collaborative Filtering**."
)


# =========================================================
# LOAD USERS
# =========================================================

available_users = (
    load_available_users()
)


# =========================================================
# NO USERS FOUND
# =========================================================

if not available_users:

    st.warning(
        "No users were found. "
        "Please make sure user accounts or "
        "user rating records are available."
    )

    st.stop()


# =========================================================
# SELECT USER
# =========================================================

st.subheader(
    "Manage user ratings"
)


selected_user_id = (
    st.selectbox(

        "Select user",

        options=available_users,

        key="admin_rating_selected_user",
    )
)


st.info(
    f"You are currently managing ratings for "
    f"**{selected_user_id}**."
)


# =========================================================
# RATING SCALE
# =========================================================

with st.container(
    border=True
):

    st.markdown(
        "### Rating scale"
    )


    st.write(
        """
        **1 ★** = Strongly dislike  
        **2 ★** = Dislike  
        **3 ★** = Neutral  
        **4 ★** = Like  
        **5 ★** = Strongly like
        """
    )


# =========================================================
# SELECTED USER PROFILE PROGRESS
# =========================================================

rating_count = (
    get_rating_count(
        selected_user_id
    )
)


progress_value = min(
    rating_count
    /
    MINIMUM_RATINGS,

    1.0
)


st.subheader(
    f"{selected_user_id}'s preference profile"
)


st.progress(
    progress_value
)


st.write(
    f"**{rating_count} / "
    f"{MINIMUM_RATINGS} songs rated**"
)


if (
    rating_count
    >=
    MINIMUM_RATINGS
):

    st.success(
        f"{selected_user_id} has enough ratings "
        f"to build a Collaborative Filtering "
        f"profile."
    )


else:

    ratings_remaining = (
        MINIMUM_RATINGS
        -
        rating_count
    )


    st.info(
        f"Rate {ratings_remaining} more "
        f"{'song' if ratings_remaining == 1 else 'songs'} "
        f"for {selected_user_id} to reach the minimum "
        f"Collaborative Filtering profile."
    )


# =========================================================
# COMMON RATING SET
# =========================================================

st.divider()


st.subheader(
    "Common rating set"
)


st.caption(
    "These common songs create overlapping rating "
    "data between users so that KNN Collaborative "
    "Filtering can compare their preferences."
)


common_songs = (
    load_common_songs()
)


# =========================================================
# NO COMMON SONGS FOUND
# =========================================================

if not common_songs:

    st.error(
        "The common songs could not be found "
        "in the Spotify dataset."
    )


# =========================================================
# DISPLAY COMMON SONGS
# =========================================================

else:

    for index, song in enumerate(
        common_songs
    ):

        with st.container(
            border=True
        ):

            # =============================================
            # SONG INFORMATION
            # =============================================

            st.markdown(
                f"### 🎵 {song['track_name']}"
            )


            st.write(
                song[
                    "artists"
                ]
            )


            st.caption(
                f"{song['track_genre']} · "
                f"{song['mood']}"
            )


            # =============================================
            # CHECK SELECTED USER'S PREVIOUS RATING
            # =============================================

            previous_rating = (
                get_song_rating(

                    selected_user_id,

                    song[
                        "track_name"
                    ],

                    song[
                        "artists"
                    ]
                )
            )


            if (
                previous_rating
                is not None
            ):

                st.caption(
                    f"{selected_user_id}'s current rating: "
                    f"{previous_rating}/5"
                )


            # =============================================
            # RATING + BUTTON COLUMNS
            # =============================================

            rating_column, button_column = (
                st.columns(
                    [4, 1]
                )
            )


            # =============================================
            # RATING SELECTOR
            # =============================================

            with rating_column:

                rating_options = [

                    "Select rating",

                    1,

                    2,

                    3,

                    4,

                    5,
                ]


                if (
                    previous_rating
                    is not None
                ):

                    default_index = (
                        int(
                            previous_rating
                        )
                    )


                else:

                    default_index = 0


                rating_value = (
                    st.selectbox(

                        "Rating",

                        options=rating_options,

                        index=default_index,

                        key=(
                            f"common_rating_"
                            f"{selected_user_id}_"
                            f"{index}"
                        ),

                        label_visibility="collapsed",
                    )
                )


            # =============================================
            # SAVE / UPDATE BUTTON
            # =============================================

            with button_column:

                button_text = (

                    "Update"

                    if previous_rating
                    is not None

                    else

                    "Save"
                )


                save_button = (
                    st.button(

                        button_text,

                        key=(
                            f"common_save_"
                            f"{selected_user_id}_"
                            f"{index}"
                        ),

                        width="stretch",
                    )
                )


            # =============================================
            # SAVE RATING FOR SELECTED USER
            # =============================================

            if save_button:

                if (
                    rating_value
                    ==
                    "Select rating"
                ):

                    st.warning(
                        "Please select a rating "
                        "from 1 to 5."
                    )


                else:

                    (
                        success,
                        message
                    ) = save_rating(

                        selected_user_id,

                        song,

                        rating_value
                    )


                    if success:

                        action_text = (

                            "updated"

                            if previous_rating
                            is not None

                            else

                            "saved"
                        )


                        st.session_state[
                            "rating_message"
                        ] = (
                            f"{song['track_name']} rating "
                            f"for {selected_user_id} "
                            f"{action_text}: "
                            f"{rating_value}/5."
                        )


                        st.rerun()


                    else:

                        st.error(
                            message
                        )


# =========================================================
# SELECTED USER RATINGS
# =========================================================

st.divider()


st.subheader(
    f"{selected_user_id}'s ratings"
)


user_ratings = (
    get_user_ratings(
        selected_user_id
    )
)


if user_ratings:

    ratings_dataframe = (
        pd.DataFrame(
            user_ratings
        )
    )


    preferred_columns = [

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
        in ratings_dataframe.columns
    ]


    ratings_dataframe = (
        ratings_dataframe[
            visible_columns
        ]
    )


    st.dataframe(

        ratings_dataframe,

        width="stretch",

        hide_index=True
    )


else:

    st.info(
        f"{selected_user_id} has not rated "
        f"any songs yet."
    )