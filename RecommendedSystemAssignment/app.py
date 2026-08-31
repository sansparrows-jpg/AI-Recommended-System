# SoundScope - Streamlit Main Application

from pathlib import Path
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from models.auth import authenticate, load_users, register_user
from models.history import add_search_history, clear_search_history, get_recent_searches
from models.preprocessing import preprocess_data
from models.ratings import get_rating_count, get_song_rating, save_rating

from spotify_auth import (
    disconnect_spotify,
    get_spotify_login_url,
    handle_spotify_callback,
    spotify_is_connected,
)

RECENT_SEARCH_LIMIT = 20

RATINGS_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "real_user_ratings.csv"
)

TRACKS_DATA_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "spotify-tracks-dataset-detailed.csv"
)


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


        /* ================================================
           SPOTIFY ALBUM COVER CARDS
        ================================================ */

        .stImage img {
            border-radius: 12px !important;
        }

        .st-key-browse_results [data-testid="stImage"] img {
            aspect-ratio: 1 / 1;
            object-fit: contain;
            background: rgba(10, 10, 18, 0.75);
        }


        /* ================================================
           REFINED SONG CARDS
        ================================================ */

        .st-key-recommended_cards [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 470px !important;
            background:
                linear-gradient(
                    145deg,
                    rgba(22, 21, 36, 0.96),
                    rgba(12, 12, 22, 0.98)
                ) !important;
            border: 1px solid rgba(167, 139, 250, 0.18) !important;
            border-radius: 16px !important;
            overflow: hidden;
        }

        .st-key-recommended_cards [data-testid="stImage"] img {
            width: 100% !important;
            aspect-ratio: 1 / 1;
            object-fit: cover !important;
            border-radius: 13px !important;
        }

        .st-key-recommended_cards .stButton > button {
            min-height: 42px !important;
            justify-content: center !important;
            text-align: center !important;
        }

        .st-key-recent_search_list [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-search_results_list [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(19, 19, 32, 0.94) !important;
            border: 1px solid rgba(167, 139, 250, 0.12) !important;
            border-radius: 12px !important;
            padding: 0.35rem !important;
        }

        .st-key-recent_search_list [data-testid="stImage"] img,
        .st-key-search_results_list [data-testid="stImage"] img {
            width: 58px !important;
            height: 58px !important;
            object-fit: cover !important;
            border-radius: 10px !important;
        }

        .st-key-recent_search_list .stButton > button,
        .st-key-search_results_list .stButton > button {
            background: transparent !important;
            border: none !important;
            min-height: 62px !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 0.35rem 0.55rem !important;
            box-shadow: none !important;
        }

        .st-key-recent_search_list .stButton > button:hover,
        .st-key-search_results_list .stButton > button:hover {
            background: rgba(139, 92, 246, 0.10) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .st-key-continue_listening [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 185px !important;
            background:
                linear-gradient(
                    145deg,
                    rgba(22, 21, 36, 0.94),
                    rgba(12, 12, 22, 0.97)
                ) !important;
            border: 1px solid rgba(167, 139, 250, 0.16) !important;
            border-radius: 15px !important;
        }

        .st-key-continue_listening .stButton > button {
            min-height: 42px !important;
            justify-content: center !important;
            text-align: center !important;
        }


        /* ================================================
           LIKED SONGS - CONSISTENT MUSIC CARDS
        ================================================ */

        .st-key-liked_songs [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 420px !important;
            background:
                linear-gradient(
                    145deg,
                    rgba(22, 21, 36, 0.96),
                    rgba(12, 12, 22, 0.98)
                ) !important;
            border:
                1px solid
                rgba(167, 139, 250, 0.17)
                !important;
            border-radius:
                16px !important;
            overflow: visible !important;
        }

        .st-key-liked_songs [data-testid="stImage"] img {
            width: 100% !important;
            height: 255px !important;
            object-fit: cover !important;
            border-radius: 13px !important;
        }

        .st-key-liked_songs .stButton > button {
            min-height: 42px !important;
            text-align: center !important;
            justify-content: center !important;
        }


        /* ================================================
           SEARCH POPOVER - FIXED CONSISTENT WIDTH
        ================================================ */

        [data-testid="stPopoverBody"] {
            width: min(820px, calc(100vw - 2rem)) !important;
            max-width: min(820px, calc(100vw - 2rem)) !important;
        }

        .st-key-recent_search_list,
        .st-key-search_results_list {
            width: 100% !important;
        }

        .st-key-recent_search_list [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-search_results_list [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 82px !important;
            width: 100% !important;
            background:
                rgba(18, 18, 30, 0.94)
                !important;
            border:
                1px solid
                rgba(167, 139, 250, 0.14)
                !important;
            border-radius:
                12px !important;
            padding:
                0.40rem 0.55rem !important;
            overflow: hidden !important;
        }

        .st-key-recent_search_list [data-testid="stImage"] img,
        .st-key-search_results_list [data-testid="stImage"] img {
            width: 58px !important;
            height: 58px !important;
            object-fit: cover !important;
            border-radius: 9px !important;
        }

        .st-key-recent_search_list .stButton > button,
        .st-key-search_results_list .stButton > button {
            min-height: 36px !important;
            width: 100% !important;
            padding: 0.25rem 0.70rem !important;
            border-radius: 9px !important;
            text-align: center !important;
            justify-content: center !important;
            background:
                rgba(139, 92, 246, 0.14)
                !important;
            border:
                1px solid
                rgba(167, 139, 250, 0.18)
                !important;
        }

        .st-key-recent_search_list .stButton > button:hover,
        .st-key-search_results_list .stButton > button:hover {
            background:
                rgba(139, 92, 246, 0.25)
                !important;
            border-color:
                rgba(214, 179, 106, 0.30)
                !important;
        }





        /* ================================================
           SEARCH 30-SECOND AUDIO PREVIEW
        ================================================ */

        .st-key-recent_search_list iframe,
        .st-key-search_results_list iframe {
            width: 100% !important;
            border-radius: 12px !important;
        }


        /* ================================================
           NOW PLAYING
        ================================================ */

        .st-key-now_playing [data-testid="stVerticalBlockBorderWrapper"] {
            background:
                linear-gradient(
                    135deg,
                    rgba(28, 26, 47, 0.97),
                    rgba(12, 12, 22, 0.98)
                ) !important;
            border:
                1px solid
                rgba(167, 139, 250, 0.20)
                !important;
            border-radius:
                18px !important;
            padding:
                0.65rem !important;
            box-shadow:
                0 14px 34px
                rgba(0, 0, 0, 0.20);
        }

        .st-key-now_playing [data-testid="stImage"] img {
            width: 100% !important;
            aspect-ratio: 1 / 1;
            object-fit: cover !important;
            border-radius: 14px !important;
        }

        .st-key-now_playing iframe {
            border-radius: 14px !important;
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
    # Spotify authorization belongs to the current
    # SoundScope user session, so clear it on logout.
    disconnect_spotify()

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
        "spotify_search_preview",
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

@st.cache_data(show_spinner=False)
def load_track_id_lookup():
    """
    Load only the columns needed to match a SoundScope song
    to its Spotify track_id.

    This does not change the recommendation dataset.
    It is used only for displaying album artwork.
    """

    if not TRACKS_DATA_PATH.exists():
        return pd.DataFrame()

    try:
        lookup = pd.read_csv(
            TRACKS_DATA_PATH,
            usecols=[
                "track_id",
                "track_name",
                "artists",
                "popularity",
            ],
            dtype={
                "track_id": str,
                "track_name": str,
                "artists": str,
            },
        ).fillna("")

    except Exception:
        return pd.DataFrame()

    lookup["popularity"] = pd.to_numeric(
        lookup["popularity"],
        errors="coerce",
    ).fillna(0)

    lookup["track_key"] = (
        lookup["track_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    lookup["artist_key"] = (
        lookup["artists"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    # If duplicates exist, prefer the most popular Spotify track.
    lookup = (
        lookup
        .sort_values(
            "popularity",
            ascending=False,
        )
        .drop_duplicates(
            subset=[
                "track_key",
                "artist_key",
            ]
        )
        .reset_index(drop=True)
    )

    return lookup

def find_spotify_track_id(
    track_name,
    artist,
):
    """
    Find the Spotify track_id for a displayed SoundScope song.
    """

    lookup = load_track_id_lookup()

    if lookup.empty:
        return None

    track_key = (
        str(track_name)
        .strip()
        .casefold()
    )

    artist_key = (
        str(artist)
        .strip()
        .casefold()
    )

    # First try exact title + exact artist field.
    exact = lookup[
        lookup["track_key"].eq(
            track_key
        )
        &
        lookup["artist_key"].eq(
            artist_key
        )
    ]

    if not exact.empty:
        return exact.iloc[0][
            "track_id"
        ]

    # Fallback for multi-artist formatting differences.
    same_title = lookup[
        lookup["track_key"].eq(
            track_key
        )
    ]

    if same_title.empty:
        return None

    first_artist = (
        artist_key
        .split(";")[0]
        .strip()
    )

    if first_artist:
        artist_match = same_title[
            same_title["artist_key"]
            .str.contains(
                first_artist,
                regex=False,
                na=False,
            )
        ]

        if not artist_match.empty:
            return artist_match.iloc[0][
                "track_id"
            ]

    return same_title.iloc[0][
        "track_id"
    ]

@st.cache_data(
    ttl=86400,
    show_spinner=False,
)
def get_spotify_oembed(
    track_id,
):
    """
    Retrieve Spotify preview metadata for one track.

    Spotify oEmbed returns a thumbnail URL that can be
    displayed as the track's album artwork.
    """

    if not track_id:
        return None

    spotify_url = (
        "https://open.spotify.com/track/"
        + str(track_id).strip()
    )

    endpoint = (
        "https://open.spotify.com/oembed?url="
        + quote(
            spotify_url,
            safe="",
        )
    )

    request = Request(
        endpoint,
        headers={
            "User-Agent":
                "SoundScope-Music-Recommendation/1.0"
        },
    )

    try:
        with urlopen(
            request,
            timeout=6,
        ) as response:
            data = json.loads(
                response.read()
                .decode("utf-8")
            )

    except Exception:
        return None

    thumbnail_url = data.get(
        "thumbnail_url"
    )

    if not thumbnail_url:
        return None

    return {
        "image_url":
            thumbnail_url,

        # Spotify's official oEmbed player HTML.
        "embed_html":
            data.get(
                "html",
                "",
            ),

        "spotify_url":
            spotify_url,

        "title":
            data.get(
                "title",
                "",
            ),
    }

def get_song_cover(
    track_name,
    artist,
):
    """
    Return Spotify album-cover information
    for a SoundScope song.
    """

    track_id = find_spotify_track_id(
        track_name,
        artist,
    )

    if not track_id:
        return None

    return get_spotify_oembed(
        track_id
    )

def render_song_cover(
    track_name,
    artist,
    width="stretch",
):
    """
    Display Spotify album artwork when available.

    A music icon is used as a fallback if the network
    is unavailable or the track cannot be matched.
    """

    cover = get_song_cover(
        track_name,
        artist,
    )

    if cover:
        st.image(
            cover["image_url"],
            width=width,
        )

        return cover

    st.markdown(
        """
        <div style="
            min-height:120px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:46px;
            border-radius:14px;
            background:
                linear-gradient(
                    135deg,
                    rgba(110,69,215,0.30),
                    rgba(214,179,106,0.12)
                );
        ">
            🎵
        </div>
        """,
        unsafe_allow_html=True,
    )

    return None

def render_spotify_player(
    track_name,
    artist,
):
    """
    Display Spotify's official embedded player
    for the selected SoundScope song.

    The audio is streamed by Spotify.
    No audio file is copied into this project.
    """

    track_id = find_spotify_track_id(
        track_name,
        artist,
    )

    if not track_id:
        st.info(
            "Spotify playback is not available "
            "for this song."
        )
        return

    spotify_data = get_spotify_oembed(
        track_id
    )

    if not spotify_data:
        st.info(
            "Spotify playback is not available "
            "for this song."
        )
        return

    embed_html = spotify_data.get(
        "embed_html",
        "",
    )

    # Fallback if Spotify oEmbed does not return HTML.
    if not embed_html:
        embed_url = (
            "https://open.spotify.com/embed/track/"
            + str(track_id).strip()
        )

        embed_html = f"""
        <iframe
            src="{embed_url}"
            width="100%"
            height="152"
            frameborder="0"
            allowfullscreen=""
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy">
        </iframe>
        """

    components.html(
        embed_html,
        height=170,
        scrolling=False,
    )

def render_now_playing():
    """
    Show the currently selected song together with
    its album cover and Spotify embedded player.
    """

    song = st.session_state.get(
        "selected_song_details"
    )

    if not song:
        return

    with st.container(
        border=True,
        key="now_playing",
    ):
        st.subheader(
            "Now Playing"
        )

        cover_col, player_col = st.columns(
            [0.9, 3.1],
            vertical_alignment="center",
        )

        with cover_col:
            cover = get_song_cover(
                song["track_name"],
                song["artists"],
            )

            if cover:
                st.image(
                    cover["image_url"],
                    width="stretch",
                )
            else:
                st.markdown(
                    """
                    <div style="
                        width:100%;
                        aspect-ratio:1/1;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        border-radius:14px;
                        font-size:52px;
                        background:
                            linear-gradient(
                                135deg,
                                rgba(110,69,215,0.30),
                                rgba(214,179,106,0.12)
                            );
                    ">
                        🎵
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with player_col:
            st.markdown(
                f"### {song['track_name']}"
            )

            st.caption(
                f"{song['artists']} · "
                f"{song['track_genre']} · "
                f"{song['mood']}"
            )

            render_spotify_player(
                song["track_name"],
                song["artists"],
            )

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

def render_spotify_30_second_embed(
    track_name,
    artist,
):
    """
    Render Spotify's official embedded track player and
    automatically stop playback after 30 seconds.

    This uses the exact Spotify track_id from the dataset.
    It does not depend on Spotify's deprecated preview_url.
    """

    track_id = find_spotify_track_id(
        track_name,
        artist,
    )

    if not track_id:
        st.info(
            "Spotify playback is not available "
            "for this song."
        )
        return

    # Every Streamlit component is isolated in its own iframe,
    # so this HTML can safely create one Spotify player.
    player_id = (
        "spotify_player_"
        + "".join(
            char
            for char in str(track_id)
            if char.isalnum()
        )
    )

    spotify_uri = (
        "spotify:track:"
        + str(track_id).strip()
    )

    preview_html = f"""
    <div
        id="{player_id}"
        style="
            width:100%;
            min-height:82px;
        ">
    </div>

    <script
        src="https://open.spotify.com/embed/iframe-api/v1"
        async>
    </script>

    <script>
        window.onSpotifyIframeApiReady = (IFrameAPI) => {{
            const element = document.getElementById(
                "{player_id}"
            );

            const options = {{
                width: "100%",
                height: 80,
                uri: "{spotify_uri}",
                theme: "dark"
            }};

            const callback = (EmbedController) => {{
                let hasStoppedAtThirty = false;

                EmbedController.addListener(
                    "playback_update",
                    (event) => {{
                        const state = event.data;

                        if (
                            !hasStoppedAtThirty &&
                            !state.isPaused &&
                            state.position >= 30000
                        ) {{
                            hasStoppedAtThirty = true;

                            EmbedController.pause();

                            // Return to the start so the next
                            // play gives another 30-second sample.
                            setTimeout(
                                () => {{
                                    EmbedController.seek(0);
                                    hasStoppedAtThirty = false;
                                }},
                                250
                            );
                        }}

                        if (
                            state.position < 30000 &&
                            state.isPaused
                        ) {{
                            hasStoppedAtThirty = false;
                        }}
                    }}
                );
            }};

            IFrameAPI.createController(
                element,
                options,
                callback
            );
        }};
    </script>
    """

    components.html(
        preview_html,
        height=92,
        scrolling=False,
    )

def render_search_song_row(
    song,
    user_id,
    button_key,
):
    """
    Display one compact song row with:
    - album artwork
    - song information
    - Spotify 30-second player
    - Open button

    Recent Searches and Search Results share this
    same component so both layouts stay consistent.
    """

    track_name = str(
        song["track_name"]
    )

    artist = str(
        song["artists"]
    )

    genre = str(
        song["track_genre"]
    )

    mood = str(
        song["mood"]
    )

    preview_state_key = (
        "spotify_search_preview"
    )

    this_preview_key = (
        f"preview_{button_key}"
    )

    with st.container(
        border=True
    ):
        (
            image_col,
            details_col,
            preview_col,
            action_col,
        ) = st.columns(
            [0.75, 3.55, 0.95, 0.85],
            vertical_alignment="center",
        )

        # Album artwork
        with image_col:
            cover = get_song_cover(
                track_name,
                artist,
            )

            if cover:
                st.image(
                    cover["image_url"],
                    width=58,
                )
            else:
                st.markdown(
                    """
                    <div style="
                        width:58px;
                        height:58px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        border-radius:9px;
                        font-size:27px;
                        background:rgba(139,92,246,0.16);
                    ">
                        🎵
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Song information
        with details_col:
            st.markdown(
                f"**{track_name}**"
            )

            st.caption(
                f"{artist} · {genre} · {mood}"
            )

        # Show / hide Spotify player.
        with preview_col:
            preview_is_open = (
                st.session_state.get(
                    preview_state_key
                )
                == this_preview_key
            )

            preview_label = (
                "Hide"
                if preview_is_open
                else "▶ 30s"
            )

            if st.button(
                preview_label,
                key=(
                    f"{this_preview_key}_button"
                ),
                width="stretch",
            ):
                if preview_is_open:
                    st.session_state.pop(
                        preview_state_key,
                        None,
                    )
                else:
                    st.session_state[
                        preview_state_key
                    ] = this_preview_key

                st.rerun()

        # Keep the existing recommendation action.
        with action_col:
            if st.button(
                "Open",
                key=button_key,
                width="stretch",
            ):
                handle_song_selection(
                    song,
                    user_id,
                )

        # Spotify player appears inside this same frame.
        if (
            st.session_state.get(
                preview_state_key
            )
            == this_preview_key
        ):
            st.caption(
                "Spotify preview · automatically stops at 30 seconds"
            )

            render_spotify_30_second_embed(
                track_name,
                artist,
            )

def render_recent_searches(user_id):
    """
    Show recent searches inside the Search popover.
    """

    recent_searches = get_recent_searches(
        user_id,
        limit=RECENT_SEARCH_LIMIT,
    )

    title_col, clear_col = st.columns(
        [4.8, 1]
    )

    with title_col:
        st.markdown("#### Recent searches")
        st.caption(
            "Continue from a song you selected earlier."
        )

    with clear_col:
        if recent_searches and st.button(
            "Clear",
            key="clear_history",
            width="stretch",
        ):
            clear_search_history(
                user_id
            )
            st.rerun()

    if not recent_searches:
        st.caption(
            "No recent searches yet. "
            "Search for a song to get started."
        )
        return

    with st.container(
        height=405,
        width=800,
        key="recent_search_list",
    ):
        for index, song in enumerate(
            recent_searches
        ):
            normal_song = {
                "track_name":
                    song["track_name"],

                "artists":
                    song["artist"],

                "track_genre":
                    song["genre"],

                "mood":
                    song["mood"],
            }

            render_search_song_row(
                normal_song,
                user_id,
                button_key=(
                    f"recent_song_{index}"
                ),
            )

def render_collaborative_for_you(user_id):
    """
    Show personalized Collaborative recommendations
    in a clean horizontally scrollable card row.

    Scores and technical explanations remain hidden
    from normal users.
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

    rating_count = get_rating_count(
        user_id
    )

    if rating_count < MIN_USER_RATINGS:
        remaining = (
            MIN_USER_RATINGS
            - rating_count
        )

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

        return (
            value[: limit - 1]
            + "…"
        )

    with st.container(
        horizontal=True,
        wrap=False,
        gap="small",
        key="recommended_cards",
    ):
        for index, song in enumerate(
            recommendations
        ):
            normal_song = {
                "track_name":
                    song["track_name"],

                "artists":
                    song["artist"],

                "track_genre":
                    song["genre"],

                "mood":
                    song["mood"],
            }

            with st.container(
                border=True,
                width=245,
            ):
                cover = get_song_cover(
                    song["track_name"],
                    song["artist"],
                )

                if cover:
                    st.image(
                        cover["image_url"],
                        width="stretch",
                    )
                else:
                    st.markdown(
                        """
                        <div style="
                            width:100%;
                            aspect-ratio:1/1;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            border-radius:14px;
                            font-size:52px;
                            background:
                                linear-gradient(
                                    135deg,
                                    rgba(110,69,215,0.30),
                                    rgba(214,179,106,0.12)
                                );
                        ">
                            🎵
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"**{shorten(song['track_name'], 25)}**"
                )

                st.caption(
                    shorten(
                        song["artist"],
                        27,
                    )
                )

                st.caption(
                    f"{song['genre']} · "
                    f"{song['mood']}"
                )

                # Recommendation scores are intentionally
                # hidden from normal users.
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
    Show the user's latest selected songs as compact,
    balanced Continue Listening cards.
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

    for index, song in enumerate(
        recent
    ):
        normal_song = {
            "track_name":
                song["track_name"],

            "artists":
                song["artist"],

            "track_genre":
                song["genre"],

            "mood":
                song["mood"],
        }

        with columns[index]:
            with st.container(
                border=True
            ):
                image_col, details_col = st.columns(
                    [0.85, 2.4],
                    vertical_alignment="center",
                )

                with image_col:
                    cover = get_song_cover(
                        song["track_name"],
                        song["artist"],
                    )

                    if cover:
                        st.image(
                            cover["image_url"],
                            width=72,
                        )
                    else:
                        st.markdown(
                            """
                            <div style="
                                width:72px;
                                height:72px;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                border-radius:12px;
                                font-size:34px;
                                background:rgba(139,92,246,0.18);
                            ">
                                🎵
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                with details_col:
                    track_name = str(
                        song["track_name"]
                    )

                    artist = str(
                        song["artist"]
                    )

                    if len(track_name) > 25:
                        track_name = (
                            track_name[:24]
                            + "…"
                        )

                    if len(artist) > 23:
                        artist = (
                            artist[:22]
                            + "…"
                        )

                    st.markdown(
                        f"**{track_name}**"
                    )

                    st.caption(
                        artist
                    )

                    st.caption(
                        f"{song['genre']} · "
                        f"{song['mood']}"
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
                        # Spotify album artwork.
                        cover = render_song_cover(
                            song["track_name"],
                            song["artists"],
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
                        liked_records = (
                            liked_songs
                            .head(8)
                            .to_dict("records")
                        )

                        # Four equal cards per row keeps the
                        # library compact and consistent.
                        for row_start in range(
                            0,
                            len(liked_records),
                            4,
                        ):
                            row_records = liked_records[
                                row_start:
                                row_start + 4
                            ]

                            liked_columns = st.columns(
                                4
                            )

                            for offset, row in enumerate(
                                row_records
                            ):
                                index = (
                                    row_start
                                    + offset
                                )

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
                                    offset
                                ]:
                                    with st.container(
                                        border=True
                                    ):
                                        liked_cover = get_song_cover(
                                            row["track_name"],
                                            row["artist"],
                                        )

                                        if liked_cover:
                                            st.image(
                                                liked_cover[
                                                    "image_url"
                                                ],
                                                width="stretch",
                                            )
                                        else:
                                            st.markdown(
                                                """
                                                <div style="
                                                    width:100%;
                                                    height:255px;
                                                    display:flex;
                                                    align-items:center;
                                                    justify-content:center;
                                                    border-radius:13px;
                                                    font-size:48px;
                                                    background:
                                                        linear-gradient(
                                                            135deg,
                                                            rgba(110,69,215,0.30),
                                                            rgba(214,179,106,0.12)
                                                        );
                                                ">
                                                    🎵
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )

                                        track_name = str(
                                            row["track_name"]
                                        )

                                        artist = str(
                                            row["artist"]
                                        )

                                        if len(track_name) > 24:
                                            track_name = (
                                                track_name[:23]
                                                + "…"
                                            )

                                        if len(artist) > 25:
                                            artist = (
                                                artist[:24]
                                                + "…"
                                            )

                                        st.markdown(
                                            f"**♥ {track_name}**"
                                        )

                                        st.caption(
                                            artist
                                        )

                                        st.caption(
                                            f"{row['genre']} · "
                                            f"{row['mood']} · "
                                            f"{int(row['rating'])} ★"
                                        )

                                        if st.button(
                                            "Open song",
                                            key=(
                                                f"liked_song_{index}"
                                            ),
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

def render_search_results(
    query,
    search_songs,
    user_id,
):
    """
    Show matching songs inside the Search popover.

    Search Results use the same row component as
    Recent Searches so both have equal frame sizes.
    """

    matches = filter_song_options(
        query,
        search_songs,
        limit=10,
    )

    st.markdown("#### Search results")
    st.caption(
        f"Top matches for '{query}'"
    )

    if not matches:
        st.warning(
            "No matching songs found.",
            icon=":material/search_off:",
        )
        return

    with st.container(
        height=405,
        width=800,
        key="search_results_list",
    ):
        for index, song in enumerate(
            matches
        ):
            render_search_song_row(
                song,
                user_id,
                button_key=(
                    f"search_song_{index}"
                ),
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

        # Spotify account connection is available
        # on both localhost and the deployed Streamlit app.
        if spotify_is_connected():
            st.caption("Spotify · Connected")

            if st.button(
                "Disconnect Spotify",
                key="disconnect_spotify",
                width="stretch",
            ):
                disconnect_spotify()
                st.rerun()

        else:
            try:
                spotify_login_url = (
                    get_spotify_login_url()
                )

                st.link_button(
                    "Connect Spotify",
                    spotify_login_url,
                    width="stretch",
                )

            except Exception:
                st.caption(
                    "Spotify configuration is missing."
                )

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

        # Play the selected song using Spotify's official
        # embedded player.
        render_now_playing()

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
                "Evaluation, Rate Music, and User Data."
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
                ],
            }
        )
    else:
        # Normal users only have access to app.py / Discover.
        navigation = st.navigation([discover_page], position="hidden")

    navigation.run()

def main():
    init_session()

    # Handle Spotify OAuth callback for both
    # localhost and the deployed Streamlit app.
    spotify_callback = handle_spotify_callback()

    if spotify_callback == "connected":
        st.toast(
            "Spotify connected successfully.",
            icon="✅",
        )

    elif spotify_callback == "error":
        error_message = st.session_state.get(
            "spotify_auth_error",
            "Spotify connection failed.",
        )

        st.error(
            f"Spotify connection failed: {error_message}"
        )

    if not st.session_state["logged_in"]:
        render_auth_page()
        return

    run_navigation()

if __name__ == "__main__":
    main()
