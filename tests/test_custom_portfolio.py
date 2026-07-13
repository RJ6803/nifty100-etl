from src.portfolio.builder import PortfolioBuilder
from src.portfolio.allocation import AllocationEngine

builder = PortfolioBuilder()

portfolio = builder.df[
    builder.df["company_id"].isin(
        ["INFY", "TCS", "HAL", "ITC", "LT"]
    )
]

weights = {
    "INFY": 30,
    "TCS": 25,
    "HAL": 20,
    "ITC": 15,
    "LT": 10
}

portfolio = AllocationEngine.custom_weight(
    portfolio,
    weights,
    1000000
)

print(
    portfolio[
        [
            "company_id",
            "weight_pct",
            "investment_amount"
        ]
    ]
)