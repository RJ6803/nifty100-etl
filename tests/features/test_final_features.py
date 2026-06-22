
def test_roa():
    profit = 100
    assets = 1000
    assert (profit/assets)*100 == 10


def test_earnings_yield():
    eps = 10
    sales = 100
    assert (eps/sales)*100 == 10


def test_operating_margin_ratio():
    opm = 25
    assert opm == 25
