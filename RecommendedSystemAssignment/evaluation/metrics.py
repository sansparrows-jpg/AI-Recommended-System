# This file contains the evaluation metrics
# used to measure the performance of the 
# recommendation system

# Metrics:
# 1. Precision@K
# 2. Recall@K
# 3. F1 Score
# 4. Accuracy@K
def precision_at_k(recommended, relevant):
    """
    Precision@K

    Purpose:
    Measures how many of the recommended songs
    are actually relevant.

    Formula:
       Precision = Correct Recommendation
                   ----------------------
                   Total Recommended Songs

    Parameters
    ----------
    recommended : list 
        Songs recommended by the recommender system.

    relevant : list
        Songs that are actually considered relevant
        (ground truth).

    Returns
    -------
    float
        Precision score between 0 and 1
    """
    
    # If no songs are recommended,
    # precision is automatically 0.
    if len(recommended) == 0:
        return 0
    
    # Convert both lists into sets
    # Sets make it easy to compare common items
    # and automatically remove duplicate values.
    recommended_set = set(recommended)
    relevant_set = set(relevant)

    # Find songs that appear in both lists
    # These are the correctly recommended songs.
    correct = recommended_set.intersection(relevant_set)

    # Apply the Precision formula
    precision = len(correct) / len(recommended)

    # Round the results to 3 decimal places.
    return round(precision, 3)

def recall_at_k(recommended, relevant):
    """
    Recall@K

    Purpose:
    Measures how many relevant songs
    were successfully recommended.

    Formula
        Recall = Correct Recommendations
                 -----------------------
                 Total Relevant Songs

    Parameters 
    ----------
    recommended : list
        Songs recommended by the recommender system

    relevant : list
        Expected relevant songs

    Returns
    -------
    float
        Recall score between 0 and 1.
    """

    # Avoid division by zero
    if len(relevant) == 0:
        return 0 
    
    # Convert lists into sets
    recommended_set = set(recommended)
    relevant_set = set(relevant)

    # Find common songs
    correct = recommended_set.intersection(relevant_set)

    # Apply Recall formula
    recall = len(correct) / len(relevant)

    return round(recall, 3)

def f1_score(precision, recall):
    """
    F1 Score

    Purpose:
    Combines Precision and Recall into 
    one overall evaluation score.

    Formula:
            2 x Precision x Recall
    F1 = ----------------------------
          Precision + Recall

    Paramets
    --------
    precision : float

    recall : float

    Returns
    -------
    float
       F1 socre between 0 and 1.
    """

    # If both Precision and Recall are zero,
    # F1 Score is also zero
    if precision + recall == 0:
        return 0
    
    # Apply the F1 formula
    f1 = (2 * precision * recall) / (precision + recall)

    return round(f1, 3)


def accuracy_at_k(recommended, relevant):
    """
    Accuracy@K

    Measures how much the recommendation set matches
    the relevant song set.
    """

    if len(recommended) == 0 and len(relevant) == 0:
        return 1

    recommended_set = set(recommended)
    relevant_set = set(relevant)
    total_unique = recommended_set.union(relevant_set)

    if len(total_unique) == 0:
        return 0

    correct = recommended_set.intersection(relevant_set)
    accuracy = len(correct) / len(total_unique)

    return round(accuracy, 3)
