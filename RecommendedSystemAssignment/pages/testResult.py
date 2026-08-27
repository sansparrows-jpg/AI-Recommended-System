import pandas as pd
import streamlit as st

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

from models.ratings import (
    get_rating_count,
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Admin Recommendation Review",
    page_icon="music",
    layout="wide",
)


# =========================================================
# ADMIN CHECK
# =========================================================

if not st.session_state.get(
    "logged_in",
    False,
):

    st.warning(
        "Please login first."
    )

    st.stop()


if (
    st.session_state.get("role")
    != "admin"
):

    st.error(
        "Access denied. Admin only."
    )

    st.stop()


# =========================================================
# TABLE
# =========================================================

def show_table(
    rows,
    columns=None,
):

    if not rows:

        st.info(
            "No recommendations available."
        )

        return


    df = pd.DataFrame(
        rows
    )


    if columns:

        visible_columns = [
            column
            for column in columns
            if column in df.columns
        ]


        df = df[
            visible_columns
        ]


    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )


# =========================================================
# FINAL TABLE
# =========================================================

def show_final_table(
    rows
):

    if not rows:

        st.info(
            "No recommendations available."
        )

        return


    df = pd.DataFrame(
        rows
    )


    if "final_score" in df.columns:

        df = df.sort_values(
            "final_score",
            ascending=False,
        )


    df = (
        df
        .head(10)
        .reset_index(
            drop=True
        )
    )


    df["rank"] = (
        df.index + 1
    )


    columns = [
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
        for column in columns
        if column in df.columns
    ]


    st.dataframe(
        df[
            visible_columns
        ],
        width="stretch",
        hide_index=True,
    )


# =========================================================
# COLLABORATIVE SOURCE
# =========================================================

def get_recommendation_source(
    song
):

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
        and
        item_score > 0
    ):

        return "Both"


    if user_score > 0:

        return "User-Based"


    if item_score > 0:

        return "Item-Based"


    return "None"


def prepare_collaborative_results(
    rows
):

    prepared = []


    for song in rows:

        row = song.copy()


        row["source"] = (
            get_recommendation_source(
                song
            )
        )


        prepared.append(
            row
        )


    return prepared


# =========================================================
# HEADER
# =========================================================

st.title(
    "Admin Recommendation Review",
    anchor=False,
)


st.caption(
    "Search for any user and regenerate the "
    "recommendation results using that user's "
    "latest searched song."
)


st.info(
    "The recommendation results are generated on demand. "
    "They are not saved into another dataset."
)


# =========================================================
# USERS
# =========================================================

users = (
    get_reviewable_users()
)


if users.empty:

    st.warning(
        "No registered users found."
    )

    st.stop()


# =========================================================
# SELECT / SEARCH USER
# =========================================================

with st.container(
    border=True
):

    st.subheader(
        "Find user"
    )

    st.caption(
        "Select a user or type a User ID / username to search."
    )


    # =====================================================
    # USER OPTIONS
    # =====================================================

    user_options = {

        (
            f"{row['user_id']} "
            f"— {row['username']}"
        ):
            row["user_id"]

        for _, row
        in users.iterrows()
    }


    # =====================================================
    # SEARCHABLE SELECTBOX
    # =====================================================

    selected_label = (
        st.selectbox(
            "Select user",
            list(
                user_options.keys()
            ),
            placeholder=(
                "Search User ID or username"
            ),
        )
    )


    # =====================================================
    # GET SELECTED USER ID
    # =====================================================

    selected_user = (
        user_options[
            selected_label
        ]
    )


# =========================================================
# LATEST SEARCH
# =========================================================

latest_search = (
    get_latest_user_search(
        selected_user
    )
)


if latest_search is None:

    st.warning(
        f"{selected_user} has "
        f"no search history."
    )


    st.info(
        "The user needs to search/select "
        "at least one song first."
    )


    st.stop()
# =========================================================
# FORMAT LATEST SEARCH TIME
# =========================================================

raw_search_time = (
    latest_search.get(
        "searched_at",
        "",
    )
)


if raw_search_time:

    parsed_search_time = (
        pd.to_datetime(
            raw_search_time,
            errors="coerce",
        )
    )


    if pd.notna(
        parsed_search_time
    ):

        formatted_search_time = (
            parsed_search_time.strftime(
                "%d %b %Y, %I:%M %p"
            )
        )


    else:

        formatted_search_time = (
            raw_search_time
        )


else:

    formatted_search_time = (
        "Unknown"
    )
