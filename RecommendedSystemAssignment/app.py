# AI Music Recommendation System
# Streamlit Main Application

import pandas as pd
import streamlit as st

from models.auth import (
    authenticate,
    register_user,
    load_users,
)

from models.history import (
    add_search_history,
    clear_search_history,
    get_recent_searches,
)

from models.ratings import (
    get_rating_count,
    get_song_rating,
    save_rating,
)

from models.preprocessing import preprocess_data


# =========================================================
# CONFIGURATION
# =========================================================

RECENT_SEARCH_LIMIT = 20


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SoundScope",
    page_icon="music",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# LOGIN SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None


# =========================================================
# LOGIN / CREATE ACCOUNT PAGE
# =========================================================

if not st.session_state["logged_in"]:

    st.title(
        "SoundScope",
        anchor=False
    )

    st.caption(
        "AI-powered music recommendation system"
    )

    st.space(
        "small"
    )


    # =====================================================
    # LOGIN / REGISTER TABS
    # =====================================================

    login_tab, register_tab = (
        st.tabs(
            [
                "Login",
                "Create Account",
            ]
        )
    )


    # =====================================================
    # LOGIN TAB
    # =====================================================

    with login_tab:

        with st.container(
            border=True
        ):

            st.subheader(
                "Welcome back"
            )

            st.caption(
                "Login to continue discovering music."
            )


            with st.form(
                "login_form"
            ):

                username = (
                    st.text_input(
                        "Username",
                        placeholder="Enter username"
                    )
                )


                password = (
                    st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter password"
                    )
                )


                login_button = (
                    st.form_submit_button(
                        "Login",
                        width="stretch"
                    )
                )


            if login_button:

                user = authenticate(
                    username,
                    password
                )


                if user:

                    st.session_state[
                        "logged_in"
                    ] = True


                    st.session_state[
                        "user_id"
                    ] = user[
                        "user_id"
                    ]


                    st.session_state[
                        "username"
                    ] = user[
                        "username"
                    ]


                    st.rerun()


                else:

                    st.error(
                        "Invalid username or password."
                    )


    # =====================================================
    # CREATE ACCOUNT TAB
    # =====================================================

    with register_tab:

        with st.container(
            border=True
        ):

            st.subheader(
                "Create your account"
            )

            st.caption(
                "Create an account to save your "
                "search history and receive personalized "
                "recommendations."
            )


            with st.form(
                "register_form"
            ):

                new_username = (
                    st.text_input(
                        "Create username",
                        placeholder="Choose a username"
                    )
                )


                new_password = (
                    st.text_input(
                        "Create password",
                        type="password",
                        placeholder="Minimum 4 characters"
                    )
                )


                confirm_password = (
                    st.text_input(
                        "Confirm password",
                        type="password",
                        placeholder="Enter password again"
                    )
                )


                register_button = (
                    st.form_submit_button(
                        "Create Account",
                        width="stretch"
                    )
                )


            if register_button:

                if (
                    new_password
                    !=
                    confirm_password
                ):

                    st.error(
                        "Passwords do not match."
                    )


                else:

                    (
                        success,
                        message,
                        user,
                    ) = register_user(
                        new_username,
                        new_password
                    )


                    if success:

                        st.success(
                            message
                        )


                        st.info(
                            "You can now login using "
                            "your new username and password."
                        )


                    else:

                        st.error(
                            message
                        )


    st.stop()


# =========================================================
# CURRENT LOGGED-IN USER
# =========================================================

current_user_id = (
    st.session_state["user_id"]
)

current_username = (
    st.session_state["username"]
)


# =========================================================
# SEARCH FUNCTIONS
# =========================================================

def fold_search_text(text):
    """
    Create simplified text for
    flexible searching.
    """

    return "".join(
        character
        for character in str(text).casefold()
        if character.isalnum()
        and character not in "aeiou"
    )


@st.cache_data(show_spinner=False)
def get_song_options():
    """
    Prepare Spotify songs for searching.
    """

    songs = preprocess_data()

    search_songs = (
        songs[
            [
                "track_name",
                "artists",
                "track_genre",
                "mood",
            ]
        ]

        .drop_duplicates(
            subset=[
                "track_name",
                "artists",
            ]
        )

        .sort_values(
            [
                "track_name",
                "artists",
            ]
        )

        .reset_index(
            drop=True
        )
    )


    search_songs[
        "search_text"
    ] = (

        search_songs[
            "track_name"
        ].astype(str)

        + " "

        + search_songs[
            "artists"
        ].astype(str)

        + " "

        + search_songs[
            "track_genre"
        ].astype(str)

        + " "

        + search_songs[
            "mood"
        ].astype(str)

    ).str.casefold()


    search_songs[
        "search_fold"
    ] = (

        search_songs[
            "search_text"
        ]

        .map(
            fold_search_text
        )
    )


    return (
        songs,
        search_songs
    )


