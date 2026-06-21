from src.etl.loader import *
from src.etl.normaliser import *


def test_companies():
    assert len(load_companies()) > 0


def test_profitandloss():
    assert len(load_profitandloss()) > 0


def test_balancesheet():
    assert len(load_balancesheet()) > 0


def test_cashflow():
    assert len(load_cashflow()) > 0


def test_stock_prices():
    assert len(load_stock_prices()) > 0


def test_normalize_year():
    assert normalize_year("FY22") == 2022


def test_normalize_ticker():
    assert normalize_ticker("tcs.ns") == "TCS"