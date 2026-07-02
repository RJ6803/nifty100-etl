import sqlite3
import pandas as pd

# Connect database

conn = sqlite3.connect("data/nifty100.db")

# Load profit_loss table

pl = pd.read_sql("SELECT * FROM profit_loss", conn)
conn.close()

# Remove TTM rows

pl = pl[pl["year"] != "TTM"]

# Extract year

pl["year_num"] = (
pl["year"]
.str.extract(r'(\d{4})')[0]
.astype(int)
)

growth_data = []

for company, group in pl.groupby("company_id"):


    group = group.sort_values("year_num")

    if len(group) < 2:
        continue

    first = group.iloc[0]
    last = group.iloc[-1]

    years = last["year_num"] - first["year_num"]

    if years <= 0:
        continue

    # Sales CAGR
    if first["sales"] > 0 and last["sales"] > 0:
        sales_cagr = (
            ((last["sales"] / first["sales"]) ** (1 / years)) - 1
        ) * 100
    else:
        sales_cagr = None

    # Profit CAGR
    if first["net_profit"] > 0 and last["net_profit"] > 0:
        profit_cagr = (
            ((last["net_profit"] / first["net_profit"]) ** (1 / years)) - 1
        ) * 100
    else:
        profit_cagr = None

    growth_data.append({
        "company_id": company,
        "sales_cagr": (
            round(sales_cagr, 2)
            if sales_cagr is not None
            else None
        ),
        "profit_cagr": (
            round(profit_cagr, 2)
            if profit_cagr is not None
            else None
        )
    })
    

growth_df = pd.DataFrame(growth_data)

growth_df.to_csv(
    "src/features/company_growth.csv",
    index=False
    )

conn = sqlite3.connect("data/nifty100.db")

growth_df.to_sql(
    "company_growth",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("company_growth table written to SQLite.")

print(growth_df.head())
print("\ncompany_growth.csv created successfully!")
