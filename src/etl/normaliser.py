def normalize_year(year):
    """
    Normalize year formats to YYYY.
    """
    year = str(year)

    if "FY" in year:
        year = year.replace("FY", "")

    if "-" in year:
        year = year.split("-")[1]

    if len(year) == 2:
        year = "20" + year

    return int(year)


def normalize_ticker(ticker):
    """
    Normalize ticker symbols.
    """
    return str(ticker).upper().replace(".NS", "").strip()