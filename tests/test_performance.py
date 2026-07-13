from src.portfolio.builder import PortfolioBuilder
from src.portfolio.performance import PortfolioPerformance

# -----------------------------------------------------
# Build Portfolio
# -----------------------------------------------------

builder = PortfolioBuilder()

portfolio = builder.create_equal_weight_portfolio(
    [
        "HAL",
        "INFY",
        "ITC",
        "LT",
        "TCS",
    ],
    total_investment=1_000_000,
)

print("\nPortfolio\n")
print(portfolio.to_string(index=False))

# -----------------------------------------------------
# Simulated Market Returns
# -----------------------------------------------------

market_returns = {
    "HAL": 25,
    "INFY": 8,
    "ITC": -5,
    "LT": 15,
    "TCS": 12,
}

performance = PortfolioPerformance(portfolio)

performance.simulate_market_value(market_returns)

performance.print_report()

print("\nSummary\n")
print(performance.summary().to_string(index=False))