import os
import pandas as pd


def test_screening_csv_exists():
    assert os.path.exists("output/company_screening.csv")


def test_screening_csv_not_empty():
    df = pd.read_csv("output/company_screening.csv")
    assert len(df) > 0


def test_required_columns():
    df = pd.read_csv("output/company_screening.csv")

    required = [
        "company_id",
        "year",
        "composite_quality_score",
        "screening_score",
        "recommendation"
    ]

    for col in required:
        assert col in df.columns


def test_recommendation_values():

    df = pd.read_csv("output/company_screening.csv")

    allowed = {
        "Strong Buy",
        "Buy",
        "Hold",
        "Avoid"
    }

    assert set(df["recommendation"]).issubset(allowed)


def test_screening_score_numeric():

    df = pd.read_csv("output/company_screening.csv")

    assert pd.api.types.is_numeric_dtype(df["screening_score"])