"""Cached, read-only dashboard data access functions."""
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/nifty100.db"

def _query(sql, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(sql, conn, params=params)

@st.cache_data(ttl=600)
def get_companies():
    return _query("SELECT id AS company_id, company_name FROM companies ORDER BY company_name")
@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    sql, params = "SELECT * FROM financial_ratios", []
    where = []
    if ticker: where.append("company_id = ?"); params.append(ticker)
    if year: where.append("year LIKE ?"); params.append(f"%{year}%")
    if where: sql += " WHERE " + " AND ".join(where)
    return _query(sql, params)
@st.cache_data(ttl=600)
def get_pl(ticker): return _query("SELECT * FROM profit_loss WHERE company_id=? ORDER BY year", (ticker,))
@st.cache_data(ttl=600)
def get_bs(ticker): return _query("SELECT * FROM balance_sheet WHERE company_id=? ORDER BY year", (ticker,))
@st.cache_data(ttl=600)
def get_cf(ticker): return _query("SELECT * FROM cashflow WHERE company_id=? ORDER BY year", (ticker,))
@st.cache_data(ttl=600)
def get_sectors(): return pd.read_excel("data/raw/sectors.xlsx")
@st.cache_data(ttl=600)
def get_peers(group_name):
    groups = pd.read_excel("data/raw/peer_groups.xlsx")
    return groups.loc[groups.peer_group_name.eq(group_name)]
@st.cache_data(ttl=600)
def get_valuation(ticker):
    from src.analytics.valuation import build_valuation_summary
    return build_valuation_summary().query("company_id == @ticker")
