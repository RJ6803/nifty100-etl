import pandas as pd

print("=" * 80)
print("BALANCE SHEET - BEL")
print("=" * 80)

bs = pd.read_excel(
    "data/raw/balancesheet.xlsx",
    header=1
)

print(bs[bs.iloc[:, 1] == "BEL"].head(15))

print("\n")

print("=" * 80)
print("PROFIT & LOSS - BEL")
print("=" * 80)

pl = pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)

print(pl[pl.iloc[:, 1] == "BEL"].head(15))