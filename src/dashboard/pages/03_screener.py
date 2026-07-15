import streamlit as st
import pandas as pd

from src.screener.engine import ScreenerEngine


PRESET_NAMES = {
    "Quality": "quality_compounder",
    "Value": "value_pick",
    "Growth": "growth_accelerator",
    "Dividend": "dividend_champion",
    "Debt Free": "debt_free_blue_chip",
    "Turnaround": "turnaround_watch",
}


def render():

    st.title("Financial Screener")

    engine = ScreenerEngine()

    # -----------------------------
    # Session state
    # -----------------------------

    if "selected_preset" not in st.session_state:
        st.session_state.selected_preset = "quality_compounder"

    st.sidebar.header("Preset Screeners")

    cols1 = st.sidebar.columns(3)

    if cols1[0].button("Quality"):
        st.session_state.selected_preset = PRESET_NAMES["Quality"]

    if cols1[1].button("Value"):
        st.session_state.selected_preset = PRESET_NAMES["Value"]

    if cols1[2].button("Growth"):
        st.session_state.selected_preset = PRESET_NAMES["Growth"]

    cols2 = st.sidebar.columns(3)

    if cols2[0].button("Dividend"):
        st.session_state.selected_preset = PRESET_NAMES["Dividend"]

    if cols2[1].button("Debt Free"):
        st.session_state.selected_preset = PRESET_NAMES["Debt Free"]

    if cols2[2].button("Turnaround"):
        st.session_state.selected_preset = PRESET_NAMES["Turnaround"]

    preset = st.session_state.selected_preset

    rules = engine.config[preset]

    st.sidebar.markdown("---")
    st.sidebar.header("Custom Filters")

    thresholds = {}

    thresholds["roe_min"] = st.sidebar.slider(
        "ROE Minimum",
        0.0,
        50.0,
        float(rules.get("roe_min", 0)),
    )

    thresholds["debt_to_equity_max"] = st.sidebar.slider(
        "Debt / Equity Maximum",
        0.0,
        10.0,
        float(rules.get("debt_to_equity_max", 10)),
    )

    thresholds["free_cash_flow_min"] = st.sidebar.slider(
        "Free Cash Flow Minimum",
        -5000.0,
        10000.0,
        float(rules.get("free_cash_flow_min", -5000)),
    )

    thresholds["revenue_cagr_5yr_min"] = st.sidebar.slider(
        "Revenue CAGR Minimum",
        -20.0,
        50.0,
        float(rules.get("revenue_cagr_5yr_min", -20)),
    )

    thresholds["pat_cagr_5yr_min"] = st.sidebar.slider(
        "PAT CAGR Minimum",
        -20.0,
        50.0,
        float(rules.get("pat_cagr_5yr_min", -20)),
    )

    thresholds["operating_profit_margin_min"] = st.sidebar.slider(
        "Operating Margin Minimum",
        -20.0,
        60.0,
        float(rules.get("operating_profit_margin_min", -20)),
    )

    thresholds["pe_max"] = st.sidebar.slider(
        "P/E Maximum",
        1.0,
        100.0,
        float(rules.get("pe_max", 100)),
    )

    thresholds["pb_max"] = st.sidebar.slider(
        "P/B Maximum",
        0.0,
        20.0,
        float(rules.get("pb_max", 20)),
    )

    thresholds["dividend_yield_min"] = st.sidebar.slider(
        "Dividend Yield Minimum",
        0.0,
        10.0,
        float(rules.get("dividend_yield_min", 0)),
    )

    thresholds["interest_coverage_min"] = st.sidebar.slider(
        "Interest Coverage Minimum",
        0.0,
        100.0,
        float(rules.get("interest_coverage_min", 0)),
    )

    df = engine.apply_filters(thresholds=thresholds)
    st.subheader("Results")
    st.success(f"{len(df)} companies match your filters")
    c1, c2, c3 = st.columns(3)
    c1.metric("Companies", len(df))

    if not df.empty:
        c2.metric(
            "Average Score",
            round(df["composite_quality_score"].mean(), 2),
        )

        c3.metric(
            "Best Score",
            round(df["composite_quality_score"].max(), 2),
        )

    columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "interest_coverage",
        "composite_quality_score",
        "quality_rank",
    ]

    available = [c for c in columns if c in df.columns]

    st.dataframe(
        df[available],
        use_container_width=True,
        height=650,
    )

    csv = df[available].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"{preset}.csv",
        mime="text/csv",
    )