import pandas as pd
import pytest

from src.models.recommender import (
    build_recommendation_model,
    load_perfume_data,
    recommend_perfumes,
)


# --------------------------------------------------
# Shared test data
# --------------------------------------------------
@pytest.fixture(scope="module")
def perfume_data():
    """Load the cleaned dataset once for all tests."""

    return load_perfume_data()


@pytest.fixture(scope="module")
def recommendation_model(perfume_data):
    """Build the recommendation model once."""

    return build_recommendation_model(
        perfume_data
    )


# --------------------------------------------------
# Dataset tests
# --------------------------------------------------
def test_dataset_is_not_empty(perfume_data):
    """The cleaned dataset must contain records."""

    assert not perfume_data.empty


def test_required_columns_exist(perfume_data):
    """The model requires these columns."""

    required_columns = {
        "perfume_id",
        "name",
        "brand",
        "notes",
        "description",
        "image_url",
        "combined_text",
    }

    assert required_columns.issubset(
        set(perfume_data.columns)
    )


def test_perfume_ids_are_unique(perfume_data):
    """Every cleaned perfume must have a unique ID."""

    assert perfume_data[
        "perfume_id"
    ].is_unique


def test_name_and_brand_are_not_empty(perfume_data):
    """Every record must contain its product identity."""

    assert perfume_data[
        "name"
    ].str.strip().ne("").all()

    assert perfume_data[
        "brand"
    ].str.strip().ne("").all()


# --------------------------------------------------
# Recommendation tests
# --------------------------------------------------
def test_recommender_returns_requested_number(
    perfume_data,
    recommendation_model,
):
    """A normal query should return five results."""

    results = recommend_perfumes(
        query="fresh citrus bergamot woody",
        perfume_data=perfume_data,
        model=recommendation_model,
        top_n=5,
    )

    assert isinstance(
        results,
        pd.DataFrame
    )

    assert len(results) == 5


def test_recommendation_columns_exist(
    perfume_data,
    recommendation_model,
):
    """Results must contain explainable fields."""

    results = recommend_perfumes(
        query="vanilla amber sweet warm",
        perfume_data=perfume_data,
        model=recommendation_model,
        top_n=5,
    )

    expected_columns = {
        "perfume_id",
        "name",
        "brand",
        "notes",
        "ranking_score",
        "ranking_percentage",
        "matched_notes",
        "has_verified_notes",
    }

    assert expected_columns.issubset(
        set(results.columns)
    )


def test_results_are_ranked_highest_first(
    perfume_data,
    recommendation_model,
):
    """Recommendation scores must be descending."""

    results = recommend_perfumes(
        query="floral rose jasmine",
        perfume_data=perfume_data,
        model=recommendation_model,
        top_n=10,
    )

    scores = results[
        "ranking_score"
    ].tolist()

    assert scores == sorted(
        scores,
        reverse=True
    )


def test_empty_query_is_rejected(
    perfume_data,
    recommendation_model,
):
    """An empty preference query must raise an error."""

    with pytest.raises(ValueError):
        recommend_perfumes(
            query="   ",
            perfume_data=perfume_data,
            model=recommendation_model,
            top_n=5,
        )


def test_recommendations_have_positive_scores(
    perfume_data,
    recommendation_model,
):
    """Returned recommendations must have positive scores."""

    results = recommend_perfumes(
        query="aquatic marine fresh",
        perfume_data=perfume_data,
        model=recommendation_model,
        top_n=5,
    )

    assert (
        results["ranking_score"] > 0
    ).all()