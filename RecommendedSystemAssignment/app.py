# SoundScope - Streamlit Main Application

from pathlib import Path

import pandas as pd
import streamlit as st

from models.auth import authenticate, load_users, register_user
from models.history import add_search_history, clear_search_history, get_recent_searches
from models.preprocessing import preprocess_data
from models.ratings import get_rating_count, get_song_rating, save_rating

RECENT_SEARCH_LIMIT = 20

RATINGS_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "real_user_ratings.csv"
)


# =========================================================
# LUXURY MUSIC APPLICATION UI
# =========================================================

def apply_luxury_ui():
    """
    Change only the Streamlit appearance.
    Recommendation logic, ratings, user data and algorithms stay unchanged.
    """

    st.markdown(
        """
        <style>
        :root {
            --bg: #080810;
            --panel: #151522;
            --panel-2: #1b1a2b;
            --purple: #8b5cf6;
            --purple-soft: #a78bfa;
            --gold: #d6b36a;
            --text: #f7f5ff;
            --muted: #9b98aa;
            --border: rgba(167, 139, 250, 0.18);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(139, 92, 246, 0.14), transparent 27%),
                radial-gradient(circle at 92% 12%, rgba(214, 179, 106, 0.08), transparent 25%),
                linear-gradient(135deg, #080810 0%, #0c0c16 45%, #11111d 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 4.25rem !important;
            padding-bottom: 2.5rem !important;
        }

        [data-testid="stHeader"] {
            background: rgba(8, 8, 16, 0.82);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(214, 179, 106, 0.10);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #121220 0%, #090910 100%);
            border-right: 1px solid rgba(214, 179, 106, 0.14);
        }

        [data-testid="stSidebar"] * {
            color: #f5f3ff;
        }

        h1 {
            font-weight: 850 !important;
            letter-spacing: -0.035em !important;
            background: linear-gradient(90deg, #ffffff, #d9ccff, #d6b36a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h2, h3, h4 {
            color: #f8f7ff !important;
            letter-spacing: -0.018em;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--muted) !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(
                145deg,
                rgba(27, 26, 43, 0.94),
                rgba(15, 15, 27, 0.94)
            );
            border: 1px solid var(--border) !important;
            border-radius: 18px !important;
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stMetric"] {
            background: linear-gradient(
                135deg,
                rgba(31, 29, 49, 0.96),
                rgba(17, 17, 30, 0.96)
            );
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
        }

        [data-testid="stMetricLabel"] {
            color: #aaa6b8 !important;
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            color: white !important;
            font-weight: 780 !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            min-height: 42px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: linear-gradient(135deg, #6e45d7, #8b5cf6);
            color: white;
            font-weight: 720;
            transition: 0.18s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(214, 179, 106, 0.50);
            background: linear-gradient(135deg, #8b5cf6, #ad7cf7);
            box-shadow: 0 10px 28px rgba(139, 92, 246, 0.28);
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background: rgba(24, 24, 40, 0.95) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }

        input {
            color: white !important;
        }

        input::placeholder {
            color: #777587 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 1.35rem;
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.09) !important;
            padding: 0 !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            color: #9694a5 !important;
            padding: 0.72rem 0.08rem !important;
            font-weight: 680;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #ddd1ff !important;
        }

        .stTabs [aria-selected="true"] {
            background: transparent !important;
            color: white !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            height: 3px !important;
            border-radius: 999px !important;
            background: linear-gradient(90deg, var(--purple), var(--gold)) !important;
        }

        [data-testid="stDataFrame"] {
            background: rgba(14, 14, 25, 0.93);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 13px;
            border: 1px solid rgba(167, 139, 250, 0.14);
        }

        details {
            background: rgba(20, 20, 34, 0.76) !important;
            border: 1px solid var(--border) !important;
            border-radius: 13px !important;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--purple), var(--gold));
        }

        hr {
            border-color: rgba(255, 255, 255, 0.08) !important;
        }

        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.03);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(90deg, #6e45d7, #d6b36a);
            border-radius: 999px;
        }


        /* ================================================
           SPOTIFY-STYLE SEARCH / COMPACT HOME LAYOUT
        ================================================ */

        .st-key-top_search .stButton > button,
        .st-key-top_search button {
            background: rgba(27, 26, 43, 0.96) !important;
            border: 1px solid rgba(167, 139, 250, 0.24) !important;
            border-radius: 999px !important;
            min-height: 46px !important;
            color: #f7f5ff !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 1rem !important;
        }

        .st-key-top_search .stButton > button:hover,
        .st-key-top_search button:hover {
            border-color: rgba(214, 179, 106, 0.48) !important;
            background: rgba(35, 32, 55, 0.98) !important;
            transform: none !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22) !important;
        }

        .st-key-recent_search_list .stButton > button {
            background: transparent !important;
            border: none !important;
            border-radius: 10px !important;
            min-height: 44px !important;
            color: #f4f2fb !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 0.55rem 0.7rem !important;
            box-shadow: none !important;
        }

        .st-key-recent_search_list .stButton > button:hover {
            background: rgba(255, 255, 255, 0.07) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .st-key-search_results_list .stButton > button {
            background: transparent !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 10px !important;
            min-height: 46px !important;
            color: #f4f2fb !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 0.6rem 0.75rem !important;
            box-shadow: none !important;
        }

        .st-key-search_results_list .stButton > button:hover {
            background: rgba(139, 92, 246, 0.12) !important;
            border-color: rgba(167, 139, 250, 0.30) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .st-key-library_panel [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(18, 18, 30, 0.72);
        }

        .st-key-recommendation_home [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 15, 27, 0.72);
        }


        /* ================================================
           EXTRA MUSIC-APP FEATURES
        ================================================ */

        .st-key-continue_listening .stButton > button,
        .st-key-browse_results .stButton > button,
        .st-key-liked_songs .stButton > button {
            background: rgba(24, 24, 40, 0.82) !important;
            border: 1px solid rgba(167, 139, 250, 0.15) !important;
            border-radius: 12px !important;
            min-height: 64px !important;
            color: #f7f5ff !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 0.7rem 0.85rem !important;
            box-shadow: none !important;
        }

        .st-key-continue_listening .stButton > button:hover,
        .st-key-browse_results .stButton > button:hover,
        .st-key-liked_songs .stButton > button:hover {
            background: rgba(139, 92, 246, 0.13) !important;
            border-color: rgba(214, 179, 106, 0.30) !important;
            transform: translateY(-1px) !important;
        }

        .st-key-mood_buttons .stButton > button,
        .st-key-genre_buttons .stButton > button {
            background: rgba(28, 27, 45, 0.92) !important;
            border: 1px solid rgba(167, 139, 250, 0.18) !important;
            border-radius: 999px !important;
            min-height: 38px !important;
            box-shadow: none !important;
        }

        .st-key-mood_buttons .stButton > button:hover,
        .st-key-genre_buttons .stButton > button:hover {
            background: linear-gradient(135deg, #6e45d7, #8b5cf6) !important;
            border-color: rgba(214, 179, 106, 0.38) !important;
        }

        .st-key-surprise_button .stButton > button {
            border-radius: 999px !important;
            min-height: 46px !important;
            background: linear-gradient(135deg, #d6b36a, #b98a3c) !important;
            color: #111018 !important;
            font-weight: 800 !important;
        }

        .st-key-surprise_button .stButton > button:hover {
            background: linear-gradient(135deg, #ead093, #d6b36a) !important;
            color: #0b0a10 !important;
        }


        /* ================================================
           CONTINUE LISTENING - CLEAN COMPACT CARDS
        ================================================ */

        .st-key-continue_listening [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 155px !important;
            background: linear-gradient(
                145deg,
                rgba(27, 26, 43, 0.90),
                rgba(14, 14, 25, 0.94)
            ) !important;
        }

        .st-key-continue_listening [data-testid="stCaptionContainer"] {
            margin-top: -0.15rem !important;
        }


        /* ================================================
           BROWSE YOUR SOUND - RESULT CARDS
        ================================================ */

        .st-key-browse_results [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 205px !important;
            background:
                linear-gradient(
                    145deg,
                    rgba(27, 26, 43, 0.92),
                    rgba(13, 13, 24, 0.96)
                ) !important;
            border:
                1px solid
                rgba(167, 139, 250, 0.17)
                !important;
            border-radius:
                16px !important;
            transition:
                border-color 0.18s ease,
                transform 0.18s ease,
                box-shadow 0.18s ease;
        }

        .st-key-browse_results [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color:
                rgba(214, 179, 106, 0.34)
                !important;
            box-shadow:
                0 12px 28px
                rgba(0, 0, 0, 0.20);
        }

        .st-key-browse_results .stButton > button {
            background:
                linear-gradient(
                    135deg,
                    #6e45d7,
                    #8b5cf6
                ) !important;
            border-radius:
                10px !important;
            min-height:
                40px !important;
            text-align:
                center !important;
            justify-content:
                center !important;
        }

        @media (max-width: 800px) {
            .block-container {
                padding-top: 4rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="SoundScope",
    page_icon="music",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply the luxury music application appearance.
apply_luxury_ui()


def init_session():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "role": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def logout():
    keys_to_clear = [
        "selected_song",
        "selected_artist",
        "selected_user",
        "content_results",
        "collaborative_results",
        "hybrid_results",
        "final_results",
        "selected_song_details",
        "song_search_query",
    ]

    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["role"] = None

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.rerun()


def render_auth_page():
    st.title("SoundScope", anchor=False)
    st.caption("AI-powered music recommendation system")
    st.space("small")

    login_tab, register_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        with st.container(border=True):
            st.subheader("Welcome back")
            st.caption("Login to continue discovering music.")

            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                )
                login_button = st.form_submit_button("Login", width="stretch")

            if login_button:
                user = authenticate(username, password)
                if user:
                    st.session_state.update(
                        logged_in=True,
                        user_id=user["user_id"],
                        username=user["username"],
                        role=user.get("role", "user"),
                    )
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with register_tab:
        with st.container(border=True):
            st.subheader("Create your account")
            st.caption(
                "Registration creates a normal user account only. "
                "Admin accounts cannot be created here."
            )

            with st.form("register_form"):
                new_username = st.text_input(
                    "Create username",
                    placeholder="Choose a username",
                )
                new_password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="Minimum 4 characters",
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Enter password again",
                )
                register_button = st.form_submit_button(
                    "Create Account",
                    width="stretch",
                )

            if register_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message, _ = register_user(
                        new_username,
                        new_password,
                    )
                    if success:
                        st.success(message)
                        st.info("You can now login with your new account.")
                    else:
                        st.error(message)


def fold_search_text(text):
    return "".join(
        char
        for char in str(text).casefold()
        if char.isalnum() and char not in "aeiou"
    )


@st.cache_data(show_spinner=False)
def get_song_options():
    songs = preprocess_data()
    search_songs = (
        songs[["track_name", "artists", "track_genre", "mood"]]
        .drop_duplicates(subset=["track_name", "artists"])
        .sort_values(["track_name", "artists"])
        .reset_index(drop=True)
    )

    search_songs["search_text"] = (
        search_songs["track_name"].astype(str)
        + " "
        + search_songs["artists"].astype(str)
        + " "
        + search_songs["track_genre"].astype(str)
        + " "
        + search_songs["mood"].astype(str)
    ).str.casefold()
    search_songs["search_fold"] = search_songs["search_text"].map(
        fold_search_text
    )

    return songs, search_songs


def get_user_count():
    """Count normal users only; admin accounts are excluded."""
    users = load_users()
    if "role" not in users.columns:
        return len(users)

    return int(
        users["role"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("user")
        .sum()
    )


def filter_song_options(query, search_songs, limit=10):
    query = query.strip().casefold()
    if not query:
        return []

    track_starts = (
        search_songs["track_name"].astype(str).str.casefold().str.startswith(query)
    )
    artist_starts = (
        search_songs["artists"].astype(str).str.casefold().str.startswith(query)
    )
    contains = search_songs["search_text"].str.contains(query, regex=False)

    folded_query = fold_search_text(query)
    folded_contains = (
        search_songs["search_fold"].str.contains(folded_query, regex=False)
        if folded_query
        else pd.Series(False, index=search_songs.index)
    )

    matches = pd.concat(
        [
            search_songs[track_starts],
            search_songs[artist_starts & ~track_starts],
            search_songs[contains & ~track_starts & ~artist_starts],
            search_songs[
                folded_contains & ~track_starts & ~artist_starts & ~contains
            ],
        ]
    )

    return (
        matches.drop_duplicates(subset=["track_name", "artists"])
        .head(limit)
        .to_dict("records")
    )


def generate_recommendations(song_name, artist, user_id):
    from models.collaborative import recommend_for_user
    from models.content_based import recommend_song
    from models.hybrid import hybrid_recommend

    content_results = recommend_song(song_name, artist)
    collaborative_results = recommend_for_user(user_id)
    hybrid_results = hybrid_recommend(song_name, artist, user_id)

    final_results = []
    for song in hybrid_results:
        item = song.copy()
        item["final_score"] = song.get("score", 0.0)
        final_results.append(item)

    final_results.sort(
        key=lambda song: song.get("final_score", 0.0),
        reverse=True,
    )

    final_results = final_results[:10]

    st.session_state.update(
        selected_song=song_name,
        selected_artist=artist,
        selected_user=user_id,
        content_results=content_results,
        collaborative_results=collaborative_results,
        hybrid_results=hybrid_results,
        final_results=final_results,
    )

    # Keep only the latest normal-user recommendation run
    # temporarily for Admin review.
    if st.session_state.get("role") == "user":
        st.session_state["admin_review"] = {
            "user_id": user_id,
            "username": st.session_state.get("username"),
            "selected_song": song_name,
            "selected_artist": artist,
            "content_results": content_results,
            "collaborative_results": collaborative_results,
            "hybrid_results": hybrid_results,
            "final_results": final_results,
        }


def handle_song_selection(song, user_id):
    st.session_state["selected_song_details"] = {
        "track_name": song["track_name"],
        "artists": song["artists"],
        "track_genre": song["track_genre"],
        "mood": song["mood"],
    }

    add_search_history(user_id, song)

    with st.spinner("Generating recommendations..."):
        generate_recommendations(
            song["track_name"],
            song["artists"],
            user_id,
        )

    st.toast("Recommendations generated successfully.", icon="🎧")


def render_top_10(final_results):
    st.subheader("Top 10 recommended songs")
    st.caption("Final ranking generated from the Hybrid Recommendation model.")

    top_10 = (
        pd.DataFrame(final_results)
        .sort_values("final_score", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_10["rank"] = top_10.index + 1

    columns = [
        "rank",
        "track_name",
        "artist",
        "genre",
        "mood",
    ]
    columns = [column for column in columns if column in top_10.columns]

    st.dataframe(
        top_10[columns],
        width="stretch",
        hide_index=True,
        height=390,
    )


def render_recent_searches(user_id):
    """
    Show the logged-in user's recent searches.

    This function is displayed inside the top Search popover,
    so Recent Searches only appear after the user opens Search.
    """

    recent_searches = get_recent_searches(
        user_id,
        limit=RECENT_SEARCH_LIMIT,
    )

    title_col, clear_col = st.columns([4, 1])

    with title_col:
        st.markdown("#### Recent searches")
        st.caption("Continue from a song you selected earlier.")

    with clear_col:
        if recent_searches and st.button(
            "Clear",
            key="clear_history",
            width="stretch",
        ):
            clear_search_history(user_id)
            st.rerun()

    if not recent_searches:
        st.caption(
            "No recent searches yet. "
            "Search for a song to get started."
        )
        return

    # Keep every recent-search record available,
    # but scroll inside the dropdown instead of the whole page.
    with st.container(
        height=360,
        key="recent_search_list",
    ):
        for index, song in enumerate(recent_searches):
            normal_song = {
                "track_name": song["track_name"],
                "artists": song["artist"],
                "track_genre": song["genre"],
                "mood": song["mood"],
            }

            label = (
                f"♫  {song['track_name']}  —  {song['artist']}"
                f"   ·   {song['genre']}   ·   {song['mood']}"
            )

            if st.button(
                label,
                key=f"recent_song_{index}",
                width="stretch",
            ):
                handle_song_selection(
                    normal_song,
                    user_id,
                )



def render_collaborative_for_you(user_id):
    """
    Show personalized Collaborative recommendations
    in one horizontally scrollable row.

    The Collaborative score and explanation are used
    internally but are hidden from normal users.
    """

    from models.collaborative import (
        MIN_USER_RATINGS,
        recommend_for_user,
    )

    st.markdown("#### Recommended for you")
    st.caption(
        "Personalized from your ratings using "
        "User-Based and Item-Based Collaborative Filtering. "
        "Swipe or scroll left and right to view more songs."
    )

    rating_count = get_rating_count(user_id)

    if rating_count < MIN_USER_RATINGS:
        remaining = MIN_USER_RATINGS - rating_count

        st.info(
            f"Rate {remaining} more song(s) to unlock "
            "Collaborative recommendations."
        )
        return

    recommendations = recommend_for_user(
        user_id,
        top_n=10,
    )

    if not recommendations:
        st.info(
            "No Collaborative recommendations are available yet."
        )
        return

    def shorten(value, limit):
        value = str(value)

        if len(value) <= limit:
            return value

        return value[: limit - 1] + "…"

    with st.container(
        horizontal=True,
        wrap=False,
        gap="small",
    ):
        for index, song in enumerate(recommendations):
            normal_song = {
                "track_name": song["track_name"],
                "artists": song["artist"],
                "track_genre": song["genre"],
                "mood": song["mood"],
            }

            with st.container(
                border=True,
                width=240,
            ):
                st.markdown("### 🎵")

                st.markdown(
                    f"**{shorten(song['track_name'], 25)}**"
                )

                st.caption(
                    shorten(
                        song["artist"],
                        28,
                    )
                )

                st.caption(
                    f"{song['genre']} · {song['mood']}"
                )

                # Collaborative score and explanation are intentionally
                # hidden from normal users. Admin can inspect them
                # on the Results / Admin Review pages.

                if st.button(
                    "Select song",
                    key=f"personalized_song_{index}",
                    width="stretch",
                ):
                    handle_song_selection(
                        normal_song,
                        user_id,
                    )



def load_current_user_ratings(user_id):
    """
    Load ratings for the currently logged-in user only.
    """

    if not RATINGS_PATH.exists():
        return pd.DataFrame()

    ratings = pd.read_csv(
        RATINGS_PATH,
        dtype=str,
    ).fillna("")

    if "user_id" not in ratings.columns:
        return pd.DataFrame()

    target_user = str(user_id).strip().casefold()

    user_ratings = ratings[
        ratings["user_id"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq(target_user)
    ].copy()

    if user_ratings.empty:
        return user_ratings

    if "rating" in user_ratings.columns:
        user_ratings["rating"] = pd.to_numeric(
            user_ratings["rating"],
            errors="coerce",
        )

    if "rated_at" in user_ratings.columns:
        user_ratings = user_ratings.sort_values(
            "rated_at",
            ascending=False,
        )

    return user_ratings.reset_index(drop=True)



def get_user_taste_profile(user_id):
    """
    Build a simple taste profile from the logged-in user's
    existing ratings. No new dataset is created.
    """

    ratings = load_current_user_ratings(user_id)

    profile = {
        "rating_count": 0,
        "liked_count": 0,
        "average_rating": 0.0,
        "favourite_genre": "Not enough data",
        "favourite_mood": "Not enough data",
    }

    if ratings.empty:
        return profile

    profile["rating_count"] = len(ratings)

    numeric_ratings = pd.to_numeric(
        ratings["rating"],
        errors="coerce",
    )

    if numeric_ratings.notna().any():
        profile["average_rating"] = float(
            numeric_ratings.mean()
        )

    liked = ratings[
        numeric_ratings >= 4
    ].copy()

    profile["liked_count"] = len(liked)

    # Prefer liked songs when learning the user's taste.
    taste_source = (
        liked
        if not liked.empty
        else ratings
    )

    if "genre" in taste_source.columns:
        genre_counts = (
            taste_source["genre"]
            .replace("", pd.NA)
            .dropna()
            .value_counts()
        )

        if not genre_counts.empty:
            profile["favourite_genre"] = (
                genre_counts.index[0]
            )

    if "mood" in taste_source.columns:
        mood_counts = (
            taste_source["mood"]
            .replace("", pd.NA)
            .dropna()
            .value_counts()
        )

        if not mood_counts.empty:
            profile["favourite_mood"] = (
                mood_counts.index[0]
            )

    return profile


def render_continue_listening(user_id):
    """
    Show a clean Continue Listening row using
    the user's latest selected songs.
    """

    recent = get_recent_searches(
        user_id,
        limit=4,
    )

    if not recent:
        return

    st.markdown("#### Continue listening")
    st.caption(
        "Jump back into songs you selected recently."
    )

    columns = st.columns(
        len(recent)
    )

    for index, song in enumerate(recent):
        normal_song = {
            "track_name": song["track_name"],
            "artists": song["artist"],
            "track_genre": song["genre"],
            "mood": song["mood"],
        }

        with columns[index]:
            with st.container(
                border=True
            ):
                icon_col, details_col = st.columns(
                    [0.55, 2.45],
                    vertical_alignment="center",
                )

                with icon_col:
                    st.markdown(
                        "<div style='font-size:42px; text-align:center;'>🎵</div>",
                        unsafe_allow_html=True,
                    )

                with details_col:
                    track_name = str(
                        song["track_name"]
                    )

                    artist = str(
                        song["artist"]
                    )

                    if len(track_name) > 27:
                        track_name = (
                            track_name[:26]
                            + "…"
                        )

                    if len(artist) > 25:
                        artist = (
                            artist[:24]
                            + "…"
                        )

                    st.markdown(
                        f"**{track_name}**"
                    )

                    st.caption(
                        artist
                    )

                    st.caption(
                        f"{song['genre']} · {song['mood']}"
                    )

                if st.button(
                    "Open song",
                    key=f"continue_song_{index}",
                    width="stretch",
                ):
                    handle_song_selection(
                        normal_song,
                        user_id,
                    )



def render_browse_music(
    user_id,
    search_songs,
):
    """
    Browse songs by mood or genre.

    The results are displayed as compact music cards.
    This only filters the existing Spotify dataset.
    """

    st.markdown("#### Browse your sound")
    st.caption(
        "Explore music by mood or genre."
    )

    # -----------------------------------------------------
    # MOOD FILTER
    # -----------------------------------------------------

    mood_values = [
        "Happy",
        "Sad",
        "Chill",
        "Angry",
    ]

    st.caption("Mood")

    with st.container(
        key="mood_buttons"
    ):
        mood_columns = st.columns(
            len(mood_values)
        )

        for index, mood in enumerate(
            mood_values
        ):
            with mood_columns[index]:
                if st.button(
                    mood,
                    key=f"browse_mood_{index}",
                    width="stretch",
                ):
                    st.session_state[
                        "browse_music_type"
                    ] = "mood"

                    st.session_state[
                        "browse_music_value"
                    ] = mood

    # -----------------------------------------------------
    # GENRE FILTER
    # -----------------------------------------------------

    top_genres = (
        search_songs["track_genre"]
        .astype(str)
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    st.caption("Popular genres")

    with st.container(
        key="genre_buttons"
    ):
        genre_columns = st.columns(
            max(
                len(top_genres),
                1,
            )
        )

        for index, genre in enumerate(
            top_genres
        ):
            with genre_columns[index]:
                if st.button(
                    str(genre).title(),
                    key=f"browse_genre_{index}",
                    width="stretch",
                ):
                    st.session_state[
                        "browse_music_type"
                    ] = "genre"

                    st.session_state[
                        "browse_music_value"
                    ] = genre

    # -----------------------------------------------------
    # SELECTED FILTER
    # -----------------------------------------------------

    browse_type = st.session_state.get(
        "browse_music_type"
    )

    browse_value = st.session_state.get(
        "browse_music_value"
    )

    if not browse_type or not browse_value:
        return

    if browse_type == "mood":
        matches = search_songs[
            search_songs["mood"]
            .astype(str)
            .str.casefold()
            .eq(
                str(
                    browse_value
                ).casefold()
            )
        ]

    else:
        matches = search_songs[
            search_songs["track_genre"]
            .astype(str)
            .str.casefold()
            .eq(
                str(
                    browse_value
                ).casefold()
            )
        ]

    matches = (
        matches
        .drop_duplicates(
            subset=[
                "track_name",
                "artists",
            ]
        )
        .head(8)
        .to_dict("records")
    )

    if not matches:
        st.info(
            f"No songs found for {browse_value}."
        )
        return

    # -----------------------------------------------------
    # RESULT HEADER
    # -----------------------------------------------------

    if browse_type == "mood":
        result_title = (
            f"{browse_value} mood"
        )
    else:
        result_title = (
            f"{str(browse_value).title()} genre"
        )

    title_col, close_col = st.columns(
        [5, 1],
        vertical_alignment="center",
    )

    with title_col:
        st.markdown(
            f"### {result_title}"
        )

        st.caption(
            f"{len(matches)} songs found"
        )

    with close_col:
        if st.button(
            "Close",
            key="close_browse_music",
            width="stretch",
        ):
            st.session_state.pop(
                "browse_music_type",
                None,
            )

            st.session_state.pop(
                "browse_music_value",
                None,
            )

            st.rerun()

    # -----------------------------------------------------
    # RESULT CARDS
    # -----------------------------------------------------

    def shorten(
        value,
        limit,
    ):
        value = str(value)

        if len(value) <= limit:
            return value

        return (
            value[: limit - 1]
            + "…"
        )

    with st.container(
        key="browse_results"
    ):
        # Four cards per row keeps the page compact.
        for row_start in range(
            0,
            len(matches),
            4,
        ):
            row_songs = matches[
                row_start:
                row_start + 4
            ]

            columns = st.columns(
                4
            )

            for offset, song in enumerate(
                row_songs
            ):
                index = (
                    row_start
                    + offset
                )

                with columns[offset]:
                    with st.container(
                        border=True
                    ):
                        # Music icon area
                        st.markdown(
                            """
                            <div style="
                                font-size: 36px;
                                margin-bottom: 8px;
                            ">
                                🎵
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Song information
                        st.markdown(
                            f"**{shorten(song['track_name'], 29)}**"
                        )

                        st.caption(
                            shorten(
                                song["artists"],
                                31,
                            )
                        )

                        st.caption(
                            f"{song['track_genre']} · "
                            f"{song['mood']}"
                        )

                        # Open the song using the existing
                        # recommendation-generation flow.
                        if st.button(
                            "Open song",
                            key=f"browse_song_{index}",
                            width="stretch",
                        ):
                            handle_song_selection(
                                song,
                                user_id,
                            )



def render_user_ratings(user_id):
    """
    Personal library for the logged-in user.

    Includes:
    - Taste Profile
    - Liked Songs (ratings 4-5)
    - Complete Rating History
    """

    user_ratings = load_current_user_ratings(
        user_id
    )

    profile = get_user_taste_profile(
        user_id
    )

    library_title = (
        f"Your music library · "
        f"{profile['rating_count']} rated songs"
    )

    with st.container(
        key="library_panel"
    ):
        with st.expander(
            library_title,
            expanded=False,
        ):
            if user_ratings.empty:
                st.info(
                    "You have not rated any songs yet."
                )
                return

            profile_tab, liked_tab, ratings_tab = (
                st.tabs(
                    [
                        "Taste Profile",
                        "Liked Songs",
                        "All Ratings",
                    ]
                )
            )

            # -------------------------------------------------
            # TASTE PROFILE
            # -------------------------------------------------

            with profile_tab:
                st.caption(
                    "A simple profile learned from "
                    "your existing rating history."
                )

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Rated Songs",
                    profile["rating_count"],
                )

                c2.metric(
                    "Average Rating",
                    (
                        f"{profile['average_rating']:.2f}/5"
                    ),
                )

                c3.metric(
                    "Favourite Genre",
                    profile["favourite_genre"],
                )

                c4.metric(
                    "Favourite Mood",
                    profile["favourite_mood"],
                )

                from models.collaborative import (
                    MIN_USER_RATINGS,
                )

                if (
                    profile["rating_count"]
                    >= MIN_USER_RATINGS
                ):
                    st.success(
                        "Personalized Collaborative "
                        "recommendations are active."
                    )
                else:
                    remaining = (
                        MIN_USER_RATINGS
                        - profile["rating_count"]
                    )

                    st.info(
                        f"Rate {remaining} more song(s) "
                        "to activate Collaborative "
                        "personalization."
                    )

            # -------------------------------------------------
            # LIKED SONGS
            # -------------------------------------------------

            with liked_tab:
                liked_songs = user_ratings[
                    pd.to_numeric(
                        user_ratings["rating"],
                        errors="coerce",
                    )
                    >= 4
                ].copy()

                st.caption(
                    "Songs rated 4 or 5 are treated "
                    "as liked songs."
                )

                if liked_songs.empty:
                    st.info(
                        "No liked songs yet."
                    )
                else:
                    st.metric(
                        "Liked Songs",
                        len(liked_songs),
                    )

                    with st.container(
                        key="liked_songs"
                    ):
                        liked_columns = st.columns(3)

                        for index, row in enumerate(
                            liked_songs
                            .head(9)
                            .to_dict("records")
                        ):
                            normal_song = {
                                "track_name":
                                    row["track_name"],

                                "artists":
                                    row["artist"],

                                "track_genre":
                                    row["genre"],

                                "mood":
                                    row["mood"],
                            }

                            with liked_columns[
                                index % 3
                            ]:
                                if st.button(
                                    (
                                        f"♥ {row['track_name']}"
                                        f"\n\n{row['artist']} "
                                        f"· {int(row['rating'])} ★"
                                    ),
                                    key=f"liked_song_{index}",
                                    width="stretch",
                                ):
                                    handle_song_selection(
                                        normal_song,
                                        user_id,
                                    )

            # -------------------------------------------------
            # ALL RATINGS
            # -------------------------------------------------

            with ratings_tab:
                st.caption(
                    "All ratings belong to your "
                    "logged-in account only."
                )

                columns = [
                    "track_name",
                    "artist",
                    "genre",
                    "mood",
                    "rating",
                    "rated_at",
                ]

                visible_columns = [
                    column
                    for column in columns
                    if column
                    in user_ratings.columns
                ]

                st.dataframe(
                    user_ratings[
                        visible_columns
                    ],
                    width="stretch",
                    hide_index=True,
                    height=390,
                )



