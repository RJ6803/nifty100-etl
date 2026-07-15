import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils import db


def render():

    st.title("Trend Analysis")

    # ----------------------------------------
    # Load companies
    # ----------------------------------------

    companies = db.get_companies()
    search = st.text_input(
        "Search Company or Ticker"
    )

    if search:
        companies = companies[
            companies["company_name"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            companies["company_id"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if companies.empty:
        st.warning("Ticker not found.")
        return

    ticker = st.selectbox(
        "Select Company",
        companies["company_id"],
        format_func=lambda x:
        f"{x} - {companies.set_index('company_id').loc[x,'company_name']}"
    )

    # ----------------------------------------
    # Load data
    # ----------------------------------------

    ratios = db.get_ratios(ticker)

    if ratios.empty:
        st.warning("No financial data available.")
        return

    ratios["year_num"] = pd.to_numeric(
        ratios["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0],
        errors="coerce"
    )
    ratios = ratios.sort_values("year_num")

    # ----------------------------------------
    # Metrics
    # ----------------------------------------

    metric_map = {
        "ROE": "return_on_equity_pct",
        "ROCE": "return_on_capital_employed_pct",
        "Net Profit Margin": "net_profit_margin_pct",
        "Operating Profit Margin": "operating_profit_margin_pct",
        "Debt / Equity": "debt_to_equity",
        "Revenue CAGR": "revenue_cagr_5yr",
        "PAT CAGR": "pat_cagr_5yr",
        "Dividend Yield": "dividend_yield_pct",
        "Interest Coverage": "interest_coverage",
        "Free Cash Flow": "free_cash_flow_cr",
        "Quality Score": "composite_quality_score"
    }

    selected_metrics = st.multiselect(
        "Choose up to 3 metrics",
        list(metric_map.keys()),
        default=["ROE"]
    )

    if len(selected_metrics) > 3:
        st.error("Maximum 3 metrics allowed.")
        return

    # ----------------------------------------
    # Plot
    # ----------------------------------------

    fig = go.Figure()

    for metric in selected_metrics:
        column = metric_map[metric]
        if column not in ratios.columns:

            continue

        y = ratios[column].fillna(0)
        fig.add_trace(
            go.Scatter(
                x=ratios["year_num"],
                y=y,
                mode="lines+markers",
                name=metric
            )
        )

        # ------------------------------------
        # YoY Annotation
        # ------------------------------------

        pct = y.pct_change() * 100

        for x, yy, p in zip(
            ratios["year_num"],
            y,
            pct
        ):

            if pd.notna(p):
                fig.add_annotation(
                    x=x,
                    y=yy,
                    text=f"{p:.1f}%",
                    showarrow=False,
                    font=dict(size=10)
                )

    fig.update_layout(
        title="10-Year Financial Trend",
        xaxis_title="Year",
        yaxis_title="Value",
        hovermode="x unified",
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ----------------------------------------
    # Data Table
    # ----------------------------------------

    st.subheader("Underlying Data")
    cols = ["year_num"]

    for metric in selected_metrics:
        cols.append(metric_map[metric])
    cols = [c for c in cols if c in ratios.columns]

    st.dataframe(
        ratios[cols],
        use_container_width=True
    )

    # ----------------------------------------
    # Missing Data Note
    # ----------------------------------------

    if len(ratios) < 10:
        st.info(
            f"Only {len(ratios)} years of data available for this company."
        )