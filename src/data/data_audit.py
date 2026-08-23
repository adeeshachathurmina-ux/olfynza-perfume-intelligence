from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "final_perfume_data.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "docs"
    / "data_audit_report.txt"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------
def load_dataset():
    """Load the perfume dataset using a compatible encoding."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset was not found at: {DATASET_PATH}"
        )

    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1"
    ]

    for encoding_name in encodings_to_try:
        try:
            dataframe = pd.read_csv(
                DATASET_PATH,
                encoding=encoding_name
            )

            print(
                "Dataset loaded successfully using encoding: "
                f"{encoding_name}"
            )

            return dataframe

        except UnicodeDecodeError:
            print(
                f"Could not read using {encoding_name}. "
                "Trying another encoding..."
            )

    raise UnicodeError(
        "Unable to read the dataset using the supported encodings."
    )

# --------------------------------------------------
# Create audit report
# --------------------------------------------------
def create_audit_report(dataframe):
    """Create a basic quality report for the dataset."""

    missing_values = dataframe.isnull().sum()
    missing_percentages = (
        dataframe.isnull().mean() * 100
    ).round(2)

    duplicate_rows = dataframe.duplicated().sum()

    report_lines = [
        "=" * 60,
        "OLFYNZA DATA AUDIT REPORT",
        "=" * 60,
        "",
        f"Dataset path: {DATASET_PATH}",
        f"Number of rows: {dataframe.shape[0]}",
        f"Number of columns: {dataframe.shape[1]}",
        f"Completely duplicated rows: {duplicate_rows}",
        "",
        "COLUMN NAMES",
        "-" * 60
    ]

    for column in dataframe.columns:
        report_lines.append(str(column))

    report_lines.extend(
        [
            "",
            "DATA TYPES",
            "-" * 60
        ]
    )

    for column in dataframe.columns:
        report_lines.append(
            f"{column}: {dataframe[column].dtype}"
        )

    report_lines.extend(
        [
            "",
            "MISSING VALUES",
            "-" * 60
        ]
    )

    for column in dataframe.columns:
        report_lines.append(
            f"{column}: "
            f"{missing_values[column]} missing "
            f"({missing_percentages[column]}%)"
        )

    report_lines.extend(
        [
            "",
            "UNIQUE VALUES PER COLUMN",
            "-" * 60
        ]
    )

    for column in dataframe.columns:
        report_lines.append(
            f"{column}: "
            f"{dataframe[column].nunique(dropna=True)}"
        )

    report_lines.extend(
        [
            "",
            "FIRST FIVE RECORDS",
            "-" * 60,
            dataframe.head().to_string(),
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60
        ]
    )

    return "\n".join(report_lines)


# --------------------------------------------------
# Run audit
# --------------------------------------------------
def main():
    perfume_data = load_dataset()

    audit_report = create_audit_report(
        perfume_data
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.write_text(
        audit_report,
        encoding="utf-8"
    )

    print(audit_report)

    print(
        "\nAudit report saved successfully at:\n"
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()