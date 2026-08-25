# SoundScope: Music Recommendation System

SoundScope is an AI-powered music recommendation system developed using Streamlit.

The system provides three recommendation approaches:

- Content-Based Filtering
- Collaborative Filtering
- Hybrid Recommendation

Users can create an account, search for songs, receive personalized recommendations, rate songs, view search history, and evaluate the recommendation models.

---

## Features

- User registration and login.
- Unified search by song title, artist, genre, and mood.
- User-specific search history.
- Song rating from 1 to 5.
- Content-Based music recommendations.
- User-Based and Item-Based Collaborative Filtering using KNN.
- Cold-start handling for users with insufficient ratings.
- Hybrid recommendation combining Content-Based and Collaborative Filtering.
- Explanation of similar users and recommendation reasons.
- Top 10 recommendation results.
- Evaluation dashboard for recommendation model performance.

---

## Project Structure

```text
RecommendedSystemAssignment/
│
├── app.py
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── spotify-tracks-dataset-detailed.csv
│   ├── real_user_ratings.csv
│   ├── search_history.csv
│   └── users.csv
│
├── models/
│   ├── auth.py
│   ├── content_based.py
│   ├── collaborative.py
│   ├── hybrid.py
│   ├── preprocessing.py
│   ├── real_user_data.py
│   ├── ratings.py
│   └── history.py
│
├── evaluation/
│   ├── dashboard.py
│   └── metrics.py
│
├── pages/
│   ├── 1_Results.py
│   ├── 2_Evaluation.py
│   └── 3_Rate_Music.py
│
└── .streamlit/
```

---

# System Flow

```text
User
  ↓
Login / Register
  ↓
Search and Select Song
  ↓
Generate Content-Based Recommendations
  ↓
Check User Rating Count
  ↓

        Ratings < 10
             ↓
     100% Content-Based
             ↓
          Hybrid
             ↓
         Final Top 10


        Ratings >= 10
             ↓
     Collaborative Filtering
             ↓
   User-Based KNN + Item-Based KNN
             ↓
        50% + 50%
             ↓
     Hybrid Recommendation
             ↓
40% Content-Based + 60% Collaborative
             ↓
         Final Top 10
```

---

# Recommendation Algorithms

## 1. Content-Based Filtering

Content-Based Filtering recommends songs that are similar to the song selected by the user.

The system uses text and audio features.

### Text Features

- Genre
- Artist
- Mood

The text features are converted into numerical features using **TF-IDF**.

### Audio Features

- Danceability
- Energy
- Tempo
- Valence
- Acousticness

The audio features are normalized using **Min-Max Scaling**.

Cosine Similarity is used to calculate how similar other songs are to the selected song.

The final Content-Based score is:

```text
Content Score
=
60% Text Similarity
+
40% Audio Similarity
```

The songs with the highest similarity scores are returned as the Top 10 Content-Based recommendations.

---

## 2. Collaborative Filtering

Collaborative Filtering generates personalized recommendations using real user rating data.

The system uses:

- User-Based KNN
- Item-Based KNN
- Euclidean Distance

User ratings are stored in:

```text
data/real_user_ratings.csv
```

A user must have at least **10 ratings** before Collaborative Filtering is activated.

### User-Based KNN

User-Based KNN compares the target user's ratings with ratings from other users.

Only songs rated by both users are used when calculating Euclidean Distance.

```text
Smaller Euclidean Distance
=
More similar user rating behaviour
```

The nearest users are used to recommend songs that they rated highly.

### Item-Based KNN

Item-Based KNN compares songs using their rating patterns across users.

Songs with similar rating behaviour are considered closer to one another.

Songs related to music previously rated highly by the current user may then be recommended.

### Collaborative Score

User-Based and Item-Based scores are combined equally:

```text
Collaborative Score
=
50% User-Based KNN
+
50% Item-Based KNN
```

The highest Collaborative scores are returned as the Top 10 Collaborative recommendations.

---

## 3. Hybrid Recommendation

The Hybrid Recommendation model combines Content-Based and Collaborative Filtering.

### Cold-Start User

If the user has fewer than 10 ratings:

```text
Content-Based = 100%
Collaborative = 0%
```

The system relies entirely on Content-Based recommendations.

### Personalized User

If the user has 10 or more ratings:

```text
Content-Based = 40%
Collaborative = 60%
```

For a Top 10 recommendation list, the system selects approximately:

```text
4 Content-Based candidates
+
6 Collaborative candidates
```

The final Hybrid score is:

```text
Hybrid Score
=
40% Content Score
+
60% Collaborative Score
```

The selected songs are ranked by Hybrid score to produce the final Top 10 recommendations.

---

# User Accounts

Users must register and log in before using the recommendation system.

Each account is assigned a unique User ID.

User accounts are stored in:

```text
data/users.csv
```

The User ID is used to connect:

- User ratings
- Search history
- Collaborative recommendations

This ensures that each user receives personalized results.

---

# Search Function

SoundScope provides a unified search field.

Users can search using:

- Song title
- Artist
- Genre
- Mood
- Partial keywords

For example:

```text
Perfect
Ed Sheeran
pop
Sad
believ
```

