import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.utils import db
from src.screener.engine import ScreenerEngine


def render():

    st.title("Sector Analysis")

    # ----------------------------------------------------
    # Load latest company dataset
    # ----------------------------------------------------

    screener = ScreenerEngine()
    data = screener.df.copy()

    # ----------------------------------------------------
    # Sector Dropdown
    # ----------------------------------------------------

    sectors = sorted(
        data["broad_sector"]
        .dropna()
        .unique()
    )

    selected_sector = st.selectbox(
        "Select Sector",
        sectors
    )

    sector_df = data[
        data["broad_sector"] == selected_sector
    ].copy()

    if sector_df.empty:
        st.warning("No companies found.")
        return

    st.subheader(f"{selected_sector} Sector")

    # ----------------------------------------------------
    # Clean Missing Values
    # ----------------------------------------------------

    sector_df["sales"] = pd.to_numeric(
        sector_df["sales"],
        errors="coerce"
    )

    sector_df["market_cap_crore"] = pd.to_numeric(
        sector_df["market_cap_crore"],
        errors="coerce"
    )

    sector_df["return_on_equity_pct"] = pd.to_numeric(
        sector_df["return_on_equity_pct"],
        errors="coerce"
    )

    sector_df = sector_df.dropna(
        subset=[
            "sales",
            "market_cap_crore",
            "return_on_equity_pct"
        ]
    )

    # ----------------------------------------------------
    # Bubble Chart
    # ----------------------------------------------------

    fig = px.scatter(
        sector_df,
        x="sales",
        y="return_on_equity_pct",
        size="market_cap_crore",
        color="sub_sector",
        hover_name="company_name",
        hover_data=[
            "company_id",
            "market_cap_crore",
            "sales",
            "return_on_equity_pct",
            "debt_to_equity",
            "composite_quality_score"
        ],
        title=f"{selected_sector} Companies",
        size_max=60
    )

    fig.update_layout(
        xaxis_title="Revenue (Crore)",
        yaxis_title="ROE (%)",
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ----------------------------------------------------
    # Sector Median KPI
    # ----------------------------------------------------

    st.subheader("Sector Median KPIs")

    medians = {
        "ROE":
            sector_df["return_on_equity_pct"].median(),
        "ROCE":
            sector_df["return_on_capital_employed_pct"].median(),
        "Net Margin":
            sector_df["net_profit_margin_pct"].median(),
        "Debt/Equity":
            sector_df["debt_to_equity"].median(),
        "Revenue CAGR":
            sector_df["revenue_cagr_5yr"].median(),
        "PAT CAGR":
            sector_df["pat_cagr_5yr"].median(),
        "Dividend Yield":
            sector_df["dividend_yield_pct"].median(),
        "Quality Score":
            sector_df["composite_quality_score"].median()
    }

    median_df = pd.DataFrame({
        "Metric": medians.keys(),
        "Median": medians.values()
    })

    bar = px.bar(
        median_df,
        x="Metric",
        y="Median",
        text="Median",
        title="Sector Median Comparison"
    )

    bar.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    bar.update_layout(
        height=550
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )

    # ----------------------------------------------------
    # Company Table
    # ----------------------------------------------------

    st.subheader("Companies")

    columns = [
        "company_id",
        "company_name",
        "sub_sector",
        "sales",
        "market_cap_crore",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "composite_quality_score"
    ]

    available = [
        c for c in columns
        if c in sector_df.columns
    ]

    st.dataframe(
        sector_df[available]
        .sort_values(
            "composite_quality_score",
            ascending=False
        ),
        use_container_width=True,
        height=500
    )

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    st.success(
        f"{len(sector_df)} companies in {selected_sector}"
    )