# =========================================================
# USER RATING COUNT / RECOMMENDATION MODE
# =========================================================

preview_rating_count = (
    get_rating_count(
        selected_user
    )
)


if (
    preview_rating_count
    >=
    MIN_USER_RATINGS
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
    -
    preview_rating_count,
)

# =========================================================
# LATEST USER SEARCH INFORMATION
# =========================================================

with st.container(
    border=True
):

    st.subheader(
        "Latest user search"
    )


# =====================================================
# FIRST ROW
# Song / Artist / User / Ratings
# =====================================================

col1, col2, col3, col4 = st.columns(
    [
        2.5,
        2.5,
        1.3,
        1,
    ]
)


with col1:

    st.metric(
        "Song",
        latest_search[
            "track_name"
        ],
    )


with col2:

    st.metric(
        "Artist",
        latest_search[
            "artist"
        ]
        or "Unknown",
    )


with col3:

    st.metric(
        "User ID",
        selected_user,
    )


with col4:

    st.metric(
        "Ratings",
        preview_rating_count,
    )

# =====================================================
# SECOND ROW
# Recommendation Mode / Latest Search Time
# =====================================================

col5, col6 = st.columns(
    [
        1,
        1,
    ]
)


with col5:

    st.metric(
        "Recommendation Mode",
        recommendation_mode,
    )


with col6:

    st.metric(
        "Latest Search",
        formatted_search_time,
    )
    # =====================================================
    # LATEST SEARCH TIME
    # =====================================================

    if latest_search.get(
        "searched_at"
    ):

        st.caption(
            "Latest search time: "
            f"{latest_search['searched_at']}"
        )

    # =====================================================
    # MODE EXPLANATION
    # =====================================================

    if (
        recommendation_mode
        ==
        "Personalized"
    ):

        st.success(
            "Personalized Mode: "
            "This user has enough rating history. "
            "Hybrid recommendations use "
            "40% Content-Based and "
            "60% Collaborative Filtering."
        )


    else:

        st.warning(
            "Cold Start Mode: "
            f"This user needs "
            f"{remaining_ratings} more rating(s) "
            f"to reach "
            f"{MIN_USER_RATINGS} ratings. "
            "The system currently relies on "
            "Content-Based Filtering."
        )

    # =====================================================
    # GENERATE BUTTON
    # =====================================================

    generate_button = (
        st.button(
            "Generate Recommendation Review",
            type="primary",
            width="stretch",
        )
    )


# =========================================================
# GENERATE
# =========================================================

