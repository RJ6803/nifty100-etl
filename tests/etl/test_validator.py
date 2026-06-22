
import pandas as pd
from src.etl.validator import *


def test_dq01():
    companies = pd.DataFrame({"id":[1,2,3]})
    assert dq01_company_id_unique(companies) is None


def test_dq02():
    pl = pd.DataFrame({"a":[1,2,3]})
    assert dq02_profit_loss_pk(pl) is None


def test_dq03():
    bs = pd.DataFrame({"a":[1,2,3]})
    assert dq03_balance_sheet_pk(bs) is None


def test_dq04():
    cf = pd.DataFrame({
        "company_id":[1],
        "year":[2022],
        "operating_activity":[1],
        "investing_activity":[1],
        "financing_activity":[1],
        "net_cash_flow":[1]
    })
    assert dq04_cashflow_pk(cf) is None


def test_dq05():
    pl = pd.DataFrame({"sales":[100]})
    assert dq05_positive_sales(pl) is None


def test_dq06():
    pl = pd.DataFrame({"opm_percentage":[20]})
    assert dq06_opm_range(pl) is None


def test_dq07():
    pl = pd.DataFrame({"eps":[10]})
    assert dq07_eps_not_null(pl) is None


def test_dq08():
    pl = pd.DataFrame({"sales":[100]})
    assert dq08_sales_not_null(pl) is None


def test_dq09():
    bs = pd.DataFrame({"total_assets":[1000]})
    assert dq09_positive_assets(bs) is None


def test_dq10():
    bs = pd.DataFrame({"total_liabilities":[1000]})
    assert dq10_positive_liabilities(bs) is None


def test_dq11():
    cf = pd.DataFrame({"net_cash_flow":[100]})
    assert dq11_cashflow_not_null(cf) is None


def test_dq12():
    sp = pd.DataFrame({"close_price":[500]})
    assert dq12_close_price_positive(sp) is None


def test_dq13():
    sp = pd.DataFrame({"volume":[10000]})
    assert dq13_volume_positive(sp) is None


def test_dq14():
    companies = pd.DataFrame({"id":[1]})
    pl = pd.DataFrame({"company_id":[1]})
    assert dq14_company_fk(pl, companies) is None


def test_dq15():
    pl = pd.DataFrame({"year":[2022]})
    assert dq15_year_range(pl) is None


def test_dq16():
    companies = pd.DataFrame({"company_name":["TCS"]})
    assert dq16_company_name_not_null(companies) is None

