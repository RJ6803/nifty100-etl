import pandas as pd
import plotly.express as px
import streamlit as st

from src.screener.engine import ScreenerEngine


def render():

    st.title("Capital Allocation Map")

    # -------------------------------------------------
    # Load capital allocation data
    # -------------------------------------------------

    capital = pd.read_csv("output/capital_allocation.csv")

    # -------------------------------------------------
    # Company master from ScreenerEngine
    # -------------------------------------------------

    engine = ScreenerEngine()

    company_master = (
        engine.df[
            [
                "company_id",
                "company_name"
            ]
        ]
        .drop_duplicates()
    )

    capital = capital.merge(
        company_master,
        on="company_id",
        how="left"
    )

    # -------------------------------------------------
    # Fix missing company names
    # -------------------------------------------------

    capital["company_name"] = (
        capital["company_name"]
        .fillna(capital["company_id"])
        .astype(str)
        .str.replace("\n", "", regex=False)
        .str.strip()
    )

    # -------------------------------------------------
    # Latest year only
    # -------------------------------------------------

    capital["year_num"] = pd.to_numeric(
        capital["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    capital = capital.loc[
        capital.groupby("company_id")["year_num"]
        .transform("max")
        .eq(capital["year_num"])
    ].copy()

    # -------------------------------------------------
    # Unique label for Treemap
    # -------------------------------------------------

    capital["display_name"] = (
        capital["company_id"]
        + " - "
        + capital["company_name"]
    )

    capital["count"] = 1

    # -------------------------------------------------
    # KPI Cards
    # -------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Companies",
        capital["company_id"].nunique()
    )

    c2.metric(
        "Allocation Patterns",
        capital["pattern_label"].nunique()
    )

    c3.metric(
        "Latest Year",
        int(capital["year_num"].max())
    )

    st.divider()

    # -------------------------------------------------
    # Treemap
    # -------------------------------------------------

    st.subheader("Capital Allocation Patterns")

    try:
        fig = px.treemap(
            capital,
            path=[
                "pattern_label",
                "display_name"
            ],
            values="count",
            color="pattern_label",
            hover_data=[
                "company_id",
                "year"
            ]
        )

        fig.update_layout(
            height=700,
            margin=dict(
                l=10,
                r=10,
                t=40,
                b=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:
        st.error("Unable to generate Treemap")
        st.exception(e)

    # -------------------------------------------------
    # Pattern Explorer
    # -------------------------------------------------

    st.divider()
    st.subheader("Explore Capital Allocation Pattern")

    patterns = sorted(
        capital["pattern_label"]
        .dropna()
        .unique()
    )

    selected_pattern = st.selectbox(
        "Select Pattern",
        patterns
    )

    filtered = capital.loc[
        capital["pattern_label"] == selected_pattern
    ].sort_values(
        "company_name"
    )

    st.success(
        f"{len(filtered)} companies belong to '{selected_pattern}'."
    )

    st.dataframe(
        filtered[
            [
                "company_id",
                "company_name",
                "year",
                "cfo_sign",
                "cfi_sign",
                "cff_sign",
                "pattern_label"
            ]
        ],

        use_container_width=True,
        height=500
    )

    # -------------------------------------------------
    # Pattern Distribution
    # -------------------------------------------------

    st.divider()
    st.subheader("Pattern Distribution")

    counts = (
        capital["pattern_label"]
        .value_counts()
        .rename_axis("Pattern")
        .reset_index(name="Companies")
    )

    fig_bar = px.bar(
        counts,
        x="Pattern",
        y="Companies",
        color="Pattern",
        text="Companies",
        title="Companies by Capital Allocation Pattern"
    )

    fig_bar.update_traces(
        textposition="outside"
    )

    fig_bar.update_layout(
        height=550,
        xaxis_title="Pattern",
        yaxis_title="Companies"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # -------------------------------------------------
    # Raw Data
    # -------------------------------------------------

    with st.expander("View Raw Capital Allocation Data"):

        st.dataframe(
            capital,
            use_container_width=True
        )