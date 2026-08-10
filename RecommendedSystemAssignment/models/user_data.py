# This file loads the generated user ratings 
# and creates the User-Item Matrix 

from pathlib import Path

import pandas as pd
import streamlit as st


RATINGS_PATH = Path(__file__).resolve().parents[1] / "data" / "user_ratings.csv"


@st.cache_data(show_spinner=False)
def load_user_matrix():

    #Load generated user ratings
    
    ratings = pd.read_csv(
        RATINGS_PATH
    )

    # Create User-Item Matrix
    # Rows    -> Users
    # Columns -> Songs
    # Values  -> Ratings

    user_matrix = ratings.pivot_table(

        index="user_id",

        columns="track_name",

        values="rating",

        fill_value=0
    )

    return user_matrix 

# Test this file 

if __name__ == "__main__":

    matrix = load_user_matrix()

    print()

    print("==============================")

    print("User-Item Matrix")

    print("==============================")

    print(matrix.head())

    print()

    print("Shape:", matrix.shape)
