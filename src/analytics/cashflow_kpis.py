from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

# ==========================================================
# Paths
# ==========================================================

DB_PATH = "data/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

INTELLIGENCE_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"
DISTRESS_FILE = OUTPUT_DIR / "distress_alerts.csv"

CAPITAL_FILE = OUTPUT_DIR / "capital_allocation.csv"


# ==========================================================
# Database Loader
# ==========================================================

class DatabaseLoader:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

    def load_companies(self):

        return pd.read_sql(
            """
            SELECT
                id AS company_id,
                company_name,
                roce_percentage,
                roe_percentage
            FROM companies
            """,
            self.conn
        )

    def load_cashflow(self):

        return pd.read_sql(
            "SELECT * FROM cashflow",
            self.conn
        )

    def load_profit_loss(self):

        return pd.read_sql(
            "SELECT * FROM profit_loss",
            self.conn
        )

    def load_balance_sheet(self):

        return pd.read_sql(
            "SELECT * FROM balance_sheet",
            self.conn
        )

    def load_financial_ratios(self):

        return pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

    def close(self):

        self.conn.close()


# ==========================================================
# Capital Allocation Loader
# ==========================================================

def load_capital_patterns():

    if not CAPITAL_FILE.exists():

        raise FileNotFoundError(
            "capital_allocation.csv not found.\n"
            "Run Sprint 2 Capital Allocation module first."
        )

    df = pd.read_csv(CAPITAL_FILE)

    return df


# ==========================================================
# Merge All Required Data
# ==========================================================

def build_master_dataframe():

    loader = DatabaseLoader()

    companies = loader.load_companies()

    cashflow = loader.load_cashflow()

    profit_loss = loader.load_profit_loss()

    balance = loader.load_balance_sheet()

    ratios = loader.load_financial_ratios()

    capital = load_capital_patterns()

    loader.close()

    # ----------------------------------

    df = cashflow.merge(

        profit_loss,

        on=["company_id", "year"],

        how="left",

        suffixes=("", "_pl")

    )

    # ----------------------------------

    df = df.merge(

        balance,

        on=["company_id", "year"],

        how="left",

        suffixes=("", "_bs")

    )

    # ----------------------------------

    df = df.merge(

        ratios,

        on=["company_id", "year"],

        how="left",

        suffixes=("", "_ratio")

    )

    # ----------------------------------

    df = df.merge(

        companies,

        on="company_id",

        how="left"

    )

    # ----------------------------------

    capital_latest = (

        capital.sort_values("year")

        .groupby("company_id")

        .tail(1)

    )

    df = df.merge(

        capital_latest[
            [
                "company_id",
                "pattern_label"
            ]
        ],

        on="company_id",

        how="left"

    )

    # Filter to exact 92 companies in companies table
    df = df[df["company_id"].isin(companies["company_id"])].copy()

    return df


# ==========================================================
# Helper Functions
# ==========================================================

def latest_year(df):

    years = (

        df["year"]

        .astype(str)

        .str.extract(r"(\d{4})")[0]

        .astype(float)

    )

    df = df.copy()

    df["year_num"] = years

    latest = (

        df.groupby("company_id")["year_num"]

        .transform("max")

    )

    return df[df["year_num"] == latest].copy()


def safe_divide(a, b):

    return np.where(

        (b == 0) | (pd.isna(b)),

        np.nan,

        a / b

    )

def quality_label(score):
    """
    Classify CFO/PAT quality score.
    """
    if score > 1.0:
        return "High Quality"
    elif score >= 0.5:
        return "Moderate"
    else:
        return "Accrual Risk"

def capex_label(capex_pct):
    """
    Classify CapEx intensity.
    """
    if capex_pct < 3:
        return "Asset Light"
    elif capex_pct <= 8:
        return "Moderate"
    else:
        return "Capital Intensive"
    
def classify_pattern(row):
    cfo = row.get("cfo_sign")
    cfi = row.get("cfi_sign")
    cff = row.get("cff_sign")

    quality = row.get("cfo_quality_score", 0)

    if cfo == "+" and cfi == "-" and cff == "-":
        if quality >= 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    if cfo == "+" and cfi == "+" and cff == "-":
        return "Liquidating Assets"

    if cfo == "-" and cfi == "+" and cff == "+":
        return "Distress Signal"

    if cfo == "-" and cfi == "-" and cff == "+":
        return "Growth Funded by Debt"

    if cfo == "+" and cfi == "+" and cff == "+":
        return "Cash Accumulator"

    if cfo == "-" and cfi == "-" and cff == "-":
        return "Pre-Revenue"

    return "Mixed"
