
def test_sales_cagr():
    first = 100
    last = 200
    years = 2

    cagr = (((last/first)**(1/years))-1)*100
    assert round(cagr,2) == 41.42


def test_profit_cagr():
    first = 50
    last = 100
    years = 2

    cagr = (((last/first)**(1/years))-1)*100
    assert round(cagr,2) == 41.42

