import pandas as pd


class PortfolioPerformance:
    """
    Portfolio Performance Analytics

    Calculates:
    - Total Investment
    - Current Portfolio Value
    - Profit / Loss
    - Return %
    - Individual Stock Returns
    """

    def __init__(self, portfolio_df: pd.DataFrame):

        self.df = portfolio_df.copy()

        if self.df.empty:
            raise ValueError("Portfolio is empty.")

        required_columns = [
            "company_id",
            "company_name",
            "investment_amount",
            "market_cap_crore",
        ]

        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Missing column: {col}")

    # -----------------------------------------------------
    # Simulate Current Market Value
    # -----------------------------------------------------

    def simulate_market_value(self, return_map=None):
        """
        Simulates market returns.

        return_map example

        {
            "TCS":12,
            "INFY":8,
            "HAL":25
        }
        """

        if return_map is None:
            return_map = {}

        current_values = []
        returns = []

        for _, row in self.df.iterrows():

            company = row["company_id"]

            investment = row["investment_amount"]

            ret = return_map.get(company, 0)

            current = investment * (1 + ret / 100)

            current_values.append(round(current, 2))

            returns.append(ret)

        self.df["return_pct"] = returns
        self.df["current_value"] = current_values
        self.df["profit_loss"] = (
            self.df["current_value"]
            - self.df["investment_amount"]
        )

        return self.df

    # -----------------------------------------------------
    # Portfolio Totals
    # -----------------------------------------------------

    def total_investment(self):

        return round(
            self.df["investment_amount"].sum(),
            2,
        )

    def current_value(self):

        return round(
            self.df["current_value"].sum(),
            2,
        )

    def total_profit(self):

        return round(
            self.current_value()
            - self.total_investment(),
            2,
        )

    def total_return_pct(self):

        invested = self.total_investment()

        if invested == 0:
            return 0

        return round(
            (
                self.total_profit()
                / invested
            )
            * 100,
            2,
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    def summary(self):

        summary = {
            "Total Investment":
                self.total_investment(),

            "Current Value":
                self.current_value(),

            "Profit / Loss":
                self.total_profit(),

            "Return (%)":
                self.total_return_pct(),
        }

        return pd.DataFrame(
            summary.items(),
            columns=["Metric", "Value"],
        )

    # -----------------------------------------------------
    # Pretty Print
    # -----------------------------------------------------

    def print_report(self):

        print("\n")
        print("=" * 70)
        print("PORTFOLIO PERFORMANCE")
        print("=" * 70)

        print(
            self.df[
                [
                    "company_id",
                    "company_name",
                    "investment_amount",
                    "current_value",
                    "profit_loss",
                    "return_pct",
                ]
            ].to_string(index=False)
        )

        print("\n")

        print(self.summary().to_string(index=False))

        print("=" * 70)