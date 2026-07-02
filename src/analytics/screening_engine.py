import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)


# Screening Score

df["screening_score"] = (
      df["composite_quality_score"] * 0.50
    + df["return_on_equity_pct"] * 0.20
    + df["net_profit_margin_pct"] * 0.10
    + df["operating_profit_margin_pct"] * 0.10
    + df["revenue_cagr_5yr"] * 0.10
)


# Recommendation

def recommendation(score):

    if score >= 25:
        return "Strong Buy"

    elif score >= 18:
        return "Buy"

    elif score >= 12:
        return "Hold"

    else:
        return "Avoid"


df["recommendation"] = df["screening_score"].apply(recommendation)


# Save required columns

result = df[
    [
        "company_id",
        "year",
        "composite_quality_score",
        "screening_score",
        "recommendation"
    ]
]

result.to_sql(
    "company_screening",
    conn,
    if_exists="replace",
    index=False
)

result.to_csv(
    "output/company_screening.csv",
    index=False
)

conn.close()

print(result.head())

print()

print("Rows :", len(result))

print("company_screening table written successfully!")

print("company_screening.csv exported.")