from src.portfolio.builder import PortfolioBuilder
from src.portfolio.rebalancer import PortfolioRebalancer

# ----------------------------------------------------
# Build Portfolio
# ----------------------------------------------------

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

print("\nCurrent Portfolio\n")
print(portfolio)

# ----------------------------------------------------
# Equal Weight Rebalancing
# ----------------------------------------------------

rebalancer = PortfolioRebalancer(portfolio)

targets = rebalancer.equal_weight_target()

rebalance_df = rebalancer.rebalance(targets)

print("\nEqual Weight Rebalance\n")

PortfolioRebalancer.print_report(rebalance_df)


# Custom Weight Rebalancing


custom_targets = {
    "HAL": 30,
    "INFY": 25,
    "ITC": 15,
    "LT": 10,
    "TCS": 20,
}

rebalance_df = rebalancer.rebalance(custom_targets)

print("\nCustom Weight Rebalance\n")

PortfolioRebalancer.print_report(rebalance_df)