import sqlite3
import pandas as pd
from src.screener.engine import ScreenerEngine


DB_PATH = "data/nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_company(company_id):
    """
    Load company metadata from ScreenerEngine (enriched ratios+sectors).
    Falls back to the canonical companies table so company_name is always populated.
    """
    engine = ScreenerEngine()
    df = engine.df.copy()
    result = df[df["company_id"] == company_id]

    if result.empty:
        # Fallback: load directly from companies table
        conn = get_connection()
        base = pd.read_sql(
            "SELECT id AS company_id, company_name FROM companies WHERE id=?",
            conn,
            params=[company_id],
        )
        conn.close()
        return base

    return result



def load_ratios(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

    conn.close()

    # convert years
    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype(float)
    )

    df = df.sort_values("year_num")

    return df


def load_profit_loss(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM profit_loss
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

    conn.close()

    return df


def load_balance_sheet(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM balance_sheet
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

    conn.close()

    return df


def load_cashflow(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def load_pros_cons(company_id):

    df = pd.read_csv(
        "output/pros_cons_generated.csv"
    )

    return df[df.company_id == company_id]


def load_cashflow_intelligence(company_id):
    df = pd.read_excel("output/cashflow_intelligence.xlsx")

    print("Looking for:", company_id)

    print("Exists:",
          company_id in df["company_id"].astype(str).str.strip().values)

    return df[
        df["company_id"].astype(str).str.strip()
        ==
        company_id.strip()
    ]

# ----------------------------------------------------------
# Load All Company IDs
# ----------------------------------------------------------

def load_all_companies():
    """
    Load canonical 92-company universe from the companies table in nifty100.db.
    This ensures we only generate tearsheets for the 92 companies in the universe,
    not the 100 rows that may appear in ScreenerEngine due to ratios data.
    """
    conn = get_connection()
    df = pd.read_sql(
        "SELECT id AS company_id, company_name FROM companies ORDER BY id",
        conn
    )
    conn.close()
    return df["company_id"].tolist()