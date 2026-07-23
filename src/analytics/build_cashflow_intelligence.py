import sqlite3
import os
import pandas as pd

# ============================================
# Cash Flow Intelligence ETL
# Sprint 5
# ============================================

# -----------------------------
# Connect Database
# -----------------------------
conn = sqlite3.connect("data/nifty100.db")

financial = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

peer = pd.read_sql(
    "SELECT * FROM peer_percentiles",
    conn
)

conn.close()

# ====================================================
# Cash Quality Score
# ====================================================

financial["cash_quality_score"] = (
      financial["fcf_positive_flag"] * 30
    + financial["cfo_pat_ratio"].fillna(0).clip(0, 2) * 35
    + financial["composite_quality_score"] * 0.35
)

financial["cash_quality_score"] = (
    financial["cash_quality_score"]
    .clip(0, 100)
    .round(2)
)

# ====================================================
# Cash Quality Label
# ====================================================

def cash_quality_label(score):

    if pd.isna(score):
        return "Unknown"

    if score >= 75:
        return "Strong"

    elif score >= 50:
        return "Moderate"

    else:
        return "Weak"


financial["cash_quality_label"] = (
    financial["cash_quality_score"]
    .apply(cash_quality_label)
)

# ====================================================
# Cash Conversion Label
# ====================================================

def cash_conversion_label(ratio):

    if pd.isna(ratio):
        return "Unknown"

    if ratio >= 1.20:
        return "Excellent"

    elif ratio >= 0.80:
        return "Good"

    else:
        return "Weak"


financial["cash_conversion_label"] = (
    financial["cfo_pat_ratio"]
    .apply(cash_conversion_label)
)

# ====================================================
# Cash Flow Trend
# ====================================================

financial["year_num"] = (
    pd.to_datetime(
        financial["year"],
        format="%b %Y",
        errors="coerce"
    ).dt.year
)

financial = financial.sort_values(
    [
        "company_id",
        "year_num"
    ]
)

financial["fcf_change"] = (
    financial.groupby("company_id")[
        "free_cash_flow_cr"
    ].diff()
)


def cashflow_trend(change):

    if pd.isna(change):
        return "Stable"

    if change > 0:
        return "Improving"

    elif change < 0:
        return "Declining"

    else:
        return "Stable"


financial["cashflow_trend"] = (
    financial["fcf_change"]
    .apply(cashflow_trend)
)

# ====================================================
# Cash Flow Insight Generator
# ====================================================

def generate_insight(row):

    quality = row["cash_quality_label"]
    conversion = row["cash_conversion_label"]
    trend = row["cashflow_trend"]

    if (
        quality == "Strong"
        and conversion == "Excellent"
        and trend == "Improving"
    ):

        return (
            "Strong cash generation with improving free "
            "cash flow and excellent cash conversion."
        )

    elif (
        quality == "Strong"
        and trend == "Stable"
    ):

        return (
            "Cash flow remains consistently strong "
            "with stable operating performance."
        )

    elif (
        quality == "Moderate"
        and trend == "Improving"
    ):

        return (
            "Cash generation is improving, although "
            "there is still room for stronger quality."
        )

    elif (
        quality == "Moderate"
        and trend == "Stable"
    ):

        return (
            "Cash generation is stable with acceptable "
            "cash conversion."
        )

    elif (
        quality == "Weak"
        and trend == "Declining"
    ):

        return (
            "Cash generation is deteriorating and "
            "requires attention."
        )

    elif (
        quality == "Weak"
    ):

        return (
            "Weak cash generation with below-average "
            "cash conversion."
        )

    else:

        return (
            "Cash flow profile remains stable."
        )


financial["cashflow_insight"] = (
    financial.apply(
        generate_insight,
        axis=1
    )
)

# ====================================================
# Final Table
# ====================================================

cashflow_intelligence = financial[
    [
        "company_id",
        "year",

        "free_cash_flow_cr",
        "cash_from_operations_cr",
        "cfo_pat_ratio",
        "fcf_positive_flag",

        "cash_quality_score",
        "cash_quality_label",
        "cash_conversion_label",
        "cashflow_trend",

        "cashflow_insight"
    ]
]

# ====================================================
# Save SQLite
# ====================================================

conn = sqlite3.connect("data/nifty100.db")

cashflow_intelligence.to_sql(
    "cashflow_intelligence",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("cashflow_intelligence table written successfully!")

# ====================================================
# Export CSV
# ====================================================

os.makedirs(
    "output",
    exist_ok=True
)

cashflow_intelligence.to_csv(
    "output/cashflow_intelligence.csv",
    index=False
)

print("cashflow_intelligence.csv exported.")

# ====================================================
# Summary
# ====================================================

print(cashflow_intelligence.head())

print(
    f"Rows : {len(cashflow_intelligence)}"
)

print(
    f"Columns : {len(cashflow_intelligence.columns)}"
)