# ==========================================================
# CFO Quality Score
# ==========================================================

def calculate_cfo_quality(df):

    df["cfo_quality_score"] = (

        df.groupby("company_id")["cfo_pat_ratio"]

        .transform("mean")

    )

    def label(score):

        if pd.isna(score):

            return "Unknown"

        elif score > 1.0:

            return "High Quality"

        elif score >= 0.5:

            return "Moderate"

        else:

            return "Accrual Risk"

    df["cfo_quality_label"] = (

        df["cfo_quality_score"]

        .apply(label)

    )

    return df


# ==========================================================
# CapEx Intensity
# ==========================================================

def calculate_capex_intensity(df):

    df["capex_intensity_pct"] = (

        safe_divide(

            abs(df["capex_cr"]),

            df["sales"]

        ) * 100

    )

    def label(value):

        if pd.isna(value):

            return "Unknown"

        elif value < 3:

            return "Asset Light"

        elif value <= 8:

            return "Moderate"

        else:

            return "Capital Intensive"

    df["capex_label"] = (

        df["capex_intensity_pct"]

        .apply(label)

    )

    return df


# ==========================================================
# FCF Conversion
# ==========================================================

def calculate_fcf_conversion(df):

    df["fcf_conversion_pct"] = (

        safe_divide(

            df["cash_from_operations_cr"],

            df["net_profit"]

        ) * 100

    )

    return df


# ==========================================================
# Distress Signal
# ==========================================================

def calculate_distress(df):

    df["distress_flag"] = np.where(

        (

            df["operating_activity"] < 0

        )

        &

        (

            df["financing_activity"] > 0

        ),

        "YES",

        "NO"

    )

    return df


# ==========================================================
# Deleveraging
# ==========================================================

def calculate_deleveraging(df):

    df = df.sort_values(

        ["company_id", "year_num"]

    )

    previous = (

        df.groupby("company_id")["borrowings"]

        .shift(1)

    )

    df["deleveraging_flag"] = np.where(

        (

            df["financing_activity"] < 0

        )

        &

        (

            df["borrowings"] < previous

        ),

        "YES",

        "NO"

    )

    return df

# ==========================================================
# 5-Year Free Cash Flow CAGR
# ==========================================================

