import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

print("=" * 80)
print("ROE / ROCE")
print("=" * 80)

df = pd.read_sql("""
SELECT
    year,
    return_on_equity_pct,
    return_on_capital_employed_pct
FROM financial_ratios
WHERE company_id='TCS'
ORDER BY year
""", conn)

print(df)

print("\n")

print("=" * 80)
print("OTHER RATIOS")
print("=" * 80)

df2 = pd.read_sql("""
SELECT
    year,
    net_profit_margin_pct,
    debt_to_equity,
    earnings_per_share
FROM financial_ratios
WHERE company_id='TCS'
ORDER BY year
""", conn)

print(df2)

conn.close()