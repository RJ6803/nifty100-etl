import pandas as pd


class StockRanker:

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def quality_score(self):

        roe = self.normalize_metric("return_on_equity_pct")

        roce = self.normalize_metric("return_on_capital_employed_pct")

        npm = self.normalize_metric("net_profit_margin_pct")

        fcf = self.normalize_metric("free_cash_flow_cr")

        cfo = self.normalize_metric("cfo_pat_ratio")

        revenue = self.normalize_metric("revenue_cagr_5yr")

        pat = self.normalize_metric("pat_cagr_5yr")

        debt = self.normalize_metric(
            "debt_to_equity",
            inverse=True
        )

        icr = self.normalize_metric(
            "interest_coverage"
        )

        profitability = (
            roe * 0.15 +
            roce * 0.10 +
            npm * 0.10
        )

        cash = (
            fcf * 0.15 +
            cfo * 0.10 +
            self.df["fcf_positive_flag"].fillna(0) * 100 * 0.05
        )

        growth = (
            revenue * 0.10 +
            pat * 0.10
        )

        leverage = (
            debt * 0.10 +
            icr * 0.05
        )

        # Raw score (0–100 weighted score)

        self.df["composite_quality_score"] = (
            profitability +
            cash +
            growth +
            leverage
        ).round(2)


        # Sector-relative normalization

        def sector_normalize(series):

            minimum = series.min()
            maximum = series.max()

            if maximum == minimum:
                return pd.Series(50, index=series.index)

            return ((series - minimum) / (maximum - minimum)) * 100


        self.df["composite_quality_score"] = (

            self.df

            .groupby("broad_sector")["composite_quality_score"]

            .transform(sector_normalize)

        )

        return self

    def sort(self):

        self.df = (
            self.df
            .sort_values(
                by=[
                    "composite_quality_score",
                    "market_cap_crore"
                ],
                ascending=[False, False]
            )
            .reset_index(drop=True)
        )

        # Create rank column
        self.df["quality_rank"] = self.df.index + 1

        return self

    def top(self, n=10):
        return self.df.head(n).reset_index(drop=True)

    def get(self):
        return self.df.reset_index(drop=True)
    
    def normalize_metric(self, column, inverse=False):

        values = self.df[column].copy()

        values = pd.to_numeric(values, errors="coerce")

        p10 = values.quantile(0.10)
        p90 = values.quantile(0.90)

        values = values.clip(lower=p10, upper=p90)

        minimum = values.min()
        maximum = values.max()

        if maximum == minimum:
            score = pd.Series(50, index=values.index)

        else:
            score = ((values - minimum) / (maximum - minimum)) * 100

        if inverse:
            score = 100 - score

        return score.fillna(0)