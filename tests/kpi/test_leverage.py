from src.analytics.ratios import *

# Debt to Equity

def test_debt_to_equity():
    assert calculate_debt_to_equity(100, 300, 200) == 0.2


def test_debt_to_equity_debt_free():
    assert calculate_debt_to_equity(0, 500, 500) == 0


def test_debt_to_equity_negative_equity():
    assert calculate_debt_to_equity(100, -500, 100) is None


# High Leverage Flag

def test_high_leverage_flag():
    assert high_leverage_flag(6.2, "Technology") is True


def test_high_leverage_financial_company():
    assert high_leverage_flag(8.5, "Financials") is False


# Interest Coverage

def test_interest_coverage():
    assert calculate_interest_coverage(500, 50, 100) == 5.5


def test_interest_zero():
    assert calculate_interest_coverage(500, 50, 0) is None


# Debt Free Label

def test_debt_free_label():
    assert get_icr_label(None) == "Debt Free"


# ICR Warning

def test_icr_warning():
    assert icr_warning_flag(1.2) is True


def test_icr_safe():
    assert icr_warning_flag(3.8) is False


# Net Debt

def test_net_debt():
    assert calculate_net_debt(1000, 250) == 750


# Asset Turnover

def test_asset_turnover():
    assert calculate_asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero_assets():
    assert calculate_asset_turnover(1000, 0) is None