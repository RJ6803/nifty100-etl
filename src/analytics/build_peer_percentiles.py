import sqlite3
import pandas as pd

# -----------------------------
# Connect Database
# -----------------------------
conn = sqlite3.connect("data/nifty100.db")

# Financial Ratios
financial = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

conn.close()

sectors = pd.read_excel(
    "data/raw/sectors.xlsx"
)[
    [
        "company_id",
        "broad_sector",
        "sub_sector"
    ]
]

financial = financial.merge(
    sectors,
    on="company_id",
    how="left"
)


financial["broad_sector"] = (
    financial["broad_sector"]
    .fillna("Unknown")
)

financial["sub_sector"] = (
    financial["sub_sector"]
    .fillna("Unknown")
)


def calculate_percentile(df, metric, ascending=True):
    """
    Calculates percentile rank inside each sector.
    """
    return (
        df.groupby("broad_sector")[metric]
          .rank(
                pct=True,
                ascending=ascending
          ) * 100
    )

metrics = {
        "return_on_equity_pct": True,
        "return_on_capital_employed_pct": True,
        "net_profit_margin_pct": True,
        "operating_profit_margin_pct": True,
        "asset_turnover": True,
        "interest_coverage": True,
        "revenue_cagr_5yr": True,
        "pat_cagr_5yr": True,
        "composite_quality_score": True,

        # lower debt is better
        "debt_to_equity": False
    }

peer_rows = []

for metric, higher_is_better in metrics.items():

    temp = financial[
        [
            "company_id",
            "year",
            "broad_sector",
            "sub_sector",
            metric
        ]
    ].copy()

    temp["percentile_rank"] = calculate_percentile(
        temp,
        metric,
        ascending=higher_is_better
    )

    temp = temp.rename(
        columns={
            metric: "value"
        }
    )
    temp["metric"] = metric
    
    temp["peer_group_name"] = temp["broad_sector"]

    peer_rows.append(
        temp[
            [
                "company_id",
                "year",
                "peer_group_name",
                "sub_sector",
                "metric",
                "value",
                "percentile_rank"
            ]
        ]
    )

peer_percentiles = pd.concat(
        peer_rows,
        ignore_index=True
    )

conn = sqlite3.connect("data/nifty100.db")

peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print(f"Peer percentiles generated: {len(peer_percentiles)} rows")
print("peer_percentiles table written successfully!")