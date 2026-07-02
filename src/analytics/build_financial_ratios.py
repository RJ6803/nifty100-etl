import sqlite3
import os
import pandas as pd


# Connect SQLite

conn = sqlite3.connect("data/nifty100.db")


# Load Source Tables

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

balance_sheet = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

company_cagr = pd.read_sql(
    "SELECT * FROM company_cagr",
    conn
)

conn.close()


# Merge Profit & Loss + Balance Sheet

financial = profit_loss.merge(
    balance_sheet,
    on=["company_id", "year"],
    how="left",
    suffixes=("_pl", "_bs")
)

financial = financial.merge(
    cashflow,
    on=["company_id", "year"],
    how="left"
)


# Merge CAGR

financial = financial.merge(
    company_cagr,
    on="company_id",
    how="left"
)


# Merge Company Information

financial = financial.merge(
    companies,
    left_on="company_id",
    right_on="id",

    how="left"

)



# KPI Calculations

# Net Profit Margin
financial["net_profit_margin_pct"] = (
    financial["net_profit"] / financial["sales"] * 100
)

# Operating Profit Margin
financial["operating_profit_margin_pct"] = (
    financial["operating_profit"] / financial["sales"] * 100
)

# Return on Equity
financial["return_on_equity_pct"] = (
    financial["net_profit"] /
    (financial["equity_capital"] + financial["reserves"])
) * 100

# Debt to Equity
financial["debt_to_equity"] = (
    financial["borrowings"] /
    (financial["equity_capital"] + financial["reserves"])
)

# Interest Coverage
financial["interest_coverage"] = financial.apply(
    lambda row:
    None if row["interest"] == 0
    else (row["operating_profit"] + row["other_income"]) / row["interest"],
    axis=1
)

# Asset Turnover
financial["asset_turnover"] = (
    financial["sales"] /
    financial["total_assets"]
)

# Free Cash Flow
financial["free_cash_flow_cr"] = (
    financial["operating_activity"] +
    financial["investing_activity"]
)

# CapEx
financial["capex_cr"] = financial["investing_activity"].abs()

# Cash From Operations
financial["cash_from_operations_cr"] = financial["operating_activity"]

# EPS
financial["earnings_per_share"] = financial["eps"]

# Book Value Per Share
financial["book_value_per_share"] = financial["book_value"]

# Dividend Payout
financial["dividend_payout_ratio_pct"] = financial["dividend_payout"]

# Total Debt
financial["total_debt_cr"] = financial["borrowings"]

# Revenue CAGR
financial["revenue_cagr_5yr"] = financial["revenue_cagr_5yr"]

# PAT CAGR
financial["pat_cagr_5yr"] = financial["pat_cagr_5yr"]

# EPS CAGR
financial["eps_cagr_5yr"] = financial["eps_cagr_5yr"]




# Composite Quality Score

financial["composite_quality_score"] = (
    financial[
        [
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "asset_turnover"
        ]
    ]
    .fillna(0)
    .mean(axis=1)
)




# Final Financial Ratios Table

financial_ratios = financial[
    [
        "company_id",
        "year",

        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",

        "free_cash_flow_cr",
        "capex_cr",
        "cash_from_operations_cr",

        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",

        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",

        "composite_quality_score"
    ]
]




# Write SQLite Table

conn = sqlite3.connect("data/nifty100.db")

financial_ratios.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("financial_ratios table written successfully!")




# Export CSV

os.makedirs("output", exist_ok=True)

financial_ratios.to_csv(
    "output/financial_ratios.csv",
    index=False
)

print("financial_ratios.csv exported.")



# Summary

print(financial_ratios.head())
print("Rows :", len(financial_ratios))
print("Columns :", len(financial_ratios.columns))