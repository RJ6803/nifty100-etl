import sqlite3

conn = sqlite3.connect("data/nifty100.db")

cur = conn.cursor()

count = cur.execute(
    "SELECT COUNT(*) FROM financial_ratios"
).fetchone()[0]

print("Rows =", count)

conn.close()