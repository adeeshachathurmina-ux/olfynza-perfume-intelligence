import pandas as pd

from src.data.data_loader import (
    load_processed_dataset,
    processed_dataset_exists,
)


def test_processed_dataset_exists():
    """The local modelling dataset must be available."""

    assert processed_dataset_exists()


def test_processed_dataset_can_be_loaded():
    """The processed dataset must load as a DataFrame."""

    data = load_processed_dataset()

    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert len(data) == 2191