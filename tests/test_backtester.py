from src.portfolio.builder import PortfolioBuilder
from src.portfolio.backtester import PortfolioBacktester

builder = PortfolioBuilder()

portfolio = builder.build(
    investment_amount=1000000,
    number_of_stocks=5
)

print("\nPortfolio\n")
print(portfolio)

backtester = PortfolioBacktester(portfolio)

print("\nBacktest Summary\n")
print(backtester.summary())

print("\nEquity Curve\n")
print(backtester.equity_curve().tail())