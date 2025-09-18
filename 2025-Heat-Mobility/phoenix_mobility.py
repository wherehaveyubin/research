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

# Import libraries
import pandas as pd
import geopandas as gpd

# Import LST data and create quantile groups
lst = pd.read_csv(workspace + "1 processed/aggregated_lst.csv")
lst["MEAN_GROUP"] = pd.qcut(lst["MEAN"], q=3, labels=["Low", "Median", "High"])

"""
# Example visualization
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))
sns.scatterplot(
    data=lst,
    x="COUNT",
    y="MEAN",
    hue="MEAN_GROUP",
    palette="viridis"
)
plt.title("Scatter Plot of COUNT vs MEAN grouped by MEAN_GROUP")
plt.show()
"""

# Join mobility data with LST groups
df_new = df.merge(
    lst[["GEOID", "MEAN_GROUP"]].rename(columns={"GEOID": "home_cbg", "MEAN_GROUP": "home_heat"}),
    left_on="visitor_home_cbgs",
    right_on="home_cbg",
    how="left"
)

df_new = df_new.merge(
    lst[["GEOID", "MEAN_GROUP"]].rename(columns={"GEOID": "poi_cbg", "MEAN_GROUP": "poi_heat"}),
    left_on="poi_cbg",
    right_on="poi_cbg",
    how="left"
)

df_new = df_new[
    ["home_cbg", "home_heat", "poi_cbg", "poi_heat", "date_range_start", "visitor"]
].rename(columns={"date_range_start": "date"})

# Mobility analysis
df_new["mobility"] = df_new["home_heat"].str[0] + df_new["poi_heat"].str[0]
mobility_summary = df_new.groupby("mobility")["visitor"].sum().reset_index()
print(mobility_summary)

"""
# Example plots
# Bar chart
mobility_summary.plot(kind="bar", x="mobility", y="visitor", legend=False)
plt.ylabel("Total Visitors")
plt.title("Mobility Patterns (HH, HL, LH, LL)")
plt.show()

# Pie chart
mobility_summary.set_index("mobility")["visitor"].plot(kind="pie", autopct="%.1f%%")
plt.title("Mobility Share")
plt.ylabel("")
plt.show()
"""

# Select main 4 mobility patterns (HH, HL, LH, LL)
df_four = df_new[df_new["mobility"].isin(["HH", "HL", "LH", "LL"])].copy()
tmp = (
    df_four.groupby(["home_cbg", "mobility"], as_index=False)["visitor"]
           .sum()
           .rename(columns={"visitor": "vis_sum"})
)

# Sort and select dominant mobility per home CBG
tmp_sorted = tmp.sort_values(["home_cbg", "visitor", "mobility"], ascending=[True, False, True])
home_mobility = (
    tmp_sorted.drop_duplicates(subset="home_cbg", keep="first")[["home_cbg", "mobility"]]
              .reset_index(drop=True)
)
home_mobility["home_cbg"] = home_mobility["home_cbg"].astype(str).str.split(".").str[0]

# Save results (CSV)
home_mobility.to_csv(workspace + "1 processed/mobility/home_mobility.csv", index=False)

# Import CBG shapefile and prepare for mapping
cbg = gpd.read_file(workspace + "0 raw/tl_2018_04_bg/tl_2018_04_bg_Maricopa_Pinal.shp")
cbg["home_cbg"] = cbg["GEOID"].str[1:]

home_mobility["home_cbg"] = home_mobility["home_cbg"].astype(str).str.split(".").str[0]
cbg["home_cbg"] = cbg["home_cbg"].astype(str)

# Merge dominant mobility with spatial data
gdf = cbg.merge(home_mobility, on="home_cbg", how="left")

# Save results (Shapefile)
gdf.to_file(workspace + "1 processed/mobility/home_mobility_map.shp",
            driver="ESRI Shapefile", encoding="utf-8")
