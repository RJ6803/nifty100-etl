import re


# ==========================================================
# SECTOR MAPPING
# ==========================================================

SECTOR_MAP = {
    "it": "Information Technology",
    "technology": "Information Technology",
    "tech": "Information Technology",

    "bank": "Financials",
    "banking": "Financials",
    "financial": "Financials",
    "financials": "Financials",

    "energy": "Energy",
    "oil": "Energy",
    "gas": "Energy",

    "pharma": "Healthcare",
    "health": "Healthcare",
    "healthcare": "Healthcare",
    "hospital": "Healthcare",

    "auto": "Consumer Discretionary",
    "automobile": "Consumer Discretionary",

    "consumer": "Consumer Staples",
    "fmcg": "Consumer Staples",

    "industrial": "Industrials",
    "industrials": "Industrials",

    "metal": "Materials",
    "metals": "Materials",
    "cement": "Materials",
    "material": "Materials",

    "real estate": "Real Estate",
    "realty": "Real Estate",

    "telecom": "Communication Services",
    "communication": "Communication Services"
}


# ==========================================================
# METRIC MAPPING
# ==========================================================

METRIC_MAP = {

    "roe": "return_on_equity_pct",
    "return on equity": "return_on_equity_pct",

    "roce": "return_on_capital_employed_pct",
    "return on capital employed": "return_on_capital_employed_pct",

    "profit margin": "net_profit_margin_pct",
    "net margin": "net_profit_margin_pct",

    "operating margin": "operating_profit_margin_pct",

    "debt equity": "debt_to_equity",
    "debt-to-equity": "debt_to_equity",
    "debt": "debt_to_equity",
    "leverage": "debt_to_equity",

    "interest coverage": "interest_coverage",

    "asset turnover": "asset_turnover",

    "revenue growth": "revenue_cagr_5yr",
    "sales growth": "revenue_cagr_5yr",

    "pat growth": "pat_cagr_5yr",

    "quality score": "composite_quality_score",
    "composite score": "composite_quality_score",
    "quality": "composite_quality_score",

    "cash flow": "fcf_positive_flag",
    "positive cash flow": "fcf_positive_flag",
    "negative cash flow": "fcf_positive_flag"
}


# ==========================================================
# OPERATOR DETECTION
# ==========================================================

OPERATORS = {

    ">": [
        "above",
        "greater than",
        "more than",
        "over",
        ">"
    ],

    "<": [
        "below",
        "less than",
        "under",
        "<"
    ],

    "=": [
        "equal",
        "equals",
        "="
    ]
}


# ==========================================================
# MAIN PARSER
# ==========================================================

def parse_query(query: str):

    query = query.lower()

    result = {
        "sector": None,
        "metric": None,
        "operator": None,
        "value": None,
        "top_n": None,
        "cashflow": None
    }

    # ------------------------------------------------------
    # Sector
    # ------------------------------------------------------

    for keyword, sector in SECTOR_MAP.items():

        if keyword in query:

            result["sector"] = sector

            break

    # ------------------------------------------------------
    # Metric
    # ------------------------------------------------------

    for keyword, metric in METRIC_MAP.items():

        if keyword in query:

            result["metric"] = metric

            break

    # ------------------------------------------------------
    # Cashflow
    # ------------------------------------------------------

    if "positive cash flow" in query:

        result["cashflow"] = "positive"

    elif "negative cash flow" in query:

        result["cashflow"] = "negative"

    # ------------------------------------------------------
    # Operator
    # ------------------------------------------------------

    for op, words in OPERATORS.items():

        for word in words:

            if word in query:

                result["operator"] = op

                break

    # ------------------------------------------------------
    # Number
    # ------------------------------------------------------

    number = re.search(r"\d+(\.\d+)?", query)

    if number:

        result["value"] = float(number.group())

    # ------------------------------------------------------
    # Top N
    # ------------------------------------------------------

    top = re.search(r"(top|best)\s+(\d+)", query)

    if top:

        result["top_n"] = int(top.group(2))

    return result


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    while True:

        q = input("\nQuery (or exit): ")

        if q.lower() == "exit":
            break

        print(parse_query(q))