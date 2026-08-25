import re

from sklearn.metrics.pairwise import cosine_similarity

from models.similarity import prepare_similarity


# =========================================================
# LOAD DATA
# =========================================================

songs, text_matrix, audio_matrix = prepare_similarity()


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_track_title(track_name):
    """
    Normalize song title for duplicate/self detection.

    Example:
    Invincible (feat. Daniel Caesar)
    -> invincible

    Remix, Acoustic and Live versions are kept separate.
    """

    title = str(track_name).strip().casefold()

    # Remove featuring information inside brackets.
    title = re.sub(
        r"\s*[\(\[]\s*(feat\.?|featuring|ft\.?|with).*?[\)\]]",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Remove "- feat. Artist" style information.
    title = re.sub(
        r"\s*[-–—]\s*(feat\.?|featuring|ft\.?|with).*$",
        "",
        title,
        flags=re.IGNORECASE,
    )

    return re.sub(
        r"\s+",
        " ",
        title,
    ).strip()


def normalize_artist(artist):
    """Normalize artist text for comparison."""

    return str(artist).strip().casefold()


def create_song_identity(track_name, artist):
    """Create normalized song identity for duplicate checking."""

    return (
        normalize_track_title(track_name),
        normalize_artist(artist),
    )


# =========================================================
# SONG LOOKUP
# =========================================================

# Exact track name + artist are used to locate
# the exact song selected by the user.

song_lookup = {}

for position, row in enumerate(
    songs.itertuples(index=False)
):
    key = (
        str(row.track_name).strip().casefold(),
        str(row.artists).strip().casefold(),
    )

    # Keep first matching dataset record.
    if key not in song_lookup:
        song_lookup[key] = position


# =========================================================
# FIND SELECTED SONG
# =========================================================

def find_song_index(song_name, artist=None):
    """Return the dataset position of the selected song."""

    song_name_key = (
        str(song_name)
        .strip()
        .casefold()
    )

    # Exact song + artist search
    if artist:
        key = (
            song_name_key,
            normalize_artist(artist),
        )

        return song_lookup.get(key)

    # Backward compatibility:
    # if no artist is supplied, use first title match.
    for position, track_name in enumerate(
        songs["track_name"]
    ):
        if (
            str(track_name).strip().casefold()
            == song_name_key
        ):
            return position

    return None


# =========================================================
# CONTENT-BASED RECOMMENDATION
# =========================================================

def recommend_song(
    song_name,
    artist=None,
    top_n=10,
):
    """
    Recommend similar songs using:

    60% TF-IDF text similarity
    40% audio-feature similarity
    """

    song_index = find_song_index(
        song_name,
        artist,
    )

    if song_index is None:
        return []

    selected_song = songs.iloc[song_index]

    selected_identity = create_song_identity(
        selected_song["track_name"],
        selected_song["artists"],
    )

    # -----------------------------------------------------
    # TEXT SIMILARITY
    # -----------------------------------------------------

    text_scores = cosine_similarity(
        text_matrix[song_index],
        text_matrix,
    ).flatten()

    # -----------------------------------------------------
    # AUDIO SIMILARITY
    # -----------------------------------------------------

    audio_scores = cosine_similarity(
        audio_matrix[song_index].reshape(1, -1),
        audio_matrix,
    ).flatten()

    # -----------------------------------------------------
    # FINAL SCORE
    #
    # 60% text + 40% audio
    # -----------------------------------------------------

    final_scores = (
        0.6 * text_scores
        +
        0.4 * audio_scores
    )

    similarity_scores = sorted(
        enumerate(final_scores),
        key=lambda result: result[1],
        reverse=True,
    )

    # -----------------------------------------------------
    # BUILD TOP N
    # -----------------------------------------------------

    recommendations = []

    # Start with selected song so duplicate
    # versions of it are also excluded.
    used_songs = {
        selected_identity
    }

    for index, score in similarity_scores:

        # Skip exact selected dataset row.
        if index == song_index:
            continue

        row = songs.iloc[index]

        track_name = row["track_name"]
        artist_name = row["artists"]

        identity = create_song_identity(
            track_name,
            artist_name,
        )

        # Skip selected song / duplicate song.
        if identity in used_songs:
            continue

        used_songs.add(identity)

        recommendations.append({
            "track_name": track_name,
            "artist": artist_name,
            "genre": row["track_genre"],
            "mood": row["mood"],
            "popularity": int(row["popularity"]),
            "similarity": round(
                float(score),
                3,
            ),
        })

        if len(recommendations) >= top_n:
            break

    return recommendations


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    TEST_SONG = "Invincible (feat. Daniel Caesar)"
    TEST_ARTIST = "Omar Apollo;Daniel Caesar"

    results = recommend_song(
        TEST_SONG,
        TEST_ARTIST,
    )

    print()
    print("=" * 50)
    print("CONTENT-BASED FILTERING")
    print("=" * 50)

    print(
        "Selected:",
        TEST_SONG,
        "—",
        TEST_ARTIST,
    )

    print()
    print("=" * 50)
    print("TOP 10 RECOMMENDATIONS")
    print("=" * 50)

    for rank, song in enumerate(
        results,
        start=1,
    ):
        print(
            f"{rank}. "
            f"{song['track_name']} — "
            f"{song['artist']}"
        )

        print(
            f"   Similarity: "
            f"{song['similarity']:.3f}"
        )