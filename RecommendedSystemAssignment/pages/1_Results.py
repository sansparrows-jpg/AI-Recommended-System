# Pandas prepares recommendation data for Streamlit tables.
import pandas as pd
import streamlit as st
from models.collaborative import find_nearest_users, get_user_similarity_details, get_recommendation_support, get_item_recommendation_support, MIN_USER_RATINGS
from models.ratings import get_rating_count
# Configure the Admin recommendation results page.

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

st.set_page_config(page_title='Recommendation Results', page_icon='music', layout='wide')

# Apply the luxury music application appearance.
apply_luxury_ui()
# The Results page can only be opened after login.
if not st.session_state.get('logged_in', False):
    st.warning('Please login first.')
    st.stop()
# Normal users cannot inspect the three recommendation modules.
if st.session_state.get('role') != 'admin':
    st.error('Access denied. Admin only.')
    st.stop()

# Reusable helper for displaying recommendation tables.
def show_table(rows, columns=None):
    if not rows:
        st.info('No recommendations available.')
        return
    df = pd.DataFrame(rows)
    if columns:
        visible_columns = [column for column in columns if column in df.columns]
        df = df[visible_columns]
    st.dataframe(df, width='stretch', hide_index=True)

# Prepare the final Hybrid output as a ranked Top 10 table.
def show_final_table(rows):
    if not rows:
        st.info('No recommendations available.')
        return
    df = pd.DataFrame(rows)
    if 'final_score' in df.columns:
        df = df.sort_values('final_score', ascending=False)
    df = df.head(10).reset_index(drop=True)
    df['rank'] = df.index + 1
    columns = ['rank', 'track_name', 'artist', 'genre', 'mood', 'popularity', 'final_score']
    visible_columns = [column for column in columns if column in df.columns]
    st.dataframe(df[visible_columns], width='stretch', hide_index=True)

# Identify whether User-Based KNN, Item-Based KNN, or both support a song.
def get_recommendation_source(song):
    """
    Determine whether a recommendation was supported by
    User-Based KNN, Item-Based KNN, or both.
    """
    user_score = float(song.get('user_knn_score', 0) or 0)
    item_score = float(song.get('item_knn_score', 0) or 0)
    if user_score > 0 and item_score > 0:
        return 'Both'
    if user_score > 0:
        return 'User-Based'
    if item_score > 0:
        return 'Item-Based'
    return 'None'

# Add a readable source label to each Collaborative recommendation.
def prepare_collaborative_results(rows):
    prepared = []
    for song in rows:
        row = song.copy()
        row['source'] = get_recommendation_source(song)
        prepared.append(row)
    return prepared
# Read the latest normal-user recommendation kept temporarily for Admin review.
admin_review = st.session_state.get('admin_review')
if not admin_review:
    st.warning('No user recommendation is available for review yet.')
    st.info('Ask a normal user to search and generate recommendations first. The latest user recommendation will remain temporarily available for Admin after the user logs out.')
    st.stop()
# Extract the user, selected song, and module outputs from the temporary snapshot.
selected_song = admin_review.get('selected_song', '')
selected_artist = admin_review.get('selected_artist', '')
selected_user = admin_review.get('user_id', '')
selected_username = admin_review.get('username', '')
content_results = admin_review.get('content_results', [])
collaborative_results = admin_review.get('collaborative_results', [])
hybrid_results = admin_review.get('hybrid_results', [])
final_results = admin_review.get('final_results', [])
# Use the rating count to decide Cold Start or Personalised mode.
rating_count = get_rating_count(selected_user)
st.title('Admin Recommendation Review', anchor=False)
st.caption('Review the latest recommendation generated by a normal user and inspect the three recommendation modules.')
st.info('This is a temporary review snapshot. Recommendation results are not saved to the dataset.')
with st.container(border=True):
    st.subheader('Recommendation information')

    # Show song information on the first row.
    # Using two equal columns prevents long values from being truncated.
    song_col, artist_col = st.columns(2)

    with song_col:
        st.metric(
            'Selected song',
            selected_song,
        )

    with artist_col:
        st.metric(
            'Artist',
            selected_artist or 'Unknown',
        )

    # Show user information on a separate row.
    # This gives the full User ID and Username more display space.
    user_col, username_col = st.columns(2)

    with user_col:
        st.metric(
            'User ID',
            selected_user,
        )

    with username_col:
        st.metric(
            'Username',
            selected_username or 'Unknown',
        )

    st.divider()

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.metric(
            'Content-Based',
            len(content_results),
        )

    with summary_col2:
        st.metric(
            'Collaborative',
            len(collaborative_results),
        )

    with summary_col3:
        st.metric(
            'Hybrid',
            len(hybrid_results),
        )

    with summary_col4:
        st.metric(
            'User Ratings',
            rating_count,
        )
