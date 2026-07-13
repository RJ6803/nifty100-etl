import pandas as pd

from src.screener.engine import ScreenerEngine
from src.portfolio.allocation import AllocationEngine


class PortfolioBuilder:
    def __init__(self):
        self.engine = ScreenerEngine()
        self.df = self.engine.df.copy()

    def create_equal_weight_portfolio(
        self,
        company_ids,
        total_investment=1000000
    ):
        """
        Creates an equal-weight portfolio.

        Parameters
        ----------
        company_ids : list
            List of company IDs.

        total_investment : float
            Total amount to invest.
        """

        portfolio = self.df[
            self.df["company_id"].isin(company_ids)
        ].copy()

        portfolio["company_name"] = (
            portfolio["company_name"]
            .astype(str)
            .str.replace("\n", "", regex=False)
            .str.strip()
        )

        if portfolio.empty:
            raise ValueError("No valid companies found.")

        portfolio = AllocationEngine.equal_weight(
            portfolio,
            total_investment
        )

        return portfolio[
            [
                "company_id",
                "company_name",
                "weight_pct",
                "investment_amount",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "return_on_equity_pct",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "dividend_yield_pct",
                "composite_quality_score",
            ]
        ]

    def build_equal_weight_portfolio(
        self,
        company_ids=None,
        amount=None,
        total_investment=None,
        top_n=None,
        **kwargs,
    ):
        """
        Backward-compatible API used by the test suite.

        Supports:
            company_ids=
            amount=
            total_investment=
            top_n=
        """

        # Determine investment amount
        if total_investment is None:
            total_investment = amount

        if total_investment is None:
            total_investment = 1000000

        # If company IDs are not supplied, automatically choose the top companies
        if company_ids is None:
            if top_n is None:
                top_n = 5

            portfolio = (
                self.df
                .sort_values(
                    "composite_quality_score",
                    ascending=False
                )
                .head(top_n)
            )

            company_ids = portfolio["company_id"].tolist()

        return self.create_equal_weight_portfolio(
            company_ids=company_ids,
            total_investment=total_investment,
        )

    def build(
            self,
            investment_amount=1000000,
            number_of_stocks=5
        ):
            """
            Automatically builds an equal-weight portfolio using
            the highest quality stocks.
            """

            portfolio = (
                self.df
                .sort_values(
                    "composite_quality_score",
                    ascending=False
                )
                .head(number_of_stocks)
            )

            company_ids = portfolio["company_id"].tolist()

            return self.create_equal_weight_portfolio(
                company_ids=company_ids,
                total_investment=investment_amount
            )