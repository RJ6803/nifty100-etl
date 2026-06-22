from src.etl.loader import *
from src.etl.normaliser import *

companies = load_companies()
profit_loss = load_profitandloss()
balance_sheet = load_balancesheet()
cashflow = load_cashflow()
stock_prices = load_stock_prices()

# normalize years
profit_loss["year"] = profit_loss["year"].apply(normalize_year)
balance_sheet["year"] = balance_sheet["year"].apply(normalize_year)
cashflow["year"] = cashflow["year"].apply(normalize_year)

# normalize tickers
stock_prices["company_id"] = stock_prices["company_id"].apply(normalize_ticker)

# save processed files
companies.to_csv("data/processed/companies_clean.csv", index=False)
profit_loss.to_csv("data/processed/profit_loss_clean.csv", index=False)
balance_sheet.to_csv("data/processed/balance_sheet_clean.csv", index=False)
cashflow.to_csv("data/processed/cashflow_clean.csv", index=False)
stock_prices.to_csv("data/processed/stock_prices_clean.csv", index=False)

print("Processed files created successfully.")