def render_search_results(query, search_songs, user_id):
    """
    Show song matches inside the Search popover.
    """

    matches = filter_song_options(
        query,
        search_songs,
        limit=10,
    )

    st.markdown("#### Search results")
    st.caption(f"Top matches for '{query}'")

    if not matches:
        st.warning(
            "No matching songs found.",
            icon=":material/search_off:",
        )
        return

    with st.container(
        height=400,
        key="search_results_list",
    ):
        for index, song in enumerate(matches):
            label = (
                f"♫  {song['track_name']}  —  {song['artists']}"
                f"   ·   {song['track_genre']}   ·   {song['mood']}"
            )

            if st.button(
                label,
                key=f"search_song_{index}",
                width="stretch",
            ):
                handle_song_selection(
                    song,
                    user_id,
                )



def render_rating_section(user_id):
    song = st.session_state.get("selected_song_details")
    if not song:
        return

    st.space("small")
    with st.container(border=True):
        st.subheader("Rate the song you selected")
        st.caption("Rate the selected song from 1 to 5.")
        st.write(f"**{song['track_name']}** — {song['artists']}")
        st.caption(f"{song['track_genre']} · {song['mood']}")

        previous_rating = get_song_rating(
            user_id,
            song["track_name"],
            song["artists"],
        )

        if previous_rating is not None:
            st.info(f"You previously rated this song {previous_rating}/5.")

        rating_value = st.select_slider(
            "Your rating",
            options=[1, 2, 3, 4, 5],
            value=previous_rating if previous_rating is not None else 3,
            format_func=lambda value: f"{value} ★",
            key=f"rating_{user_id}_{song['track_name']}_{song['artists']}",
        )

        st.caption(
            "1 = Strongly dislike · 2 = Dislike · 3 = Neutral · "
            "4 = Like · 5 = Strongly like"
        )

        if st.button(
            "Save Rating",
            key=f"save_rating_{user_id}_{song['track_name']}_{song['artists']}",
            width="stretch",
        ):
            success, message = save_rating(user_id, song, rating_value)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        rating_count = get_rating_count(user_id)
        label = "song" if rating_count == 1 else "songs"
        st.caption(f"You have rated {rating_count} {label}.")


