import sqlite3
import pandas as pd


DB_PATH = "data/nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)



# Database existence tests


def test_database_exists():
    conn = get_connection()
    assert conn is not None
    conn.close()



# Table existence tests


def test_companies_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='companies'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_profit_loss_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='profit_loss'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_balance_sheet_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='balance_sheet'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_cashflow_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cashflow'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_stock_prices_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='stock_prices'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_company_kpis_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='company_kpis'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_company_growth_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='company_growth'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_final_company_features_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='final_company_features'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_validation_failures_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='validation_failures'",
        conn
    )
    conn.close()

    assert len(tables) == 1


def test_load_audit_table_exists():
    conn = get_connection()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='load_audit'",
        conn
    )
    conn.close()

    assert len(tables) == 1



# Row count tests


def test_companies_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM companies", conn)
    conn.close()

    assert len(df) > 0


def test_profit_loss_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM profit_loss", conn)
    conn.close()

    assert len(df) > 0


def test_balance_sheet_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM balance_sheet", conn)
    conn.close()

    assert len(df) > 0


def test_cashflow_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM cashflow", conn)
    conn.close()

    assert len(df) > 0


def test_stock_prices_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stock_prices", conn)
    conn.close()

    assert len(df) > 0



# Feature table tests

def test_company_kpis_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM company_kpis", conn)
    conn.close()

    assert len(df) > 0


def test_company_growth_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM company_growth", conn)
    conn.close()

    assert len(df) > 0


def test_final_company_features_not_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM final_company_features", conn)
    conn.close()

    assert len(df) > 0