def calculate_fcf_cagr(df):

    ratios = df.copy()

    # Create numeric year for sorting
    ratios["year_num"] = (
        ratios["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
    )

    ratios["year_num"] = pd.to_numeric(
        ratios["year_num"],
        errors="coerce"
    )

    ratios = ratios.sort_values(
        ["company_id", "year_num"]
    )

    print("\n========== FCF DEBUG ==========")
    print("Columns:")
    print(ratios.columns.tolist())

    print("\nFree Cash Flow Statistics:")
    print(ratios["free_cash_flow_cr"].describe())

    print("\nMissing FCF values:")
    print(ratios["free_cash_flow_cr"].isna().sum())

    print("\nTotal rows:")
    print(len(ratios))

    print("===============================\n")

    cagr_map = {}
    debug_companies = ["ABB", "RELIANCE", "TCS"]
    for company, grp in ratios.groupby("company_id"):

        debug = company in debug_companies

        if debug:
            print(f"\n{company}")
            print(f"Rows before dropna : {len(grp)}")

        grp = grp.dropna(subset=["free_cash_flow_cr"])
        
        if len(grp) < 5:
            cagr_map[company] = np.nan

            if debug:
                print(f"{company}: only {len(grp)} years")

            continue
        last5 = grp.tail(5)
        start = last5.iloc[0]["free_cash_flow_cr"]
        end = last5.iloc[-1]["free_cash_flow_cr"]
        if debug:
            print(last5[["year","free_cash_flow_cr"]])
            print("Start =", start)
            print("End =", end)

        if start <= 0 or end <= 0:
            print(f"{company}: skipped because start={start}, end={end}")
            cagr_map[company] = np.nan
            continue

        years = len(last5) - 1

        cagr = (
            (end / start) ** (1 / years)
            - 1
        ) * 100

        cagr_map[company] = round(cagr, 2)

    df["fcf_cagr_5yr"] = df["company_id"].map(cagr_map)

    

    return df

# ==========================================================
# Export Outputs
# ==========================================================

def export_outputs(df):

    sectors = pd.read_excel("data/raw/sectors.xlsx", usecols=["company_id", "broad_sector"])
    print("Current working directory:", Path.cwd())
    print("Reading file:", Path("data/raw/sectors.xlsx").resolve())
    print("Sector file shape:", sectors.shape)
    print("Before merge")
    print("df rows:", len(df))
    print("df companies:", df["company_id"].nunique())

    print("sector rows:", len(sectors))
    print("sector companies:", sectors["company_id"].nunique())

    print("Duplicate company_ids in sectors:")
    print(
        sectors["company_id"]
        .value_counts()
        .loc[lambda s: s > 1]
    )

    print("Duplicate company_ids in df:")
    print(
        df["company_id"]
        .value_counts()
        .loc[lambda s: s > 1]
    )
    merged = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    df = merged
    print("Rows:", len(sectors))
    print("Unique companies:", sectors["company_id"].nunique())
    output = df[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "pattern_label"
        ]
    ].copy()

    print("Output:", output.shape)
    print(output["company_id"].nunique())

    output.rename(
        columns={
            "broad_sector": "sector",
            "pattern_label":
            "capital_allocation_label"
        },
        inplace=True
    )

    output.to_excel(
        INTELLIGENCE_FILE,
        index=False
    )

    print(output.shape)
    print(output["company_id"].nunique())
    saved = pd.read_excel(INTELLIGENCE_FILE)

    print(saved.shape)
    print(saved["company_id"].nunique())

    distress = df[
        df["distress_flag"] == "YES"
    ][
        [
            "company_id",
            "company_name",
            "operating_activity",
            "financing_activity",
            "net_profit"
        ]
    ]

    distress.to_csv(
        DISTRESS_FILE,
        index=False
    )

    print()
    print("Files Generated")
    print("-------------------------")
    print(INTELLIGENCE_FILE)
    print(DISTRESS_FILE)

def export_pattern_changes():
    capital = load_capital_patterns().copy()
    capital["year_num"] = pd.to_numeric(capital["year"].astype(str).str.extract(r"(\d{2,4})")[0], errors="coerce")
    capital = capital.sort_values(["company_id", "year_num"])
    capital["previous_pattern"] = capital.groupby("company_id")["pattern_label"].shift()
    changes = capital.loc[capital.previous_pattern.notna() & capital.pattern_label.ne(capital.previous_pattern), ["company_id", "year", "previous_pattern", "pattern_label"]]
    changes.rename(columns={"year": "year_changed", "pattern_label": "new_pattern"}).to_csv(OUTPUT_DIR / "pattern_changes.csv", index=False)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    df = build_master_dataframe()

    print("\nMASTER DATAFRAME")
    print(df.shape)

    print(df.groupby("company_id").size().head(20))

    df = calculate_cfo_quality(df)

    df = calculate_fcf_cagr(df)

    df = latest_year(df)

    df = calculate_capex_intensity(df)

    df = calculate_fcf_conversion(df)

    df = calculate_distress(df)

    df = calculate_deleveraging(df)

    export_outputs(df)
    missing = [
        "ULTRACEMCO",
        "UNIONBANK",
        "UNITDSPR",
        "VBL",
        "VEDL",
        "WIPRO",
        "ZOMATO",
        "ZYDUSLIFE",
    ]

    print(df[df.company_id.isin(missing)][["company_id","year"]])
    print("Rows before export:", len(df))
    print("Companies before export:", df.company_id.nunique())

    missing = sorted(
        set(DatabaseLoader().load_companies()["company_id"])
        - set(df.company_id)
    )

    print("Missing before export:")
    print(missing)
    export_pattern_changes()

    print(df[[
        "company_id",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity_pct",
        "capex_label",
        "fcf_conversion_pct",
        "distress_flag",
        "deleveraging_flag"
    ]].head())

    print()

    print("Companies :", df.company_id.nunique())

    print("Rows      :", len(df))
