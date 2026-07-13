from src.portfolio.builder import PortfolioBuilder
from src.portfolio.metrics import PortfolioMetrics

builder = PortfolioBuilder()

portfolio = builder.build_equal_weight_portfolio(
    amount=1000000,
    top_n=5
)

metrics = PortfolioMetrics(portfolio)

metrics.print_summary()

print("\nSummary DataFrame:\n")
print(metrics.summary())