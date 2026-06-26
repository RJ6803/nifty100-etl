from src.analytics.ratios import *

# Net Profit Margin

def test_net_profit_margin():
    assert calculate_net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert calculate_net_profit_margin(100, 0) is None


# Operating Profit Margin

def test_operating_profit_margin():
    assert calculate_operating_profit_margin(250, 1000) == 25.0


def test_opm_difference_detected():
    assert check_opm_difference(22.5, 20.0) is True


# Return on Equity

def test_roe():
    assert calculate_roe(150, 500, 500) == 15.0


def test_roe_negative_equity():
    assert calculate_roe(100, -500, 100) is None


# Return on Capital Employed

def test_roce():
    assert calculate_roce(200, 500, 500, 500) == 13.33


def test_roce_zero_capital():
    assert calculate_roce(100, -500, 0, 0) is None


# Return on Assets

def test_roa():
    assert calculate_roa(150, 1000) == 15.0


def test_roa_zero_assets():
    assert calculate_roa(100, 0) is None


