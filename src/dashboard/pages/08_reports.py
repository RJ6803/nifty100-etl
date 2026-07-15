import pandas as pd
import streamlit as st

from src.dashboard.utils import db


def render():

    st.title("Financial Reports")

    # ----------------------------
    # Company selector
    # ----------------------------

    companies = db.get_companies()

    search = st.text_input(
        "Search company or ticker"
    )

    if search:
        companies = companies[
            companies["company_name"]
            .str.contains(search, case=False, na=False)
            |
            companies["company_id"]
            .str.contains(search, case=False, na=False)
        ]

    if companies.empty:
        st.warning("No company found.")
        return

    ticker = st.selectbox(
        "Select Company",
        companies["company_id"],
        format_func=lambda x:
            f"{x} - {companies.set_index('company_id').loc[x,'company_name']}"
    )

    # ----------------------------
    # Load reports
    # ----------------------------

    docs = pd.read_excel(
        "data/raw/documents.xlsx",
        header=1

    )

    docs.columns = docs.columns.str.strip()
    docs = docs[docs["company_id"] == ticker]

    if docs.empty:
        st.info("No reports available.")
        return

    docs = docs.sort_values(
        "Year",
        ascending=False
    )

    st.subheader("Available Annual Reports")

    for _, row in docs.iterrows():
        c1, c2 = st.columns([1, 5])
        c1.write(f"**{int(row['Year'])}**")
        c2.markdown(
            f"[Open Annual Report]({row['Annual_Report']})"
        )

    st.divider()

    st.dataframe(
        docs,
        use_container_width=True
    )