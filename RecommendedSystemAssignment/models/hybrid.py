# =========================================================
# HYBRID RECOMMENDATION SYSTEM
#
# Cold Start (< 10 ratings):
#   100% Content-Based
#
# Personalized (10+ ratings):
#   40% Content-Based
#   60% Collaborative
#
# Top 10:
#   4 Content-Based + 6 Collaborative
#
# Hybrid Score:
#   0.4(Content Score) + 0.6(Collaborative Score)
# =========================================================

from models.content_based import recommend_song
from models.collaborative import recommend_for_user
from models.ratings import get_rating_count


# =========================================================
# CONFIGURATION
# =========================================================

RATING_THRESHOLD = 10

CONTENT_NORMAL_WEIGHT = 0.4
COLLABORATIVE_NORMAL_WEIGHT = 0.6

CONTENT_COLD_START_WEIGHT = 1.0
COLLABORATIVE_COLD_START_WEIGHT = 0.0


# =========================================================
# SONG KEY
# =========================================================

def create_hybrid_song_key(track_name, artist):
    """Use track name + artist as unique song identity."""

    return (
        str(track_name).strip().casefold(),
        str(artist).strip().casefold(),
    )


# =========================================================
# HYBRID WEIGHTS
# =========================================================

def get_hybrid_weights(user_id):
    """
    < 10 ratings:
        100% Content-Based

    10+ ratings:
        40% Content-Based
        60% Collaborative
    """

    if not user_id:
        return 1.0, 0.0, 0

    rating_count = get_rating_count(user_id)

    if rating_count < RATING_THRESHOLD:
        return (
            CONTENT_COLD_START_WEIGHT,
            COLLABORATIVE_COLD_START_WEIGHT,
            rating_count,
        )

    return (
        CONTENT_NORMAL_WEIGHT,
        COLLABORATIVE_NORMAL_WEIGHT,
        rating_count,
    )


# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

def normalize_weights(content_weight, collaborative_weight):
    """Make sure both weights add up to 1."""

    content_weight = float(content_weight)
    collaborative_weight = float(collaborative_weight)

    total = content_weight + collaborative_weight

    if total <= 0:
        return 1.0, 0.0

    return (
        content_weight / total,
        collaborative_weight / total,
    )


# =========================================================
# SLOT ALLOCATION
# =========================================================

def get_blend_quotas(
    top_n,
    content_weight,
    collaborative_weight,
):
    """
    Example:

    Top 10 + 40/60
    → 4 Content-Based
    → 6 Collaborative
    """

    if top_n <= 0:
        return 0, 0

    if collaborative_weight <= 0:
        return top_n, 0

    if content_weight <= 0:
        return 0, top_n

    content_quota = round(
        top_n * content_weight
    )

    if top_n >= 2:
        content_quota = max(
            1,
            min(
                top_n - 1,
                content_quota,
            )
        )

    collaborative_quota = (
        top_n - content_quota
    )

    return (
        content_quota,
        collaborative_quota,
    )


# =========================================================
# HYBRID SOURCE
# =========================================================

def determine_hybrid_source(
    content_score,
    collaborative_score,
):
    """Show which models support a recommendation."""

    if content_score > 0 and collaborative_score > 0:
        return "Both"

    if content_score > 0:
        return "Content-Based"

    if collaborative_score > 0:
        return "Collaborative"

    return "None"


# =========================================================
# BUILD RESULT
# =========================================================

def build_hybrid_result(
    song_key,
    content_lookup,
    collaborative_lookup,
    blend_group,
    content_weight,
    collaborative_weight,
):
    """Build one Hybrid recommendation result."""

    content_song = content_lookup.get(song_key)
    collaborative_song = collaborative_lookup.get(song_key)

    content_score = (
        float(content_song.get("similarity", 0))
        if content_song
        else 0.0
    )

    collaborative_score = (
        float(
            collaborative_song.get(
                "collaborative_score",
                0,
            )
        )
        if collaborative_song
        else 0.0
    )

    metadata_song = (
        content_song
        if content_song
        else collaborative_song
    )

    hybrid_score = (
        content_score * content_weight
        +
        collaborative_score * collaborative_weight
    )

    return {
        "track_name": metadata_song["track_name"],
        "artist": metadata_song["artist"],
        "genre": metadata_song["genre"],
        "mood": metadata_song["mood"],
        "popularity": metadata_song.get("popularity", 0),

        "blend_group": blend_group,

        "source": determine_hybrid_source(
            content_score,
            collaborative_score,
        ),

        "content_score": round(
            content_score,
            3,
        ),

        "collaborative_score": round(
            collaborative_score,
            3,
        ),

        "score": round(
            hybrid_score,
            3,
        ),
    }


# =========================================================
# ADD UNIQUE SONGS
# =========================================================

def add_recommendations(
    results,
    limit,
    selected_keys,
    blend_groups,
    group_name,
):
    """
    Add unique songs from a recommendation list.

    Returns the number of songs added.
    """

    added = 0

    for song in results:

        if added >= limit:
            break

        song_key = create_hybrid_song_key(
            song["track_name"],
            song["artist"],
        )

        if song_key in selected_keys:
            continue

        selected_keys.append(song_key)
        blend_groups[song_key] = group_name

        added += 1

    return added


