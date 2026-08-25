import streamlit as st

from models.data_loader import load_data


def create_mood(energy, valence):
    """
    Create a mood label based on energy and valence
    """

    if energy >= 0.5 and valence >= 0.5:
        return "Happy"
    
    elif energy >= 0.5 and valence < 0.5:
        return "Angry"
    
    elif energy < 0.5 and valence >= 0.5:
        return "Chill"
    
    else:
        return "Sad"
    
@st.cache_data
def preprocess_data():
    """
    Load and preprocess the Spotify dataset
    """

    # Load the Spotify dataset
    songs = load_data()

    # Remove rows with missing values
    songs = songs.dropna()

    # Remove duplicate rows 
    songs = songs.drop_duplicates()

    # Keep only the columns needed 
    songs = songs[
        [ 
            "track_name",
            "artists",
            "track_genre",
            "popularity",
            "danceability",
            "energy",
            "tempo",
            "valence",
            "acousticness"
        ]
    ]

    # Create a new Mood column 
    songs["mood"] = songs.apply(
        lambda row: create_mood(row["energy"], row["valence"]), 
        axis=1
    )

    # IMPORTANT:
    # Reset index after removing rows.
    # 
    # This keeps the DataFrame position 
    # aligned with the TF-IDF and 
    # audio features matrices
    songs = songs.reset_index(
        drop=True
    )

    # Return cleaned dataset
    return songs