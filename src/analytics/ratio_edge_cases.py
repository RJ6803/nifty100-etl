import sqlite3
import pandas as pd
import os

DB_PATH = "data/nifty100.db"
OUTPUT_LOG = "output/ratio_edge_cases.log"

os.makedirs("output", exist_ok=True)

conn = sqlite3.connect(DB_PATH)


# Load tables

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        roce_percentage,
        roe_percentage
    FROM companies
    """,
    conn,
)

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

profit_loss = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        operating_profit,
        other_income
    FROM profit_loss
    """,
    conn,
)

balance_sheet = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        equity_capital,
        reserves,
        borrowings
    FROM balance_sheet
    """,
    conn,
)

conn.close()


# Load sectors

sectors = pd.read_excel("data/raw/sectors.xlsx")

sectors = sectors[
    [
        "company_id",
        "broad_sector"
    ]
]


# Compute ROCE

roce_df = profit_loss.merge(
    balance_sheet,
    on=["company_id", "year"],
    how="inner"
)

roce_df["ebit"] = (
    roce_df["operating_profit"].fillna(0)
    +
    roce_df["other_income"].fillna(0)
)

roce_df["capital_employed"] = (
    roce_df["equity_capital"].fillna(0)
    +
    roce_df["reserves"].fillna(0)
    +
    roce_df["borrowings"].fillna(0)
)

roce_df["computed_roce"] = (
    roce_df["ebit"]
    /
    roce_df["capital_employed"]
) * 100

roce_df.loc[
    roce_df["capital_employed"] <= 0,
    "computed_roce"
] = None


# Merge everything

df = financial_ratios.merge(
    companies,
    on="company_id",
    how="left"
)

df = df.merge(
    sectors,
    on="company_id",
    how="left"
)

df = df.merge(
    roce_df[
        [
            "company_id",
            "year",
            "computed_roce"
        ]
    ],
    on=["company_id", "year"],
    how="left"
)


# Financial sector carve-out

df["high_leverage_suppressed"] = (
    df["broad_sector"]
    .fillna("")
    .str.upper()
    .eq("FINANCIALS")
)


# Logging

with open(OUTPUT_LOG, "w", encoding="utf-8") as log:

    log.write("=" * 70 + "\n")
    log.write("DAY 13 RATIO EDGE CASE REPORT\n")
    log.write("=" * 70 + "\n\n")

    anomaly_count = 0

    for _, row in df.iterrows():

        company = row["company_id"]
        year = row["year"]


        # ROCE comparison

        if (
            pd.notna(row["computed_roce"])
            and
            pd.notna(row["roce_percentage"])
        ):

            diff = abs(
                row["computed_roce"]
                -
                row["roce_percentage"]
            )

            if diff > 5:

                if row["roce_percentage"] < 1:
                    category = "DATA_SOURCE_ISSUE"

                elif diff <= 15:
                    category = "VERSION_DIFFERENCE"

                else:
                    category = "FORMULA_DIFFERENCE"

                log.write(f"{company} ({year})\n")
                log.write("Metric : ROCE\n")
                log.write(
                    f"Computed : {row['computed_roce']:.2f}\n"
                )
                log.write(
                    f"Source   : {row['roce_percentage']:.2f}\n"
                )
                log.write(
                    f"Difference : {diff:.2f}\n"
                )
                log.write(
                    f"Category : {category}\n\n"
                )

                anomaly_count += 1


        # ROE comparison

        if (
            pd.notna(row["return_on_equity_pct"])
            and
            pd.notna(row["roe_percentage"])
        ):

            diff = abs(
                row["return_on_equity_pct"]
                -
                row["roe_percentage"]
            )

            if diff > 5:

                if row["roe_percentage"] < 1:
                    category = "DATA_SOURCE_ISSUE"

                elif diff <= 15:
                    category = "VERSION_DIFFERENCE"

                else:
                    category = "FORMULA_DIFFERENCE"

                log.write(f"{company} ({year})\n")
                log.write("Metric : ROE\n")
                log.write(
                    f"Computed : {row['return_on_equity_pct']:.2f}\n"
                )
                log.write(
                    f"Source   : {row['roe_percentage']:.2f}\n"
                )
                log.write(
                    f"Difference : {diff:.2f}\n"
                )
                log.write(
                    f"Category : {category}\n\n"
                )

                anomaly_count += 1

    log.write("=" * 70 + "\n")
    log.write(f"TOTAL ANOMALIES : {anomaly_count}\n")
    log.write("=" * 70 + "\n")

print("ratio_edge_cases.log created successfully.")
print(f"Total anomalies found : {anomaly_count}")

financial_companies = df[
    df["high_leverage_suppressed"]
]

print()
print(
    "Financial companies with leverage suppression :",
    len(financial_companies["company_id"].unique())
)

print()
print(
    financial_companies[
        [
            "company_id",
            "broad_sector",
            "debt_to_equity",
            "high_leverage_suppressed"
        ]
    ].head()
)


print(df.head())

df.to_csv(
    "output/ratio_edge_cases.csv",
    index=False
)

print("\n" + "=" * 60)
print("EDGE CASE SUMMARY")
print("=" * 60)

print(f"Total companies analysed : {df['company_id'].nunique()}")

financial_count = (
    df.loc[
        df["high_leverage_suppressed"] == True,
        "company_id"
    ].nunique()
)

print(f"Financial companies detected : {financial_count}")

print(f"Total records analysed : {len(df)}")

print("=" * 60)
print("Outputs generated:")
print("  output/ratio_edge_cases.csv")
print("  output/ratio_edge_cases.log")
print("=" * 60)