from typing import Any

import pandas as pd
import streamlit as st
from supabase import Client, create_client


TABLE_NAME = "recommendation_feedback"


# --------------------------------------------------
# Read Supabase credentials
# --------------------------------------------------
def get_supabase_credentials():
    """
    Read Supabase credentials from Streamlit Secrets.

    Credentials are never stored directly in the source code.
    """

    try:
        supabase_settings = st.secrets["supabase"]

        project_url = str(
            supabase_settings["url"]
        ).strip()

        secret_key = str(
            supabase_settings["secret_key"]
        ).strip()

    except (
        KeyError,
        FileNotFoundError,
    ):
        return None, None

    if not project_url or not secret_key:
        return None, None

    return project_url, secret_key


# --------------------------------------------------
# Check cloud configuration
# --------------------------------------------------
def supabase_is_configured():
    """Return True when required credentials are available."""

    project_url, secret_key = (
        get_supabase_credentials()
    )

    return bool(
        project_url
        and secret_key
    )


# --------------------------------------------------
# Create database client
# --------------------------------------------------
@st.cache_resource
def get_supabase_client():
    """
    Create and cache the Supabase client.

    The secret key remains in Streamlit Secrets and is
    not displayed in the user interface.
    """

    project_url, secret_key = (
        get_supabase_credentials()
    )

    if not project_url or not secret_key:
        return None

    client: Client = create_client(
        project_url,
        secret_key,
    )

    return client


# --------------------------------------------------
# Prepare database-safe record
# --------------------------------------------------
def prepare_database_record(
    record: dict[str, Any],
):
    """Convert a feedback record into database-safe values."""

    database_record = {}

    for key, value in record.items():
        if pd.isna(value):
            database_record[key] = None

        elif key == "ranking_score":
            try:
                database_record[key] = float(
                    value
                )
            except (TypeError, ValueError):
                database_record[key] = 0.0

        elif key == "recommendation_position":
            try:
                database_record[key] = int(
                    value
                )
            except (TypeError, ValueError):
                database_record[key] = 0

        else:
            database_record[key] = str(
                value
            )

    return database_record


# --------------------------------------------------
# Insert feedback
# --------------------------------------------------
def insert_feedback_record(
    record: dict[str, Any],
):
    """
    Insert one feedback record into Supabase.

    Returns a consistent result dictionary for the
    Streamlit recommendation page.
    """

    client = get_supabase_client()

    if client is None:
        return {
            "success": False,
            "duplicate": False,
            "configured": False,
            "message": (
                "Cloud feedback storage is not configured."
            ),
        }

    database_record = prepare_database_record(
        record
    )

    try:
        response = (
            client
            .table(TABLE_NAME)
            .insert(database_record)
            .execute()
        )

        inserted_data = (
            response.data
            if response.data
            else []
        )

        return {
            "success": True,
            "duplicate": False,
            "configured": True,
            "message": (
                "Thank you. Your anonymous feedback "
                "was saved securely."
            ),
            "data": inserted_data,
        }

    except Exception as error:
        print(
            "SUPABASE INSERT ERROR:",
            repr(error),
            flush=True,
        )

        error_message = str(
            error
        ).lower()

        duplicate_detected = (
            "duplicate key" in error_message
            or "23505" in error_message
            or "unique constraint" in error_message
        )

        if duplicate_detected:
            return {
                "success": False,
                "duplicate": True,
                "configured": True,
                "message": (
                    "This feedback was already recorded "
                    "for this perfume in the current session."
                ),
            }

        return {
            "success": False,
            "duplicate": False,
            "configured": True,
            "message": (
                "The feedback could not be saved to cloud "
                "storage. Please try again."
            ),
        }

# --------------------------------------------------
# Connection health check
# --------------------------------------------------
def test_supabase_connection():
    """Test whether the feedback table can be reached."""

    client = get_supabase_client()

    if client is None:
        return {
            "success": False,
            "message": (
                "Supabase credentials are unavailable."
            ),
        }

    try:
        client.table(
            TABLE_NAME
        ).select(
            "feedback_id"
        ).limit(
            1
        ).execute()

        return {
            "success": True,
            "message": (
                "OLFYNZA connected to Supabase successfully."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "message": (
                "OLFYNZA could not connect to the "
                "Supabase feedback table."
            ),
            "technical_error": str(error),
        }
        # --------------------------------------------------
# Load all cloud feedback
# --------------------------------------------------
def load_feedback_records():
    """
    Load feedback records from the Supabase table.

    Returns an empty DataFrame if cloud storage is not
    configured or the request cannot be completed.
    """

    client = get_supabase_client()

    if client is None:
        return pd.DataFrame()

    try:
        response = (
            client
            .table(TABLE_NAME)
            .select("*")
            .order(
                "submitted_at_utc",
                desc=True,
            )
            .execute()
        )

        records = (
            response.data
            if response.data
            else []
        )

        return pd.DataFrame(
            records
        )

    except Exception as error:
        print(
            "SUPABASE LOAD ERROR:",
            repr(error),
            flush=True,
        )

        return pd.DataFrame()


# --------------------------------------------------
# Connection health check
# --------------------------------------------------
def test_supabase_connection():
    """
    Test whether the Supabase feedback table can be reached.

    This function does not display or return credentials.
    """

    client = get_supabase_client()

    if client is None:
        return {
            "success": False,
            "message": (
                "Supabase credentials are unavailable."
            ),
        }

    try:
        (
            client
            .table(TABLE_NAME)
            .select("feedback_id")
            .limit(1)
            .execute()
        )

        return {
            "success": True,
            "message": (
                "OLFYNZA connected to Supabase successfully."
            ),
        }

    except Exception as error:
        print(
            "SUPABASE CONNECTION ERROR:",
            repr(error),
            flush=True,
        )

        return {
            "success": False,
            "message": (
                "OLFYNZA could not connect to the "
                "Supabase feedback table."
            ),
        }