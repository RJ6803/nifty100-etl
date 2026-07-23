import sqlite3
import pandas as pd

# ==========================================
# DATABASE
# ==========================================

DATABASE = "data/nifty100.db"

conn = sqlite3.connect(DATABASE)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

financial = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow_intelligence",
    conn
)

conn.close()

# ==========================================
# KEEP LATEST YEAR ONLY
# ==========================================

financial["year_num"] = pd.to_datetime(
    financial["year"],
    format="%b %Y",
    errors="coerce"
).dt.year

financial.loc[
    financial["year"] == "TTM",
    "year_num"
] = 9999

financial = (
    financial
    .sort_values("year_num")
    .groupby("company_id")
    .tail(1)
    .drop(columns="year_num")
)


cashflow["year_num"] = pd.to_datetime(
    cashflow["year"],
    format="%b %Y",
    errors="coerce"
).dt.year

cashflow.loc[
    cashflow["year"] == "TTM",
    "year_num"
] = 9999

cashflow = (
    cashflow
    .sort_values("year_num")
    .groupby("company_id")
    .tail(1)
    .drop(columns="year_num")
)
# ==========================================
# MERGE
# ==========================================

df = companies.merge(
    financial,
    left_on="id",
    right_on="company_id",
    how="left"
)

df = df.merge(
    cashflow,
    on=["company_id", "year"],
    how="left"
)

# ==========================================
# BUILD SEARCH TEXT
# ==========================================
def value(v):
    return "" if pd.isna(v) else str(v)

def build_text(row):

    parts = [
        value(row["company_name"]),
        f"ROE {value(row['return_on_equity_pct'])}",
        f"ROCE {value(row['return_on_capital_employed_pct'])}",
        f"Profit Margin {value(row['net_profit_margin_pct'])}",
        f"Debt Equity {value(row['debt_to_equity'])}",
        f"Composite Score {value(row['composite_quality_score'])}",
        value(row.get("cash_quality_label")),
        value(row.get("cashflow_trend")),
        value(row.get("cashflow_insight"))
    ]

    return " ".join(
        x for x in parts if x
    )

df["company_name"] = (
    df["company_name"]
    .astype(str)
    .str.replace("\n", " ", regex=False)
    .str.strip()
)

df["search_text"] = df.apply(
    build_text,
    axis=1
)

df["search_text"] = (
    df["search_text"]
    .str.lower()
)

# ==========================================
# FINAL TABLE
# ==========================================

nlp_index = df[
    [
        "company_id",
        "company_name",
        "year",
        "search_text"
    ]
]

# ==========================================
# SAVE
# ==========================================

conn = sqlite3.connect(DATABASE)

nlp_index.to_sql(
    "nlp_search_index",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print(
    f"NLP Search Index generated: {len(nlp_index)} companies"
)

print("nlp_search_index table written successfully!")