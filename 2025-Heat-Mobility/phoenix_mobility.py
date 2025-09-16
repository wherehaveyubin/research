import pandas as pd

# Set workspace path
workspace = "*/data/"

# Import raw mobility data
df_raw = pd.read_csv(
    workspace + "0 raw/mobility_phoenix/od_flow-visitor_home_cbgs-poi_cbg-Maricopa_Pinal_County-2023-01-02_2023-12-25.csv.gz",
    compression="gzip"
)
print(df_raw.head())

# Filter data for summer period (June 1 – August 28, 2023)
df_raw["date_range_start"] = pd.to_datetime(df_raw["date_range_start"])
df = df_raw[
    (df_raw["date_range_start"] >= "2023-06-01") &
    (df_raw["date_range_start"] <= "2023-08-28")
]

# Export sample (first 20 rows)
df_export = df.head(20)
df_export.to_csv(workspace + "mobility_sample.csv", index=False)

