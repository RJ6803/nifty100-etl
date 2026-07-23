import pandas as pd

from src.analytics.cashflow_kpis import (
    quality_label,
    capex_label,
    classify_pattern
)

# Free Cash Flow

def test_free_cash_flow():

    operating = 100
    investing = -40

    assert operating + investing == 60

# CFO Quality

def test_quality_high():

    assert quality_label(1.4) == "High Quality"


def test_quality_moderate():

    assert quality_label(0.8) == "Moderate"


def test_quality_low():

    assert quality_label(0.3) == "Accrual Risk"


# CapEx Labels

def test_capex_asset_light():

    assert capex_label(2.5) == "Asset Light"


def test_capex_moderate():

    assert capex_label(5.5) == "Moderate"


def test_capex_capital_intensive():

    assert capex_label(12.2) == "Capital Intensive"

# FCF Conversion

def test_fcf_conversion():

    free_cash_flow = 200
    operating_profit = 100

    ratio = free_cash_flow / operating_profit * 100

    assert ratio == 200


# Capital Allocation Patterns

def test_pattern_reinvestor():

    row = pd.Series({
        "cfo_sign": "+",
        "cfi_sign": "-",
        "cff_sign": "-",
        "cfo_quality_score": 0.8
    })

    assert classify_pattern(row) == "Reinvestor"


def test_pattern_shareholder_returns():

    row = pd.Series({
        "cfo_sign": "+",
        "cfi_sign": "-",
        "cff_sign": "-",
        "cfo_quality_score": 1.5
    })

    assert classify_pattern(row) == "Shareholder Returns"


def test_pattern_liquidating():

    row = pd.Series({
        "cfo_sign": "+",
        "cfi_sign": "+",
        "cff_sign": "-"
    })

    assert classify_pattern(row) == "Liquidating Assets"


def test_pattern_distress():

    row = pd.Series({
        "cfo_sign": "-",
        "cfi_sign": "+",
        "cff_sign": "+"
    })

    assert classify_pattern(row) == "Distress Signal"


def test_pattern_growth_debt():

    row = pd.Series({
        "cfo_sign": "-",
        "cfi_sign": "-",
        "cff_sign": "+"
    })

    assert classify_pattern(row) == "Growth Funded by Debt"


def test_pattern_cash_accumulator():

    row = pd.Series({
        "cfo_sign": "+",
        "cfi_sign": "+",
        "cff_sign": "+"
    })

    assert classify_pattern(row) == "Cash Accumulator"


def test_pattern_pre_revenue():

    row = pd.Series({
        "cfo_sign": "-",
        "cfi_sign": "-",
        "cff_sign": "-"
    })

    assert classify_pattern(row) == "Pre-Revenue"


def test_pattern_mixed():

    row = pd.Series({
        "cfo_sign": "+",
        "cfi_sign": "-",
        "cff_sign": "+"
    })

    assert classify_pattern(row) == "Mixed"

