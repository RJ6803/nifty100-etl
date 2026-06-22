
def test_net_profit_margin():
    sales = 1000
    profit = 200
    result = (profit / sales) * 100
    assert result == 20


def test_debt_ratio():
    borrowings = 500
    assets = 1000
    result = (borrowings / assets) * 100
    assert result == 50


def test_asset_turnover():
    sales = 1000
    assets = 500
    result = sales / assets
    assert result == 2

