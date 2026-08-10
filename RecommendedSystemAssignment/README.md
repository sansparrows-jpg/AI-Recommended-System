# SoundScope: Music Recommendation System

SoundScope is a Streamlit music recommendation app that compares three recommendation approaches:

- Content-Based Filtering
- Collaborative Filtering
- Hybrid Recommendation

The Discover page generates recommendations from a selected song and optional user ID. The final Top 10 recommendations are shown immediately on the Discover page and repeated on the Results page with the full model comparison.

## Features

- Unified search for song title, artist, category/genre, and mood/emotion.
- Content-based recommendations using song metadata and audio feature similarity.
- Collaborative recommendations using user-item ratings and user similarity.
- Hybrid recommendations combining content and collaborative signals.
- Final Top 10 ranked recommendations from all three modules.
- Evaluation page with precision, recall, F1 score, similarity score, accuracy, and RMSE.
- Streamlit caching for dataset loading, user matrix loading, similarity preparation, and repeated calculations.

## Project Structure

```text
.
├── app.py
├── data/
├── evaluation/
├── models/
├── pages/
├── .streamlit/
└── requirements.txt
```

## Current Project Architecture

```text
┌──────────────────────────────────────────────┐
│ User                                         │
│ Search song / artist / category / emotion   │
│ Enter optional User ID                       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Streamlit Web Interface                      │
│ app.py                                       │
│ - Discover page                              │
│ - Unified search box                         │
│ - Top 10 recommendation preview              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Data Loading and Preprocessing               │
│ models/data_loader.py                        │
│ models/preprocessing.py                      │
│ - Load Spotify tracks CSV                    │
│ - Clean missing and duplicate data           │
│ - Keep required song/audio columns           │
│ - Generate mood from energy and valence      │
│ - Cache processed data for performance       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Recommendation Request                       │
│ Inputs: selected song + optional user ID     │
└──────────────┬───────────────┬───────────────┘
               │               │
               ▼               ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│ Content-Based        │ │ Collaborative        │ │ Hybrid               │
│ models/content_      │ │ models/collaborative │ │ models/hybrid.py     │
│ based.py             │ │ .py                  │ │                      │
│                      │ │                      │ │ Combines content     │
│ Uses song features:  │ │ Uses user ratings:   │ │ similarity and user  │
│ - Genre/category     │ │ - User-item matrix   │ │ preference signals   │
│ - Artist             │ │ - User similarity    │ │                      │
│ - Danceability       │ │ - Similar listeners  │ │ Content signal: 60%  │
│ - Energy             │ │ - Rated songs        │ │ Collaborative: 40%   │
│ - Tempo              │ │                      │ │ when user ID exists  │
│ - Valence            │ │ Returns songs from   │ │                      │
│ - Acousticness       │ │ similar users        │ │ Returns hybrid score │
│ - Mood/emotion       │ │                      │ │                      │
│                      │ │                      │ │                      │
│ TF-IDF + audio       │ │ Cosine similarity    │ │ Weighted score       │
│ cosine similarity    │ │ between users        │ │                      │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────┐
│ Score Comparison and Final Ranking           │
│ models/ranking.py                            │
│ - Similarity score                           │
│ - Predicted rating                           │
│ - Hybrid score                               │
│ - Popularity                                 │
│ - Dynamic weights                            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Final Top 10 Recommended Songs               │
│ Stored in Streamlit session state            │
└──────────────┬───────────────────────────────┘
               │
               ├───────────────────────────────┐
               ▼                               ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ Discover Page                │ │ Results Page                  │
│ app.py                       │ │ pages/1_Results.py            │
│ Shows Top 10 immediately     │ │ Shows Top 10 + module tables   │
└──────────────────────────────┘ └──────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Evaluation Page                              │
│ pages/2_Evaluation.py                        │
│ evaluation/dashboard.py                      │
│ evaluation/metrics.py                        │
│ - Precision                                  │
│ - Recall                                     │
│ - F1 score                                   │
│ - Similarity score                           │
│ - Accuracy                                   │
│ - RMSE for collaborative rating prediction   │
└──────────────────────────────────────────────┘
```

### Architecture Notes

- The project now uses Streamlit only. The old HTML, CSS, JavaScript, and Flask-style request flow were removed.
- The search box is unified: one input can match song title, artist, category/genre, or mood/emotion.
- Expensive data preparation and similarity calculations are cached to reduce loading time.
- Recommendation results are stored in `st.session_state`, so the Discover and Results pages can show the same generated Top 10 list.
- The Evaluation page compares all three modules using classification metrics and recommendation quality scores.

## Installation

Open PowerShell in the project folder and install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

Start the Streamlit server from this folder:

```powershell
streamlit run app.py
```

The project includes `.streamlit/config.toml`, so the app uses port `8501` by default:

```text
http://localhost:8501
```

## How to Use

1. Open the Discover page.
2. Search by song, artist, category/genre, or mood/emotion.
3. Select a matching song.
4. Enter a user ID such as `User001` for collaborative and hybrid recommendations.
5. Click Generate recommendations.
6. Review the Top 10 songs on the Discover page or open Results for all module outputs.
7. Open Evaluation to compare model quality metrics.

## Dataset Notes

The project expects these files in the `data/` folder:

- `spotify-tracks-dataset-detailed.csv`
- `user_ratings.csv`

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `ModuleNotFoundError` | Install dependencies with `python -m pip install -r requirements.txt`. |
| App opens on the wrong port | Run `streamlit run app.py --server.port=8501`. |
| No collaborative results | Use a valid user ID from `data/user_ratings.csv`, such as `User001`. |
| New changes do not appear | Refresh the browser or restart `streamlit run app.py`. |
