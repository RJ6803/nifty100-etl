from pathlib import Path
import numpy as np

import matplotlib
# PDF reports run without a desktop/Tk display.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHART_DIR = Path("reports/temp")
CHART_DIR.mkdir(parents=True, exist_ok=True)


def revenue_chart(df, company):

    plt.figure(figsize=(5,3))

    plt.bar(df["year"], df["sales"])

    plt.xticks(rotation=90)

    plt.title(f"{company} Revenue")

    plt.tight_layout()

    path = CHART_DIR / f"{company}_revenue.png"

    plt.savefig(path)

    plt.close()

    return str(path)


def profit_chart(df, company):

    plt.figure(figsize=(5,3))

    plt.bar(df["year"], df["net_profit"])

    plt.xticks(rotation=90)

    plt.title(f"{company} Net Profit")

    plt.tight_layout()

    path = CHART_DIR / f"{company}_profit.png"

    plt.savefig(path)

    plt.close()

    return str(path)


def roe_chart(df, company):

    plt.figure(figsize=(5,3))

    plt.plot(
        df["year"],
        df["return_on_equity_pct"],
        marker="o"
    )

    plt.xticks(rotation=90)

    plt.title("ROE")

    plt.tight_layout()

    path = CHART_DIR / f"{company}_roe.png"

    plt.savefig(path)

    plt.close()

    return str(path)


def roce_chart(df, company):

    plt.figure(figsize=(5,3))

    plt.plot(
        df["year"],
        df["return_on_capital_employed_pct"],
        marker="o"
    )

    plt.xticks(rotation=90)

    plt.title("ROCE")

    plt.tight_layout()

    path = CHART_DIR / f"{company}_roce.png"

    plt.savefig(path)

    plt.close()

    return str(path)

def balance_sheet_chart(df, company):

    plt.figure(figsize=(6, 3.5))

    # -------------------------
    # Build stacked values
    # -------------------------

    equity = (
        df["equity_capital"].fillna(0)
        + df["reserves"].fillna(0)
    )

    borrowings = df["borrowings"].fillna(0)

    liabilities = df["other_liabilities"].fillna(0)

    x = np.arange(len(df))

    plt.bar(
        x,
        equity,
        label="Equity"
    )

    plt.bar(
        x,
        borrowings,
        bottom=equity,
        label="Borrowings"
    )

    plt.bar(
        x,
        liabilities,
        bottom=equity + borrowings,
        label="Other Liabilities"
    )

    plt.xticks(
        x,
        df["year"],
        rotation=90
    )

    plt.ylabel("₹ Cr")

    plt.title(f"{company} Balance Sheet Composition")

    plt.legend(fontsize=8)

    plt.tight_layout()

    path = CHART_DIR / f"{company}_balance.png"

    plt.savefig(path)

    plt.close()

    return str(path)

def cashflow_waterfall_chart(df, company):
    if df.empty:
        return None

    latest = df.iloc[-1]

    cfo = latest["operating_activity"]
    cfi = latest["investing_activity"]
    cff = latest["financing_activity"]
    net = latest["net_cash_flow"]

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net CF"
    ]

    values = [
        cfo,
        cfi,
        cff,
        net
    ]

    colors_list = []

    for v in values:
        if v >= 0:
            colors_list.append("green")
        else:
            colors_list.append("red")

    plt.figure(figsize=(6,4))

    plt.bar(
        labels,
        values,
        color=colors_list
    )

    plt.axhline(
        y=0,
        color="black",
        linewidth=1
    )

    plt.title(
        f"{company} Cash Flow Waterfall"
    )

    plt.ylabel("₹ Cr")

    plt.tight_layout()

    path = CHART_DIR / f"{company}_cashflow.png"

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return str(path)

def roe_roce_chart(df, company):

    import matplotlib.pyplot as plt

    plt.figure(figsize=(6,3))

    plt.plot(
        df["year"],
        df["return_on_equity_pct"],
        marker="o",
        linewidth=2,
        label="ROE"
    )

    plt.plot(
        df["year"],
        df["return_on_capital_employed_pct"],
        marker="s",
        linewidth=2,
        label="ROCE"
    )

    plt.xticks(rotation=90)

    plt.title(f"{company} ROE vs ROCE")

    plt.ylabel("%")

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    path = CHART_DIR / f"{company}_roe_roce.png"

    plt.savefig(path)

    plt.close()

    return str(path)
