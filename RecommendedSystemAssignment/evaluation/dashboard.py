"""
SoundScope Evaluation

Content-Based:
- Average Similarity Score

Collaborative:
- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10
- RMSE

Hybrid:
- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10
"""

from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    f1_score,
    hit_rate_at_k,
    rmse,
)

from models.content_based import recommend_song

from models.collaborative import (
    K_NEIGHBORS,
    MIN_USER_RATINGS,
    calculate_user_distance,
    calculate_item_distance,
    distance_to_similarity,
)

from models.real_user_data import (
    load_real_user_matrix,
    load_song_metadata,
)


# =========================================================
# CONFIGURATION
# =========================================================

TOP_N = 10
HOLDOUT_LIMIT = 2
LIKE_RATING = 4

CONTENT_WEIGHT = 0.4
COLLABORATIVE_WEIGHT = 0.6

USER_WEIGHT = 0.5
ITEM_WEIGHT = 0.5


# =========================================================
# BASIC HELPERS
# =========================================================

def average(values):
    """Calculate average and round to 3 decimal places."""

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        3,
    )


def track_key(track_name, artist):
    """Create comparable song identity."""

    return (
        str(track_name).strip().casefold(),
        str(artist).strip().casefold(),
    )


def metadata_maps(metadata):
    """Create song_key -> metadata lookup."""

    return {
        row["song_key"]: row
        for _, row in metadata.iterrows()
    }


# =========================================================
# HOLD-OUT SELECTION
# =========================================================

def choose_holdouts(user_id, matrix):
    """
    Select up to 2 songs rated 4 or 5.

    Rules:
    - At least 10 training ratings must remain.
    - At least one liked song must remain.
    - Hidden songs must be rated by another user.
    """

    ratings = matrix.loc[user_id]

    rating_count = int(
        ratings.notna().sum()
    )

    max_hide = min(
        HOLDOUT_LIMIT,
        rating_count - MIN_USER_RATINGS,
    )

    if max_hide <= 0:
        return []

    liked = ratings[
        ratings >= LIKE_RATING
    ]

    # Keep at least one liked song
    # for Content-Based evaluation.
    max_hide = min(
        max_hide,
        len(liked) - 1,
    )

    if max_hide <= 0:
        return []

    other_users = matrix.drop(
        index=user_id
    )

    support = other_users.notna().sum()

    candidates = [
        song_key
        for song_key in liked.index
        if support.get(song_key, 0) > 0
    ]

    # Stable ordering:
    # 1. More support
    # 2. Higher rating
    # 3. Song key
    candidates.sort(
        key=lambda song_key: (
            -support.get(song_key, 0),
            -ratings[song_key],
            str(song_key).casefold(),
        )
    )

    return candidates[:max_hide]


# =========================================================
# K NEAREST USERS
# =========================================================

def nearest_users(user_id, matrix):
    """Find K nearest users using Euclidean Distance."""

    neighbours = []

    for other_user in matrix.index:

        if other_user == user_id:
            continue

        distance, common_count = (
            calculate_user_distance(
                user_id,
                other_user,
                matrix,
            )
        )

        if distance is None:
            continue

        neighbours.append({
            "user_id": other_user,
            "distance": float(distance),
            "similarity": float(
                distance_to_similarity(distance)
            ),
            "common_ratings": common_count,
        })

    # Lowest Euclidean Distance first.
    neighbours.sort(
        key=lambda user: (
            user["distance"],
            str(user["user_id"]).casefold(),
        )
    )

    return neighbours[:K_NEIGHBORS]


# =========================================================
# USER-BASED KNN
# =========================================================

def user_based_scores(user_id, matrix):
    """Calculate User-Based KNN recommendation scores."""

    target = matrix.loc[user_id]

    seen_songs = set(
        target[
            target.notna()
        ].index
    )

    totals = {}

    for neighbour in nearest_users(
        user_id,
        matrix,
    ):

        neighbour_ratings = matrix.loc[
            neighbour["user_id"]
        ]

        similarity = neighbour["similarity"]

        for song_key, rating in neighbour_ratings.items():

            if song_key in seen_songs:
                continue

            if rating != rating:  # NaN
                continue

            if rating < LIKE_RATING:
                continue

            values = totals.setdefault(
                song_key,
                {
                    "weighted": 0.0,
                    "similarity": 0.0,
                },
            )

            values["weighted"] += (
                similarity
                *
                (float(rating) / 5.0)
            )

            values["similarity"] += similarity

    scores = {}

    for song_key, values in totals.items():

        similarity_total = values["similarity"]

        if similarity_total <= 0:
            continue

        scores[song_key] = (
            values["weighted"]
            /
            similarity_total
        )

    return scores


