from src.portfolio.builder import PortfolioBuilder
from src.portfolio.risk import PortfolioRisk

builder = PortfolioBuilder()

portfolio = builder.build(
    investment_amount=1000000,
    number_of_stocks=5
)

risk = PortfolioRisk(portfolio)

print("\nPortfolio Risk Metrics\n")

print(risk.summary())