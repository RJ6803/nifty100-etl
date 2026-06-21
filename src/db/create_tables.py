import sqlite3

conn = sqlite3.connect("data/nifty100.db")

cursor = conn.cursor()

# Companies Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_name TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
)
""")


# Profit & Loss Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS profit_loss (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year TEXT,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
)
""")


# Balance Sheet Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS balance_sheet (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year TEXT,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
)
""")


# Cash Flow Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year TEXT,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
)
""")


# Stock Prices Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT,
    date TEXT,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    adjusted_close REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully!")