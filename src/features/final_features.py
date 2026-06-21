import pandas as pd

# Load previous outputs

kpi_df = pd.read_csv("src/features/company_kpis.csv")
growth_df = pd.read_csv("src/features/company_growth.csv")

# Merge datasets

final_df = kpi_df.merge(
growth_df,
on="company_id",
how="left"
)

# Additional Features

# Return on Assets

final_df["roa"] = (
final_df["net_profit"] /
final_df["total_assets"]
) * 100

# Earnings Yield

final_df["earnings_yield"] = (
final_df["eps"] /
final_df["sales"]
) * 100

# Operating Margin Ratio

final_df["operating_margin_ratio"] = (
final_df["opm_percentage"]
)

# Save final feature dataset

final_df.to_csv(
"src/features/final_company_features.csv",
index=False
)

print(final_df.head())
print("\nfinal_company_features.csv created successfully!")
