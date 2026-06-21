from src.etl.loader import *
import pandas as pd

def dq01_company_id_unique(companies):
    duplicates = companies["id"].duplicated().sum()

    if duplicates > 0:
        return {
            "rule":"DQ01",
            "severity":"CRITICAL",
            "table":"companies",
            "message":f"{duplicates} duplicate IDs found"
        }

    return None

def dq02_profit_loss_pk(pl):
    duplicates = pl.duplicated().sum()

    if duplicates > 0:
        return {
            "rule":"DQ02",
            "severity":"CRITICAL",
            "table":"profitandloss",
            "message":f"{duplicates} duplicate rows"
        }

    return None

def dq03_balance_sheet_pk(bs):
    duplicates = bs.duplicated().sum()

    if duplicates > 0:
        return {
            "rule":"DQ03",
            "severity":"CRITICAL",
            "table":"balancesheet",
            "message":f"{duplicates} duplicate rows"
        }

    return None

def dq04_cashflow_pk(cf):
    duplicates = cf.duplicated(
    subset=[
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow"
    ]
    ).sum()

    if duplicates > 0:
        return {
            "rule":"DQ04",
            "severity":"CRITICAL",
            "table":"cashflow",
            "message":f"{duplicates} duplicate rows"
        }

    return None

def dq05_positive_sales(pl):
    failures = pl[pl["sales"] < 0]

    if len(failures):
        return {
            "rule":"DQ05",
            "severity":"WARNING",
            "table":"profitandloss",
            "message":f"{len(failures)} negative sales rows"
        }

    return None

def dq06_opm_range(pl):
    failures = pl[
        (pl["opm_percentage"] < -100) |
        (pl["opm_percentage"] > 100)
    ]

    if len(failures):
        return {
            "rule":"DQ06",
            "severity":"WARNING",
            "table":"profitandloss",
            "message":f"{len(failures)} invalid OPM values"
        }

    return None

def dq07_eps_not_null(pl):
    failures = pl["eps"].isna().sum()

    if failures:
        return {
            "rule":"DQ07",
            "severity":"WARNING",
            "table":"profitandloss",
            "message":f"{failures} missing EPS values"
        }

    return None

def dq08_sales_not_null(pl):
    failures = pl["sales"].isna().sum()

    if failures:
        return {
            "rule":"DQ08",
            "severity":"WARNING",
            "table":"profitandloss",
            "message":f"{failures} missing sales values"
        }

    return None

def dq09_positive_assets(bs):
    failures = bs[bs["total_assets"] < 0]

    if len(failures):
        return {
            "rule":"DQ09",
            "severity":"WARNING",
            "table":"balancesheet",
            "message":f"{len(failures)} negative assets"
        }

    return None

def dq10_positive_liabilities(bs):
    failures = bs[bs["total_liabilities"] < 0]

    if len(failures):
        return {
            "rule":"DQ10",
            "severity":"WARNING",
            "table":"balancesheet",
            "message":f"{len(failures)} negative liabilities"
        }

    return None

def dq11_cashflow_not_null(cf):
    failures = cf["net_cash_flow"].isna().sum()

    if failures:
        return {
            "rule":"DQ11",
            "severity":"WARNING",
            "table":"cashflow",
            "message":f"{failures} missing cash flow values"
        }

    return None

def dq12_close_price_positive(sp):
    failures = sp[sp["close_price"] <= 0]

    if len(failures):
        return {
            "rule":"DQ12",
            "severity":"WARNING",
            "table":"stock_prices",
            "message":f"{len(failures)} invalid close prices"
        }

    return None

def dq13_volume_positive(sp):
    failures = sp[sp["volume"] < 0]

    if len(failures):
        return {
            "rule":"DQ13",
            "severity":"WARNING",
            "table":"stock_prices",
            "message":f"{len(failures)} negative volume rows"
        }

    return None

def dq14_company_fk(pl, companies):
    missing = ~pl["company_id"].isin(companies["id"])

    failures = missing.sum()

    if failures:
        return {
            "rule":"DQ14",
            "severity":"CRITICAL",
            "table":"profitandloss",
            "message":f"{failures} invalid company ids"
        }

    return None

def dq15_year_range(pl):

    year_numeric = pd.to_numeric(pl["year"], errors="coerce")

    failures = pl[
        (year_numeric < 2010) |
        (year_numeric > 2030)
    ]

    if len(failures):
        return {
            "rule":"DQ15",
            "severity":"WARNING",
            "table":"profitandloss",
            "message":f"{len(failures)} invalid years"
        }

    return None

def dq16_company_name_not_null(companies):
    failures = companies["company_name"].isna().sum()

    if failures:
        return {
            "rule":"DQ16",
            "severity":"WARNING",
            "table":"companies",
            "message":f"{failures} missing company names"
        }

    return None





companies = load_companies()
pl = load_profitandloss()
bs = load_balancesheet()
cf = load_cashflow()
sp = load_stock_prices()



results = []

for rule in [
    dq01_company_id_unique(companies),
    dq02_profit_loss_pk(pl),
    dq03_balance_sheet_pk(bs),
    dq04_cashflow_pk(cf),
    dq05_positive_sales(pl),
    dq06_opm_range(pl),
    dq07_eps_not_null(pl),
    dq08_sales_not_null(pl),
    dq09_positive_assets(bs),
    dq10_positive_liabilities(bs),
    dq11_cashflow_not_null(cf),
    dq12_close_price_positive(sp),
    dq13_volume_positive(sp),
    dq14_company_fk(pl, companies),
    dq15_year_range(pl),
    dq16_company_name_not_null(companies)
]:
    if rule:
        results.append(rule)




validation_report = pd.DataFrame(results)

validation_report.to_csv(
    "output/validation_failures.csv",
    index=False
)

print(validation_report)