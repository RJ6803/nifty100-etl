from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv("output/capital_allocation.csv")

# Extract numeric year
df["year_num"] = (
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year_num"] = pd.to_numeric(
    df["year_num"],
    errors="coerce"
)

df = df.sort_values(
    ["company_id", "year_num"]
)

changes = []

for company, grp in df.groupby("company_id"):

    grp = grp.reset_index(drop=True)

    for i in range(1, len(grp)):

        previous = grp.loc[i - 1, "pattern_label"]
        current = grp.loc[i, "pattern_label"]

        if previous != current:

            changes.append({

                "company_id": company,

                "year": grp.loc[i, "year"],

                "previous_pattern": previous,

                "current_pattern": current

            })

changes = pd.DataFrame(changes)

changes.to_csv(
    OUTPUT_DIR / "pattern_changes.csv",
    index=False
)

print(changes.head())

print()

print("Pattern Changes Found :", len(changes))

print()

print("Saved to:")

print(OUTPUT_DIR / "pattern_changes.csv")