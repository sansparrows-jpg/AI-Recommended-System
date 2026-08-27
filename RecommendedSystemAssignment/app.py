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

st.set_page_config(
    page_title="SoundScope",
    page_icon="music",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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

    st.success("Recommendations generated successfully.")


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
        "popularity",
        "final_score",
    ]
    columns = [column for column in columns if column in top_10.columns]

    st.dataframe(top_10[columns], width="stretch", hide_index=True)


def render_recent_searches(user_id):
    recent_searches = get_recent_searches(user_id, limit=RECENT_SEARCH_LIMIT)
    title_col, clear_col = st.columns([8, 1])

    with title_col:
        st.markdown("#### Recent searches")

    with clear_col:
        if recent_searches and st.button(
            "Clear",
            key="clear_history",
            width="stretch",
        ):
            clear_search_history(user_id)
            st.rerun()

    if not recent_searches:
        st.caption("No recent searches yet. Search for a song to get started.")
        return

    for index, song in enumerate(recent_searches):
        normal_song = {
            "track_name": song["track_name"],
            "artists": song["artist"],
            "track_genre": song["genre"],
            "mood": song["mood"],
        }
        label = (
            f"🎵  {song['track_name']}  —  {song['artist']}"
            f"  ·  {song['genre']}  ·  {song['mood']}"
        )

        if st.button(label, key=f"recent_song_{index}", width="stretch"):
            handle_song_selection(normal_song, user_id)



def render_collaborative_for_you(user_id):
    """
    Show personalized Collaborative recommendations
    in square cards inside one horizontally scrollable row.
    """

    from models.collaborative import MIN_USER_RATINGS, recommend_for_user

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

    def shorten(text, limit):
        text = str(text)
        return text if len(text) <= limit else text[: limit - 1] + "…"

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

            score = float(
                song.get("collaborative_score", 0)
                or 0
            )

            with st.container(
                border=True,
                width=240,
            ):
                st.markdown("### 🎵")

                st.markdown(
                    f"**{shorten(song['track_name'], 24)}**"
                )

                st.caption(
                    shorten(song["artist"], 26)
                )

                st.caption(
                    f"{song['genre']} · {song['mood']}"
                )

                st.markdown(
                    f"**Collaborative Score:** {score:.3f}"
                )

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


def render_user_ratings(user_id):
    """
    Display the full rating history of
    the currently logged-in user only.
    """

    user_ratings = load_current_user_ratings(
        user_id
    )

    st.space("small")

    with st.container(border=True):
        st.subheader("Your ratings")
        st.caption(
            "All songs rated by your account. "
            "Ratings from other users are not shown."
        )

        if user_ratings.empty:
            st.info("You have not rated any songs yet.")
            return

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
            if column in user_ratings.columns
        ]

        st.caption(
            f"{len(user_ratings)} rated "
            f"{'song' if len(user_ratings) == 1 else 'songs'}."
        )

        st.dataframe(
            user_ratings[visible_columns],
            width="stretch",
            hide_index=True,
        )

def render_search_results(query, search_songs, user_id):
    matches = filter_song_options(query, search_songs, limit=10)

    st.markdown("#### Search results")
    st.caption(f"Showing results for '{query}'")

    if not matches:
        st.warning("No matching songs found.", icon=":material/search_off:")
        return

    for index, song in enumerate(matches):
        label = (
            f"🎵  {song['track_name']}  —  {song['artists']}"
            f"  ·  {song['track_genre']}  ·  {song['mood']}"
        )

        if st.button(label, key=f"search_song_{index}", width="stretch"):
            handle_song_selection(song, user_id)


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
    user_id = st.session_state["user_id"]
    username = st.session_state["username"]
    role = st.session_state.get("role", "user")
    songs, search_songs = get_song_options()

    account_col, logout_col = st.columns([5, 1])

    with account_col:
        role_label = "Admin" if role == "admin" else "User"
        st.caption(f"Logged in as {username} ({user_id}) · {role_label}")

    with logout_col:
        if st.button("Logout", width="stretch"):
            logout()

    st.title("SoundScope", anchor=False)
    st.caption(
        "AI-powered music recommendations with Content-Based, "
        "Collaborative, and Hybrid ranking."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric("Tracks", f"{len(songs):,}")
    with col2:
        with st.container(border=True):
            st.metric("Users", f"{get_user_count():,}")
    with col3:
        with st.container(border=True):
            st.metric("Models", 3)

    st.space("small")
    st.subheader("Discover music")

    query = st.text_input(
        "Search",
        placeholder="What do you want to play?",
        key="song_search_query",
        label_visibility="collapsed",
    )

    # Search / Recent Searches section
    with st.container(border=True):
        if query.strip():
            render_search_results(query, search_songs, user_id)
        else:
            render_recent_searches(user_id)

    # Recommended for You is a separate section
    if role == "user" and not query.strip():
        st.space("small")

        with st.container(border=True):
            render_collaborative_for_you(user_id)

    st.caption(f"Recommendations are personalized for {username} ({user_id}).")

    final_results = st.session_state.get("final_results", [])
    if final_results:
        st.space("small")
        render_top_10(final_results)

        if role == "admin":
            st.caption(
                "Use the sidebar to open Results, Evaluation, and Rate Music."
            )

    render_rating_section(user_id)

    if role == "user":
        render_user_ratings(user_id)


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
