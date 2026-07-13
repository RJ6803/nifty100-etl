from src.portfolio.builder import PortfolioBuilder

builder = PortfolioBuilder()

portfolio = builder.create_equal_weight_portfolio(
    [
        "INFY",
        "TCS",
        "HAL",
        "ITC",
        "LT"
    ],
    total_investment=1000000
)

print(portfolio)