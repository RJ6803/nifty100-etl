import numpy as np
import pandas as pd


class PortfolioRisk:

    def __init__(self, portfolio: pd.DataFrame):
        self.portfolio = portfolio.copy()

    # --------------------------------------------------
    # Simulated historical returns
    # --------------------------------------------------
    def generate_returns(self, periods=252, seed=42):

        np.random.seed(seed)

        returns = {}

        for _, row in self.portfolio.iterrows():

            symbol = row["company_id"]

            expected_return = row.get("pat_cagr_5yr", 10) / 100

            daily_mean = expected_return / 252

            daily_std = 0.02

            returns[symbol] = np.random.normal(
                daily_mean,
                daily_std,
                periods
            )

        return pd.DataFrame(returns)

    # --------------------------------------------------
    # Portfolio Daily Returns
    # --------------------------------------------------
    def portfolio_returns(self):

        returns = self.generate_returns()

        weights = (
            self.portfolio["weight_pct"].values / 100
        )

        portfolio_daily = returns.dot(weights)

        return portfolio_daily

    # --------------------------------------------------
    # Annual Volatility
    # --------------------------------------------------
    def annual_volatility(self):

        daily = self.portfolio_returns()

        return daily.std() * np.sqrt(252)

    # --------------------------------------------------
    # Annual Return
    # --------------------------------------------------
    def annual_return(self):

        daily = self.portfolio_returns()

        return daily.mean() * 252

    # --------------------------------------------------
    # Sharpe Ratio
    # --------------------------------------------------
    def sharpe_ratio(self, risk_free_rate=0.06):

        annual_return = self.annual_return()

        volatility = self.annual_volatility()

        if volatility == 0:
            return 0

        return (
            annual_return - risk_free_rate
        ) / volatility

    # --------------------------------------------------
    # Maximum Drawdown
    # --------------------------------------------------
    def max_drawdown(self):

        returns = self.portfolio_returns()

        cumulative = (1 + returns).cumprod()

        running_max = cumulative.cummax()

        drawdown = (
            cumulative - running_max
        ) / running_max

        return drawdown.min()

    # --------------------------------------------------
    # Value at Risk (95%)
    # --------------------------------------------------
    def value_at_risk(self, confidence=0.95):

        returns = self.portfolio_returns()

        percentile = (1 - confidence) * 100

        return np.percentile(
            returns,
            percentile
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(self):

        data = {
            "Metric": [
                "Annual Return",
                "Annual Volatility",
                "Sharpe Ratio",
                "Maximum Drawdown",
                "Value at Risk (95%)",
            ],
            "Value": [
                round(self.annual_return() * 100, 2),
                round(self.annual_volatility() * 100, 2),
                round(self.sharpe_ratio(), 2),
                round(self.max_drawdown() * 100, 2),
                round(self.value_at_risk() * 100, 2),
            ],
        }

        return pd.DataFrame(data)