# =========================================================
# ITEM-BASED KNN
# =========================================================

def item_based_scores(user_id, matrix):
    """Calculate Item-Based KNN recommendation scores."""

    target = matrix.loc[user_id]

    liked_songs = target[
        target >= LIKE_RATING
    ]

    unseen_songs = target[
        target.isna()
    ].index

    scores = {}

    for candidate in unseen_songs:

        similarities = []

        for liked_song, user_rating in liked_songs.items():

            distance, _ = (
                calculate_item_distance(
                    candidate,
                    liked_song,
                    matrix,
                )
            )

            if distance is None:
                continue

            similarities.append(
                (
                    distance_to_similarity(
                        distance
                    ),
                    float(user_rating),
                )
            )

        if not similarities:
            continue

        # Highest item similarity first.
        similarities.sort(
            key=lambda item: (
                -item[0],
                -item[1],
            )
        )

        nearest = similarities[
            :K_NEIGHBORS
        ]

        weighted = sum(
            similarity * (rating / 5.0)
            for similarity, rating in nearest
        )

        similarity_total = sum(
            similarity
            for similarity, _ in nearest
        )

        if similarity_total <= 0:
            continue

        scores[candidate] = (
            weighted
            /
            similarity_total
        )

    return scores


# =========================================================
# COLLABORATIVE EVALUATION
# =========================================================

def collaborative_from_matrix(
    user_id,
    matrix,
    top_n=10,
):
    """
    Collaborative score:

    50% User-Based KNN
    +
    50% Item-Based KNN
    """

    user_scores = user_based_scores(
        user_id,
        matrix,
    )

    item_scores = item_based_scores(
        user_id,
        matrix,
    )

    # Sort first so Python set ordering
    # cannot change evaluation results.
    all_songs = sorted(
        set(user_scores)
        |
        set(item_scores),
        key=lambda song_key:
            str(song_key).casefold(),
    )

    results = []

    for song_key in all_songs:

        user_score = user_scores.get(
            song_key,
            0.0,
        )

        item_score = item_scores.get(
            song_key,
            0.0,
        )

        collaborative_score = (
            USER_WEIGHT * user_score
            +
            ITEM_WEIGHT * item_score
        )

        results.append({
            "song_key": song_key,
            "user_knn_score": user_score,
            "item_knn_score": item_score,
            "collaborative_score":
                collaborative_score,
        })

    # Stable ranking for equal scores.
    results.sort(
        key=lambda song: (
            -song["collaborative_score"],
            -song["user_knn_score"],
            -song["item_knn_score"],
            str(song["song_key"]).casefold(),
        )
    )

    return results[:top_n]


# =========================================================
# COLLABORATIVE RESULT KEYS
# =========================================================

def collaborative_results_to_keys(
    results,
    metadata_by_song,
):
    """Convert Collaborative results to track identities."""

    keys = []

    for song in results:

        metadata = metadata_by_song.get(
            song["song_key"]
        )

        if metadata is None:
            continue

        keys.append(
            track_key(
                metadata["track_name"],
                metadata["artist"],
            )
        )

    return keys


# =========================================================
# HYBRID HELPER
# =========================================================

def add_unique(
    source_keys,
    limit,
    selected,
):
    """Add unique recommendations until limit is reached."""

    added = 0

    for key in source_keys:

        if added >= limit:
            break

        if key in selected:
            continue

        selected.append(key)
        added += 1

    return added


# =========================================================
# HYBRID EVALUATION
# =========================================================