if generate_button:

    with st.spinner(
        f"Generating recommendations "
        f"for {selected_user}..."
    ):

        try:

            generated_review = (
                generate_user_review(
                    selected_user
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


# =========================================================
# CURRENT REVIEW
# =========================================================

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

    st.stop()


# =========================================================
# PREVENT WRONG USER RESULT
# =========================================================

if (
    review.get("user_id")
    !=
    selected_user
):

    st.info(
        f"Click Generate Recommendation Review "
        f"to inspect {selected_user}."
    )

    st.stop()


# =========================================================
# CHECK LATEST SONG
# =========================================================

if (
    review.get(
        "selected_song"
    )
    !=
    latest_search.get(
        "track_name"
    )
    or
    review.get(
        "selected_artist",
        "",
    )
    !=
    latest_search.get(
        "artist",
        "",
    )
):

    st.warning(
        "The user's latest search changed. "
        "Generate the review again."
    )

    st.stop()


# =========================================================
# RESULT VALUES
# =========================================================

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


# =========================================================
# INFORMATION
# =========================================================

st.markdown("")


with st.container(
    border=True
):

    st.subheader(
        "Recommendation information"
    )


    (
        info1,
        info2,
        info3,
        info4,
    ) = st.columns(
        [
            2,
            2,
            1,
            1,
        ]
    )


    with info1:

        st.metric(
            "Selected song",
            selected_song,
        )


    with info2:

        st.metric(
            "Artist",
            selected_artist
            or
            "Unknown",
        )


    with info3:

        st.metric(
            "User ID",
            selected_user,
        )


    with info4:

        st.metric(
            "Username",
            selected_username
            or
            "Unknown",
        )


    st.divider()


    (
        summary1,
        summary2,
        summary3,
        summary4,
    ) = st.columns(4)


    with summary1:

        st.metric(
            "Content-Based",
            len(
                content_results
            ),
        )


    with summary2:

        st.metric(
            "Collaborative",
            len(
                collaborative_results
            ),
        )


    with summary3:

        st.metric(
            "Hybrid",
            len(
                hybrid_results
            ),
        )


    with summary4:

        st.metric(
            "User Ratings",
            rating_count,
        )


# =========================================================
# TABS
# =========================================================

(
    overview_tab,
    content_tab,
    collaborative_tab,
    hybrid_tab,
) = st.tabs(
    [
        "Overview",
        "Content-Based",
        "Collaborative",
        "Hybrid",
    ]
)


# =========================================================
# OVERVIEW
# =========================================================

with overview_tab:

    st.subheader(
        "Final Top 10 Recommended Songs"
    )


    if (
        rating_count
        >=
        MIN_USER_RATINGS
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


    show_final_table(
        final_results
    )


# =========================================================
# CONTENT
# =========================================================

with content_tab:

    st.subheader(
        "Content-Based Filtering"
    )


    st.caption(
        "Uses song metadata, audio features "
        "and Cosine Similarity."
    )


    show_table(
        content_results,
        [
            "track_name",
            "artist",
            "genre",
            "mood",
            "popularity",
            "similarity",
        ],
    )


# =========================================================
# COLLABORATIVE
# =========================================================

with collaborative_tab:

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
        <
        MIN_USER_RATINGS
    ):

        remaining = (
            MIN_USER_RATINGS
            -
            rating_count
        )


        st.warning(
            f"{selected_user} currently has "
            f"{rating_count} ratings."
        )


        st.info(
            f"{remaining} more rating(s) "
            f"are required to activate "
            f"Collaborative Filtering."
        )


    else:

        (
            recommendation_tab,
            users_tab,
            explanation_tab,
        ) = st.tabs(
            [
                "Recommendations",
                "Similar Users",
                "Why This Song?",
            ]
        )


        # ================================================
        # RECOMMENDATIONS
        # ================================================

        with recommendation_tab:

            prepared = (
                prepare_collaborative_results(
                    collaborative_results
                )
            )


            show_table(
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
            )


            st.caption(
                "Collaborative Score = "
                "50% User-Based KNN + "
                "50% Item-Based KNN."
            )


        # ================================================
        # SIMILAR USERS
        # ================================================

        with users_tab:

            neighbours = (
                find_nearest_users(
                    selected_user
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
                            f"compare_"
                            f"{selected_user}"
                        ),
                    )
                )


                details = (
                    get_user_similarity_details(
                        selected_user,
                        selected_neighbour,
                    )
                )


                if details:

                    c1, c2, c3 = (
                        st.columns(3)
                    )


                    with c1:

                        st.metric(
                            "Euclidean Distance",
                            f"{details['distance']:.3f}",
                        )


                    with c2:

                        st.metric(
                            "Similarity",
                            f"{details['similarity']:.3f}",
                        )


                    with c3:

                        st.metric(
                            "Common Ratings",
                            details[
                                "common_ratings"
                            ],
                        )


        # ================================================
        # WHY THIS SONG
        # ================================================

        with explanation_tab:

            if not collaborative_results:

                st.info(
                    "No Collaborative "
                    "recommendations available."
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
                            f"explain_"
                            f"{selected_user}"
                        ),
                    )
                )


                recommendation_song = (
                    song_options[
                        selected_song_label
                    ]
                )


                source = (
                    get_recommendation_source(
                        recommendation_song
                    )
                )


                c1, c2, c3, c4 = (
                    st.columns(4)
                )


                with c1:

                    st.metric(
                        "Source",
                        source,
                    )


                with c2:

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


                with c3:

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


                with c4:

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


                # ----------------------------------------
                # USER REASON
                # ----------------------------------------

                with user_reason_tab:

                    support = (
                        get_recommendation_support(
                            selected_user,

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
                        and
                        support.get(
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
                        )


                    else:

                        st.info(
                            "No User-Based explanation available."
                        )


                # ----------------------------------------
                # ITEM REASON
                # ----------------------------------------

                with item_reason_tab:

                    support = (
                        get_item_recommendation_support(
                            selected_user,

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
                        and
                        support.get(
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
                        )


                    else:

                        st.info(
                            "No Item-Based explanation available."
                        )


# =========================================================
# HYBRID
# =========================================================

with hybrid_tab:

    st.subheader(
        "Hybrid Recommendation"
    )


    if (
        rating_count
        >=
        MIN_USER_RATINGS
    ):

        col1, col2 = (
            st.columns(2)
        )


        with col1:

            st.metric(
                "Content-Based Weight",
                "40%",
            )


        with col2:

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


    show_table(
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
    )