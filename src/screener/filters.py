import pandas as pd
import numpy as np


class StockFilter:

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def roe(self, minimum=15):
        self.df = self.df[
            self.df["return_on_equity_pct"] >= minimum
        ]
        return self

    def debt_to_equity(self, maximum=1):

        financials = self.df[
            self.df["broad_sector"] == "Financials"
        ]

        non_financials = self.df[
            self.df["broad_sector"] != "Financials"
        ]

        non_financials = non_financials[
            non_financials["debt_to_equity"] <= maximum
        ]

        self.df = pd.concat(
            [non_financials, financials],
            ignore_index=True
        )

        print(
            f"Debt/Equity filter applied only to non-financial companies (max={maximum}). "
            f"Financial companies skipped."
        )

        return self

    def revenue_cagr(self, minimum=10):
        self.df = self.df[
            self.df["revenue_cagr_5yr"] >= minimum
        ]
        return self

    def profit_margin(self, minimum=10):
        self.df = self.df[
            self.df["net_profit_margin_pct"] >= minimum
        ]
        return self

    def free_cash_flow(self):
        self.df = self.df[
            self.df["free_cash_flow_cr"] > 0
        ]
        return self

    def roce(self, minimum=15):
        self.df = self.df[
            self.df["roce_percentage"] >= minimum
        ]
        return self

    def pe(self, maximum=40):
        self.df = self.df[
            self.df["pe_ratio"] <= maximum
        ]
        return self

    def pb(self, maximum=10):
        self.df = self.df[
            self.df["pb_ratio"] <= maximum
        ]
        return self

    def market_cap(self, minimum=10000):
        self.df = self.df[
            self.df["market_cap_crore"] >= minimum
        ]
        return self

    def sector(self, sector_name):
        self.df = self.df[
            self.df["broad_sector"] == sector_name
        ]
        return self

    def custom(self, column, operator, value):

        if operator == ">":
            self.df = self.df[self.df[column] > value]

        elif operator == ">=":
            self.df = self.df[self.df[column] >= value]

        elif operator == "<":
            self.df = self.df[self.df[column] < value]

        elif operator == "<=":
            self.df = self.df[self.df[column] <= value]

        elif operator == "==":
            self.df = self.df[self.df[column] == value]

        return self

    def get(self):
        return self.df.reset_index(drop=True)

    def operating_profit_margin(self, minimum):
        self.df = self.df[
            self.df["operating_profit_margin_pct"] >= minimum
        ]
        return self

    def net_profit(self, minimum):
        self.df = self.df[
            self.df["net_profit"] >= minimum
        ]
        return self

    def eps_cagr(self, minimum):
        self.df = self.df[
            self.df["eps_cagr_5yr"] >= minimum
        ]
        return self
    
    def asset_turnover(self, minimum):
        self.df = self.df[
            self.df["asset_turnover"] >= minimum
        ]
        return self
    
    def sales(self, minimum):
        self.df = self.df[
            self.df["sales"] >= minimum
        ]
        return self
    
    def pat_cagr(self, minimum):
        self.df = self.df[
            self.df["pat_cagr_5yr"] >= minimum
        ]
        return self
    
    def debt_to_equity_exact(self, value):
        self.df = self.df[self.df["debt_to_equity"] == value]
        return self
    
    def dividend_yield(self, minimum):
        self.df = self.df[
            self.df["dividend_yield_pct"] >= minimum
        ]
        return self
    
    def interest_coverage(self, minimum):

        icr = self.df["interest_coverage"].copy()

        # Convert "Debt Free" to infinity
        icr = icr.replace("Debt Free", np.inf)

        # Convert everything else to numeric
        icr = pd.to_numeric(icr, errors="coerce")

        self.df = self.df[
            icr >= minimum
        ]

        return self
    
    def dividend_payout(self, maximum):
        self.df = self.df[
            self.df["dividend_payout_ratio_pct"] <= maximum
        ]
        return self
    
    def debt_declining(self):

        self.df = self.df[
            self.df["debt_declining"] == True
        ]

        return self

