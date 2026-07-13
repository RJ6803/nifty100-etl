import numpy as np
import pandas as pd


class PortfolioBacktester:
    """
    Backtests a portfolio using historical (or simulated) returns.
    """

    def __init__(self, portfolio_df):
        self.portfolio = portfolio_df.copy()

    # --------------------------------------------------
    # Generate simulated daily returns
    # --------------------------------------------------
    def generate_returns(self, periods=252, seed=42):

        np.random.seed(seed)

        returns = {}

        for _, row in self.portfolio.iterrows():

            company = row["company_id"]

            expected_return = (
                row.get("pat_cagr_5yr", 10) / 100
            )

            daily_mean = expected_return / 252

            daily_std = 0.02

            returns[company] = np.random.normal(
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

        return returns.dot(weights)

    # --------------------------------------------------
    # Equity Curve
    # --------------------------------------------------
    def equity_curve(
        self,
        initial_investment=1000000
    ):

        portfolio_returns = self.portfolio_returns()

        equity = (
            1 + portfolio_returns
        ).cumprod()

        equity *= initial_investment

        return equity

    # --------------------------------------------------
    # CAGR
    # --------------------------------------------------
    def cagr(self):

        equity = self.equity_curve()

        years = len(equity) / 252

        start = equity.iloc[0]
        end = equity.iloc[-1]

        return (
            (end / start) ** (1 / years)
        ) - 1

    # --------------------------------------------------
    # Annual Return
    # --------------------------------------------------
    def annual_return(self):

        return (
            self.portfolio_returns().mean()
            * 252
        )

    # --------------------------------------------------
    # Annual Volatility
    # --------------------------------------------------
    def annual_volatility(self):

        return (
            self.portfolio_returns().std()
            * np.sqrt(252)
        )

    # --------------------------------------------------
    # Sharpe Ratio
    # --------------------------------------------------
    def sharpe_ratio(
        self,
        risk_free_rate=0.06
    ):

        vol = self.annual_volatility()

        if vol == 0:
            return 0

        return (
            self.annual_return() - risk_free_rate
        ) / vol

    # --------------------------------------------------
    # Maximum Drawdown
    # --------------------------------------------------
    def max_drawdown(self):

        equity = self.equity_curve()

        running_max = equity.cummax()

        drawdown = (
            equity - running_max
        ) / running_max

        return drawdown.min()

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    def summary(
        self,
        initial_investment=1000000
    ):

        equity = self.equity_curve(
            initial_investment
        )

        return pd.DataFrame(
            [
                {
                    "Metric": "Initial Investment",
                    "Value": initial_investment,
                },
                {
                    "Metric": "Final Portfolio Value",
                    "Value": round(
                        equity.iloc[-1],
                        2,
                    ),
                },
                {
                    "Metric": "Total Profit",
                    "Value": round(
                        equity.iloc[-1]
                        - initial_investment,
                        2,
                    ),
                },
                {
                    "Metric": "CAGR (%)",
                    "Value": round(
                        self.cagr() * 100,
                        2,
                    ),
                },
                {
                    "Metric": "Annual Return (%)",
                    "Value": round(
                        self.annual_return() * 100,
                        2,
                    ),
                },
                {
                    "Metric": "Annual Volatility (%)",
                    "Value": round(
                        self.annual_volatility() * 100,
                        2,
                    ),
                },
                {
                    "Metric": "Sharpe Ratio",
                    "Value": round(
                        self.sharpe_ratio(),
                        2,
                    ),
                },
                {
                    "Metric": "Maximum Drawdown (%)",
                    "Value": round(
                        self.max_drawdown() * 100,
                        2,
                    ),
                },
            ]
        )