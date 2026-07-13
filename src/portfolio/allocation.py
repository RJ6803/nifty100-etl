import pandas as pd


class AllocationEngine:
    """
    Handles portfolio allocation strategies.
    """

    @staticmethod
    def equal_weight(portfolio: pd.DataFrame,
                     total_investment: float):
        """
        Allocate equal weight to every stock.
        """

        if portfolio.empty:
            raise ValueError("Portfolio is empty.")

        n = len(portfolio)

        weight = 100 / n
        amount = total_investment / n

        portfolio = portfolio.copy()

        portfolio["weight_pct"] = weight
        portfolio["investment_amount"] = amount

        return portfolio

    @staticmethod
    def custom_weight(portfolio: pd.DataFrame,
                      weights: dict,
                      total_investment: float):
        """
        Allocate custom weights.

        weights example

        {
            "INFY":30,
            "TCS":25,
            "HAL":20,
            "ITC":15,
            "LT":10
        }
        """

        portfolio = portfolio.copy()

        total_weight = sum(weights.values())

        if abs(total_weight - 100) > 0.001:
            raise ValueError(
                "Total portfolio weight must equal 100%"
            )

        portfolio["weight_pct"] = portfolio["company_id"].map(weights)

        if portfolio["weight_pct"].isna().any():
            raise ValueError(
                "Missing weight for one or more companies."
            )

        portfolio["investment_amount"] = (
            portfolio["weight_pct"] / 100
        ) * total_investment

        return portfolio