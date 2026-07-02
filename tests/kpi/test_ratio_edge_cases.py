import os
import pandas as pd


def test_ratio_edge_cases_csv_exists():
    assert os.path.exists("output/ratio_edge_cases.csv")


def test_ratio_edge_cases_log_exists():
    assert os.path.exists("output/ratio_edge_cases.log")


def test_ratio_edge_cases_not_empty():
    df = pd.read_csv("output/ratio_edge_cases.csv")
    assert len(df) > 0


def test_required_columns_present():
    df = pd.read_csv("output/ratio_edge_cases.csv")

    required = [
        "company_id",
        "year",
        "computed_roce",
        "high_leverage_suppressed"
    ]

    for col in required:
        assert col in df.columns


def test_financial_companies_detected():
    df = pd.read_csv("output/ratio_edge_cases.csv")

    count = (
        df.loc[
            df["high_leverage_suppressed"] == True,
            "company_id"
        ]
        .nunique()
    )

    assert count > 0