from pathlib import Path

import pandas as pd
import streamlit as st

from models.auth import load_users



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


users_tab, summary_tab, ratings_tab, history_tab = st.tabs(
    [
        "Users",
        "Activity Summary",
        "Ratings",
        "Search History",
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
