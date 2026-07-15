import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics.peer import PeerComparisonEngine
from src.screener.engine import ScreenerEngine


def render():

    st.title("Peer Comparison")
    engine = PeerComparisonEngine()

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------

    screener = ScreenerEngine()
    data = screener.df.copy()
    peer_groups = pd.read_excel("data/raw/peer_groups.xlsx")

    # -------------------------------------------------
    # Peer Group Selection
    # -------------------------------------------------

    groups = sorted(peer_groups["peer_group_name"].dropna().unique())

    selected_group = st.sidebar.selectbox(
        "Peer Group",
        groups
    )

    st.subheader(f"{selected_group} Peer Group")

    group_df = peer_groups[
        peer_groups["peer_group_name"] == selected_group
    ]

    companies = data[
        data["company_id"].isin(group_df["company_id"])
    ].copy()

    if companies.empty:
        st.warning("No companies found for this peer group.")
        return

    companies = companies.sort_values("company_name")

    # -------------------------------------------------
    # Company Selection
    # -------------------------------------------------

    selected_company = st.selectbox(
        "Select Company",
        companies["company_id"],
        format_func=lambda x: companies.loc[
            companies["company_id"] == x,
            "company_name"
        ].values[0]
    )

    company = companies[
        companies["company_id"] == selected_company
    ].iloc[0]

    # -------------------------------------------------
    # Radar Metrics
    # -------------------------------------------------

    metrics = {
        "ROE": "return_on_equity_pct",
        "ROCE": "return_on_capital_employed_pct",
        "Profit Margin": "net_profit_margin_pct",
        "Revenue CAGR": "revenue_cagr_5yr",
        "PAT CAGR": "pat_cagr_5yr",
        "Debt/Equity": "debt_to_equity",
        "Dividend Yield": "dividend_yield_pct",
        "Quality Score": "composite_quality_score"
    }

    radar_labels = list(metrics.keys())
    company_values = []
    peer_values = []

    for column in metrics.values():

        company_values.append(
            float(company.get(column, 0) or 0)
        )

        peer_values.append(
            float(companies[column].fillna(0).mean())
        )

    company_values.append(company_values[0])
    peer_values.append(peer_values[0])
    radar_labels.append(radar_labels[0])

    # -------------------------------------------------
    # Radar Chart
    # -------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=company_values,
            theta=radar_labels,
            fill="toself",
            name=company["company_name"],
            line=dict(width=3)
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=peer_values,
            theta=radar_labels,
            fill="toself",
            name="Peer Average",
            opacity=0.6,
            line=dict(dash="dash")
        )
    )

    fig.update_layout(
        title="Company vs Peer Average",
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        showlegend=True,
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.divider()

    # -------------------------------------------------
    # KPI Table
    # -------------------------------------------------

    st.subheader("Peer Comparison Table")

    display_columns = [
        "company_id",
        "company_name",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "dividend_yield_pct",
        "composite_quality_score"
    ]

    table = companies[
        display_columns
    ].copy()

    table = table.rename(
        columns={
            "company_id": "Ticker",
            "company_name": "Company",
            "return_on_equity_pct": "ROE",
            "return_on_capital_employed_pct": "ROCE",
            "net_profit_margin_pct": "Net Margin",
            "debt_to_equity": "Debt/Equity",
            "revenue_cagr_5yr": "Revenue CAGR",
            "pat_cagr_5yr": "PAT CAGR",
            "dividend_yield_pct": "Dividend Yield",
            "composite_quality_score": "Quality Score"
        }
    )

    benchmark_ids = group_df.loc[
        group_df["is_benchmark"] == True,
        "company_id"
    ].tolist()

    def highlight(row):

        if row["Ticker"] == selected_company:

            return [
                "background-color:#1E3A8A;color:white;font-weight:bold"
            ] * len(row)

        if row["Ticker"] in benchmark_ids:

            return [
                "background-color:#14532D;color:white;font-weight:bold"
            ] * len(row)

        return [""] * len(row)

    st.dataframe(
        table.style.highlight_null(
            color="#333333"
        ).apply(
            highlight,
            axis=1
        ),
        use_container_width=True,
        height=500
    )

    st.success(
        f"Selected Company : {company['company_name']}"
    )

    if selected_company in benchmark_ids:

        st.info("This company is the Benchmark for this peer group.")

    else:

        benchmark_company = group_df.loc[
            group_df["is_benchmark"] == True,
            "company_id"
        ]

        if not benchmark_company.empty:

            benchmark = companies[
                companies["company_id"] == benchmark_company.iloc[0]
            ]

            if not benchmark.empty:

                st.info(
                    f"Benchmark Company : {benchmark.iloc[0]['company_name']}"
                )