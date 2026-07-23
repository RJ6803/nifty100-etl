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

# Latest record for each company
latest = (
    df.sort_values(["company_id", "year_num"])
      .groupby("company_id")
      .tail(1)
)

summary = (
    latest["pattern_label"]
    .value_counts()
    .rename_axis("capital_allocation_pattern")
    .reset_index(name="company_count")
)

summary.to_csv(
    OUTPUT_DIR / "capital_allocation_distribution.csv",
    index=False
)

print(summary)

print("\nSaved:")
print(OUTPUT_DIR / "capital_allocation_distribution.csv")