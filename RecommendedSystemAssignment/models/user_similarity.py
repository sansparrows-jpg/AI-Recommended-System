# This file calculates similarity
# between users using Cosine Similarity
import streamlit as st


from sklearn.metrics.pairwise import cosine_similarity

from models.user_data import load_user_matrix

@st.cache_resource
def calculate_user_similarity():
    # Load User-Item Matrix 
    user_matrix = load_user_matrix()

    # Calculate User Similarity
    similarity_matrix = cosine_similarity(
        user_matrix
    )

    return user_matrix, similarity_matrix

# Test this file
if __name__ == "__main__":

    user_matrix, similarity_matrix = calculate_user_similarity()

    print()

    print("==============================")

    print("User Similarity Matrix")

    print("==============================")

    print("Matrix Shape:", similarity_matrix.shape)

    print()

    print("First User Similarities:")

    print(similarity_matrix[0][:10])