def build_hybrid_results(
    content_results,
    collaborative_results,
    metadata_by_song,
    top_n=10,
):
    """
    Same Hybrid behaviour as production:

    Top 4 Content-Based
    +
    Top 6 Collaborative

    Hybrid Score:
    40% Content + 60% Collaborative
    """

    content_quota = round(
        top_n * CONTENT_WEIGHT
    )

    collaborative_quota = (
        top_n - content_quota
    )

    # -----------------------------------------------------
    # CONTENT RESULTS
    # -----------------------------------------------------

    content_scores = {
        track_key(
            song["track_name"],
            song["artist"],
        ): float(song["similarity"])
        for song in content_results
    }

    content_keys = list(
        content_scores.keys()
    )

    # -----------------------------------------------------
    # COLLABORATIVE RESULTS
    # -----------------------------------------------------

    collaborative_scores = {}
    collaborative_keys = []

    for song in collaborative_results:

        metadata = metadata_by_song.get(
            song["song_key"]
        )

        if metadata is None:
            continue

        key = track_key(
            metadata["track_name"],
            metadata["artist"],
        )

        collaborative_scores[key] = float(
            song["collaborative_score"]
        )

        collaborative_keys.append(key)

    # -----------------------------------------------------
    # SELECT 4 CONTENT + 6 COLLABORATIVE
    # -----------------------------------------------------

    selected = []

    add_unique(
        content_keys,
        content_quota,
        selected,
    )

    collaborative_added = add_unique(
        collaborative_keys,
        collaborative_quota,
        selected,
    )

    # If Collaborative has fewer than
    # the required number of recommendations,
    # fill remaining positions with Content-Based.
    if collaborative_added < collaborative_quota:

        add_unique(
            content_keys,
            top_n - len(selected),
            selected,
        )

    # If Content-Based has fewer recommendations,
    # fill remaining positions with Collaborative.
    if len(selected) < top_n:

        add_unique(
            collaborative_keys,
            top_n - len(selected),
            selected,
        )

    # -----------------------------------------------------
    # HYBRID SCORE
    # -----------------------------------------------------

    hybrid = []

    for key in selected:

        content_score = content_scores.get(
            key,
            0.0,
        )

        collaborative_score = (
            collaborative_scores.get(
                key,
                0.0,
            )
        )

        hybrid_score = (
            CONTENT_WEIGHT * content_score
            +
            COLLABORATIVE_WEIGHT
            * collaborative_score
        )

        hybrid.append({
            "key": key,
            "score": hybrid_score,
        })

    # Highest Hybrid score first.
    hybrid.sort(
        key=lambda song: (
            -song["score"],
            str(song["key"]).casefold(),
        )
    )

    return [
        song["key"]
        for song in hybrid[:top_n]
    ]


# =========================================================
# RMSE RATING PREDICTION
# =========================================================

def predict_rating(
    user_id,
    song_key,
    matrix,
):
    """Predict hidden rating using User-Based KNN."""

    weighted = 0.0
    similarity_total = 0.0

    for neighbour in nearest_users(
        user_id,
        matrix,
    ):

        rating = matrix.loc[
            neighbour["user_id"],
            song_key,
        ]

        if rating != rating:  # NaN
            continue

        similarity = neighbour["similarity"]

        weighted += (
            similarity
            *
            float(rating)
        )

        similarity_total += similarity

    if similarity_total <= 0:
        return None

    return (
        weighted
        /
        similarity_total
    )


# =========================================================
# METRIC HELPERS
# =========================================================

def empty_bucket():
    return {
        "precision": [],
        "recall": [],
        "f1": [],
        "hit_rate": [],
    }


def add_metrics(
    bucket,
    recommended,
    relevant,
):
    """Calculate and store one user's metrics."""

    precision = precision_at_k(
        recommended,
        relevant,
    )

    recall = recall_at_k(
        recommended,
        relevant,
    )

    bucket["precision"].append(
        precision
    )

    bucket["recall"].append(
        recall
    )

    bucket["f1"].append(
        f1_score(
            precision,
            recall,
        )
    )

    bucket["hit_rate"].append(
        hit_rate_at_k(
            recommended,
            relevant,
        )
    )


def summarize(bucket):
    """Average evaluation results across users."""

    return {
        key: average(values)
        for key, values in bucket.items()
    }


# =========================================================
# MAIN EVALUATION
# =========================================================

