import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

companies = [
    "ABB",
    "TCS",
    "RELIANCE"
]

for company in companies:

    print("="*60)
    print(company)

    print("\nProfit Loss")

    print(pd.read_sql(f"""
    SELECT year,
           sales,
           net_profit,
           operating_profit,
           opm_percentage
    FROM profit_loss
    WHERE company_id='{company}'
    ORDER BY year
    """, conn))

    print("\nBalance Sheet")

    print(pd.read_sql(f"""
    SELECT year,
           equity_capital,
           reserves,
           borrowings,
           total_assets
    FROM balance_sheet
    WHERE company_id='{company}'
    ORDER BY year
    """, conn))

    print("\nFinancial Ratios")

    print(pd.read_sql(f"""
    SELECT *
    FROM financial_ratios
    WHERE company_id='{company}'
    ORDER BY year
    """, conn))

conn.close()