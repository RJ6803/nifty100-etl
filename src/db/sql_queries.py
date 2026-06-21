import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

queries = {

"Total Companies":
"""
SELECT COUNT(*) AS total_companies
FROM companies
""",

"Profit Loss Rows":
"""
SELECT COUNT(*) AS rows
FROM profit_loss
""",

"Balance Sheet Rows":
"""
SELECT COUNT(*) AS rows
FROM balance_sheet
""",

"Cashflow Rows":
"""
SELECT COUNT(*) AS rows
FROM cashflow
""",

"Stock Price Rows":
"""
SELECT COUNT(*) AS rows
FROM stock_prices
""",

"Top 10 Companies by ROE":
"""
SELECT company_name, roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10
""",

"Top 10 Companies by ROCE":
"""
SELECT company_name, roce_percentage
FROM companies
ORDER BY roce_percentage DESC
LIMIT 10
""",

"Highest Net Profit":
"""
SELECT company_id,
MAX(net_profit) AS max_profit
FROM profit_loss
GROUP BY company_id
ORDER BY max_profit DESC
LIMIT 10
"""
}

for name, query in queries.items():
    print("\n", "="*50)
    print(name)
    print("="*50)
    print(pd.read_sql(query, conn))

conn.close()