def get_evaluation_dashboard():

    matrix = load_real_user_matrix()
    metadata = load_song_metadata()

    if matrix.empty or metadata.empty:

        return {
            "content": {
                "similarity": 0.0,
                "users_evaluated": 0,
            },
            "collaborative": {},
            "hybrid": {},
            "evaluation_users": [],
        }

    metadata_by_song = metadata_maps(
        metadata
    )

    collaborative_bucket = empty_bucket()
    hybrid_bucket = empty_bucket()

    content_similarities = []

    actual_ratings = []
    predicted_ratings = []

    evaluated_users = []

    # =====================================================
    # EVALUATE EACH ELIGIBLE USER
    # =====================================================

    for user_id in matrix.index:

        holdouts = choose_holdouts(
            user_id,
            matrix,
        )

        if not holdouts:
            continue

        # -------------------------------------------------
        # CREATE TRAINING MATRIX
        #
        # Hidden ratings exist only in memory.
        # real_user_ratings.csv is never changed.
        # -------------------------------------------------

        train_matrix = matrix.copy()

        for song_key in holdouts:

            train_matrix.loc[
                user_id,
                song_key,
            ] = float("nan")

        # -------------------------------------------------
        # CONTENT-BASED SEED
        # -------------------------------------------------

        remaining_likes = train_matrix.loc[
            user_id
        ]

        remaining_likes = remaining_likes[
            remaining_likes
            >=
            LIKE_RATING
        ]

        if remaining_likes.empty:
            continue

        # Highest rating first.
        # Song key is used as stable tie-breaker.
        seed_song_key = sorted(
            remaining_likes.index,
            key=lambda key: (
                -remaining_likes[key],
                str(key).casefold(),
            )
        )[0]

        seed_metadata = metadata_by_song.get(
            seed_song_key
        )

        if seed_metadata is None:
            continue

        # -------------------------------------------------
        # RELEVANT HIDDEN SONGS
        # -------------------------------------------------

        relevant = []

        for song_key in holdouts:

            song_metadata = metadata_by_song.get(
                song_key
            )

            if song_metadata is None:
                continue

            relevant.append(
                track_key(
                    song_metadata["track_name"],
                    song_metadata["artist"],
                )
            )

        if not relevant:
            continue

        # -------------------------------------------------
        # CONTENT-BASED EVALUATION
        # -------------------------------------------------

        content_results = recommend_song(
            seed_metadata["track_name"],
            seed_metadata["artist"],
            top_n=TOP_N,
        )

        if content_results:

            similarity_average = (
                sum(
                    float(song["similarity"])
                    for song in content_results
                )
                /
                len(content_results)
            )

            content_similarities.append(
                similarity_average
            )

        # -------------------------------------------------
        # COLLABORATIVE EVALUATION
        # -------------------------------------------------

        collaborative_candidates = (
            collaborative_from_matrix(
                user_id,
                train_matrix,
                top_n=50,
            )
        )

        collaborative_top10 = (
            collaborative_candidates[
                :TOP_N
            ]
        )

        collaborative_keys = (
            collaborative_results_to_keys(
                collaborative_top10,
                metadata_by_song,
            )
        )

        # -------------------------------------------------
        # HYBRID EVALUATION
        # -------------------------------------------------

        hybrid_keys = build_hybrid_results(
            content_results,
            collaborative_candidates,
            metadata_by_song,
            top_n=TOP_N,
        )

        # -------------------------------------------------
        # HOLD-OUT METRICS
        # -------------------------------------------------

        add_metrics(
            collaborative_bucket,
            collaborative_keys,
            relevant,
        )

        add_metrics(
            hybrid_bucket,
            hybrid_keys,
            relevant,
        )

        # -------------------------------------------------
        # RMSE
        # -------------------------------------------------

        for song_key in holdouts:

            predicted = predict_rating(
                user_id,
                song_key,
                train_matrix,
            )

            if predicted is None:
                continue

            actual_ratings.append(
                float(
                    matrix.loc[
                        user_id,
                        song_key,
                    ]
                )
            )

            predicted_ratings.append(
                predicted
            )

        evaluated_users.append(
            user_id
        )

    # =====================================================
    # FINAL EVALUATION RESULTS
    # =====================================================

    content = {
        "similarity":
            average(content_similarities),
    }

    collaborative = summarize(
        collaborative_bucket
    )

    hybrid = summarize(
        hybrid_bucket
    )

    if actual_ratings:

        collaborative["rmse"] = round(
            rmse(
                actual_ratings,
                predicted_ratings,
            ),
            3,
        )

    else:

        collaborative["rmse"] = None

    user_count = len(
        evaluated_users
    )

    content["users_evaluated"] = user_count
    collaborative["users_evaluated"] = user_count
    hybrid["users_evaluated"] = user_count

    return {
        "content": content,
        "collaborative": collaborative,
        "hybrid": hybrid,
        "evaluation_users": evaluated_users,
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    results = get_evaluation_dashboard()

    print()
    print("=" * 50)
    print("SOUNDSCOPE EVALUATION")
    print("=" * 50)

    print(
        "Users:",
        results["evaluation_users"],
    )

    print()
    print("CONTENT-BASED")
    print(
        results["content"]
    )

    print()
    print("COLLABORATIVE")
    print(
        results["collaborative"]
    )

    print()
    print("HYBRID")
    print(
        results["hybrid"]
    )