# =========================================================
# REGISTERED USER COUNT
# =========================================================

def get_user_count():
    """
    Get total registered accounts
    from users.csv.
    """

    return len(
        load_users()
    )


# =========================================================
# FILTER SEARCH RESULTS
# =========================================================

def filter_song_options(
    query,
    search_songs,
    limit=10
):
    """
    Search songs by:

    1. Track name
    2. Artist
    3. Genre
    4. Mood
    """

    query = (
        query
        .strip()
        .casefold()
    )


    if not query:

        return []


    track_starts = (

        search_songs[
            "track_name"
        ]

        .astype(str)

        .str.casefold()

        .str.startswith(
            query
        )
    )


    artist_starts = (

        search_songs[
            "artists"
        ]

        .astype(str)

        .str.casefold()

        .str.startswith(
            query
        )
    )


    contains = (

        search_songs[
            "search_text"
        ]

        .str.contains(
            query,
            regex=False
        )
    )


    folded_query = (
        fold_search_text(
            query
        )
    )


    if folded_query:

        folded_contains = (

            search_songs[
                "search_fold"
            ]

            .str.contains(
                folded_query,
                regex=False
            )
        )

    else:

        folded_contains = (
            pd.Series(
                False,
                index=search_songs.index
            )
        )


    ranked_matches = pd.concat(
        [

            search_songs[
                track_starts
            ],

            search_songs[
                artist_starts
                & ~track_starts
            ],

            search_songs[
                contains
                & ~track_starts
                & ~artist_starts
            ],

            search_songs[
                folded_contains
                & ~track_starts
                & ~artist_starts
                & ~contains
            ],
        ]
    )


    ranked_matches = (

        ranked_matches

        .drop_duplicates(
            subset=[
                "track_name",
                "artists",
            ]
        )

        .head(
            limit
        )
    )


    return (
        ranked_matches
        .to_dict(
            "records"
        )
    )


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

def generate_recommendations(
    song_name,
    artist,
    user_id
):
    """
    Generate recommendations using:

    Content-Based:
        Song Name + Artist

    Collaborative:
        Logged-in User ID

    Hybrid:
        Song Name + Artist + User ID

    Final Top 10:
        Hybrid Recommendation
    """

    from models.collaborative import (
        recommend_for_user
    )

    from models.content_based import (
        recommend_song
    )

    from models.hybrid import (
        hybrid_recommend
    )


    content_results = (
        recommend_song(
            song_name,
            artist
        )
    )


    collaborative_results = (
        recommend_for_user(
            user_id
        )
    )


    hybrid_results = (
        hybrid_recommend(
            song_name,
            artist,
            user_id
        )
    )


    final_results = []


    for song in hybrid_results:

        final_song = (
            song.copy()
        )


        final_song[
            "final_score"
        ] = song[
            "score"
        ]


        final_results.append(
            final_song
        )


    final_results.sort(

        key=lambda song:
            song[
                "final_score"
            ],

        reverse=True
    )


    final_results = (
        final_results[:10]
    )


    st.session_state[
        "selected_song"
    ] = song_name


    st.session_state[
        "selected_artist"
    ] = artist


    st.session_state[
        "selected_user"
    ] = user_id


    st.session_state[
        "content_results"
    ] = content_results


    st.session_state[
        "collaborative_results"
    ] = collaborative_results


    st.session_state[
        "hybrid_results"
    ] = hybrid_results


    st.session_state[
        "final_results"
    ] = final_results


# =========================================================
# HANDLE SONG CLICK
# =========================================================