st.markdown('')
# Separate the final result and three recommendation modules into tabs.
overview_tab, content_tab, collaborative_tab, hybrid_tab = st.tabs(['Overview', 'Content-Based', 'Collaborative', 'Hybrid'])
# Overview shows the final Top 10 received by the normal user.
with overview_tab:
    st.subheader('Final Top 10 recommended songs')
    if rating_count >= MIN_USER_RATINGS:
        st.info('Personalised Hybrid mode is active. The Hybrid model uses 40% Content-Based and 60% Collaborative weighting.')
    else:
        st.info('Cold-start mode is active. The user has fewer than 10 ratings, so the system currently relies on Content-Based recommendations.')
    show_final_table(final_results)
# Content-Based shows songs similar to the selected seed song.
with content_tab:
    st.subheader('Content-Based Filtering')
    st.caption("Recommends songs based on the selected song's metadata and audio features using Cosine Similarity.")
    show_table(content_results, ['track_name', 'artist', 'genre', 'mood', 'popularity', 'similarity'])
# Collaborative uses User-Based KNN and Item-Based KNN.
with collaborative_tab:
    st.subheader('Collaborative Filtering')
    st.caption('Uses User-Based KNN and Item-Based KNN with Euclidean Distance.')
    if rating_count < MIN_USER_RATINGS:
        remaining = MIN_USER_RATINGS - rating_count
        st.warning(f'{selected_user} currently has {rating_count} ratings. Collaborative Filtering requires at least {MIN_USER_RATINGS} ratings.')
        st.info(f'{remaining} more rating(s) are needed before User-Based and Item-Based KNN can be used.')
    else:
        recommendation_tab, users_tab, explanation_tab = st.tabs(['Recommendations', 'Similar Users', 'Why This Song?'])
        with recommendation_tab:
            st.markdown('### Collaborative Top 10')
            st.caption('The Source column shows whether each recommendation is supported by User-Based KNN, Item-Based KNN, or both.')
            prepared_collaborative = prepare_collaborative_results(collaborative_results)
            show_table(prepared_collaborative, ['track_name', 'artist', 'genre', 'mood', 'popularity', 'source', 'user_knn_score', 'item_knn_score', 'collaborative_score'])
            st.info('Both = supported by User-Based KNN and Item-Based KNN. User-Based = supported by similar users. Item-Based = supported by similar songs.')
        with users_tab:
            st.markdown(f'### Users similar to {selected_user}')
            st.caption('Smaller Euclidean Distance means the rating behaviour is more similar.')
            # Find the nearest users using Euclidean Distance on common ratings.
            neighbours = find_nearest_users(selected_user)
            if not neighbours:
                st.info('No similar users were found.')
            else:
                neighbour_rows = []
                for rank, neighbour in enumerate(neighbours, start=1):
                    neighbour_rows.append({'rank': rank, 'user_id': neighbour['user_id'], 'distance': round(neighbour['distance'], 3), 'similarity': round(neighbour['similarity'], 3), 'common_ratings': neighbour['common_ratings']})
                st.dataframe(pd.DataFrame(neighbour_rows), width='stretch', hide_index=True)
                closest_user = neighbours[0]['user_id']
                st.success(f'The most similar user to {selected_user} is {closest_user}.')
                neighbour_ids = [neighbour['user_id'] for neighbour in neighbours]
                selected_neighbour = st.selectbox('Compare rating behaviour with', neighbour_ids, key=f'similar_user_comparison_{selected_user}')
                # Load the detailed rating comparison for the selected neighbour.
                details = get_user_similarity_details(selected_user, selected_neighbour)
                if details:
                    st.markdown(f'### {selected_user} vs {selected_neighbour}')
                    metric1, metric2, metric3 = st.columns(3)
                    with metric1:
                        st.metric('Euclidean Distance', f"{details['distance']:.3f}")
                    with metric2:
                        st.metric('Similarity Score', f"{details['similarity']:.3f}")
                    with metric3:
                        st.metric('Common Ratings', details['common_ratings'])
                    metric4, metric5, metric6 = st.columns(3)
                    with metric4:
                        st.metric('Exact Same Ratings', details['exact_matches'])
                    with metric5:
                        st.metric('Within 1 Point', details['close_matches'])
                    with metric6:
                        st.metric('Average Difference', f"{details['average_difference']:.2f}")
                    st.info(f"{selected_user} and {selected_neighbour} rated {details['common_ratings']} same songs. They gave exactly the same rating for {details['exact_matches']} songs.")
                    with st.expander('View common rating comparison', expanded=False):
                        comparison_rows = []
                        for row in details['comparison']:
                            comparison_rows.append({'track_name': row['track_name'], 'artist': row['artist'], selected_user: row['target_rating'], selected_neighbour: row['neighbour_rating'], 'difference': row['difference'], 'difference_squared': row['squared_difference']})
                        comparison_df = pd.DataFrame(comparison_rows)
                        st.dataframe(comparison_df, width='stretch', hide_index=True)
                        squared_total = comparison_df['difference_squared'].sum() if not comparison_df.empty else 0
                        st.caption(f"Euclidean Distance = √({squared_total}) = {details['distance']:.3f}")
        # Explain why a Collaborative song was recommended.
        with explanation_tab:
            st.markdown('### Why was this song recommended?')
            st.caption('Choose a recommended song to see how User-Based and Item-Based KNN contributed to it.')
            if not collaborative_results:
                st.info('No Collaborative recommendations are available.')
            else:
                song_options = {f"{song['track_name']} — {song['artist']}": song for song in collaborative_results}
                selected_label = st.selectbox('Select recommended song', list(song_options.keys()), key=f'collaborative_explanation_song_{selected_user}')
                recommendation_song = song_options[selected_label]
                source = get_recommendation_source(recommendation_song)
                score1, score2, score3, score4 = st.columns(4)
                with score1:
                    st.metric('Source', source)
                with score2:
                    st.metric('User-Based KNN', f"{recommendation_song.get('user_knn_score', 0):.3f}")
                with score3:
                    st.metric('Item-Based KNN', f"{recommendation_song.get('item_knn_score', 0):.3f}")
                with score4:
                    st.metric('Collaborative Score', f"{recommendation_song.get('collaborative_score', 0):.3f}")
                st.caption('Collaborative Score = 50% User-Based KNN + 50% Item-Based KNN.')
                user_reason_tab, item_reason_tab = st.tabs(['User-Based Reason', 'Item-Based Reason'])
                with user_reason_tab:
                    user_score = float(recommendation_song.get('user_knn_score', 0) or 0)
                    if user_score <= 0:
                        st.info('This song was not supported by User-Based KNN.')
                    else:
                        # User-Based reason: check which similar users rated this song highly.
                        support = get_recommendation_support(selected_user, recommendation_song['track_name'], recommendation_song['artist'])
                        if support:
                            if not support['target_has_rated']:
                                st.info(f'{selected_user} has never rated this song before.')
                            liked_supporters = support['liked_supporters']
                            if liked_supporters:
                                supporter_rows = []
                                for supporter in liked_supporters:
                                    supporter_rows.append({'similar_user': supporter['user_id'], 'similarity': round(supporter['similarity'], 3), 'distance': round(supporter['distance'], 3), 'rating': supporter['rating']})
                                st.success(f'{len(liked_supporters)} similar user(s) rated this song 4 or 5.')
                                st.dataframe(pd.DataFrame(supporter_rows), width='stretch', hide_index=True)
                                strongest = max(liked_supporters, key=lambda user: user['similarity'])
                                st.caption(f"Strongest User-Based support: {strongest['user_id']} rated this song {strongest['rating']}/5 and has similarity {strongest['similarity']:.3f} with {selected_user}.")
                            else:
                                st.info('No nearest user rated this song 4 or 5.')
                with item_reason_tab:
                    item_score = float(recommendation_song.get('item_knn_score', 0) or 0)
                    if item_score <= 0:
                        st.info('This song was not supported by Item-Based KNN.')
                    else:
                        # Item-Based reason: compare the recommendation with songs the user already liked.
                        item_support = get_item_recommendation_support(selected_user, recommendation_song['track_name'], recommendation_song['artist'])
                        if item_support and item_support['supporting_items']:
                            st.success(f'This song is similar in rating behaviour to songs that {selected_user} previously rated 4 or 5.')
                            item_rows = []
                            for item in item_support['supporting_items']:
                                item_rows.append({'liked_song': item['track_name'], 'artist': item['artist'], 'user_rating': item['user_rating'], 'distance': round(item['distance'], 3), 'similarity': round(item['similarity'], 3), 'common_users': item['common_users']})
                            st.dataframe(pd.DataFrame(item_rows), width='stretch', hide_index=True)
                            strongest_item = item_support['supporting_items'][0]
                            st.caption(f"Strongest Item-Based support: {recommendation_song['track_name']} is most similar to {strongest_item['track_name']} with similarity {strongest_item['similarity']:.3f}. {selected_user} rated {strongest_item['track_name']} {strongest_item['user_rating']}/5.")
                        else:
                            st.info('No Item-Based explanation is available.')
# Hybrid combines Content-Based and Collaborative scores for the final ranking.
with hybrid_tab:
    st.subheader('Hybrid Recommendation')
    if rating_count >= MIN_USER_RATINGS:
        weight1, weight2 = st.columns(2)
        with weight1:
            st.metric('Content-Based Weight', '40%')
        with weight2:
            st.metric('Collaborative Weight', '60%')
        st.caption('Hybrid Score = 40% Content-Based score + 60% Collaborative score.')
    else:
        st.info('Cold-start mode: Hybrid currently uses Content-Based recommendations only.')
    show_table(hybrid_results, ['track_name', 'artist', 'genre', 'mood', 'popularity', 'content_score', 'collaborative_score', 'score'])
