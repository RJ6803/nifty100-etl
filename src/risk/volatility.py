import numpy as np
import pandas as pd


class PortfolioVolatility:
    """
    Calculates volatility statistics for a portfolio.
    """

    def __init__(self, portfolio_df, price_history_df):
        self.portfolio = portfolio_df.copy()
        self.prices = price_history_df.copy()

    # --------------------------------------------------
    # Prepare price matrix
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

        prices = self._price_matrix()

        returns = prices.pct_change().dropna()

        return returns

    # --------------------------------------------------
    # Stock Volatility
    # --------------------------------------------------
    def stock_volatility(self):

        returns = self.daily_returns()

        vol = returns.std()

        annual_vol = vol * np.sqrt(252)

        result = annual_vol.reset_index()

        result.columns = [
            "company_id",
            "annual_volatility"
        ]

        return result

    # --------------------------------------------------
    # Portfolio Volatility
    # --------------------------------------------------
    def portfolio_volatility(self):

        returns = self.daily_returns()

        common = [
            c
            for c in self.portfolio["company_id"]
            if c in returns.columns
        ]

        if len(common) == 0:
            return None

        weights = (
            self.portfolio
            .set_index("company_id")
            .loc[common]["weight_pct"]
            .values
            / 100
        )

        covariance = (
            returns[common]
            .cov()
            * 252
        )

        portfolio_variance = (
            weights.T
            @ covariance.values
            @ weights
        )

        portfolio_volatility = np.sqrt(
            portfolio_variance
        )

        return round(
            float(portfolio_volatility * 100),
            2
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(self):

        stock_vol = self.stock_volatility()

        portfolio_vol = self.portfolio_volatility()

        summary = pd.DataFrame(
            [
                {
                    "Metric": "Portfolio Volatility (%)",
                    "Value": portfolio_vol
                },
                {
                    "Metric": "Average Stock Volatility (%)",
                    "Value": round(
                        stock_vol["annual_volatility"].mean() * 100,
                        2
                    )
                }
            ]
        )

        return summary