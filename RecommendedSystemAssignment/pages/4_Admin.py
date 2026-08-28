from pathlib import Path

import pandas as pd
import streamlit as st

from models.auth import load_users
from models.admin_review import (
    generate_user_review,
    get_latest_user_search,
    get_reviewable_users,
)
from models.collaborative import (
    MIN_USER_RATINGS,
    find_nearest_users,
    get_item_recommendation_support,
    get_recommendation_support,
    get_user_similarity_details,
)
from models.ratings import get_rating_count



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
    page_title="User Data",
    page_icon="👥",
    layout="wide",
)

# Apply the luxury music application appearance.
apply_luxury_ui()


# =========================================================
# SECTION HEADER HELPER
# =========================================================

def section_header(title, description=None):
    """
    Display a section title with an optional description.
    This is only a UI helper and does not change any data logic.
    """
    st.subheader(title)

    if description:
        st.caption(description)


# =========================================================
# ADMIN REVIEW HELPERS
# =========================================================

def review_show_table(
    rows,
    columns=None,
    height=360,
):
    """Display Admin Review recommendation data."""
    if not rows:
        st.info(
            "No recommendations available."
        )
        return

    dataframe = pd.DataFrame(
        rows
    )

    if columns:
        visible_columns = [
            column
            for column in columns
            if column in dataframe.columns
        ]

        dataframe = dataframe[
            visible_columns
        ]

    st.dataframe(
        dataframe,
        width="stretch",
        hide_index=True,
        height=height,
    )


def review_show_final_table(rows):
    """Display the final recommendation list as a ranked Top 10."""
    if not rows:
        st.info(
            "No recommendations available."
        )
        return

    dataframe = pd.DataFrame(
        rows
    )

    if "final_score" in dataframe.columns:
        dataframe = dataframe.sort_values(
            "final_score",
            ascending=False,
        )

    dataframe = (
        dataframe
        .head(10)
        .reset_index(drop=True)
    )

    dataframe["rank"] = (
        dataframe.index + 1
    )

    visible_columns = [
        column
        for column in [
            "rank",
            "track_name",
            "artist",
            "genre",
            "mood",
            "popularity",
            "final_score",
        ]
        if column in dataframe.columns
    ]

    st.dataframe(
        dataframe[
            visible_columns
        ],
        width="stretch",
        hide_index=True,
        height=390,
    )


def get_review_source(song):
    """
    Identify whether User-Based KNN,
    Item-Based KNN, or both support a song.
    """
    user_score = float(
        song.get(
            "user_knn_score",
            0,
        )
        or 0
    )

    item_score = float(
        song.get(
            "item_knn_score",
            0,
        )
        or 0
    )

    if (
        user_score > 0
        and item_score > 0
    ):
        return "Both"

    if user_score > 0:
        return "User-Based"

    if item_score > 0:
        return "Item-Based"

    return "None"


def prepare_review_collaborative(rows):
    """Add a readable source to Collaborative results."""
    prepared = []

    for song in rows:
        row = song.copy()
        row["source"] = (
            get_review_source(
                song
            )
        )
        prepared.append(
            row
        )

    return prepared


def format_search_time(raw_search_time):
    """Format a stored search timestamp for display."""
    if not raw_search_time:
        return "Unknown"

    parsed_search_time = pd.to_datetime(
        raw_search_time,
        errors="coerce",
    )

    if pd.notna(
        parsed_search_time
    ):
        return parsed_search_time.strftime(
            "%d %b %Y, %I:%M %p"
        )

    return raw_search_time



# =========================================================
# ADMIN ACCESS
# =========================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please sign in first.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()


# =========================================================
# PATHS / LOADERS
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


@st.cache_data(show_spinner=False)
def load_csv(path_string):
    path = Path(path_string)

    if not path.exists():
        return pd.DataFrame()

    return (
        pd.read_csv(
            path,
            dtype=str,
        )
        .fillna("")
    )


users = load_users()
ratings = load_csv(
    str(RATINGS_PATH)
)
history = load_csv(
    str(HISTORY_PATH)
)

