from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "spotify-tracks-dataset-detailed.csv"


@st.cache_data(show_spinner=False)
def load_data():
    # Read the Spotify dataset
    songs = pd.read_csv(DATA_PATH)

    # Return the dataframe
    return songs
