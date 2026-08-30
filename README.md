# SoundScope: Music Recommendation System

SoundScope is an AI-powered music recommendation system developed using Python and Streamlit.

The system provides three main recommendation approaches:

- Content-Based Filtering
- Collaborative Filtering
- Hybrid Recommendation

SoundScope also supports user accounts, song ratings, search history, Spotify album artwork and playback, recommendation explanations, evaluation tools, and Admin user management.

---

## Features

### User Features

- User registration and login.
- Search by song title, artist, genre, mood, and partial keywords.
- Recent search history for each user.
- Spotify album artwork and embedded playback.
- Song rating from 1 to 5.
- Personalized Collaborative recommendations after sufficient ratings are collected.
- Cold-start handling for users with fewer than 10 ratings.
- Final Top 10 Hybrid recommendations.
- Continue Listening.
- Browse music by mood and genre.
- Taste Profile.
- Liked Songs.
- Personal rating history.

### Admin Features

- View detailed Content-Based, Collaborative, and Hybrid recommendation results.
- Inspect similar users found by User-Based KNN.
- View User-Based and Item-Based reasons for a recommendation.
- Evaluate recommendation model performance.
- Manage user ratings.
- View registered users.
- View user activity summaries.
- View all rating records.
- View user search history.
- Review a user's latest recommendation results.

---

## Project Structure

```text
RecommendedSystemAssignment/
│
├── app.py
├── spotify_auth.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
│
├── data/
│   ├── spotify-tracks-dataset-detailed.csv
│   ├── real_user_ratings.csv
│   ├── search_history.csv
│   └── users.csv
│
├── models/
│   ├── admin_review.py
│   ├── auth.py
│   ├── collaborative.py
│   ├── content_based.py
│   ├── history.py
│   ├── hybrid.py
│   ├── preprocessing.py
│   ├── ratings.py
│   └── real_user_data.py
│
├── evaluation/
│   ├── dashboard.py
│   └── metrics.py
│
└── pages/
    ├── 1_Results.py
    ├── 2_Evaluation.py
    ├── 3_Rate_Music.py
    └── 4_Admin.py
```

---

## User Roles

SoundScope has two roles.

### User

A normal user can:

- Login or create an account.
- Search and select songs.
- Receive recommendations.
- Play songs using Spotify.
- Rate songs.
- View recent searches.
- View personalized recommendations.
- View Taste Profile, Liked Songs, and personal rating history.

Normal users cannot access the Admin pages.

### Admin

An Admin can access:

- Discover
- Results
- Evaluation
- Rate Music
- User Data

Admin accounts are managed manually and cannot be created through the normal registration page.

---

## System Flow

