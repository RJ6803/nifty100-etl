
from src.etl.normaliser import normalize_year, normalize_ticker


def test_normalize_year_fy22():
    assert normalize_year("FY22") == 2022


def test_normalize_year_fy23():
    assert normalize_year("FY23") == 2023


def test_normalize_year_2024():
    assert normalize_year("2024") == 2024


def test_normalize_year_range():
    assert normalize_year("2021-22") == 2022


def test_normalize_ticker_ns():
    assert normalize_ticker("tcs.ns") == "TCS"


def test_normalize_ticker_upper():
    assert normalize_ticker("INFY") == "INFY"


def test_normalize_ticker_spaces():
    assert normalize_ticker(" reliance.ns ") == "RELIANCE"

