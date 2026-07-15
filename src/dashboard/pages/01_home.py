import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.utils import db
from src.screener.engine import ScreenerEngine

def render():
    st.title("Nifty 100 Analytics")
    year = st.sidebar.selectbox("Financial year", list(range(2024, 2018, -1)))
    ratios = db.get_ratios(year=year); sectors = db.get_sectors()
    latest = ratios.merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")
    market = pd.read_excel("data/raw/market_cap.xlsx"); market = market.loc[market.year.eq(year)]
    latest = latest.merge(market[["company_id", "pe_ratio"]], on="company_id", how="left")
    vals = [latest.return_on_equity_pct.mean(), latest.pe_ratio.median(), latest.debt_to_equity.median(), len(sectors), latest.revenue_cagr_5yr.median(), int(latest.debt_to_equity.fillna(1).eq(0).sum())]
    for col, label, value in zip(
        st.columns(6),
        ["Average ROE", "Median P/E", "Median D/E", "Total Companies", "Median Revenue CAGR", "Debt-Free"],
        vals,
    ):
        if pd.isna(value):
            display = "N/A"
        elif label in ["Average ROE", "Median Revenue CAGR"]:
            display = f"{value:.2f}%"
        elif isinstance(value, float):
            display = f"{value:.2f}"
        else:
            display = value

        col.metric(label, display)

    counts = (
        sectors["broad_sector"]
        .value_counts()
        .rename_axis("sector")
        .reset_index(name="companies")
    )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            px.pie(
                counts,
                names="sector",
                values="companies",
                hole=0.5,
                title="Companies by Sector",
            ),
            use_container_width=True,
        )

    with right:
        scored = ScreenerEngine().df.sort_values(
            "composite_quality_score",
            ascending=False,
        )

        st.subheader("Top 5 Quality Companies")

        st.dataframe(
            scored[
                [
                    "company_name",
                    "broad_sector",
                    "return_on_equity_pct",
                    "revenue_cagr_5yr",
                    "composite_quality_score",
                ]
            ].head(5),
            use_container_width=True,
        )