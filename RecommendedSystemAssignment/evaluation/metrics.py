# =========================================================
# RECOMMENDATION SYSTEM EVALUATION METRICS
# =========================================================

import math


# =========================================================
# PRECISION@K
# =========================================================

def precision_at_k(recommended, relevant):
    """
    Measures the proportion of recommended
    songs that are relevant.
    """

    if not recommended:
        return 0.0

    recommended_set = set(recommended)
    relevant_set = set(relevant)

    correct = recommended_set & relevant_set

    return len(correct) / len(recommended)


# =========================================================
# RECALL@K
# =========================================================

def recall_at_k(recommended, relevant):
    """
    Measures the proportion of relevant
    songs successfully recommended.
    """

    if not relevant:
        return 0.0

    recommended_set = set(recommended)
    relevant_set = set(relevant)

    correct = recommended_set & relevant_set

    return len(correct) / len(relevant)


# =========================================================
# F1 SCORE
# =========================================================

def f1_score(precision, recall):
    """
    Combines Precision and Recall
    into one score.
    """

    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        /
        (precision + recall)
    )


# =========================================================
# HIT RATE@K
# =========================================================

def hit_rate_at_k(recommended, relevant):
    """
    Returns 1 when at least one relevant song
    appears in the recommendation list.
    """

    recommended_set = set(recommended)
    relevant_set = set(relevant)

    if recommended_set & relevant_set:
        return 1.0

    return 0.0


# =========================================================
# RMSE
# =========================================================

def rmse(actual, predicted):
    """
    Root Mean Square Error.

    Lower RMSE indicates better
    rating prediction accuracy.
    """

    if not actual or not predicted:
        return None

    if len(actual) != len(predicted):
        return None

    squared_errors = [
        (float(actual_value) - float(predicted_value)) ** 2
        for actual_value, predicted_value
        in zip(actual, predicted)
    ]

    return math.sqrt(
        sum(squared_errors)
        /
        len(squared_errors)
    )