if "role" in users.columns:
    normal_users = users[
        users["role"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("user")
    ].copy()
else:
    normal_users = users.copy()


# =========================================================
# SUMMARY HELPERS
# =========================================================

def build_user_summary():
    columns = [
        column
        for column in [
            "user_id",
            "username",
        ]
        if column in normal_users.columns
    ]

    summary = normal_users[
        columns
    ].copy()

    if (
        not ratings.empty
        and "user_id" in ratings.columns
    ):
        ratings_copy = ratings.copy()

        if "rating" in ratings_copy.columns:
            ratings_copy["rating"] = pd.to_numeric(
                ratings_copy["rating"],
                errors="coerce",
            )

            rating_summary = (
                ratings_copy
                .groupby("user_id")
                .agg(
                    rating_count=(
                        "rating",
                        "count",
                    ),
                    average_rating=(
                        "rating",
                        "mean",
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
                how="left",
            )

    if (
        not history.empty
        and "user_id" in history.columns
    ):
        search_summary = (
            history
            .groupby("user_id")
            .size()
            .reset_index(
                name="search_count"
            )
        )

        summary = summary.merge(
            search_summary,
            on="user_id",
            how="left",
        )

    if "rating_count" not in summary.columns:
        summary["rating_count"] = 0

    if "average_rating" not in summary.columns:
        summary["average_rating"] = 0.0

    if "search_count" not in summary.columns:
        summary["search_count"] = 0

    summary["rating_count"] = (
        summary["rating_count"]
        .fillna(0)
        .astype(int)
    )

    summary["average_rating"] = (
        summary["average_rating"]
        .fillna(0.0)
    )

    summary["search_count"] = (
        summary["search_count"]
        .fillna(0)
        .astype(int)
    )

    return (
        summary
        .sort_values("user_id")
        .reset_index(drop=True)
    )


summary = build_user_summary()


# =========================================================
# HEADER
# =========================================================

st.title("Admin User Data", anchor=False)
st.caption("View registered users, ratings, and search activity. Passwords are hidden.")


# =========================================================
# TOP METRICS
# =========================================================

total_users = len(
    normal_users
)

total_ratings = len(
    ratings
)

total_searches = len(
    history
)

active_raters = (
    ratings["user_id"].nunique()
    if (
        not ratings.empty
        and "user_id" in ratings.columns
    )
    else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Registered users",
    total_users,
)

c2.metric(
    "Rating records",
    total_ratings,
)

c3.metric(
    "Users with ratings",
    active_raters,
)

c4.metric(
    "Search records",
    total_searches,
)


(
    users_tab,
    summary_tab,
    ratings_tab,
    history_tab,
    review_tab,
) = st.tabs(
    [
        "Users",
        "Activity Summary",
        "Ratings",
        "Search History",
        "Admin Review",
    ]
)


# =========================================================
# USERS
# =========================================================

with users_tab:
    left, right = st.columns(
        [2.2, 1]
    )

    with left:
        section_header(
            "Registered listeners",
            "User account information without passwords.",
        )

        if normal_users.empty:
            st.info(
                "No registered users found."
            )
        else:
            visible = [
                column
                for column in [
                    "user_id",
                    "username",
                    "role",
                ]
                if column in normal_users.columns
            ]

            st.dataframe(
                normal_users[
                    visible
                ].reset_index(
                    drop=True
                ),
                width="stretch",
                hide_index=True,
                height=430,
            )

    with right:
        with st.container(border=True):
            section_header(
                "Account overview",
                "Quick account-level information.",
            )

            st.metric(
                "Normal users",
                total_users,
            )

            admin_count = (
                int(
                    users["role"]
                    .astype(str)
                    .str.strip()
                    .str.casefold()
                    .eq("admin")
                    .sum()
                )
                if "role" in users.columns
                else 0
            )

            st.metric(
                "Admin accounts",
                admin_count,
            )

            st.caption(
                "Create Account always creates a normal user. "
                "Admin accounts are managed manually."
            )


# =========================================================
# ACTIVITY SUMMARY
# =========================================================

with summary_tab:
    section_header(
        "User activity summary",
        "Ratings and search activity for each registered listener.",
    )

    if summary.empty:
        st.info(
            "No user activity is available."
        )
    else:
        filter_col, info_col = st.columns(
            [2, 1]
        )

        with filter_col:
            user_filter = st.text_input(
                "Find user",
                placeholder="Search User ID or username",
                key="admin_summary_filter",
            )

        filtered_summary = summary.copy()

        if user_filter.strip():
            query = user_filter.strip().casefold()

            user_series = (
                filtered_summary["user_id"]
                .astype(str)
                .str.casefold()
            )

            username_series = (
                filtered_summary["username"]
                .astype(str)
                .str.casefold()
                if "username" in filtered_summary.columns
                else pd.Series(
                    "",
                    index=filtered_summary.index,
                )
            )

            filtered_summary = filtered_summary[
                user_series.str.contains(
                    query,
                    regex=False,
                )
                |
                username_series.str.contains(
                    query,
                    regex=False,
                )
            ]

        with info_col:
            st.metric(
                "Users in view",
                len(
                    filtered_summary
                ),
            )

        st.dataframe(
            filtered_summary,
            width="stretch",
            hide_index=True,
            height=445,
        )


# =========================================================
# RATINGS
# =========================================================

with ratings_tab:
    section_header(
        "All user ratings",
        "Filter rating records by listener.",
    )

    if ratings.empty:
        st.info(
            "No rating data is available."
        )
    else:
        rating_users = sorted(
            ratings["user_id"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        filter_col, count_col = st.columns(
            [2, 1]
        )

        with filter_col:
            selected_rating_user = st.selectbox(
                "User",
                [
                    "All Users",
                    *rating_users,
                ],
                key="admin_rating_user",
            )

        filtered_ratings = ratings.copy()

        if selected_rating_user != "All Users":
            filtered_ratings = filtered_ratings[
                filtered_ratings["user_id"]
                .astype(str)
                .eq(
                    selected_rating_user
                )
            ]

        with count_col:
            st.metric(
                "Records in view",
                len(
                    filtered_ratings
                ),
            )

        columns = [
            "user_id",
            "track_name",
            "artist",
            "genre",
            "mood",
            "rating",
            "rated_at",
        ]

        visible = [
            column
            for column in columns
            if column in filtered_ratings.columns
        ]

        st.dataframe(
            filtered_ratings[
                visible
            ],
            width="stretch",
            hide_index=True,
            height=460,
        )


# =========================================================
# SEARCH HISTORY
# =========================================================

with history_tab:
    section_header(
        "User search history",
        "Inspect which songs users selected in the app.",
    )

    if history.empty:
        st.info(
            "No search history is available."
        )
    else:
        history_users = sorted(
            history["user_id"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        filter_col, count_col = st.columns(
            [2, 1]
        )

        with filter_col:
            selected_history_user = st.selectbox(
                "User",
                [
                    "All Users",
                    *history_users,
                ],
                key="admin_history_user",
            )

        filtered_history = history.copy()

        if selected_history_user != "All Users":
            filtered_history = filtered_history[
                filtered_history["user_id"]
                .astype(str)
                .eq(
                    selected_history_user
                )
            ]

        with count_col:
            st.metric(
                "Records in view",
                len(
                    filtered_history
                ),
            )

        preferred = [
            "user_id",
            "track_name",
            "artist",
            "genre",
            "mood",
            "searched_at",
            "search_time",
            "timestamp",
        ]

        visible = [
            column
            for column in preferred
            if column in filtered_history.columns
        ]

        if not visible:
            visible = list(
                filtered_history.columns
            )

        st.dataframe(
            filtered_history[
                visible
            ],
            width="stretch",
            hide_index=True,
            height=460,
        )

# =========================================================
# ADMIN REVIEW
# =========================================================

with review_tab:
    section_header(
        "Admin Recommendation Review",
        "Select any normal user and regenerate recommendation "
        "results from that user's latest searched song.",
    )

    st.info(
        "Recommendation results are generated on demand. "
        "They are not saved into another dataset."
    )

    # -----------------------------------------------------
    # LOAD REVIEWABLE USERS
    # -----------------------------------------------------

    review_users = (
        get_reviewable_users()
    )

    if review_users.empty:
        st.warning(
            "No registered users found."
        )

    else:
        # -------------------------------------------------
        # SELECT USER
        # -------------------------------------------------

        with st.container(
            border=True
        ):
            st.subheader(
                "Find user"
            )

            st.caption(
                "Select a user or type a User ID / username to search."
            )

            user_options = {
                (
                    f"{row['user_id']} "
                    f"— {row['username']}"
                ):
                    row["user_id"]

                for _, row
                in review_users.iterrows()
            }

            selected_label = (
                st.selectbox(
                    "Select user",
                    list(
                        user_options.keys()
                    ),
                    key="user_data_admin_review_user",
                    placeholder=(
                        "Search User ID or username"
                    ),
                )
            )

            selected_review_user = (
                user_options[
                    selected_label
                ]
            )

        # -------------------------------------------------
        # LATEST USER SEARCH
        # -------------------------------------------------

        latest_search = (
            get_latest_user_search(
                selected_review_user
            )
        )

        if latest_search is None:
            st.warning(
                f"{selected_review_user} has no search history."
            )

            st.info(
                "The user needs to search/select at least one song first."
            )

        else:
            formatted_search_time = (
                format_search_time(
                    latest_search.get(
                        "searched_at",
                        "",
                    )
                )
            )

            preview_rating_count = (
                get_rating_count(
                    selected_review_user
                )
            )

            if (
                preview_rating_count
                >= MIN_USER_RATINGS
            ):
                recommendation_mode = (
                    "Personalized"
                )
            else:
                recommendation_mode = (
                    "Cold Start"
                )

            remaining_ratings = max(
                0,
                MIN_USER_RATINGS
                - preview_rating_count,
            )

            # ---------------------------------------------
            # LATEST SEARCH INFORMATION
            # ---------------------------------------------

            with st.container(
                border=True
            ):
                st.subheader(
                    "Latest user search"
                )

                info1, info2, info3, info4 = st.columns(
                    [
                        2.5,
                        2.5,
                        1.3,
                        1,
                    ]
                )

                with info1:
                    st.metric(
                        "Song",
                        latest_search[
                            "track_name"
                        ],
                    )

                with info2:
                    st.metric(
                        "Artist",
                        latest_search[
                            "artist"
                        ]
                        or "Unknown",
                    )

                with info3:
                    st.metric(
                        "User ID",
                        selected_review_user,
                    )

                with info4:
                    st.metric(
                        "Ratings",
                        preview_rating_count,
                    )

                mode_col, time_col = st.columns(
                    2
                )

                with mode_col:
                    st.metric(
                        "Recommendation Mode",
                        recommendation_mode,
                    )

                with time_col:
                    st.metric(
                        "Latest Search",
                        formatted_search_time,
                    )

                if (
                    recommendation_mode
                    == "Personalized"
                ):
                    st.success(
                        "Personalized Mode: this user has enough "
                        "rating history. Hybrid recommendations use "
                        "40% Content-Based and 60% Collaborative Filtering."
                    )

                else:
                    st.warning(
                        "Cold Start Mode: "
                        f"{remaining_ratings} more rating(s) are needed "
                        f"to reach {MIN_USER_RATINGS} ratings. "
                        "The system currently relies on "
                        "Content-Based Filtering."
                    )

                generate_button = st.button(
                    "Generate Recommendation Review",
                    type="primary",
                    width="stretch",
                    key=(
                        "generate_admin_review_"
                        f"{selected_review_user}"
                    ),
                )

            # ---------------------------------------------
            # GENERATE REVIEW
            # ---------------------------------------------

            if generate_button:
                with st.spinner(
                    "Generating recommendations "
                    f"for {selected_review_user}..."
                ):
                    try:
                        generated_review = (
                            generate_user_review(
                                selected_review_user
                            )
                        )

                        if generated_review is None:
                            st.error(
                                "Unable to generate review."
                            )

                        else:
                            st.session_state[
                                "admin_on_demand_review"
                            ] = generated_review

                            st.success(
                                "Recommendation review "
                                "generated successfully."
                            )

                    except Exception as error:
                        st.error(
                            "Recommendation generation failed."
                        )

                        st.exception(
                            error
                        )

            # ---------------------------------------------
            # CURRENT REVIEW
            # ---------------------------------------------

            review = (
                st.session_state.get(
                    "admin_on_demand_review"
                )
            )

            if not review:
                st.info(
                    "Select a user and click "
                    "'Generate Recommendation Review'."
                )

            elif (
                review.get(
                    "user_id"
                )
                != selected_review_user
            ):
                st.info(
                    "Click Generate Recommendation Review "
                    f"to inspect {selected_review_user}."
                )

            elif (
                review.get(
                    "selected_song"
                )
                != latest_search.get(
                    "track_name"
                )
                or
                review.get(
                    "selected_artist",
                    "",
                )
                != latest_search.get(
                    "artist",
                    "",
                )
            ):
                st.warning(
                    "The user's latest search changed. "
                    "Generate the review again."
                )

            else:
                # -----------------------------------------
                # REVIEW RESULT VALUES
                # -----------------------------------------

                selected_song = review.get(
                    "selected_song",
                    "",
                )

                selected_artist = review.get(
                    "selected_artist",
                    "",
                )

                selected_username = review.get(
                    "username",
                    "",
                )

                rating_count = int(
                    review.get(
                        "rating_count",
                        0,
                    )
                    or 0
                )

                content_results = review.get(
                    "content_results",
                    [],
                )

                collaborative_results = review.get(
                    "collaborative_results",
                    [],
                )

                hybrid_results = review.get(
                    "hybrid_results",
                    [],
                )

                final_results = review.get(
                    "final_results",
                    [],
                )

                # -----------------------------------------
                # REVIEW INFORMATION
                # -----------------------------------------

                st.space(
                    "small"
                )

                with st.container(
                    border=True
                ):
                    st.subheader(
                        "Recommendation information"
                    )

                    detail1, detail2, detail3, detail4 = st.columns(
                        [
                            2,
                            2,
                            1,
                            1,
                        ]
                    )

                    with detail1:
                        st.metric(
                            "Selected song",
                            selected_song,
                        )

                    with detail2:
                        st.metric(
                            "Artist",
                            selected_artist
                            or "Unknown",
                        )

                    with detail3:
                        st.metric(
                            "User ID",
                            selected_review_user,
                        )

                    with detail4:
                        st.metric(
                            "Username",
                            selected_username
                            or "Unknown",
                        )

                    st.divider()

                    result1, result2, result3, result4 = st.columns(
                        4
                    )

                    with result1:
                        st.metric(
                            "Content-Based",
                            len(
                                content_results
                            ),
                        )

                    with result2:
                        st.metric(
                            "Collaborative",
                            len(
                                collaborative_results
                            ),
                        )

                    with result3:
                        st.metric(
                            "Hybrid",
                            len(
                                hybrid_results
                            ),
                        )

                    with result4:
                        st.metric(
                            "User Ratings",
                            rating_count,
                        )

                # -----------------------------------------
                # REVIEW RESULT TABS
                # -----------------------------------------

                (
                    review_overview_tab,
                    review_content_tab,
                    review_collaborative_tab,
                    review_hybrid_tab,
                ) = st.tabs(
                    [
                        "Overview",
                        "Content-Based",
                        "Collaborative",
                        "Hybrid",
                    ]
                )

                # =========================================
                # OVERVIEW
                # =========================================

                with review_overview_tab:
                    st.subheader(
                        "Final Top 10 Recommended Songs"
                    )

                    if (
                        rating_count
                        >= MIN_USER_RATINGS
                    ):
                        st.info(
                            "Personalised Hybrid mode is active. "
                            "40% Content-Based + "
                            "60% Collaborative."
                        )
                    else:
                        st.info(
                            "Cold-start mode is active. "
                            "The user has fewer than 10 ratings, "
                            "so Content-Based Filtering is used."
                        )

                    review_show_final_table(
                        final_results
                    )

                # =========================================
                # CONTENT-BASED
                # =========================================

                with review_content_tab:
                    st.subheader(
                        "Content-Based Filtering"
                    )

                    st.caption(
                        "Uses song metadata, audio features "
                        "and Cosine Similarity."
                    )

                    review_show_table(
                        content_results,
                        [
                            "track_name",
                            "artist",
                            "genre",
                            "mood",
                            "popularity",
                            "similarity",
                        ],
                        height=420,
                    )

                # =========================================
                # COLLABORATIVE
                # =========================================

                with review_collaborative_tab:
                    st.subheader(
                        "Collaborative Filtering"
                    )

                    st.caption(
                        "Uses User-Based KNN and "
                        "Item-Based KNN with "
                        "Euclidean Distance."
                    )

                    if (
                        rating_count
                        < MIN_USER_RATINGS
                    ):
                        remaining = (
                            MIN_USER_RATINGS
                            - rating_count
                        )

                        st.warning(
                            f"{selected_review_user} currently has "
                            f"{rating_count} ratings."
                        )

                        st.info(
                            f"{remaining} more rating(s) are required "
                            "to activate Collaborative Filtering."
                        )

                    else:
                        (
                            collab_recommendation_tab,
                            collab_users_tab,
                            collab_explanation_tab,
                        ) = st.tabs(
                            [
                                "Recommendations",
                                "Similar Users",
                                "Why This Song?",
                            ]
                        )

                        # ---------------------------------
                        # COLLABORATIVE RECOMMENDATIONS
                        # ---------------------------------

                        with collab_recommendation_tab:
                            prepared = (
                                prepare_review_collaborative(
                                    collaborative_results
                                )
                            )

                            review_show_table(
                                prepared,
                                [
                                    "track_name",
                                    "artist",
                                    "genre",
                                    "mood",
                                    "popularity",
                                    "source",
                                    "user_knn_score",
                                    "item_knn_score",
                                    "collaborative_score",
                                ],
                                height=420,
                            )

                            st.caption(
                                "Collaborative Score = "
                                "50% User-Based KNN + "
                                "50% Item-Based KNN."
                            )

                        # ---------------------------------
                        # SIMILAR USERS
                        # ---------------------------------

                        with collab_users_tab:
                            neighbours = (
                                find_nearest_users(
                                    selected_review_user
                                )
                            )

                            if not neighbours:
                                st.info(
                                    "No similar users found."
                                )

                            else:
                                neighbour_rows = []

                                for rank, neighbour in enumerate(
                                    neighbours,
                                    start=1,
                                ):
                                    neighbour_rows.append(
                                        {
                                            "rank":
                                                rank,

                                            "user_id":
                                                neighbour[
                                                    "user_id"
                                                ],

                                            "distance":
                                                round(
                                                    neighbour[
                                                        "distance"
                                                    ],
                                                    3,
                                                ),

                                            "similarity":
                                                round(
                                                    neighbour[
                                                        "similarity"
                                                    ],
                                                    3,
                                                ),

                                            "common_ratings":
                                                neighbour[
                                                    "common_ratings"
                                                ],
                                        }
                                    )

                                st.dataframe(
                                    pd.DataFrame(
                                        neighbour_rows
                                    ),
                                    width="stretch",
                                    hide_index=True,
                                    height=300,
                                )

                                neighbour_ids = [
                                    item[
                                        "user_id"
                                    ]
                                    for item
                                    in neighbours
                                ]

                                selected_neighbour = (
                                    st.selectbox(
                                        "Compare with user",
                                        neighbour_ids,
                                        key=(
                                            "user_data_review_compare_"
                                            f"{selected_review_user}"
                                        ),
                                    )
                                )

                                details = (
                                    get_user_similarity_details(
                                        selected_review_user,
                                        selected_neighbour,
                                    )
                                )

                                if details:
                                    comparison1, comparison2, comparison3 = st.columns(
                                        3
                                    )

                                    with comparison1:
                                        st.metric(
                                            "Euclidean Distance",
                                            f"{details['distance']:.3f}",
                                        )

                                    with comparison2:
                                        st.metric(
                                            "Similarity",
                                            f"{details['similarity']:.3f}",
                                        )

                                    with comparison3:
                                        st.metric(
                                            "Common Ratings",
                                            details[
                                                "common_ratings"
                                            ],
                                        )

                        # ---------------------------------
                        # WHY THIS SONG
                        # ---------------------------------

                        with collab_explanation_tab:
                            if not collaborative_results:
                                st.info(
                                    "No Collaborative recommendations available."
                                )

                            else:
                                song_options = {
                                    (
                                        f"{song['track_name']} "
                                        f"— {song['artist']}"
                                    ):
                                        song

                                    for song
                                    in collaborative_results
                                }

                                selected_song_label = (
                                    st.selectbox(
                                        "Select recommended song",
                                        list(
                                            song_options.keys()
                                        ),
                                        key=(
                                            "user_data_review_explain_"
                                            f"{selected_review_user}"
                                        ),
                                    )
                                )

                                recommendation_song = (
                                    song_options[
                                        selected_song_label
                                    ]
                                )

                                source = (
                                    get_review_source(
                                        recommendation_song
                                    )
                                )

                                score1, score2, score3, score4 = st.columns(
                                    4
                                )

                                with score1:
                                    st.metric(
                                        "Source",
                                        source,
                                    )

                                with score2:
                                    st.metric(
                                        "User-Based",
                                        (
                                            f"{float(
                                                recommendation_song.get(
                                                    'user_knn_score',
                                                    0
                                                )
                                                or 0
                                            ):.3f}"
                                        ),
                                    )

                                with score3:
                                    st.metric(
                                        "Item-Based",
                                        (
                                            f"{float(
                                                recommendation_song.get(
                                                    'item_knn_score',
                                                    0
                                                )
                                                or 0
                                            ):.3f}"
                                        ),
                                    )

                                with score4:
                                    st.metric(
                                        "Collaborative",
                                        (
                                            f"{float(
                                                recommendation_song.get(
                                                    'collaborative_score',
                                                    0
                                                )
                                                or 0
                                            ):.3f}"
                                        ),
                                    )

                                (
                                    user_reason_tab,
                                    item_reason_tab,
                                ) = st.tabs(
                                    [
                                        "User-Based Reason",
                                        "Item-Based Reason",
                                    ]
                                )

                                with user_reason_tab:
                                    support = (
                                        get_recommendation_support(
                                            selected_review_user,
                                            recommendation_song[
                                                "track_name"
                                            ],
                                            recommendation_song[
                                                "artist"
                                            ],
                                        )
                                    )

                                    if (
                                        support
                                        and support.get(
                                            "liked_supporters"
                                        )
                                    ):
                                        rows = []

                                        for supporter in support[
                                            "liked_supporters"
                                        ]:
                                            rows.append(
                                                {
                                                    "similar_user":
                                                        supporter[
                                                            "user_id"
                                                        ],

                                                    "similarity":
                                                        round(
                                                            supporter[
                                                                "similarity"
                                                            ],
                                                            3,
                                                        ),

                                                    "rating":
                                                        supporter[
                                                            "rating"
                                                        ],
                                                }
                                            )

                                        st.dataframe(
                                            pd.DataFrame(
                                                rows
                                            ),
                                            width="stretch",
                                            hide_index=True,
                                            height=280,
                                        )

                                    else:
                                        st.info(
                                            "No User-Based explanation available."
                                        )

                                with item_reason_tab:
                                    support = (
                                        get_item_recommendation_support(
                                            selected_review_user,
                                            recommendation_song[
                                                "track_name"
                                            ],
                                            recommendation_song[
                                                "artist"
                                            ],
                                        )
                                    )

                                    if (
                                        support
                                        and support.get(
                                            "supporting_items"
                                        )
                                    ):
                                        rows = []

                                        for item in support[
                                            "supporting_items"
                                        ]:
                                            rows.append(
                                                {
                                                    "liked_song":
                                                        item[
                                                            "track_name"
                                                        ],

                                                    "artist":
                                                        item[
                                                            "artist"
                                                        ],

                                                    "user_rating":
                                                        item[
                                                            "user_rating"
                                                        ],

                                                    "distance":
                                                        round(
                                                            item[
                                                                "distance"
                                                            ],
                                                            3,
                                                        ),

                                                    "similarity":
                                                        round(
                                                            item[
                                                                "similarity"
                                                            ],
                                                            3,
                                                        ),
                                                }
                                            )

                                        st.dataframe(
                                            pd.DataFrame(
                                                rows
                                            ),
                                            width="stretch",
                                            hide_index=True,
                                            height=300,
                                        )

                                    else:
                                        st.info(
                                            "No Item-Based explanation available."
                                        )

                # =========================================
                # HYBRID
                # =========================================

                with review_hybrid_tab:
                    st.subheader(
                        "Hybrid Recommendation"
                    )

                    if (
                        rating_count
                        >= MIN_USER_RATINGS
                    ):
                        weight1, weight2 = st.columns(
                            2
                        )

                        with weight1:
                            st.metric(
                                "Content-Based Weight",
                                "40%",
                            )

                        with weight2:
                            st.metric(
                                "Collaborative Weight",
                                "60%",
                            )

                        st.caption(
                            "Hybrid Score = "
                            "40% Content-Based + "
                            "60% Collaborative."
                        )

                    else:
                        st.info(
                            "Cold-start mode: "
                            "Content-Based recommendations "
                            "are currently used."
                        )

                    review_show_table(
                        hybrid_results,
                        [
                            "track_name",
                            "artist",
                            "genre",
                            "mood",
                            "popularity",
                            "content_score",
                            "collaborative_score",
                            "score",
                        ],
                        height=420,
                    )

