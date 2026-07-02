from src.analytics.cagr import *


# NORMAL CAGR

def test_revenue_cagr_normal():
    value, flag = revenue_cagr(100, 200, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


def test_pat_cagr_normal():
    value, flag = pat_cagr(50, 100, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


def test_eps_cagr_normal():
    value, flag = eps_cagr(10, 20, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


# ZERO BASE

def test_zero_base():
    value, flag = revenue_cagr(0, 100, 5)

    assert value is None
    assert flag == "ZERO_BASE"


# TURNAROUND

def test_turnaround():
    value, flag = pat_cagr(-100, 200, 5)

    assert value is None
    assert flag == "TURNAROUND"


# DECLINE TO LOSS

def test_decline_to_loss():
    value, flag = revenue_cagr(200, -50, 5)

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


# BOTH NEGATIVE


def test_both_negative():
    value, flag = eps_cagr(-10, -20, 5)

    assert value is None
    assert flag == "BOTH_NEGATIVE"


# INSUFFICIENT YEARS

def test_insufficient_years():
    value, flag = revenue_cagr(100, 200, 0)

    assert value is None
    assert flag == "INSUFFICIENT"


# LARGE GROWTH

def test_large_growth():
    value, flag = revenue_cagr(100, 800, 10)

    assert value > 20
    assert flag == "NORMAL"


# NO GROWTH

def test_no_growth():
    value, flag = revenue_cagr(100, 100, 5)

    assert value == 0
    assert flag == "NORMAL"