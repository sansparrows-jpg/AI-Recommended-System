# Use Path to locate the users and rating CSV files.
from pathlib import Path
import pandas as pd
import streamlit as st
from models.preprocessing import preprocess_data
from models.ratings import get_rating_count, get_song_rating, get_user_ratings, save_rating
# Configure the Streamlit page.

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

st.set_page_config(page_title='Rate Music - SoundScope', page_icon='⭐', layout='wide')

# Apply the luxury music application appearance.
apply_luxury_ui()
# Stop the page if no account is logged in.
if not st.session_state.get('logged_in', False):
    st.warning('Please login from the Home page first.')
    st.stop()
# Read the current logged-in account from session state.
current_user_id = st.session_state.get('user_id', '')
current_username = st.session_state.get('username', '')
current_role = str(st.session_state.get('role', '')).strip()
# Only Admin can manage another user's ratings.
if current_role.casefold() != 'admin':
    st.error('Access denied. Only administrators can manage Collaborative Filtering ratings.')
    st.stop()
# A user needs at least 10 ratings before Collaborative Filtering is active.
MINIMUM_RATINGS = 10
USER_RATINGS_FILE = Path('data/real_user_ratings.csv')
USERS_FILE = Path('data/users.csv')
# Common songs create overlapping rating data so KNN can compare users.
COMMON_RATING_TARGETS = [('Perfect', 'Ed Sheeran'), ('Shape of You', 'Ed Sheeran'), ('Believer', 'Imagine Dragons'), ('Baby', 'Justin Bieber'), ('Happier', 'Marshmello'), ('Bad Habits', 'Ed Sheeran'), ('Photograph', 'Ed Sheeran'), ("Don't Blame Me", 'Taylor Swift'), ('I Feel It Coming', 'The Weeknd'), ('STAY', 'Justin Bieber')]

# Load the normal user IDs that Admin is allowed to manage.
def load_available_users():
    """
    Load users that the administrator can manage.

    First try to get users from data/users.csv.

    If data/users.csv is not available,
    user IDs are loaded from data/user_ratings.csv.
    """
    user_ids = set()
    if USERS_FILE.exists():
        try:
            users_dataframe = pd.read_csv(USERS_FILE)
            if 'user_id' in users_dataframe.columns:
                if 'role' in users_dataframe.columns:
                    normal_users = users_dataframe[users_dataframe['role'].astype(str).str.strip().str.casefold() != 'admin']
                else:
                    normal_users = users_dataframe
                for user_id in normal_users['user_id'].dropna().astype(str).str.strip():
                    if user_id:
                        user_ids.add(user_id)
        except Exception:
            pass
    if USER_RATINGS_FILE.exists():
        try:
            ratings_dataframe = pd.read_csv(USER_RATINGS_FILE)
            if 'user_id' in ratings_dataframe.columns:
                for user_id in ratings_dataframe['user_id'].dropna().astype(str).str.strip():
                    if user_id:
                        user_ids.add(user_id)
        except Exception:
            pass
    user_ids = [user_id for user_id in user_ids if user_id.casefold() != str(current_user_id).strip().casefold()]
    return sorted(user_ids)

# Cache the common-song lookup because preprocessing the Spotify dataset is expensive.
@st.cache_data(show_spinner=False)
def load_common_songs():
    """
    Find the common rating songs
    inside the Spotify dataset.

    Song title + artist keyword
    are used so we select the
    correct version of each song.
    """
    songs = preprocess_data()
    common_songs = []
    for track_name, artist_keyword in COMMON_RATING_TARGETS:
        track_match = songs['track_name'].astype(str).str.strip().str.casefold() == track_name.strip().casefold()
        artist_match = songs['artists'].astype(str).str.contains(artist_keyword, case=False, regex=False, na=False)
        matches = songs[track_match & artist_match]
        if not matches.empty:
            if 'popularity' in matches.columns:
                matches = matches.sort_values('popularity', ascending=False)
            song = matches.iloc[0]
            common_songs.append({'track_name': song['track_name'], 'artists': song['artists'], 'track_genre': song['track_genre'], 'mood': song['mood']})
    return common_songs
# Show the save/update message after Streamlit reruns the page.
if 'rating_message' in st.session_state:
    st.success(st.session_state.pop('rating_message'))
