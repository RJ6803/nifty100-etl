import pandas as pd


class PortfolioMetrics:
    """
    Calculates weighted portfolio metrics.

    Expected columns:
        weight_pct
        investment_amount
        return_on_equity_pct
        pe_ratio
        pb_ratio
        revenue_cagr_5yr
        pat_cagr_5yr
        dividend_yield_pct
        composite_quality_score
    """

    def __init__(self, portfolio_df: pd.DataFrame):
        self.df = portfolio_df.copy()

        if self.df.empty:
            raise ValueError("Portfolio is empty.")

        if "weight_pct" not in self.df.columns:
            raise ValueError("weight_pct column missing.")

    # ----------------------------------------------------------
    # Internal weighted average helper
    # ----------------------------------------------------------

    def _weighted_average(self, column: str) -> float:
        if column not in self.df.columns:
            return 0.0

        data = self.df[[column, "weight_pct"]].copy()

        data[column] = pd.to_numeric(data[column], errors="coerce")
        data["weight_pct"] = pd.to_numeric(data["weight_pct"], errors="coerce")

        data = data.dropna()

        if data.empty:
            return 0.0

        total_weight = data["weight_pct"].sum()

        if total_weight == 0:
            return 0.0

        weighted_avg = (data[column] * data["weight_pct"]).sum() / total_weight

        return round(weighted_avg, 2)

    # ----------------------------------------------------------
    # Individual Metrics
    # ----------------------------------------------------------

    def total_investment(self):
        return round(self.df["investment_amount"].sum(), 2)

    def total_stocks(self):
        return len(self.df)

    def average_roe(self):
        return self._weighted_average("return_on_equity_pct")

    def average_pe(self):
        return self._weighted_average("pe_ratio")

    def average_pb(self):
        return self._weighted_average("pb_ratio")

    def revenue_cagr(self):
        return self._weighted_average("revenue_cagr_5yr")

    def pat_cagr(self):
        return self._weighted_average("pat_cagr_5yr")

    def dividend_yield(self):
        return self._weighted_average("dividend_yield_pct")

    def quality_score(self):
        return self._weighted_average("composite_quality_score")

    # ----------------------------------------------------------
    # Complete Summary
    # ----------------------------------------------------------

    def summary(self):

        summary = {
            "Total Investment": self.total_investment(),
            "Total Stocks": self.total_stocks(),
            "Weighted ROE (%)": self.average_roe(),
            "Weighted PE": self.average_pe(),
            "Weighted PB": self.average_pb(),
            "Revenue CAGR 5Y (%)": self.revenue_cagr(),
            "PAT CAGR 5Y (%)": self.pat_cagr(),
            "Dividend Yield (%)": self.dividend_yield(),
            "Portfolio Quality Score": self.quality_score(),
        }

        return pd.DataFrame(
            summary.items(),
            columns=["Metric", "Value"]
        )

    # ----------------------------------------------------------
    # Pretty Print
    # ----------------------------------------------------------

    def print_summary(self):

        print("\n")
        print("=" * 55)
        print("PORTFOLIO SUMMARY")
        print("=" * 55)

        print(f"Total Investment        : ₹{self.total_investment():,.2f}")
        print(f"Number of Stocks        : {self.total_stocks()}")

        print("-" * 55)

        print(f"Weighted ROE            : {self.average_roe():.2f}%")
        print(f"Weighted PE             : {self.average_pe():.2f}")
        print(f"Weighted PB             : {self.average_pb():.2f}")
        print(f"Revenue CAGR (5Y)       : {self.revenue_cagr():.2f}%")
        print(f"PAT CAGR (5Y)           : {self.pat_cagr():.2f}%")
        print(f"Dividend Yield          : {self.dividend_yield():.2f}%")
        print(f"Portfolio Quality Score : {self.quality_score():.2f}")

        print("=" * 55)