import sqlite3
import pandas as pd

DB = "data/nifty100.db"

conn = sqlite3.connect(DB)

profit = pd.read_sql("SELECT * FROM profit_loss", conn)
balance = pd.read_sql("SELECT * FROM balance_sheet", conn)
ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)

conn.close()

companies = [
    "ABB",
    "TCS",
    "RELIANCE"
]

print("=" * 80)
print("DAY 12 MANUAL VERIFICATION")
print("=" * 80)

for company in companies:

    print("\n")
    print("=" * 50)
    print(company)
    print("=" * 50)

    # latest common year
    pl = profit[
        (profit.company_id == company) &
        (profit.year != "TTM")
    ].copy()

    bs = balance[
        (balance.company_id == company) &
        (balance.year != "Sep 2024")
    ].copy()

    latest_year = sorted(pl.year)[-1]

    pl_row = pl[pl.year == latest_year].iloc[0]
    bs_row = bs[bs.year == latest_year].iloc[0]

    ratio_row = ratios[
        (ratios.company_id == company) &
        (ratios.year == latest_year)
    ].iloc[0]

    # -------------------------
    # ROE
    # -------------------------

    equity = (
        bs_row["equity_capital"] +
        bs_row["reserves"]
    )

    manual_roe = (
        pl_row["net_profit"] /
        equity
    ) * 100

    db_roe = ratio_row["return_on_equity_pct"]

    roe_diff = abs(
        manual_roe - db_roe
    )

    print("\nROE Verification")

    print(f"Manual ROE   : {manual_roe:.2f}")
    print(f"Database ROE : {db_roe:.2f}")
    print(f"Difference   : {roe_diff:.4f}%")

    if roe_diff < 0.1:
        print("PASS")
    else:
        print("FAIL")

    # -------------------------
    # Revenue CAGR
    # -------------------------

    history = pl.sort_values("year")

    if len(history) >= 6:

        start_sales = history.iloc[-6]["sales"]
        end_sales = history.iloc[-1]["sales"]

        years = 5

        manual_cagr = (
            ((end_sales / start_sales) ** (1 / years) - 1)
            * 100
        )

        db_cagr = ratio_row["revenue_cagr_5yr"]

        cagr_diff = abs(
            manual_cagr - db_cagr
        )

        print("\nRevenue CAGR Verification")

        print(f"Manual CAGR   : {manual_cagr:.2f}")
        print(f"Database CAGR : {db_cagr:.2f}")
        print(f"Difference    : {cagr_diff:.4f}%")

        if cagr_diff < 0.1:
            print("PASS")
        else:
            print("FAIL")

    else:
        print("\nNot enough history.")