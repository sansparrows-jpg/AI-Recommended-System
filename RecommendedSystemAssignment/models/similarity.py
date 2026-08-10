import streamlit as st

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

from models.preprocessing import preprocess_data

@st.cache_resource
def prepare_similarity():
    
    # load the cleaned dataset
    songs = preprocess_data().copy()

    # TEXT FEATURES 
    # combine important features into one text column 
    songs["combined_features"] = (
        songs["track_genre"] + " " +
        songs["track_genre"] + " " +   # Genre repeated
        songs["artists"] + " " +
        songs["artists"] + " " +       # Artist repeated
        songs["mood"]
    )

    # TF-IDF
    # Convert text into numerical vectors
    tfidf = TfidfVectorizer(stop_words="english")

    text_matrix = tfidf.fit_transform(
        songs["combined_features"]
    )

    # AUDIO FEATURES
    audio_features = songs[
        [
            "danceability",
            "energy",
            "tempo",
            "valence",
            "acousticness"
        ]
    ]

    scaler = MinMaxScaler()

    audio_matrix = scaler.fit_transform(audio_features)

    # Return prepared data only
    return songs, text_matrix, audio_matrix