def render_discover_page():
    """
    Main SoundScope listener workspace.

    The layout follows common music-app usability patterns:
    - Search stays in the top application bar.
    - Recent searches appear only when Search is opened.
    - Personalized recommendations are the main Home content.
    - Final Top 10 and rating controls sit side-by-side.
    - Full rating history stays available in a collapsed library section.
    """

    user_id = st.session_state["user_id"]
    username = st.session_state["username"]
    role = st.session_state.get("role", "user")
    songs, search_songs = get_song_options()

    # -----------------------------------------------------
    # TOP APPLICATION BAR
    # -----------------------------------------------------

    logo_col, search_col, account_col = st.columns(
        [1.35, 4.0, 1.55],
        vertical_alignment="center",
    )

    with logo_col:
        st.markdown("## SoundScope")
        st.caption("Music Recommendation")

    with search_col:
        # Streamlit does not expose a reliable Python mouse-hover/focus event.
        # A popover gives the closest stable Spotify-style search experience:
        # the recent-search panel appears only after Search is clicked.
        with st.container(key="top_search"):
            with st.popover("⌕  What do you want to play?"):
                query = st.text_input(
                    "Search music",
                    placeholder="Song, artist, genre or mood",
                    key="song_search_query",
                    label_visibility="collapsed",
                )

                if query.strip():
                    render_search_results(
                        query,
                        search_songs,
                        user_id,
                    )
                else:
                    render_recent_searches(
                        user_id
                    )


    with account_col:
        role_label = (
            "Admin"
            if role == "admin"
            else "Listener"
        )

        st.caption(
            f"{username} · {user_id}"
        )

        st.caption(role_label)

        if st.button(
            "Logout",
            width="stretch",
        ):
            logout()

    st.divider()

    # -----------------------------------------------------
    # HOME HEADER + SYSTEM INFORMATION
    # -----------------------------------------------------

    title_col, metric_col1, metric_col2, metric_col3 = st.columns(
        [2.4, 1, 1, 1],
        vertical_alignment="center",
    )

    with title_col:
        st.title(
            f"Made for {username}",
            anchor=False,
        )

        st.caption(
            "Personalized music discovery powered by "
            "Content-Based, Collaborative, and Hybrid recommendation."
        )

    with metric_col1:
        st.metric(
            "Tracks",
            f"{len(songs):,}",
        )

    with metric_col2:
        st.metric(
            "Users",
            f"{get_user_count():,}",
        )

    with metric_col3:
        st.metric(
            "Models",
            3,
        )

    # -----------------------------------------------------
    # PERSONALIZED HOME FEED
    # -----------------------------------------------------

    if role == "user":
        st.space("small")

        with st.container(
            border=True,
            key="recommendation_home",
        ):
            render_collaborative_for_you(
                user_id
            )

        st.space("small")
        render_continue_listening(
            user_id
        )

        st.space("small")
        render_browse_music(
            user_id,
            search_songs,
        )

    # -----------------------------------------------------
    # CURRENT RECOMMENDATION
    # -----------------------------------------------------

    final_results = st.session_state.get(
        "final_results",
        [],
    )

    if final_results:
        st.space("small")

        result_col, rating_col = st.columns(
            [2.5, 1],
            vertical_alignment="top",
        )

        with result_col:
            with st.container(border=True):
                render_top_10(
                    final_results
                )

        with rating_col:
            render_rating_section(
                user_id
            )

        st.caption(
            f"Recommendations are personalized for "
            f"{username} ({user_id})."
        )

        if role == "admin":
            st.caption(
                "Use the sidebar to open Results, "
                "Evaluation, Rate Music, User Data, "
                "and Admin Review."
            )

    else:
        st.space("small")

        st.info(
            "Open Search above and choose a song to generate "
            "your Hybrid Top 10 recommendations."
        )

    # -----------------------------------------------------
    # PERSONAL LIBRARY
    # -----------------------------------------------------

    if role == "user":
        st.space("small")
        render_user_ratings(
            user_id
        )



def run_navigation():
    discover_page = st.Page(
        render_discover_page,
        title="Discover",
        default=True,
    )

    if st.session_state.get("role") == "admin":
        navigation = st.navigation(
            {
                "SoundScope": [discover_page],
                "Admin Access": [
                    st.Page("pages/1_Results.py", title="Results"),
                    st.Page("pages/2_Evaluation.py", title="Evaluation"),
                    st.Page("pages/3_Rate_Music.py", title="Rate Music"),
                    st.Page("pages/4_Admin.py",title="User Data"),
                    st.Page("pages/testResult.py",title="Admin Review"),
                ],
            }
        )
    else:
        # Normal users only have access to app.py / Discover.
        navigation = st.navigation([discover_page], position="hidden")

    navigation.run()


def main():
    init_session()

    if not st.session_state["logged_in"]:
        render_auth_page()
        return

    run_navigation()


if __name__ == "__main__":
    main()
