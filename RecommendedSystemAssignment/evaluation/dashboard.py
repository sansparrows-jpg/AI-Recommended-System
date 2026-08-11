"""
Evaluation data used by the SoundScope evaluation page.
"""

from functools import lru_cache

import numpy as np

from evaluation.metrics import (
    accuracy_at_k,
    f1_score,
    precision_at_k,
    recall_at_k,
)
from models.collaborative import recommend_for_user, similarity_matrix, user_matrix
from models.content_based import recommend_song
from models.hybrid import hybrid_recommend
from models.ranking import generate_final_recommendations


EVALUATION_CASES = [
    {"song": "Comedy", "user": "User001"},
    {"song": "Perfect", "user": "User002"},
    {"song": "Believer", "user": "User003"},
    {"song": "Shape of You", "user": "User004"},
    {"song": "Stay", "user": "User005"},
]


def average_score(recommendations, score_key):
    scores = [float(song.get(score_key, 0)) for song in recommendations]

    if not scores:
        return 0

    return round(sum(scores) / len(scores), 3)


def evaluate_recommendations(recommendations, relevant):
    recommended = [song["track_name"] for song in recommendations]

    precision = precision_at_k(recommended, relevant)
    recall = recall_at_k(recommended, relevant)
    f1 = f1_score(precision, recall)
    accuracy = accuracy_at_k(recommended, relevant)

    return precision, recall, f1, accuracy


def collaborative_rmse():
    actual = []
    predicted = []
    values = user_matrix.to_numpy(dtype=float)

    for user_index, row in enumerate(values):
        neighbours = similarity_matrix[user_index].copy()
        neighbours[user_index] = 0

        for track_index, rating in enumerate(row):
            if rating <= 0:
                continue

            other_ratings = values[:, track_index]
            valid = (other_ratings > 0) & (neighbours > 0)

            if not np.any(valid):
                continue

            estimate = np.average(other_ratings[valid], weights=neighbours[valid])
            actual.append(rating)
            predicted.append(estimate)

    if not actual:
        return None

    rmse = np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2))

    return round(float(rmse), 3)


def collaborative_similarity_score():
    scores = []

    for user_index in range(similarity_matrix.shape[0]):
        neighbours = similarity_matrix[user_index].copy()
        neighbours[user_index] = 0

        if neighbours.size > 0:
            scores.append(float(np.max(neighbours)))

    if not scores:
        return 0

    return round(float(np.mean(scores)), 3)


def collaborative_accuracy(rmse):
    if rmse is None:
        return 0

    return round(max(0, 1 - (rmse / 5)), 3)


def average(values):
    if not values:
        return 0

    return round(sum(values) / len(values), 3)


def empty_metric_bucket():
    return {
        "precision": [],
        "recall": [],
        "f1": [],
        "accuracy": [],
        "similarity": [],
    }


def append_classification_metrics(bucket, recommendations, relevant):
    precision, recall, f1, accuracy = evaluate_recommendations(
        recommendations,
        relevant,
    )
    bucket["precision"].append(precision)
    bucket["recall"].append(recall)
    bucket["f1"].append(f1)
    bucket["accuracy"].append(accuracy)


def summarize_bucket(bucket):
    return {
        "precision": average(bucket["precision"]),
        "recall": average(bucket["recall"]),
        "f1": average(bucket["f1"]),
        "similarity": average(bucket["similarity"]),
        "accuracy": average(bucket["accuracy"]),
    }


@lru_cache(maxsize=1)
def get_evaluation_dashboard():
    content = empty_metric_bucket()
    collaborative = empty_metric_bucket()
    hybrid = empty_metric_bucket()

    for case in EVALUATION_CASES:
        content_results = recommend_song(case["song"])
        collaborative_results = recommend_for_user(case["user"])
        hybrid_results = hybrid_recommend(case["song"], case["user"])
        final_results = generate_final_recommendations(
            content_results,
            collaborative_results,
            hybrid_results,
        )
        relevant = [song["track_name"] for song in final_results]

        append_classification_metrics(content, content_results, relevant)
        append_classification_metrics(collaborative, collaborative_results, relevant)
        append_classification_metrics(hybrid, hybrid_results, relevant)

        content["similarity"].append(average_score(content_results, "similarity"))
        collaborative["similarity"].append(collaborative_similarity_score())
        hybrid["similarity"].append(average_score(hybrid_results, "score"))

    rmse = collaborative_rmse()
    collaborative_summary = summarize_bucket(collaborative)
    collaborative_summary["rmse"] = rmse
    collaborative_summary["rating_accuracy"] = collaborative_accuracy(rmse)
    collaborative_summary["match_accuracy"] = collaborative_summary["accuracy"]
    collaborative_summary["accuracy"] = collaborative_summary["rating_accuracy"]

    return {
        "content": summarize_bucket(content),
        "collaborative": collaborative_summary,
        "hybrid": summarize_bucket(hybrid),
    }
