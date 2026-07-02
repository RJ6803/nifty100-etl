import math


# CAGR ENGINE

def calculate_cagr(start_value, end_value, years):
    """
    Generic CAGR calculator.

    Returns:
        (cagr_value, flag)
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    if start_value > 0 and end_value > 0:

        cagr = (
            (end_value / start_value)
            ** (1 / years)
            - 1
        ) * 100

        return round(cagr, 2), "NORMAL"

    return None, "UNKNOWN"


# Revenue CAGR

def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(
        start_sales,
        end_sales,
        years
    )


# PAT CAGR

def pat_cagr(start_profit, end_profit, years):
    return calculate_cagr(
        start_profit,
        end_profit,
        years
    )


# EPS CAGR

def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(
        start_eps,
        end_eps,
        years
    )