st.title('Rate Music', anchor=False)
st.caption(f'Logged in as {current_username} ({current_role})')
st.write('Select a user and manage their song ratings from **1 to 5**. These ratings are used to build user preference profiles for **Collaborative Filtering**.')
# Load all users available for rating management.
available_users = load_available_users()
if not available_users:
    st.warning('No users were found. Please make sure user accounts or user rating records are available.')
    st.stop()
st.subheader('Manage user ratings')
# Choose which user's ratings the Admin wants to manage.
selected_user_id = st.selectbox('Select user', options=available_users, key='admin_rating_selected_user')
st.info(f'You are currently managing ratings for **{selected_user_id}**.')
with st.container(border=True):
    st.markdown('### Rating scale')
    st.write('\n        **1 ★** = Strongly dislike  \n        **2 ★** = Dislike  \n        **3 ★** = Neutral  \n        **4 ★** = Like  \n        **5 ★** = Strongly like\n        ')
# Check how many songs this user has already rated.
rating_count = get_rating_count(selected_user_id)
progress_value = min(rating_count / MINIMUM_RATINGS, 1.0)
st.subheader(f"{selected_user_id}'s preference profile")
st.progress(progress_value)
st.write(f'**{rating_count} / {MINIMUM_RATINGS} songs rated**')
if rating_count >= MINIMUM_RATINGS:
    st.success(f'{selected_user_id} has enough ratings to build a Collaborative Filtering profile.')
else:
    ratings_remaining = MINIMUM_RATINGS - rating_count
    st.info(f"Rate {ratings_remaining} more {('song' if ratings_remaining == 1 else 'songs')} for {selected_user_id} to reach the minimum Collaborative Filtering profile.")
st.divider()
st.subheader('Common rating set')
st.caption('These common songs create overlapping rating data between users so that KNN Collaborative Filtering can compare their preferences.')
# Load the shared songs used for KNN rating overlap.
common_songs = load_common_songs()
if not common_songs:
    st.error('The common songs could not be found in the Spotify dataset.')
else:
    # Display each common song and allow its rating to be saved or updated.
    for index, song in enumerate(common_songs):
        with st.container(border=True):
            st.markdown(f"### 🎵 {song['track_name']}")
            st.write(song['artists'])
            st.caption(f"{song['track_genre']} · {song['mood']}")
            # Read the user's existing rating so the page can show Save or Update.
            previous_rating = get_song_rating(selected_user_id, song['track_name'], song['artists'])
            if previous_rating is not None:
                st.caption(f"{selected_user_id}'s current rating: {previous_rating}/5")
            rating_column, button_column = st.columns([4, 1])
            with rating_column:
                rating_options = ['Select rating', 1, 2, 3, 4, 5]
                if previous_rating is not None:
                    default_index = int(previous_rating)
                else:
                    default_index = 0
                rating_value = st.selectbox('Rating', options=rating_options, index=default_index, key=f'common_rating_{selected_user_id}_{index}', label_visibility='collapsed')
            with button_column:
                button_text = 'Update' if previous_rating is not None else 'Save'
                save_button = st.button(button_text, key=f'common_save_{selected_user_id}_{index}', width='stretch')
            # Validate and save the selected rating.
            if save_button:
                if rating_value == 'Select rating':
                    st.warning('Please select a rating from 1 to 5.')
                else:
                    success, message = save_rating(selected_user_id, song, rating_value)
                    if success:
                        action_text = 'updated' if previous_rating is not None else 'saved'
                        st.session_state['rating_message'] = f"{song['track_name']} rating for {selected_user_id} {action_text}: {rating_value}/5."
                        st.rerun()
                    else:
                        st.error(message)
st.divider()
st.subheader(f"{selected_user_id}'s ratings")
# Load the selected user's full rating history.
user_ratings = get_user_ratings(selected_user_id)
if user_ratings:
    ratings_dataframe = pd.DataFrame(user_ratings)
    preferred_columns = ['track_name', 'artist', 'genre', 'mood', 'rating', 'rated_at']
    visible_columns = [column for column in preferred_columns if column in ratings_dataframe.columns]
    ratings_dataframe = ratings_dataframe[visible_columns]
    st.dataframe(ratings_dataframe, width='stretch', hide_index=True)
else:
    st.info(f'{selected_user_id} has not rated any songs yet.')
