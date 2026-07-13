"""Config-driven financial screener and composite quality scoring."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
import yaml

from src.screener.exporter import ScreenerExporter


DB_PATH = Path("data/nifty100.db")
CONFIG_PATH = Path("config/screener_config.yaml")


class ScreenerEngine:
    """Screen the latest financial-ratio observation for every company.

    ``dataframe`` is intentionally injectable: it makes analyst experiments and
    unit tests independent from SQLite while preserving the production loader.
    """

    def __init__(self, db_path=DB_PATH, config_path=CONFIG_PATH, dataframe=None):
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        with self.config_path.open(encoding="utf-8") as stream:
            self.config = yaml.safe_load(stream) or {}
        self.conn = None
        self.df = dataframe.copy() if dataframe is not None else self.load_data()
        self.df = self.add_composite_quality_score(self.df)

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def load_data(self):
        self.conn = sqlite3.connect(self.db_path)
        ratios = pd.read_sql("SELECT * FROM financial_ratios", self.conn)
        ratios["year_num"] = pd.to_numeric(
            ratios["year"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce"
        )
        latest = ratios.groupby("company_id")["year_num"].transform("max")
        ratios = ratios.loc[ratios["year_num"].eq(latest)].drop(columns="year_num")

        companies = pd.read_sql(
            "SELECT id AS company_id, company_name, roce_percentage FROM companies", self.conn
        )
        profit = pd.read_sql("SELECT company_id, year, sales, net_profit FROM profit_loss", self.conn)
        profit["year_num"] = pd.to_numeric(profit["year"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
        profit = profit.loc[profit.groupby("company_id")["year_num"].transform("max").eq(profit["year_num"])]
        cagr = pd.read_sql("SELECT company_id, revenue_cagr_3yr FROM company_cagr", self.conn)

        balance = pd.read_sql("SELECT company_id, year, borrowings FROM balance_sheet", self.conn)
        balance["year"] = pd.to_numeric(balance["year"], errors="coerce")
        balance = balance.sort_values(["company_id", "year"])
        balance["debt_declining"] = balance["borrowings"].lt(balance.groupby("company_id")["borrowings"].shift())
        debt = balance.groupby("company_id", as_index=False).tail(1)[["company_id", "debt_declining"]]

        sectors = pd.read_excel("data/raw/sectors.xlsx", usecols=["company_id", "broad_sector", "sub_sector"])
        market = pd.read_excel("data/raw/market_cap.xlsx")
        market["year_num"] = pd.to_numeric(market["year"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
        market = market.loc[market.groupby("company_id")["year_num"].transform("max").eq(market["year_num"])]
        market = market[["company_id", "market_cap_crore", "pe_ratio", "pb_ratio", "dividend_yield_pct"]]

        return (ratios.merge(companies, on="company_id", how="left")
                .merge(sectors, on="company_id", how="left")
                .merge(market, on="company_id", how="left")
                .merge(profit[["company_id", "sales", "net_profit"]], on="company_id", how="left")
                .merge(cagr, on="company_id", how="left")
                .merge(debt, on="company_id", how="left").reset_index(drop=True))

    @staticmethod
    def _winsor_score(values, inverse=False):
        numeric = pd.to_numeric(values.replace("Debt Free", np.inf) if isinstance(values, pd.Series) else values, errors="coerce")
        finite = numeric.replace([np.inf, -np.inf], np.nan).dropna()
        if finite.empty:
            return pd.Series(0.0, index=values.index)
        low, high = finite.quantile(.10), finite.quantile(.90)
        clipped = numeric.clip(low, high).fillna(low)
        score = pd.Series(50.0, index=values.index) if high == low else (clipped - low) * 100 / (high - low)
        return 100 - score if inverse else score

    @classmethod
    def add_composite_quality_score(cls, dataframe):
        df = dataframe.copy()
        for column in ("return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                       "free_cash_flow_cr", "cfo_pat_ratio", "revenue_cagr_5yr", "pat_cagr_5yr",
                       "debt_to_equity", "interest_coverage"):
            if column not in df:
                df[column] = np.nan
        raw = (
            cls._winsor_score(df.return_on_equity_pct) * .15 + cls._winsor_score(df.return_on_capital_employed_pct) * .10 +
            cls._winsor_score(df.net_profit_margin_pct) * .10 + cls._winsor_score(df.free_cash_flow_cr) * .15 +
            cls._winsor_score(df.cfo_pat_ratio) * .10 + df.get("fcf_positive_flag", pd.Series(0, index=df.index)).fillna(0).astype(float).clip(0, 1) * 5 +
            cls._winsor_score(df.revenue_cagr_5yr) * .10 + cls._winsor_score(df.pat_cagr_5yr) * .10 +
            cls._winsor_score(df.debt_to_equity, inverse=True) * .10 + cls._winsor_score(df.interest_coverage) * .05
        )
        df["composite_quality_score_raw"] = raw.round(2)
        sector = df.get("broad_sector", pd.Series("Unclassified", index=df.index)).fillna("Unclassified")
        def relative(s):
            return pd.Series(50.0, s.index) if s.max() == s.min() else (s - s.min()) * 100 / (s.max() - s.min())
        df["composite_quality_score"] = raw.groupby(sector, group_keys=False).transform(relative).round(2)
        return df

    def apply_filters(self, preset=None, thresholds: Mapping | None = None):
        """Apply named preset or analyst supplied threshold mapping."""
        if thresholds is None:
            if preset not in self.config:
                raise KeyError(f"Unknown screener preset: {preset}")
            thresholds = self.config[preset]
        df = self.df.copy()
        min_columns = {
            "roe_min": "return_on_equity_pct", "free_cash_flow_min": "free_cash_flow_cr",
            "revenue_cagr_5yr_min": "revenue_cagr_5yr", "pat_cagr_5yr_min": "pat_cagr_5yr",
            "operating_profit_margin_min": "operating_profit_margin_pct", "dividend_yield_min": "dividend_yield_pct",
            "interest_coverage_min": "interest_coverage", "market_cap_min": "market_cap_crore",
            "net_profit_min": "net_profit", "eps_cagr_5yr_min": "eps_cagr_5yr",
            "asset_turnover_min": "asset_turnover", "sales_min": "sales", "revenue_cagr_3yr_min": "revenue_cagr_3yr",
        }
        max_columns = {"pe_max": "pe_ratio", "pb_max": "pb_ratio", "dividend_payout_max": "dividend_payout_ratio_pct"}
        for key, column in min_columns.items():
            if key in thresholds:
                values = pd.to_numeric(df[column].replace("Debt Free", np.inf), errors="coerce")
                df = df.loc[values.ge(thresholds[key])]
        for key, column in max_columns.items():
            if key in thresholds:
                df = df.loc[pd.to_numeric(df[column], errors="coerce").le(thresholds[key])]
        if "debt_to_equity_max" in thresholds:
            # Banks, insurers and other Financials are intentionally retained.
            non_financial = df["broad_sector"].fillna("").ne("Financials")
            debt_ok = pd.to_numeric(df["debt_to_equity"], errors="coerce").le(thresholds["debt_to_equity_max"])
            df = df.loc[~non_financial | debt_ok]
        if "debt_to_equity_exact" in thresholds:
            df = df.loc[pd.to_numeric(df["debt_to_equity"], errors="coerce").eq(thresholds["debt_to_equity_exact"])]
        if thresholds.get("debt_declining"):
            df = df.loc[df["debt_declining"].fillna(False)]
        return df.sort_values(["composite_quality_score", "market_cap_crore"], ascending=[False, False], na_position="last").reset_index(drop=True).assign(quality_rank=lambda x: x.index + 1)

    def run(self, output_path="output/screener_output.xlsx"):
        results = {name: self.apply_filters(name) for name in self.config}
        ScreenerExporter().export(results, output_path, self.config)
        return results


if __name__ == "__main__":
    ScreenerEngine().run()
