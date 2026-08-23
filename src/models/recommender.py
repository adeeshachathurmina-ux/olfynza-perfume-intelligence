from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# File path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perfumes_clean.csv"
)


# --------------------------------------------------
# Load cleaned perfume data
# --------------------------------------------------
def load_perfume_data():
    """Load and prepare the cleaned perfume dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "Clean dataset was not found. "
            "Run src/data/clean_data.py first."
        )

    perfume_data = pd.read_csv(
        DATASET_PATH,
        encoding="utf-8"
    )

    text_columns = [
        "name",
        "brand",
        "notes",
        "description",
        "combined_text"
    ]

    for column in text_columns:
        perfume_data[column] = (
            perfume_data[column]
            .fillna("")
            .astype(str)
        )

    return perfume_data


# --------------------------------------------------
# Build separate TF-IDF models
# --------------------------------------------------
def build_recommendation_model(perfume_data):
    """
    Create separate representations for verified notes
    and general descriptive text.
    """

    notes_vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=10000
    )

    description_vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=15000
    )

    notes_matrix = notes_vectorizer.fit_transform(
        perfume_data["notes"]
    )

    description_text = (
        perfume_data["name"]
        + " "
        + perfume_data["brand"]
        + " "
        + perfume_data["description"]
    )

    description_matrix = (
        description_vectorizer.fit_transform(
            description_text
        )
    )

    return {
        "notes_vectorizer": notes_vectorizer,
        "description_vectorizer": description_vectorizer,
        "notes_matrix": notes_matrix,
        "description_matrix": description_matrix
    }


# --------------------------------------------------
# Find matched query terms
# --------------------------------------------------
def find_matched_terms(query, perfume_text):
    """Return query words found in the perfume information."""

    query_terms = {
        term.strip().lower()
        for term in query.split()
        if len(term.strip()) > 2
    }

    perfume_text = str(perfume_text).lower()

    matched_terms = [
        term
        for term in query_terms
        if term in perfume_text
    ]

    return sorted(matched_terms)


# --------------------------------------------------
# Generate weighted recommendations
# --------------------------------------------------
def recommend_perfumes(
    query,
    perfume_data,
    model,
    top_n=5
):
    """
    Rank perfumes using notes and descriptions separately.

    Notes receive more weight because they are the most
    directly relevant fragrance information in this dataset.
    """

    cleaned_query = str(query).strip().lower()

    if not cleaned_query:
        raise ValueError(
            "The preference query cannot be empty."
        )

    notes_query_vector = model[
        "notes_vectorizer"
    ].transform([cleaned_query])

    description_query_vector = model[
        "description_vectorizer"
    ].transform([cleaned_query])

    notes_scores = cosine_similarity(
        notes_query_vector,
        model["notes_matrix"]
    ).flatten()

    description_scores = cosine_similarity(
        description_query_vector,
        model["description_matrix"]
    ).flatten()

    has_notes = (
        perfume_data["notes"]
        .str.strip()
        .ne("")
        .astype(float)
        .to_numpy()
    )

    # Baseline scoring design:
    # 70% verified note similarity
    # 30% general description similarity
    weighted_scores = (
        0.70 * notes_scores
        + 0.30 * description_scores
    )

    # Small quality adjustment for records with verified notes
    weighted_scores = (
        weighted_scores
        + 0.02 * has_notes
    )

    ranked_indices = weighted_scores.argsort()[::-1]

    recommendations = []

    for index in ranked_indices:
        final_score = float(weighted_scores[index])

        if final_score <= 0:
            continue

        perfume = perfume_data.iloc[index]

        matched_notes = find_matched_terms(
            cleaned_query,
            perfume["notes"]
        )

        matched_description_terms = find_matched_terms(
            cleaned_query,
            (
                perfume["name"]
                + " "
                + perfume["brand"]
                + " "
                + perfume["description"]
            )
        )

        recommendations.append(
            {
                "perfume_id": perfume["perfume_id"],
                "name": perfume["name"],
                "brand": perfume["brand"],
                "notes": perfume["notes"],
                "description": perfume["description"],
                "image_url": perfume["image_url"],
                "notes_score": round(
                    float(notes_scores[index]),
                    4
                ),
                "description_score": round(
                    float(description_scores[index]),
                    4
                ),
                "ranking_score": round(
                    final_score,
                    4
                ),
                "ranking_percentage": round(
                    min(final_score, 1.0) * 100,
                    1
                ),
                "matched_notes": matched_notes,
                "matched_description_terms": (
                    matched_description_terms
                ),
                "has_verified_notes": bool(
                    has_notes[index]
                )
            }
        )

        if len(recommendations) == top_n:
            break

    return pd.DataFrame(recommendations)


# --------------------------------------------------
# Console test
# --------------------------------------------------
def main():
    perfume_data = load_perfume_data()

    model = build_recommendation_model(
        perfume_data
    )

    test_query = (
        "fresh citrus woody bergamot "
        "moderate daytime fragrance"
    )

    recommendations = recommend_perfumes(
        query=test_query,
        perfume_data=perfume_data,
        model=model,
        top_n=5
    )

    print("=" * 72)
    print("OLFYNZA NOTES-WEIGHTED RECOMMENDATION TEST")
    print("=" * 72)

    print(f"\nPreference query:\n{test_query}\n")

    if recommendations.empty:
        print(
            "No recommendations were found "
            "for this preference query."
        )
        return

    for rank, row in recommendations.iterrows():
        notes_text = row["notes"]

        if not notes_text:
            notes_text = "Verified notes not available"

        matched_notes = row["matched_notes"]

        matched_notes_text = (
            ", ".join(matched_notes)
            if matched_notes
            else "No direct note words matched"
        )

        print(
            f"{rank + 1}. "
            f"{row['name']} by {row['brand']}"
        )

        print(
            f"   Ranking score: "
            f"{row['ranking_percentage']}%"
        )

        print(
            f"   Notes similarity: "
            f"{row['notes_score']}"
        )

        print(
            f"   Description similarity: "
            f"{row['description_score']}"
        )

        print(
            f"   Directly matched notes: "
            f"{matched_notes_text}"
        )

        print(
            f"   Notes: {notes_text[:200]}"
        )

        print()

    print("=" * 72)
    print(
        "The ranking score combines note similarity and "
        "description similarity. It is not a prediction of "
        "whether a person will like a perfume."
    )
    print("=" * 72)


if __name__ == "__main__":
    main()