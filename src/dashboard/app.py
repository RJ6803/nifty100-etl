"""Nifty 100 Analytics Streamlit entry point."""

import importlib
import os
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Home": "01_home",
    "Company Profile": "02_profile",
    "Screener": "03_screener",
    "Peers": "04_peers",
    "Trends": "05_trends",
    "Sectors": "06_sectors",
    "Capital Allocation": "07_capital",
    "Reports": "08_reports",
}

st.sidebar.title("Navigation")

choice = st.sidebar.radio("", list(PAGES.keys()))

module = importlib.import_module(
    f"src.dashboard.pages.{PAGES[choice]}"
)

module.render()