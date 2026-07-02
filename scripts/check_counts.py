import sqlite3

conn = sqlite3.connect("data/nifty100.db")
cur = conn.cursor()

tables = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cashflow",
    "stock_prices"
]

for t in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {count}")

conn.close()