def calculate_net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) * 100
    """

    if sales is None or sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def calculate_operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100
    """

    if sales is None or sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)


def calculate_roe(net_profit, equity_capital, reserves):
    """
    Return on Equity
    ROE = Net Profit / (Equity + Reserves) * 100
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def calculate_roce(ebit, equity_capital, reserves, borrowings):
    """
    Return on Capital Employed
    ROCE = EBIT / (Equity + Reserves + Borrowings) * 100
    """

    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return round((ebit / capital_employed) * 100, 2)


def calculate_roa(net_profit, total_assets):
    """
    Return on Assets
    ROA = Net Profit / Total Assets * 100
    """

    if total_assets is None or total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)


def check_opm_difference(calculated_opm, source_opm):
    """
    Cross-check calculated OPM against source OPM.

    Returns:
        True  -> Difference > 1%
        False -> Difference <= 1%
    """

    if calculated_opm is None or source_opm is None:
        return False

    difference = abs(calculated_opm - source_opm)

    return difference > 1





# ==========================================================
# DAY 9 – LEVERAGE & EFFICIENCY RATIOS
# ==========================================================

def calculate_debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt to Equity Ratio

    Returns:
        0 if borrowings == 0
        None if equity <= 0
    """

    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(de_ratio, sector="Others"):
    """
    Flag companies with D/E > 5,
    excluding Financial sector.
    """

    if sector.lower() == "financials":
        return False

    if de_ratio is None:
        return False

    return de_ratio > 5


def calculate_interest_coverage(
    operating_profit,
    other_income,
    interest
):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None

    ebit = operating_profit + other_income

    return round(ebit / interest, 2)


def get_icr_label(icr):
    """
    Label for Interest Coverage.
    """

    if icr is None:
        return "Debt Free"

    return "Normal"


def icr_warning_flag(icr):
    """
    Company at risk if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def calculate_net_debt(
    borrowings,
    investments
):
    """
    Net Debt
    """

    return borrowings - investments


def calculate_asset_turnover(
    sales,
    total_assets
):
    """
    Asset Turnover
    """

    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)