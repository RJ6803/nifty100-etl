import re

def normalize_year(year):
    """
    Convert various year formats into YYYY integer.
    Examples:
    FY22       -> 2022
    22         -> 2022
    Dec 2012   -> 2012
    Mar 2023   -> 2023
    2021       -> 2021
    """

    year = str(year).strip()

    # FY22 -> 22
    year = year.replace("FY", "")

    # Search for a 4-digit year
    match = re.search(r"\d{4}", year)

    if match:
        return int(match.group())

    # Handle two-digit years
    match = re.search(r"\d{2}", year)

    if match:
        return int("20" + match.group())

    return None


def normalize_ticker(ticker):
    """
    Normalize ticker symbols.
    """
    return str(ticker).upper().replace(".NS", "").strip()