```text
Start
  ↓
Open SoundScope
  ↓
Login / Register
  ↓
Display Home Page
  ↓
Search / Select Song
  ↓
Save Search History
  ↓
Load and Preprocess Spotify Song Data
  ↓
Generate Content-Based Recommendations
  ↓
Check User Rating Count
  ↓

        Ratings < 10
             ↓
          Cold Start
             ↓
     100% Content-Based
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

Users can then rate the selected song or search for another song.

---

# Recommendation Algorithms

## 1. Content-Based Filtering

Content-Based Filtering recommends songs that are similar to the song selected by the user.

The system uses text and audio features.

### Text Features

- Genre
- Artist
- Mood

The text features are converted into numerical representations using **TF-IDF**.

### Audio Features

- Danceability
- Energy
- Tempo
- Valence
- Acousticness

The audio features are normalized using **Min-Max Scaling**.

**Cosine Similarity** is used to measure how similar other songs are to the selected song.

The final Content-Based score is:

```text
Content Score
=
60% Text Similarity
+
40% Audio Similarity
```

Songs with higher similarity scores are ranked higher and returned as the Top 10 Content-Based recommendations.

---

## 2. Collaborative Filtering

Collaborative Filtering generates personalized recommendations using real user-rating data.

The system uses:

- User-Based KNN
- Item-Based KNN
- Euclidean Distance
- K = 5

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

The nearest users are used to recommend songs they rated highly that the target user has not already rated.

### Item-Based KNN

Item-Based KNN compares songs using their rating patterns across users.

Only users who rated both songs are used when calculating Euclidean Distance.

Songs with similar rating behaviour to songs previously rated highly by the target user may be recommended.

### Collaborative Score

User-Based and Item-Based scores are combined equally:

```text
Collaborative Score
=
50% User-Based KNN
+
50% Item-Based KNN
```

The songs with the highest Collaborative scores are returned as Collaborative recommendations.

---

## 3. Hybrid Recommendation

The Hybrid Recommendation model combines Content-Based and Collaborative Filtering.

### Cold-Start User

If the user has fewer than 10 ratings:

```text
Content-Based = 100%
Collaborative = 0%
```

The system relies on Content-Based Filtering so that a new user can still receive recommendations.

### Personalized User

If the user has 10 or more ratings, the system forms the Top 10 candidate list using approximately:

```text
4 Content-Based candidates
+
6 Collaborative candidates
```

Duplicate songs are removed, and missing positions are filled using available recommendations from the other module.

The final Hybrid score is:

```text
Hybrid Score
=
40% Content Score
+
60% Collaborative Score
```

Songs with higher Hybrid scores are ranked higher in the final Top 10 recommendation list.

---

# Search Function

SoundScope provides a unified search field.

Users can search using:

- Song title
- Artist
- Genre
- Mood
- Partial keywords

Examples:

```text
Perfect
Ed Sheeran
pop
Sad
believ
```

The system returns up to 10 matching songs.

Search results display:

- Album artwork
- Track name
- Artist
- Genre
- Mood
- Spotify playback control
- Open button

Selecting a song generates recommendation results and stores the song in the user's search history.

---

# Spotify Integration

SoundScope uses Spotify integration for album artwork and music playback.

The project uses:

- Spotify track IDs from the Spotify Tracks Dataset.
- Spotify oEmbed for album artwork and embedded playback.
- Spotify OAuth for connecting a Spotify account.

Spotify credentials are stored in:

```text
.streamlit/secrets.toml
```

Example structure:

```toml
SPOTIFY_CLIENT_ID = "your_client_id"
SPOTIFY_CLIENT_SECRET = "your_client_secret"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8501"
```

Do not commit `secrets.toml` to a public repository.

---

# Search History

Songs selected by a user are automatically stored in:

```text
data/search_history.csv
```

Each user's history is stored separately.

Recent Searches and Continue Listening use this information.

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

If a user rates the same song again, the existing rating is updated rather than creating a duplicate rating record.

Ratings of **4 or 5** are treated as positive preferences for Collaborative Filtering and hold-out evaluation.

---

# Results Page

The Results page is available to the **Admin**.

It provides four sections:

### Overview

Displays information about the selected user and recommendation run.

### Content-Based

Displays Content-Based recommendations together with similarity scores.

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

Explains why a recommended song is supported by:

- User-Based KNN
- Item-Based KNN

### Hybrid

Displays:

- Content-Based weight
- Collaborative weight
- Content score
- Collaborative score
- Final Hybrid score

---

# Evaluation

The Evaluation page is available to the **Admin**.

SoundScope evaluates each recommendation approach using evaluation methods suitable for its purpose.

## Content-Based Evaluation

Content-Based Filtering is evaluated using:

```text
Average Similarity Score
```

A higher score indicates that the recommended songs are more similar to the selected seed song.

A 5-point Likert-scale user questionnaire can also be used to evaluate recommendation relevance and user satisfaction.

## Real-User Hold-Out Evaluation

Collaborative and Hybrid recommendations are evaluated using real-user hold-out testing.

For each eligible user:

1. Songs rated 4 or 5 are treated as relevant songs.
2. Up to two relevant songs are temporarily hidden.
3. At least 10 ratings remain for training.
4. The system generates Top 10 recommendations.
5. The recommendations are compared with the hidden songs.

The original rating CSV file is not permanently modified during evaluation.

## Collaborative Evaluation Metrics

Collaborative Filtering is evaluated using:

- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10
- RMSE

### Precision@10

Measures the proportion of relevant songs among the Top 10 recommendations.

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

Measures the rating prediction error of the User-Based KNN component.

Lower is better.

## Hybrid Evaluation Metrics

Hybrid Recommendation is evaluated using:

- Precision@10
- Recall@10
- F1 Score
- Hit Rate@10

Collaborative and Hybrid results are displayed in a comparison table and evaluation chart.

---

# Current Evaluation Results

The current evaluation produced the following results.

### Content-Based Filtering

```text
Average Similarity Score = 0.859
```

### Collaborative Filtering

```text
Precision@10 = 0.143
Recall@10    = 0.714
F1 Score     = 0.238
Hit Rate@10  = 1.000
RMSE         = 1.097
```

### Hybrid Recommendation

```text
Precision@10 = 0.071
Recall@10    = 0.357
F1 Score     = 0.119
Hit Rate@10  = 0.429
```

Under the current hold-out evaluation, Collaborative Filtering achieved the highest F1 Score.

---

# Rate Music

The Rate Music page is available to the **Admin**.

The Admin can:

- Select a registered user.
- View the user's rating count.
- Check whether the user has enough ratings for Collaborative Filtering.
- View the common rating set.
- View current song ratings.
- Update user ratings.
- Review the selected user's rating records.

These ratings are used to build user preference profiles for Collaborative Filtering.

---

# Admin User Data

The User Data page is available to the **Admin**.

It contains five sections.

### Users

Displays registered users and account roles without showing passwords.

### Activity Summary

Displays:

- User ID
- Username
- Rating count
- Average rating
- Search count

### Ratings

Displays all user-rating records and allows filtering by user.

### Search History

Displays songs selected by users together with search timestamps.

### Admin Review

Allows the Admin to select a normal user and review recommendation results generated from that user's latest searched song.

The Admin Review includes:

- Latest searched song
- Artist
- User ID
- Rating count
- Recommendation mode
- Latest search time
- Content-Based results
- Collaborative results
- Hybrid results

Recommendation review results are generated on demand and are not stored in a separate dataset.

---

# Dataset

SoundScope mainly uses the following files.

### Spotify Tracks Dataset

```text
data/spotify-tracks-dataset-detailed.csv
```

Contains song metadata and audio features used by Content-Based Filtering.

Important fields include:

- Track name
- Artist
- Genre
- Mood
- Danceability
- Energy
- Tempo
- Valence
- Acousticness
- Popularity
- Spotify track ID

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

Stores registered accounts, User IDs, and roles.

### Search History

```text
data/search_history.csv
```

Stores account-specific song selections and search timestamps.

---

# Installation

Open PowerShell or a terminal inside the project folder.

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

---

# Spotify Configuration

Create:

```text
.streamlit/secrets.toml
```

Add your Spotify Developer credentials:

```toml
SPOTIFY_CLIENT_ID = "your_client_id"
SPOTIFY_CLIENT_SECRET = "your_client_secret"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8501"
```

Make sure `.streamlit/secrets.toml` is included in `.gitignore`.

---

# Run the Application

Start SoundScope from the project root:

```powershell
python -m streamlit run app.py
```

Open the application at:

```text
http://127.0.0.1:8501
```

Using `127.0.0.1` is recommended because it matches the Spotify OAuth redirect URI.

---

# How to Use

## Normal User

1. Start the Streamlit application.
2. Create an account or login.
3. Search for a song, artist, genre, or mood.
4. Select a song.
5. View the generated Top 10 recommendations.
6. Play the selected song using Spotify.
7. Rate songs from 1 to 5.
8. View Recent Searches and Continue Listening.
9. Browse songs by mood or genre.
10. View Taste Profile, Liked Songs, and personal rating history.
11. After at least 10 ratings, personalized Collaborative recommendations become active.

## Admin

1. Login using an Admin account.
2. Use **Results** to inspect Content-Based, Collaborative, and Hybrid recommendation results.
3. Use **Evaluation** to review recommendation model performance.
4. Use **Rate Music** to manage user ratings.
5. Use **User Data** to review users, activity, ratings, search history, and recommendation activity.

---

# Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `python -m pip install -r requirements.txt` |
| Streamlit does not start | Run `python -m streamlit run app.py` from the project root |
| Spotify does not connect | Check `.streamlit/secrets.toml` and use `http://127.0.0.1:8501` |
| Album artwork does not appear | Check internet access and Spotify track matching |
| No Collaborative recommendations | Make sure the user has at least 10 ratings |
| Collaborative values do not change | More overlapping ratings between users may be required |
| New rating does not affect KNN | The song may not have enough ratings from other users |
| Changes do not appear | Refresh the browser or restart Streamlit |
| Evaluation does not change | New ratings may not affect the selected hold-out songs or Top 10 ranking |

---

# Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Altair
- Spotify oEmbed
- Spotify OAuth

---

# Summary

SoundScope combines **Content-Based Filtering, User-Based KNN, Item-Based KNN, and Hybrid Recommendation** to support personalized music discovery.

The system handles cold-start users with Content-Based Filtering and activates Collaborative Filtering after sufficient rating information is available. It also provides Spotify playback, user accounts, ratings, search history, recommendation explanations, evaluation tools, and Admin user-management functions through a Streamlit interface.
