import sqlite3
import pandas as pd
import numpy as np
import os



# Load Database

conn = sqlite3.connect("data/nifty100.db")

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

conn.close()



# Merge Tables

df = cashflow.merge(
    profit_loss,
    on=["company_id", "year"],
    how="left"
)

df = df.drop(
    columns=["id_x", "id_y"],
    errors="ignore"
)


# 1. Free Cash Flow

df["free_cash_flow"] = (
    df["operating_activity"]
    +
    df["investing_activity"]
)



# 2. CFO Quality Score

df["cfo_pat_ratio"] = np.where(
    df["net_profit"] != 0,
    df["operating_activity"] /
    df["net_profit"],
    np.nan
)


# 3. CFO Quality Score

def quality_label(ratio):

    if pd.isna(ratio):
        return None

    if ratio > 1.0:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


df["cfo_quality_score"] = (
    df.groupby("company_id")["cfo_pat_ratio"]
      .transform(lambda x: x.rolling(5, min_periods=1).mean())
)

df["cfo_quality_label"] = (
    df["cfo_quality_score"]
    .apply(quality_label)
)


# 4. CapEx Intensity

df["capex_intensity"] = np.where(
    df["sales"] != 0,
    abs(df["investing_activity"]) /
    df["sales"] * 100,
    np.nan
)


def capex_label(value):

    if pd.isna(value):
        return None

    if value < 3:
        return "Asset Light"

    if value <= 8:
        return "Moderate"

    return "Capital Intensive"


df["capex_label"] = (
    df["capex_intensity"]
    .apply(capex_label)
)


# 5. FCF Conversion Rate

df["fcf_conversion_rate"] = np.where(
    df["operating_profit"] != 0,
    df["free_cash_flow"] /
    df["operating_profit"] * 100,
    np.nan
)



# 6. Capital Allocation Pattern

def get_sign(value):

    if pd.isna(value):
        return "0"

    if value > 0:
        return "+"

    if value < 0:
        return "-"

    return "0"


df["cfo_sign"] = df["operating_activity"].apply(get_sign)
df["cfi_sign"] = df["investing_activity"].apply(get_sign)
df["cff_sign"] = df["financing_activity"].apply(get_sign)


def classify_pattern(row):

    cfo = row["cfo_sign"]
    cfi = row["cfi_sign"]
    cff = row["cff_sign"]

    # (+,-,-)
    if cfo == "+" and cfi == "-" and cff == "-":

        if (
            pd.notna(row["cfo_quality_score"])
            and row["cfo_quality_score"] > 1.0
        ):
            return "Shareholder Returns"

        return "Reinvestor"

    # (+,+,-)
    if cfo == "+" and cfi == "+" and cff == "-":
        return "Liquidating Assets"

    # (-,+,+)
    if cfo == "-" and cfi == "+" and cff == "+":
        return "Distress Signal"

    # (-,-,+)
    if cfo == "-" and cfi == "-" and cff == "+":
        return "Growth Funded by Debt"

    # (+,+,+)
    if cfo == "+" and cfi == "+" and cff == "+":
        return "Cash Accumulator"

    # (-,-,-)
    if cfo == "-" and cfi == "-" and cff == "-":
        return "Pre-Revenue"

    # (+,-,+)
    if cfo == "+" and cfi == "-" and cff == "+":
        return "Mixed"

    return "Other"


df["pattern_label"] = df.apply(
    classify_pattern,
    axis=1
)



# Export Capital Allocation Report




os.makedirs("output", exist_ok=True)

capital_df = df[
    [
        "company_id",
        "year",
        "cfo_sign",
        "cfi_sign",
        "cff_sign",
        "pattern_label"
    ]
]

capital_df.to_csv(
    "output/capital_allocation.csv",
    index=False
)



# Save KPI Table

conn = sqlite3.connect("data/nifty100.db")

df.to_sql(
    "cashflow_kpis",
    conn,
    if_exists="replace",
    index=False
)



conn.close()

print(df.head())

print("\ncapital_allocation.csv created successfully!")
print("cashflow_kpis table written to SQLite.")