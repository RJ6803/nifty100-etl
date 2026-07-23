import pandas as pd

RAW_PATH = "data/raw/"

def load_excel(filename):
    return pd.read_excel(
        RAW_PATH + filename,
        skiprows=1
    )

def load_companies():
    return load_excel("companies.xlsx")

def load_profitandloss():
    return pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)

def load_balancesheet():
    return pd.read_excel(
    "data/raw/balancesheet.xlsx",
    header=1
)

def load_cashflow():
    cf = pd.read_excel(
        "data/raw/cashflow.xlsx",
        header=1
    )

    cf.columns = [
        "id",
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow"
    ]

    cf = cf.drop_duplicates(
    subset=[
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow"
    ]
)
    print("Total rows:", len(cf))
    print(cf[cf["company_id"] == "ATGL"])

    return cf

def load_analysis():
    return pd.read_excel(RAW_PATH + "analysis.xlsx")

def load_documents():
    return pd.read_excel(RAW_PATH + "documents.xlsx")

def load_financial_ratios():
    return pd.read_excel(RAW_PATH + "financial_ratios.xlsx")

def load_market_cap():
    return pd.read_excel(RAW_PATH + "market_cap.xlsx")

def load_peer_groups():
    return pd.read_excel(RAW_PATH + "peer_groups.xlsx")

def load_prosandcons():
    return pd.read_excel(RAW_PATH + "prosandcons.xlsx")

def load_sectors():
    return pd.read_excel(RAW_PATH + "sectors.xlsx")

def load_stock_prices():
    return pd.read_excel(
    "data/raw/stock_prices.xlsx",
    header=0
)