The system returns up to 10 matching songs.

---

# Search History

Songs selected by a user are automatically stored in:

```text
data/search_history.csv
```

Each user's search history is stored separately.

Users can also clear their own recent search history.

---

# Rating Function

Users can rate songs using a 1 to 5 scale:

```text
1 = Strongly Dislike
2 = Dislike
3 = Neutral
4 = Like
5 = Strongly Like
```

Ratings are stored in:

```text
data/real_user_ratings.csv
```

If the user rates the same song again, the existing rating is updated instead of creating a duplicate record.

Ratings of **4 or 5** are considered positive preferences for recommendation and evaluation purposes.

---

# Results Page

The Results page provides four main sections:

### Overview

Displays the final Top 10 recommendations.

### Content-Based

Displays Content-Based recommendations and similarity scores.

### Collaborative

Displays:

- Collaborative Top 10
- User-Based KNN score
- Item-Based KNN score
- Collaborative score
- Recommendation source

The Collaborative section also contains:

#### Similar Users

Shows the nearest users based on Euclidean Distance and common ratings.

#### Why This Song?

Explains why a song was recommended using:

- User-Based reasoning
- Item-Based reasoning

### Hybrid

Displays:

- Content-Based weight
- Collaborative weight
- Content score
- Collaborative score
- Final Hybrid score

---

# Evaluation

The Evaluation page measures the performance of the recommendation models.

The evaluation is performed across eligible real users rather than only the currently logged-in user.

---

## Content-Based Evaluation

Content-Based Filtering is evaluated using:

```text
Average Similarity Score
```

A higher similarity score means the recommended songs are more similar to the selected seed songs.

---

## Real-User Hold-Out Evaluation

Collaborative and Hybrid recommendations use a real-user hold-out evaluation.

For each eligible user:

1. Songs rated 4 or 5 are treated as relevant songs.
2. Up to two relevant songs are temporarily hidden.
3. At least 10 ratings remain for training.
4. The system generates Top 10 recommendations.
5. The recommendations are compared with the hidden songs.

The original CSV file is not changed during the evaluation.

---

## Collaborative Evaluation Metrics

Collaborative Filtering is evaluated using:

- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10
- RMSE

### Precision@10

Measures how many of the Top 10 recommendations are relevant.

Higher is better.

### Recall@10

Measures how many hidden relevant songs are successfully recovered.

Higher is better.

### F1 Score

Combines Precision and Recall into one performance score.

Higher is better.

### Hit Rate@10

Measures whether at least one relevant hidden song appears in the Top 10 recommendations.

Higher is better.

### RMSE

Measures the difference between predicted and actual user ratings.

Lower is better.

---

## Hybrid Evaluation Metrics

Hybrid Recommendation is evaluated using:

- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10

Collaborative and Hybrid results are displayed in a comparison table and evaluation chart.

The model with the highest F1 Score is identified as the best-performing model in the hold-out evaluation.

---

# Dataset

SoundScope mainly uses the following files:

### Spotify Track Dataset

```text
data/spotify-tracks-dataset-detailed.csv
```

Contains song metadata and audio features used by Content-Based Filtering.

### Real User Ratings

```text
data/real_user_ratings.csv
```

Contains:

```text
user_id
track_name
artist
genre
mood
rating
rated_at
```

Used by Collaborative Filtering, Hybrid Recommendation, and hold-out evaluation.

### User Accounts

```text
data/users.csv
```

Stores registered user accounts and User IDs.

### Search History

```text
data/search_history.csv
```

Stores account-specific recent song selections.

---

# Installation

Open PowerShell or a terminal inside the project folder.

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

---

# Run the Application

Start SoundScope using:

```powershell
streamlit run app.py
```

Streamlit will normally open the application at:

```text
http://localhost:8501
```

---

# How to Use

1. Start the Streamlit application.
2. Create an account or login.
3. Search for a song, artist, genre, or mood.
4. Select a song.
5. View the generated Top 10 recommendations.
6. Open the Results page to compare Content-Based, Collaborative, and Hybrid recommendations.
7. Rate songs to build the user's preference history.
8. Once the user has at least 10 ratings, Collaborative Filtering becomes active.
9. Open the Evaluation page to view the recommendation model performance.
10. Use the Rate Music page to view and update existing ratings.

---

# Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `python -m pip install -r requirements.txt` |
| Streamlit does not start | Run `streamlit run app.py` from the project root folder |
| No Collaborative recommendations | Make sure the logged-in user has at least 10 ratings |
| Collaborative values do not change | More overlapping ratings between users may be required |
| New rating does not affect KNN | The song may not have enough ratings from other users |
| Changes do not appear | Refresh the browser or restart Streamlit |
| Evaluation does not change | New ratings may not affect the selected hold-out songs or Top 10 ranking |

---

# Technologies Used

- Python
- Streamlit
- Pandas
- Scikit-learn
- Altair

---

# Summary

SoundScope combines Content-Based Filtering, User-Based KNN, Item-Based KNN, and Hybrid Recommendation to provide personalized music recommendations.

The system also supports user accounts, search history, song ratings, cold-start handling, recommendation explanations, and model evaluation through real-user rating data.