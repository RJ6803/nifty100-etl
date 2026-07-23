
import re
import sqlite3
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ANALYSIS_FILE = Path("data/raw/analysis.xlsx")
DATABASE = Path("data/nifty100.db")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


FIELDS = {
    "compounded_sales_growth": "revenue_cagr_5yr",
    "compounded_profit_growth": "pat_cagr_5yr",
    "stock_price_cagr": None,
    "roe": "return_on_equity_pct",
}

# Accepts:
# 10 Years: 21%
# 10 Year : 21%
# 10Y 21%
# 5 Years = 18.5%
# 3 Year-12%
PATTERN = re.compile(
    r"(\d+)\s*(?:Year|Years|Y)\s*[:=\-]?\s*(-?[\d.]+)\s*%",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# Parse Excel
# ---------------------------------------------------------

def parse_analysis():

    df = pd.read_excel(ANALYSIS_FILE, header=1)

    required_columns = [
        "company_id",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in analysis.xlsx: {missing}"
        )

    parsed_rows = []
    failed_rows = []

    for _, row in df.iterrows():

        company = row["company_id"]

        for field in FIELDS:

            value = row[field]

            if pd.isna(value):
                continue

            text = str(value).strip()

            match = PATTERN.search(text)

            if match:

                parsed_rows.append(
                    {
                        "company_id": company,
                        "metric_type": field,
                        "period_years": int(match.group(1)),
                        "value_pct": float(match.group(2)),
                    }
                )

            else:

                failed_rows.append(
                    {
                        "company_id": company,
                        "metric_type": field,
                        "source_text": text,
                    }
                )

    parsed = pd.DataFrame(parsed_rows)

    failures = pd.DataFrame(failed_rows)

    parsed.to_csv(
        OUTPUT_DIR / "analysis_parsed.csv",
        index=False
    )

    failures.to_csv(
        OUTPUT_DIR / "parse_failures.csv",
        index=False
    )

    return parsed, failures


# ---------------------------------------------------------
# Cross Validation
# ---------------------------------------------------------

def cross_validate(parsed):

    conn = sqlite3.connect(DATABASE)

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn,
    )

    conn.close()

    # Latest record only
    ratios["year_num"] = pd.to_datetime(
        ratios["year"],
        format="%b %Y",
        errors="coerce"
    ).dt.year

    ratios.loc[
        ratios["year"]=="TTM",
        "year_num"
    ]=9999

    latest = (
        ratios
        .sort_values("year_num")
        .groupby("company_id")
        .tail(1)
        .drop(columns="year_num")
        .set_index("company_id")
    )

    validation = []

    for _, row in parsed.iterrows():

        company = row["company_id"]

        metric = row["metric_type"]

        parsed_value = row["value_pct"]

        db_column = FIELDS[metric]

        if db_column is None:

            validation.append(
                {
                    **row,
                    "computed_value": None,
                    "difference_pct": None,
                    "manual_review": False,
                    "remarks": "No database comparison available"
                }
            )

            continue

        if company not in latest.index:

            validation.append({
                **row,
                "computed_value": None,
                "difference_pct": None,
                "manual_review": True,
                "remarks": "Company not found in financial_ratios"
            })

            continue

        db_value = latest.at[company, db_column]

        if pd.isna(db_value):

            validation.append({
                **row,
                "computed_value": None,
                "difference_pct": None,
                "manual_review": True,
                "remarks": "Missing financial ratio"
            })

            continue

        diff = abs(parsed_value - db_value)

        validation.append({

            **row,

            "computed_value": round(db_value,2),

            "difference_pct": round(diff,2),

            "manual_review": diff > 5,

            "remarks":
                "Difference > 5%"
                if diff > 5
                else "OK"

        })

    validation = pd.DataFrame(validation)

    validation.to_csv(
        OUTPUT_DIR / "analysis_cagr_cross_validation.csv",
        index=False,
    )

    return validation


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def run():

    print("Parsing analysis.xlsx...")

    parsed, failures = parse_analysis()

    validation = cross_validate(parsed)

    print("=" * 50)
    print("Analysis Parser Summary")
    print("=" * 50)

    print(f"Parsed rows          : {len(parsed)}")

    print(f"Parse failures       : {len(failures)}")

    print(f"Validated rows       : {len(validation)}")

    print(f"Manual review needed : {validation['manual_review'].sum()}")

    print("=" * 50)

    print("Done.")


if __name__ == "__main__":
    run()