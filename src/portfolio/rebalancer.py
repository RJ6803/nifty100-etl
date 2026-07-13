import pandas as pd


class PortfolioRebalancer:
    """
    Portfolio Rebalancer

    Compares current portfolio weights with target weights
    and generates BUY / SELL / HOLD recommendations.
    """

    def __init__(self, portfolio_df: pd.DataFrame):

        self.df = portfolio_df.copy()

        if self.df.empty:
            raise ValueError("Portfolio is empty.")

        required_columns = [
            "company_id",
            "company_name",
            "weight_pct",
            "investment_amount",
        ]

        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Missing column: {col}")

    # ----------------------------------------------------
    # Equal Weight Target
    # ----------------------------------------------------

    def equal_weight_target(self):

        total = len(self.df)

        target = 100 / total

        target_weights = {
            cid: target
            for cid in self.df["company_id"]
        }

        return target_weights

    # ----------------------------------------------------
    # Custom Target
    # ----------------------------------------------------

    def custom_target(self, target_weights: dict):

        total = round(sum(target_weights.values()), 2)

        if total != 100:
            raise ValueError(
                f"Target weights must sum to 100. Current = {total}"
            )

        return target_weights

    # ----------------------------------------------------
    # Rebalance
    # ----------------------------------------------------

    def rebalance(
        self,
        target_weights: dict,
        tolerance: float = 0.50,
    ):

        df = self.df.copy()

        target_list = []

        actions = []

        deviations = []

        rebalance_amount = []

        total_value = df["investment_amount"].sum()

        for _, row in df.iterrows():

            cid = row["company_id"]

            current_weight = row["weight_pct"]

            target_weight = target_weights.get(
                cid,
                current_weight
            )

            deviation = round(
                target_weight - current_weight,
                2
            )

            amount = round(
                total_value * deviation / 100,
                2
            )

            if abs(deviation) <= tolerance:
                action = "HOLD"
                amount = 0.0

            elif deviation > 0:
                action = "BUY"

            else:
                action = "SELL"

            target_list.append(target_weight)
            deviations.append(deviation)
            actions.append(action)
            rebalance_amount.append(abs(amount))

        df["target_weight_pct"] = target_list

        df["weight_difference_pct"] = deviations

        df["action"] = actions

        df["rebalance_amount"] = rebalance_amount

        return df

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    @staticmethod
    def summary(rebalance_df):

        buy = rebalance_df[
            rebalance_df["action"] == "BUY"
        ]["rebalance_amount"].sum()

        sell = rebalance_df[
            rebalance_df["action"] == "SELL"
        ]["rebalance_amount"].sum()

        hold = len(
            rebalance_df[
                rebalance_df["action"] == "HOLD"
            ]
        )

        summary = {
            "Total Portfolio Value":
                round(
                    rebalance_df["investment_amount"].sum(),
                    2,
                ),

            "Total Buy":
                round(buy, 2),

            "Total Sell":
                round(sell, 2),

            "Net Cash Required":
                round(max(buy - sell, 0), 2),

            "Buy Orders":
                len(
                    rebalance_df[
                        rebalance_df["action"] == "BUY"
                    ]
                ),

            "Sell Orders":
                len(
                    rebalance_df[
                        rebalance_df["action"] == "SELL"
                    ]
                ),

            "Hold Positions":
                hold,
        }

        return pd.DataFrame(
            summary.items(),
            columns=["Metric", "Value"]
        )

    # ----------------------------------------------------
    # Pretty Print
    # ----------------------------------------------------

    @staticmethod
    def print_report(rebalance_df):

        print("\n")
        print("=" * 80)
        print("PORTFOLIO REBALANCE REPORT")
        print("=" * 80)

        print(
            rebalance_df[
                [
                    "company_id",
                    "company_name",
                    "weight_pct",
                    "target_weight_pct",
                    "weight_difference_pct",
                    "action",
                    "rebalance_amount",
                ]
            ]
        )

        print("\n")

        summary = PortfolioRebalancer.summary(
            rebalance_df
        )

        print(summary)

        print("=" * 80)