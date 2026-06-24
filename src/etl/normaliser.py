import re

def normalize_year(year):

    year = str(year).strip()

    # FY22 -> 2022
    if year.startswith("FY"):
        return int("20" + year.replace("FY", ""))

    # 2021-22 -> 2022
    if re.match(r"\d{4}-\d{2}$", year):
        return int("20" + year[-2:])

    # Dec 2012 -> 2012
    match = re.search(r"(20\d{2})", year)
    if match:
        return int(match.group(1))

    # 2022
    if year.isdigit():
        return int(year)

    return None


def normalize_ticker(ticker):
    """
    Normalize ticker symbols.
    """
    return str(ticker).upper().replace(".NS", "").strip()