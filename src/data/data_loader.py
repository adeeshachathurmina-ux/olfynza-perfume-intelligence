from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perfumes_clean.csv"
)


def processed_dataset_exists():
    """Check whether the processed perfume data is available."""

    return PROCESSED_DATASET_PATH.exists()


def load_processed_dataset():
    """
    Load the processed perfume dataset.

    Raises a clear error when the local dataset is unavailable.
    """

    if not processed_dataset_exists():
        raise FileNotFoundError(
            "The processed OLFYNZA dataset is unavailable. "
            "Run the local data-cleaning pipeline before "
            "starting the recommendation features."
        )

    return pd.read_csv(
        PROCESSED_DATASET_PATH,
        encoding="utf-8",
    )