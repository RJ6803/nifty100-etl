import numpy as np
import pandas as pd
from scipy.stats import norm


class PortfolioVaR:
    """
    Calculates Value at Risk (VaR) and Expected Shortfall (CVaR)
    for a portfolio.
    """

    def __init__(self, portfolio_df, price_history_df):
        self.portfolio = portfolio_df.copy()
        self.prices = price_history_df.copy()

    # --------------------------------------------------
    # Price Matrix
    # --------------------------------------------------
    def _price_matrix(self):

        df = self.prices.copy()

        df["date"] = pd.to_datetime(df["date"])

        matrix = (
            df.pivot(
                index="date",
                columns="company_id",
                values="adjusted_close"
            )
            .sort_index()
        )

        return matrix

    # --------------------------------------------------
    # Portfolio Daily Returns
    # --------------------------------------------------
    def portfolio_returns(self):

        prices = self._price_matrix()

        returns = prices.pct_change().dropna()

        companies = [
            c
            for c in self.portfolio["company_id"]
            if c in returns.columns
        ]

        weights = (
            self.portfolio
            .set_index("company_id")
            .loc[companies]["weight_pct"]
            .values
            / 100
        )

        portfolio_returns = returns[companies].dot(weights)

        return portfolio_returns

    # --------------------------------------------------
    # Historical VaR
    # --------------------------------------------------
    def historical_var(
        self,
        confidence=0.95
    ):

        r = self.portfolio_returns()

        percentile = (1 - confidence) * 100

        var = np.percentile(
            r,
            percentile
        )

        return round(abs(var) * 100, 2)

    # --------------------------------------------------
    # Parametric VaR
    # --------------------------------------------------
    def parametric_var(
        self,
        confidence=0.95
    ):

        r = self.portfolio_returns()

        mean = r.mean()

        std = r.std()

        z = norm.ppf(1 - confidence)

        var = mean + z * std

        return round(abs(var) * 100, 2)

    # --------------------------------------------------
    # Expected Shortfall (CVaR)
    # --------------------------------------------------
    def expected_shortfall(
        self,
        confidence=0.95
    ):

        r = self.portfolio_returns()

        cutoff = np.percentile(
            r,
            (1 - confidence) * 100
        )

        losses = r[r <= cutoff]

        if len(losses) == 0:
            return 0.0

        return round(abs(losses.mean()) * 100, 2)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(self):

        return pd.DataFrame(
            [
                {
                    "Metric": "Historical VaR (95%)",
                    "Value": self.historical_var()
                },
                {
                    "Metric": "Parametric VaR (95%)",
                    "Value": self.parametric_var()
                },
                {
                    "Metric": "Expected Shortfall (95%)",
                    "Value": self.expected_shortfall()
                }
            ]
        )