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

print(
    financial[
        [
            "company_id",
            "year",
            "net_profit",
            "equity_capital",
            "reserves"
        ]
    ].head(20)
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

sectors = pd.read_excel(
    "data/raw/sectors.xlsx"
)[
    [
        "company_id",
        "broad_sector",
        "sub_sector"
    ]
]

financial = financial.merge(
    sectors,
    on="company_id",
    how="left"
)

print(financial.columns.tolist())

financial["return_on_equity_pct"] = financial["roe_percentage"]

# KPI Calculations

# Net Profit Margin
financial["net_profit_margin_pct"] = (
    financial["net_profit"] / financial["sales"] * 100
)

# Operating Profit Margin
financial["operating_profit_margin_pct"] = (
    financial["operating_profit"] / financial["sales"] * 100
)

print("\n===== DEBUG TCS ROE =====")

print(
    financial.loc[
        financial["company_id"] == "TCS",
        [
            "company_id",
            "year",
            "net_profit",
            "equity_capital",
            "reserves",
            "return_on_equity_pct",
        ],
    ].tail()
)

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


# Return on Capital Employed (ROCE)
financial["return_on_capital_employed_pct"] = (
    financial["roce_percentage"]
)

# CFO / PAT Ratio
financial["cfo_pat_ratio"] = financial.apply(
    lambda row:
    None
    if row["net_profit"] == 0
    else row["cash_from_operations_cr"] / row["net_profit"],
    axis=1
)

# Free Cash Flow Positive Flag
financial["fcf_positive_flag"] = (
    financial["free_cash_flow_cr"] > 0
).astype(int)

# Temporary FCF Growth Score
financial["fcf_growth_score"] = (
    financial["free_cash_flow_cr"]
)

# Revenue CAGR
financial["revenue_cagr_5yr"] = financial["revenue_cagr_5yr"]

# PAT CAGR
financial["pat_cagr_5yr"] = financial["pat_cagr_5yr"]

# EPS CAGR
financial["eps_cagr_5yr"] = financial["eps_cagr_5yr"]




# NORMALIZE KPI VALUES (0-100)

def normalize(series):
    s = series.copy()

    # Ignore missing values
    valid = s.dropna()

    if len(valid) == 0:
        return pd.Series(0, index=s.index)

    p10 = valid.quantile(0.10)
    p90 = valid.quantile(0.90)

    # Winsorize
    s = s.clip(lower=p10, upper=p90)

    minimum = s.min()
    maximum = s.max()

    if maximum == minimum:
        return pd.Series(50, index=s.index)

    return ((s - minimum) / (maximum - minimum)) * 100

def normalize_by_sector(df, value_column):
    return (
        df.groupby("broad_sector")[value_column]
          .transform(lambda s: normalize(s))
    )

print(financial.columns.tolist())

print(financial[["company_id"]].head())

financial["roe_score"] = normalize_by_sector(
    financial,
    "return_on_equity_pct"
).fillna(50)

financial["roce_score"] = normalize_by_sector(
    financial,
    "return_on_capital_employed_pct"
).fillna(50)

financial["npm_score"] = normalize_by_sector(
    financial,
    "net_profit_margin_pct"
).fillna(50)

financial["fcf_score"] = normalize_by_sector(
    financial,
    "fcf_growth_score"
).fillna(50)

financial["cfo_pat_score"] = normalize_by_sector(
    financial,
    "cfo_pat_ratio"
).fillna(50)

financial["revenue_growth_score"] = normalize_by_sector(
    financial,
    "revenue_cagr_5yr"
).fillna(50)

financial["pat_growth_score"] = normalize_by_sector(
    financial,
    "pat_cagr_5yr"
).fillna(50)

financial["de_score"] = (
    100 - normalize_by_sector(
        financial,
        "debt_to_equity"
    )
).fillna(50)

financial["interest_score"] = normalize_by_sector(
    financial,
    "interest_coverage"
).fillna(50)

financial["profitability_score"] = (
      financial["roe_score"] * (15/35)
    + financial["roce_score"] * (10/35)
    + financial["npm_score"] * (10/35)
)

financial["cash_quality_score"] = (
      financial["fcf_score"] * 0.50
    + financial["cfo_pat_score"] * 0.33
    + financial["fcf_positive_flag"] * 100 * 0.17
)

financial["growth_score"] = (
      financial["revenue_growth_score"] * 0.50
    + financial["pat_growth_score"] * 0.50
)

financial["leverage_score"] = (
      financial["de_score"] * (10/15)
    + financial["interest_score"] * (5/15)
)

financial["profitability_score"] = (
    financial["profitability_score"]
    .fillna(50)
)

financial["cash_quality_score"] = (
    financial["cash_quality_score"]
    .fillna(50)
)

financial["growth_score"] = (
    financial["growth_score"]
    .fillna(50)
)

financial["leverage_score"] = (
    financial["leverage_score"]
    .fillna(50)
)

financial["composite_quality_score"] = (
      financial["profitability_score"] * 0.35
    + financial["cash_quality_score"] * 0.30
    + financial["growth_score"] * 0.20
    + financial["leverage_score"] * 0.15
)

financial["composite_quality_score"] = (
    financial["composite_quality_score"]
    .fillna(50)
    .round(2)
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

        "return_on_capital_employed_pct",
        "cfo_pat_ratio",
        "fcf_positive_flag",

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