def handle_song_selection(
    song,
    user_id
):
    """
    Save selected song to account history,
    remember selected song for rating,
    and generate recommendations.
    """

    st.session_state[
        "selected_song_details"
    ] = {

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


    add_search_history(
        user_id,
        song
    )


    with st.spinner(
        "Generating recommendations..."
    ):

        generate_recommendations(

            song[
                "track_name"
            ],

            song[
                "artists"
            ],

            user_id
        )


    st.success(
        "Recommendations generated successfully."
    )


# =========================================================
# TOP 10 DISPLAY
# =========================================================

def render_top_10(
    final_results
):
    """
    Display final Top 10 recommendations.
    """

    st.subheader(
        "Top 10 recommended songs"
    )


    st.caption(
        "Final ranking generated from "
        "the Hybrid Recommendation model."
    )


    if not final_results:

        st.info(
            "No final recommendation available yet."
        )

        return


    top_10 = (

        pd.DataFrame(
            final_results
        )

        .sort_values(
            "final_score",
            ascending=False
        )

        .head(
            10
        )

        .reset_index(
            drop=True
        )
    )


    top_10[
        "rank"
    ] = (
        top_10.index
        + 1
    )


    preferred_columns = [

        "rank",

        "track_name",

        "artist",

        "genre",

        "mood",

        "popularity",

        "final_score",
    ]


    visible_columns = [

        column

        for column in preferred_columns

        if column
        in top_10.columns
    ]


    st.dataframe(

        top_10[
            visible_columns
        ],

        width="stretch",

        hide_index=True
    )


# =========================================================
# LOAD SONG DATA
# =========================================================

songs, search_songs = (
    get_song_options()
)


# =========================================================
# LOGGED-IN USER / LOGOUT
# =========================================================

top_left, top_right = (
    st.columns(
        [5, 1]
    )
)


with top_left:

    st.caption(
        f"Logged in as "
        f"{current_username} "
        f"({current_user_id})"
    )


with top_right:

    logout_button = (
        st.button(
            "Logout",
            width="stretch"
        )
    )


    if logout_button:

        st.session_state[
            "logged_in"
        ] = False


        st.session_state[
            "user_id"
        ] = None


        st.session_state[
            "username"
        ] = None


        st.session_state.pop(
            "selected_song",
            None
        )

        st.session_state.pop(
            "selected_artist",
            None
        )

        st.session_state.pop(
            "selected_user",
            None
        )

        st.session_state.pop(
            "content_results",
            None
        )

        st.session_state.pop(
            "collaborative_results",
            None
        )

        st.session_state.pop(
            "hybrid_results",
            None
        )

        st.session_state.pop(
            "final_results",
            None
        )

        st.session_state.pop(
            "selected_song_details",
            None
        )

        st.session_state.pop(
            "song_search_query",
            None
        )


        st.rerun()


# =========================================================
# APPLICATION HEADER
# =========================================================

st.title(
    "SoundScope",
    anchor=False
)


st.caption(
    "AI-powered music recommendations with "
    "Content-Based, Collaborative, and Hybrid ranking."
)


# =========================================================
# SYSTEM INFORMATION
# =========================================================

col1, col2, col3 = (
    st.columns(3)
)


with col1:

    with st.container(
        border=True
    ):

        st.metric(
            "Tracks",
            f"{len(songs):,}"
        )


with col2:

    with st.container(
        border=True
    ):

        st.metric(
            "Users",
            f"{get_user_count():,}"
        )


with col3:

    with st.container(
        border=True
    ):

        st.metric(
            "Models",
            3
        )


# =========================================================
# DISCOVER MUSIC
# =========================================================

st.space(
    "small"
)


st.subheader(
    "Discover music"
)


# =========================================================
# SEARCH BAR
# =========================================================

song_query = st.text_input(

    "Search",

    placeholder="What do you want to play?",

    key="song_search_query",

    label_visibility="collapsed",
)


# =========================================================
# SEARCH PANEL
# =========================================================

with st.container(
    border=True
):

    if not song_query.strip():

        recent_searches = (
            get_recent_searches(
                current_user_id,
                limit=RECENT_SEARCH_LIMIT
            )
        )


        recent_header, clear_column = (
            st.columns(
                [8, 1]
            )
        )


        with recent_header:

            st.markdown(
                "#### Recent searches"
            )


        with clear_column:

            if recent_searches:

                clear_button = (
                    st.button(
                        "Clear",
                        key="clear_history",
                        width="stretch"
                    )
                )


                if clear_button:

                    clear_search_history(
                        current_user_id
                    )

                    st.rerun()


        if recent_searches:

            for index, song in enumerate(
                recent_searches
            ):

                normal_song = {

                    "track_name":
                        song[
                            "track_name"
                        ],

                    "artists":
                        song[
                            "artist"
                        ],

                    "track_genre":
                        song[
                            "genre"
                        ],

                    "mood":
                        song[
                            "mood"
                        ],
                }


                song_label = (

                    f"🎵  "
                    f"{song['track_name']}"

                    f"  —  "
                    f"{song['artist']}"

                    f"  ·  "
                    f"{song['genre']}"

                    f"  ·  "
                    f"{song['mood']}"
                )


                clicked = (
                    st.button(

                        song_label,

                        key=(
                            f"recent_song_"
                            f"{index}"
                        ),

                        width="stretch"
                    )
                )


                if clicked:

                    handle_song_selection(
                        normal_song,
                        current_user_id
                    )


        else:

            st.caption(
                "No recent searches yet. "
                "Search for a song to get started."
            )


    else:

        filtered_song_options = (
            filter_song_options(

                song_query,

                search_songs,

                limit=10
            )
        )


        st.markdown(
            "#### Search results"
        )


        st.caption(
            f"Showing results for "
            f"'{song_query}'"
        )


        if not filtered_song_options:

            st.warning(
                "No matching songs found.",
                icon=":material/search_off:"
            )


        else:

            for index, song in enumerate(
                filtered_song_options
            ):

                song_label = (

                    f"🎵  "
                    f"{song['track_name']}"

                    f"  —  "
                    f"{song['artists']}"

                    f"  ·  "
                    f"{song['track_genre']}"

                    f"  ·  "
                    f"{song['mood']}"
                )


                clicked = (
                    st.button(

                        song_label,

                        key=(
                            f"search_song_"
                            f"{index}"
                        ),

                        width="stretch"
                    )
                )


                if clicked:

                    handle_song_selection(
                        song,
                        current_user_id
                    )


# =========================================================
# LOGGED-IN USER INFORMATION
# =========================================================

st.caption(
    f"Recommendations are personalized for "
    f"{current_username} "
    f"({current_user_id})."
)


# =========================================================
# DISPLAY TOP 10
# =========================================================

final_results = (
    st.session_state.get(
        "final_results",
        []
    )
)


if final_results:

    st.space(
        "small"
    )


    render_top_10(
        final_results
    )


    st.caption(
        "Open the Results page from the sidebar "
        "to compare all three recommendation methods."
    )


# =========================================================
# RATE SELECTED SONG
# =========================================================

selected_song_details = (
    st.session_state.get(
        "selected_song_details"
    )
)


if selected_song_details:

    st.space(
        "small"
    )


    with st.container(
        border=True
    ):

        st.subheader(
            "Rate the song you selected"
        )


        st.caption(
            "After listening to or knowing the song, "
            "you can rate it from 1 to 5."
        )


        st.write(
            f"**{selected_song_details['track_name']}** "
            f"— {selected_song_details['artists']}"
        )


        st.caption(
            f"{selected_song_details['track_genre']} · "
            f"{selected_song_details['mood']}"
        )


        previous_rating = (
            get_song_rating(

                current_user_id,

                selected_song_details[
                    "track_name"
                ],

                selected_song_details[
                    "artists"
                ]
            )
        )


        if previous_rating is not None:

            st.info(
                f"You previously rated this song "
                f"{previous_rating}/5."
            )


        rating_widget_key = (

            f"rating_"
            f"{current_user_id}_"
            f"{selected_song_details['track_name']}_"
            f"{selected_song_details['artists']}"
        )


        rating_value = (
            st.select_slider(

                "Your rating",

                options=[
                    1,
                    2,
                    3,
                    4,
                    5,
                ],

                value=(
                    previous_rating
                    if previous_rating is not None
                    else 3
                ),

                format_func=lambda value:
                    f"{value} ★",

                key=rating_widget_key,
            )
        )


        st.caption(
            "1 = Strongly dislike · "
            "2 = Dislike · "
            "3 = Neutral · "
            "4 = Like · "
            "5 = Strongly like"
        )


        save_rating_button = (
            st.button(

                "Save Rating",

                key=(
                    f"save_rating_"
                    f"{current_user_id}_"
                    f"{selected_song_details['track_name']}_"
                    f"{selected_song_details['artists']}"
                ),

                width="stretch"
            )
        )


        if save_rating_button:

            success, message = (
                save_rating(

                    current_user_id,

                    selected_song_details,

                    rating_value
                )
            )


            if success:

                st.success(
                    message
                )

                st.rerun()


            else:

                st.error(
                    message
                )


        rating_count = (
            get_rating_count(
                current_user_id
            )
        )


        st.caption(
            f"You have rated "
            f"{rating_count} "
            f"{'song' if rating_count == 1 else 'songs'}."
        )