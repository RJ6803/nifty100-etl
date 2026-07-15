import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils import db
from src.screener.engine import ScreenerEngine


def render():

    st.title("Company Profile")
    companies = db.get_companies()
    search = st.text_input(
        "Search Company Name or Ticker"
    )

    if search:

        filtered = companies[
            companies["company_name"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            companies["company_id"].astype(str).str.contains(
                search,
                case=False,
                na=False
            )
        ]

    else:

        filtered = companies

    if filtered.empty:

        st.warning(
            "Ticker not found — please try another."
        )
        return

    ticker = st.selectbox(
        "Select Company",
        filtered["company_id"],
        format_func=lambda x:
            f"{x} - "
            f"{filtered.set_index('company_id').loc[x,'company_name']}"
    )

    engine = ScreenerEngine()

    latest = engine.df.query(
        "company_id == @ticker"
    )

    if latest.empty:

        st.info("No financial data available.")
        return

    latest = latest.iloc[0]

    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:

        st.subheader(latest.company_name)

        st.write(
            f"**Sector:** {latest.broad_sector}"
        )

        st.write(
            f"**Sub Sector:** {latest.sub_sector}"
        )

        st.write(
            f"**NSE Ticker:** {ticker}"
        )

    with col2:

        st.info(
            "Company description not available."
        )

    st.markdown("---")
    metric_cols = st.columns(6)

    metrics = [
        ("ROE", latest.return_on_equity_pct),
        ("ROCE", latest.return_on_capital_employed_pct),
        ("Net Profit Margin", latest.net_profit_margin_pct),
        ("Debt / Equity", latest.debt_to_equity),
        ("Revenue CAGR 5Y", latest.revenue_cagr_5yr),
        ("Free Cash Flow", latest.free_cash_flow_cr)
    ]

    for column, (label, value) in zip(metric_cols, metrics):

        if pd.isna(value):
            column.metric(label, "N/A")

        else:
            column.metric(label, round(float(value), 2))

    st.markdown("---")
    pl = db.get_pl(ticker)

    if not pl.empty:

        pl["year_num"] = pd.to_numeric(
            pl["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0],
            errors="coerce"
        )

        fig = px.bar(
            pl,
            x="year_num",
            y=["sales", "net_profit"],
            barmode="group",
            title="Revenue and Net Profit (10 Years)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("Revenue history unavailable.")

    ratios = db.get_ratios(ticker)

    if not ratios.empty:
        ratios["year_num"] = pd.to_numeric(
            ratios["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0],
            errors="coerce"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=ratios["year_num"],
                y=ratios["return_on_equity_pct"],
                mode="lines+markers",
                name="ROE",
                yaxis="y1"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=ratios["year_num"],
                y=ratios["return_on_capital_employed_pct"],
                mode="lines+markers",
                name="ROCE",
                yaxis="y2"
            )
        )

        fig.update_layout(
            title="ROE vs ROCE (10 Years)",
            xaxis_title="Year",

            yaxis=dict(
                title="ROE"
            ),

            yaxis2=dict(
                title="ROCE",
                overlaying="y",
                side="right"
            ),

            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("Ratio history unavailable.")

    st.markdown("---")
    st.subheader("Pros & Cons")

    try:
        pc = pd.read_excel(
            "data/raw/prosandcons.xlsx",
            header=1
        )

        item = pc.loc[
            pc["company_id"] == ticker
        ]

        if not item.empty:

            left, right = st.columns(2)
            with left:
                st.success(
                    "✓ " + str(item.iloc[0]["pros"])
                )

            with right:
                st.error(
                    "✗ " + str(item.iloc[0]["cons"])
                )

        else:
            st.info(
                "Pros and Cons data unavailable."
            )

    except Exception:
        st.info(
            "Pros and Cons data unavailable."
        )