import pandas as pd
import numpy as np


class PortfolioCorrelation:
    """
    Computes correlation statistics for a portfolio.
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
    # Daily Returns
    # --------------------------------------------------
    def daily_returns(self):

        return self._price_matrix().pct_change().dropna()

    # --------------------------------------------------
    # Correlation Matrix
    # --------------------------------------------------
    def correlation_matrix(self):

        returns = self.daily_returns()

        companies = [
            c
            for c in self.portfolio["company_id"]
            if c in returns.columns
        ]

        return returns[companies].corr()

    # --------------------------------------------------
    # Average Correlation
    # --------------------------------------------------
    def average_correlation(self):

        corr = self.correlation_matrix()

        if len(corr) <= 1:
            return 0.0

        mask = np.triu(
            np.ones(corr.shape),
            k=1
        ).astype(bool)

        values = corr.where(mask).stack()

        return round(values.mean(), 4)

    # --------------------------------------------------
    # Diversification Score
    # --------------------------------------------------
    def diversification_score(self):

        avg_corr = self.average_correlation()

        score = (1 - avg_corr) * 100

        score = max(
            0,
            min(score, 100)
        )

        return round(score, 2)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(self):

        return pd.DataFrame(
            [
                {
                    "Metric": "Average Correlation",
                    "Value": self.average_correlation()
                },
                {
                    "Metric": "Diversification Score",
                    "Value": self.diversification_score()
                }
            ]
        )