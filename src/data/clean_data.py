from pathlib import Path
import re

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "final_perfume_data.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "perfumes_clean.csv"
)

CLEANING_REPORT_PATH = (
    PROJECT_ROOT
    / "docs"
    / "data_cleaning_report.txt"
)


# --------------------------------------------------
# Load original dataset
# --------------------------------------------------
def load_dataset():
    """Load the original dataset using its confirmed encoding."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {INPUT_PATH}"
        )

    return pd.read_csv(
        INPUT_PATH,
        encoding="latin-1"
    )


# --------------------------------------------------
# Basic text cleaning
# --------------------------------------------------
def clean_text(value):
    """
    Remove unnecessary spaces and control characters
    while preserving readable perfume information.
    """

    if pd.isna(value):
        return ""

    value = str(value)

    value = value.replace("\n", " ")
    value = value.replace("\r", " ")
    value = value.replace("\t", " ")

    value = re.sub(r"\s+", " ", value)

    return value.strip()


# --------------------------------------------------
# Note normalisation
# --------------------------------------------------
def normalise_notes(value):
    """
    Standardise spacing and comma-separated fragrance notes.
    """

    cleaned_value = clean_text(value)

    if not cleaned_value:
        return ""

    notes = [
        note.strip().lower()
        for note in cleaned_value.split(",")
        if note.strip()
    ]

    # Preserve order while removing repeated notes
    unique_notes = list(dict.fromkeys(notes))

    return ", ".join(unique_notes)


# --------------------------------------------------
# Create model text
# --------------------------------------------------
def create_combined_text(row):
    """
    Combine useful text fields for the future
    content-based recommendation model.
    """

    parts = [
        row["brand"],
        row["name"],
        row["notes"],
        row["description"]
    ]

    valid_parts = [
        clean_text(part).lower()
        for part in parts
        if clean_text(part)
    ]

    return " ".join(valid_parts)


# --------------------------------------------------
# Clean dataset
# --------------------------------------------------
def clean_dataset(dataframe):
    """Apply reproducible cleaning rules."""

    original_rows = len(dataframe)

    cleaned_data = dataframe.copy()

    # Standardise column names
    cleaned_data.columns = [
        column.strip()
        .lower()
        .replace(" ", "_")
        for column in cleaned_data.columns
    ]

    required_columns = [
        "name",
        "brand",
        "description",
        "notes",
        "image_url"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in cleaned_data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing: "
            + ", ".join(missing_columns)
        )

    # Clean text columns
    for column in [
        "name",
        "brand",
        "description",
        "image_url"
    ]:
        cleaned_data[column] = (
            cleaned_data[column]
            .apply(clean_text)
        )

    cleaned_data["notes"] = (
        cleaned_data["notes"]
        .apply(normalise_notes)
    )

    # Remove records without essential identity fields
    cleaned_data = cleaned_data[
        cleaned_data["name"].ne("")
        & cleaned_data["brand"].ne("")
    ].copy()

    rows_after_identity_check = len(cleaned_data)

    # Remove fully duplicated rows
    cleaned_data = cleaned_data.drop_duplicates().copy()

    rows_after_full_duplicates = len(cleaned_data)

    # Remove duplicate products by name and brand
    cleaned_data = cleaned_data.drop_duplicates(
        subset=["name", "brand"],
        keep="first"
    ).copy()

    rows_after_product_duplicates = len(cleaned_data)

    # Recommendation eligibility
    cleaned_data["has_notes"] = (
        cleaned_data["notes"].ne("")
    )

    cleaned_data["has_description"] = (
        cleaned_data["description"].ne("")
    )

    cleaned_data["recommendation_eligible"] = (
        cleaned_data["has_notes"]
        | cleaned_data["has_description"]
    )

    # Create searchable model text
    cleaned_data["combined_text"] = cleaned_data.apply(
        create_combined_text,
        axis=1
    )

    # Add stable project ID
    cleaned_data = cleaned_data.reset_index(drop=True)

    cleaned_data.insert(
        0,
        "perfume_id",
        [
            f"OLF-{index:05d}"
            for index in range(
                1,
                len(cleaned_data) + 1
            )
        ]
    )

    # Final column order
    cleaned_data = cleaned_data[
        [
            "perfume_id",
            "name",
            "brand",
            "description",
            "notes",
            "image_url",
            "has_notes",
            "has_description",
            "recommendation_eligible",
            "combined_text"
        ]
    ]

    cleaning_statistics = {
        "original_rows": original_rows,
        "rows_after_identity_check": (
            rows_after_identity_check
        ),
        "rows_after_full_duplicates": (
            rows_after_full_duplicates
        ),
        "rows_after_product_duplicates": (
            rows_after_product_duplicates
        ),
        "final_rows": len(cleaned_data),
        "records_with_notes": int(
            cleaned_data["has_notes"].sum()
        ),
        "records_without_notes": int(
            (~cleaned_data["has_notes"]).sum()
        ),
        "eligible_records": int(
            cleaned_data[
                "recommendation_eligible"
            ].sum()
        )
    }

    return cleaned_data, cleaning_statistics


# --------------------------------------------------
# Save cleaning report
# --------------------------------------------------
def create_cleaning_report(statistics):
    """Create a human-readable cleaning report."""

    removed_identity = (
        statistics["original_rows"]
        - statistics["rows_after_identity_check"]
    )

    removed_full_duplicates = (
        statistics["rows_after_identity_check"]
        - statistics["rows_after_full_duplicates"]
    )

    removed_product_duplicates = (
        statistics["rows_after_full_duplicates"]
        - statistics["rows_after_product_duplicates"]
    )

    return f"""
============================================================
OLFYNZA DATA CLEANING REPORT
============================================================

Input file:
{INPUT_PATH}

Output file:
{OUTPUT_PATH}

Original records:
{statistics["original_rows"]}

Records removed due to missing name or brand:
{removed_identity}

Completely duplicated records removed:
{removed_full_duplicates}

Duplicate name and brand records removed:
{removed_product_duplicates}

Final cleaned records:
{statistics["final_rows"]}

Records containing fragrance notes:
{statistics["records_with_notes"]}

Records without fragrance notes:
{statistics["records_without_notes"]}

Records eligible for recommendation:
{statistics["eligible_records"]}

IMPORTANT CLEANING DECISIONS
------------------------------------------------------------
1. The original raw data was not overwritten.
2. Missing fragrance notes were kept as empty values.
3. Descriptions were not presented as verified fragrance notes.
4. Duplicate products were identified using name and brand.
5. Text spacing and note formatting were standardised.
6. A combined_text field was created for future modelling.

============================================================
END OF REPORT
============================================================
""".strip()


# --------------------------------------------------
# Run cleaning pipeline
# --------------------------------------------------
def main():
    raw_data = load_dataset()

    cleaned_data, statistics = clean_dataset(
        raw_data
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned_data.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    cleaning_report = create_cleaning_report(
        statistics
    )

    CLEANING_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    CLEANING_REPORT_PATH.write_text(
        cleaning_report,
        encoding="utf-8"
    )

    print(cleaning_report)

    print(
        "\nClean dataset saved successfully at:\n"
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()