# =========================================================
# HYBRID RECOMMENDATION
# =========================================================

def hybrid_recommend(
    song_name,
    artist=None,
    user_id=None,
    top_n=10,
    force_weights=None,
    force_weight=None,
):
    """
    Generate Hybrid recommendations.

    Personalized Top 10:
        4 highest Content-Based
        6 highest Collaborative

    Final results are ranked by
    Hybrid Score from highest to lowest.
    """

    # Backward compatibility
    if force_weights is None and force_weight is not None:
        force_weights = force_weight

    # -----------------------------------------------------
    # Get weights
    # -----------------------------------------------------

    if force_weights is not None:

        content_weight = float(
            force_weights[0]
        )

        collaborative_weight = float(
            force_weights[1]
        )

    else:

        (
            content_weight,
            collaborative_weight,
            _,
        ) = get_hybrid_weights(
            user_id
        )

    content_weight, collaborative_weight = (
        normalize_weights(
            content_weight,
            collaborative_weight,
        )
    )

    # -----------------------------------------------------
    # Get allocation
    # -----------------------------------------------------

    content_quota, collaborative_quota = (
        get_blend_quotas(
            top_n,
            content_weight,
            collaborative_weight,
        )
    )

    # -----------------------------------------------------
    # Generate recommendations
    # -----------------------------------------------------

    content_results = recommend_song(
        song_name,
        artist,
    )

    if user_id and collaborative_weight > 0:

        collaborative_results = recommend_for_user(
            user_id,
            top_n=max(
                50,
                top_n * 5,
            ),
        )

    else:

        collaborative_results = []

    # -----------------------------------------------------
    # Lookup tables
    # -----------------------------------------------------

    content_lookup = {
        create_hybrid_song_key(
            song["track_name"],
            song["artist"],
        ): song
        for song in content_results
    }

    collaborative_lookup = {
        create_hybrid_song_key(
            song["track_name"],
            song["artist"],
        ): song
        for song in collaborative_results
    }

    # -----------------------------------------------------
    # Select candidates
    # -----------------------------------------------------

    selected_keys = []
    blend_groups = {}

    content_added = add_recommendations(
        content_results,
        content_quota,
        selected_keys,
        blend_groups,
        "Content-Based Slot",
    )

    collaborative_added = add_recommendations(
        collaborative_results,
        collaborative_quota,
        selected_keys,
        blend_groups,
        "Collaborative Slot",
    )

    # -----------------------------------------------------
    # Backup if Collaborative has too few songs
    # -----------------------------------------------------

    if collaborative_added < collaborative_quota:

        missing = top_n - len(
            selected_keys
        )

        add_recommendations(
            content_results,
            missing,
            selected_keys,
            blend_groups,
            "Content-Based Backup",
        )

    # -----------------------------------------------------
    # Backup if Content-Based has too few songs
    # -----------------------------------------------------

    if len(selected_keys) < top_n:

        missing = top_n - len(
            selected_keys
        )

        add_recommendations(
            collaborative_results,
            missing,
            selected_keys,
            blend_groups,
            "Collaborative Backup",
        )

    # -----------------------------------------------------
    # Build final results
    # -----------------------------------------------------

    final_results = [
        build_hybrid_result(
            song_key,
            content_lookup,
            collaborative_lookup,
            blend_groups[song_key],
            content_weight,
            collaborative_weight,
        )

        for song_key in selected_keys
    ]

    # Highest Hybrid score first
    final_results.sort(
        key=lambda song: song["score"],
        reverse=True,
    )

    return final_results[:top_n]


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    TEST_USER = "User102"
    TEST_SONG = "Money Rain - Phonk Remix"
    TEST_ARTIST = "VTORNIK;Phonk"

    content_weight, collaborative_weight, rating_count = (
        get_hybrid_weights(
            TEST_USER
        )
    )

    content_quota, collaborative_quota = (
        get_blend_quotas(
            10,
            content_weight,
            collaborative_weight,
        )
    )

    print()
    print("=" * 50)
    print("HYBRID RECOMMENDATION")
    print("=" * 50)

    print("User:", TEST_USER)
    print("Ratings:", rating_count)
    print("Selected Song:", TEST_SONG)
    print("Artist:", TEST_ARTIST)

    print()
    print("Content Weight:", content_weight)
    print("Collaborative Weight:", collaborative_weight)
    print("Content Slots:", content_quota)
    print("Collaborative Slots:", collaborative_quota)

    results = hybrid_recommend(
        TEST_SONG,
        TEST_ARTIST,
        TEST_USER,
    )

    print()
    print("=" * 50)
    print("FINAL HYBRID TOP 10")
    print("=" * 50)

    for rank, song in enumerate(
        results,
        start=1,
    ):

        print(
            f"{rank}. "
            f"{song['track_name']} — "
            f"{song['artist']}"
        )

        print(
            f"   Blend: {song['blend_group']} | "
            f"Source: {song['source']}"
        )

        print(
            f"   Content: {song['content_score']:.3f} | "
            f"Collaborative: "
            f"{song['collaborative_score']:.3f} | "
            f"Hybrid: {song['score']:.3f}"
        )