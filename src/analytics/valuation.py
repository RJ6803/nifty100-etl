from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


DB_PATH = "data/nifty100.db"
MARKET_PATH = "data/raw/market_cap.xlsx"
OUTPUT_DIR = "output"


def load_latest_market_data():
    """Load latest market cap row for every company."""

    market = pd.read_excel(MARKET_PATH)

    market.columns = market.columns.str.strip()

    market["year"] = pd.to_numeric(
        market["year"],
        errors="coerce"
    )

    latest = (
        market.groupby("company_id")["year"]
        .transform("max")
    )

    market = market.loc[
        market["year"] == latest
    ].copy()

    return market


def load_company_master():

    with sqlite3.connect(DB_PATH) as conn:

        companies = pd.read_sql(
            """
            SELECT
                id AS company_id,
                company_name
            FROM companies
            """,
            conn,
        )

    return companies


def load_latest_ratios():

    with sqlite3.connect(DB_PATH) as conn:

        ratios = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            """,
            conn,
        )

    ratios.columns = ratios.columns.str.strip()

    ratios["year_num"] = pd.to_numeric(
        ratios["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    latest = (
        ratios.groupby("company_id")["year_num"]
        .transform("max")
    )

    ratios = ratios.loc[
        ratios["year_num"] == latest
    ].copy()

    return ratios


def load_sector_master():

    sectors = pd.read_excel(
        "data/raw/sectors.xlsx"
    )

    sectors.columns = (
        sectors.columns
        .astype(str)
        .str.strip()
    )

    sectors = sectors[
        [
            "company_id",
            "broad_sector"
        ]
    ].drop_duplicates()

    return sectors


def build_valuation_summary():

    companies = load_company_master()

    sectors = load_sector_master()

    market = load_latest_market_data()

    ratios = load_latest_ratios()

    df = (
        companies
        .merge(sectors, on="company_id", how="left")
        .merge(market, on="company_id", how="left")
        .merge(ratios, on="company_id", how="left")
    )

    required_columns = [
        "market_cap_crore",
        "free_cash_flow_cr",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ]

    for col in required_columns:

        if col not in df.columns:

            df[col] = np.nan

    ####################################################
    # FCF Yield
    ####################################################

    df["FCF_yield_pct"] = (
        df["free_cash_flow_cr"]
        .div(
            df["market_cap_crore"].replace(
                0,
                np.nan
            )
        )
        * 100
    )

    ####################################################
    # Sector Median PE
    ####################################################

    sector_median = (
        df.groupby("broad_sector")["pe_ratio"]
        .transform("median")
    )

    df["5yr_median_PE"] = sector_median

    ####################################################
    # Premium / Discount
    ####################################################

    df["PE_vs_sector_median_pct"] = (
        (
            df["pe_ratio"] /
            sector_median
        )
        - 1
    ) * 100

    ####################################################
    # Flags
    ####################################################

    df["flag"] = "N/A"

    valid = (
        df["pe_ratio"].notna()
        &
        sector_median.notna()
    )

    df.loc[valid, "flag"] = "Fair"

    df.loc[
        valid
        &
        (
            df["pe_ratio"]
            >
            sector_median * 1.5
        ),
        "flag",
    ] = "Caution"

    df.loc[
        valid
        &
        (
            df["pe_ratio"]
            <
            sector_median * 0.7
        ),
        "flag",
    ] = "Discount"

    ####################################################
    # Round values
    ####################################################

    round_cols = [
        "P/E",
        "P/B",
        "EV/EBITDA",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
    ]

    rename = {
        "broad_sector": "sector",
        "pe_ratio": "P/E",
        "pb_ratio": "P/B",
        "ev_ebitda": "EV/EBITDA",
    }

    df = df.rename(columns=rename)

    for c in round_cols:

        if c in df.columns:

            df[c] = df[c].round(2)

    final_columns = [
        "company_id",
        "company_name",
        "sector",
        "P/E",
        "P/B",
        "EV/EBITDA",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag",
    ]

    summary = df[final_columns].sort_values(
        "company_name"
    )

    summary["company_name"] = (
        summary["company_name"]
        .astype(str)
        .str.replace("\n", "", regex=False)
        .str.strip()
    )

    return summary


def export_valuation():

    output = Path(OUTPUT_DIR)

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = build_valuation_summary()

    summary.to_excel(
        output / "valuation_summary.xlsx",
        index=False,
    )

    summary.loc[
        summary["flag"].isin(
            ["Discount", "Caution"]
        )
    ].to_csv(
        output / "valuation_flags.csv",
        index=False,
    )

    print(
        f"Generated valuation_summary.xlsx ({len(summary)} companies)"
    )

    print(
        f"Generated valuation_flags.csv ({len(summary.loc[summary['flag'].isin(['Discount','Caution'])])} flagged companies)"
    )


if __name__ == "__main__":
    export_valuation()