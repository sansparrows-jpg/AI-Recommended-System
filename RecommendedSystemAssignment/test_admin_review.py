# =========================================================
# TEST ADMIN USER RECOMMENDATION REVIEW
# =========================================================

from models.admin_review import (
    generate_user_review,
    get_latest_user_search,
    get_reviewable_users,
)


# =========================================================
# PRINT TOP SONGS
# =========================================================

def print_top_songs(
    title,
    rows,
    score_column=None,
    limit=3,
):
    print()

    print(title)

    print(
        "-" * len(title)
    )


    if not rows:

        print(
            "No results."
        )

        return


    for index, song in enumerate(
        rows[:limit],
        start=1,
    ):

        track_name = song.get(
            "track_name",
            "Unknown",
        )


        artist = song.get(
            "artist",
            "Unknown",
        )


        if (
            score_column
            and
            score_column in song
        ):

            score = song.get(
                score_column,
                0,
            )


            print(
                f"{index}. "
                f"{track_name} "
                f"— {artist} "
                f"({score_column}={score})"
            )


        else:

            print(
                f"{index}. "
                f"{track_name} "
                f"— {artist}"
            )


# =========================================================
# MAIN TEST
# =========================================================

def main():

    users = (
        get_reviewable_users()
    )


    print(
        "=" * 60
    )

    print(
        "SOUNDSCOPE ADMIN REVIEW TEST"
    )

    print(
        "=" * 60
    )


    # =====================================================
    # CHECK USERS
    # =====================================================

    if users.empty:

        print(
            "No normal users were found "
            "inside data/users.csv."
        )

        return


    print()

    print(
        "Available users:"
    )

    print()


    for _, user in users.iterrows():

        print(
            f"{user['user_id']} "
            f"- "
            f"{user['username']}"
        )


    # =====================================================
    # ADMIN SELECT USER
    # =====================================================

    print()


    entered_user = input(
        "Enter User ID "
        "(example User102): "
    ).strip()


    user_lookup = {

        str(user_id)
        .casefold():

            str(user_id)

        for user_id in users[
            "user_id"
        ]
    }


    selected_user = (
        user_lookup.get(
            entered_user.casefold()
        )
    )


    if not selected_user:

        print()

        print(
            "User not found."
        )

        return


    # =====================================================
    # GET LATEST SEARCH
    # =====================================================

    latest_search = (
        get_latest_user_search(
            selected_user
        )
    )


    if latest_search is None:

        print()

        print(
            f"{selected_user} has "
            f"no search history."
        )

        return


    print()

    print(
        "Latest search:"
    )


    print(
        f"Song   : "
        f"{latest_search['track_name']}"
    )


    print(
        f"Artist : "
        f"{latest_search['artist']}"
    )


    print(
        f"Time   : "
        f"{latest_search['searched_at'] or 'Not available'}"
    )


    # =====================================================
    # GENERATE
    # =====================================================

    print()

    print(
        "Generating recommendations..."
    )


    review = (
        generate_user_review(
            selected_user
        )
    )


    if review is None:

        print(
            "Unable to generate review."
        )

        return


    # =====================================================
    # RESULT SUMMARY
    # =====================================================

    print()

    print(
        "=" * 60
    )

    print(
        "REVIEW GENERATED"
    )

    print(
        "=" * 60
    )


    print(
        f"User: "
        f"{review['user_id']} "
        f"({review['username']})"
    )


    print(
        f"Song: "
        f"{review['selected_song']} "
        f"— {review['selected_artist']}"
    )


    print(
        f"Ratings: "
        f"{review['rating_count']}"
    )


    print(
        f"Content-Based: "
        f"{len(review['content_results'])}"
    )


    print(
        f"Collaborative: "
        f"{len(review['collaborative_results'])}"
    )


    print(
        f"Hybrid: "
        f"{len(review['hybrid_results'])}"
    )


    # =====================================================
    # SAMPLE RESULTS
    # =====================================================

    print_top_songs(
        "Content-Based Top 3",
        review[
            "content_results"
        ],
        "similarity",
    )


    print_top_songs(
        "Collaborative Top 3",
        review[
            "collaborative_results"
        ],
        "collaborative_score",
    )


    print_top_songs(
        "Hybrid Top 3",
        review[
            "hybrid_results"
        ],
        "score",
    )


    print()

    print(
        "TEST COMPLETE."
    )


if __name__ == "__main__":

    main()