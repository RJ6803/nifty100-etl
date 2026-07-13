from src.portfolio.builder import PortfolioBuilder
from src.portfolio.metrics import PortfolioMetrics
from src.portfolio.export import PortfolioExporter


# Build Portfolio

builder = PortfolioBuilder()

portfolio = builder.create_equal_weight_portfolio(
    company_ids=[
        "INFY",
        "TCS",
        "HAL",
        "ITC",
        "LT",
    ],
    total_investment=1_000_000,
)

print("\nPortfolio\n")
print(portfolio)

# Calculate Metrics

metrics = PortfolioMetrics(portfolio)

metrics.print_summary()

summary_df = metrics.summary()

print("\nSummary DataFrame\n")
print(summary_df)


# Export

exporter = PortfolioExporter()

exporter.export(
    portfolio_df=portfolio,
    metrics=dict(
        zip(summary_df["Metric"], summary_df["Value"])
    ),
    filename="Portfolio_Report.xlsx",
)