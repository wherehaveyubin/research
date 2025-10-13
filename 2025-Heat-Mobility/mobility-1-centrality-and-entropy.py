# =========================================
# 0. Import libraries
# =========================================
import pandas as pd
import geopandas as gpd
import glob
import os
import networkx as nx
from scipy.stats import linregress
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from scipy.stats import gaussian_kde
from mapclassify import JenksCaspall


# =========================================
# 1. Load mobility data
# =========================================
# Set workspace path
workspace = "*"

# Import Census Block Group shp file
cbg = gpd.read_file(workspace + "0-raw/tl_2018_04_bg/tl_2018_04_bg_Maricopa_Pinal.shp")  # 2,704 rows
cbg = cbg.drop(columns=["GEOID_int", "GEOID_in_1"], errors="ignore")
cbg = cbg[["GEOID", "geometry"]]
cbg["GEOID"] = cbg["GEOID"].str[1:]  # Remove potential prefix
valid_geoids = set(cbg["GEOID"])

# Import raw mobility dataset
df_raw = pd.read_csv(
    workspace + "0-raw/mobility_phoenix/od_flow-visitor_home_cbgs-poi_cbg-Maricopa_Pinal_County-2023-01-02_2023-12-25.csv.gz",
    compression="gzip"
) # 12,036,112 rows

df_raw = df_raw[
    df_raw["visitor_home_cbgs"].astype(str).isin(valid_geoids) &
    df_raw["poi_cbg"].astype(str).isin(valid_geoids)
].copy() # 12,036,112 rows

# Filter data for the summer period (June–August 2023)
df_raw["date_range_start"] = pd.to_datetime(df_raw["date_range_start"])
df_raw = df_raw[
    (df_raw["date_range_start"] >= "2023-06-01") &
    (df_raw["date_range_start"] <= "2023-08-28")
] # 3,351,816 rows

# Aggregate visitors by month
df_raw.loc[:, "month"] = df_raw["date_range_start"].dt.to_period("M").astype(str)
df = (
    df_raw.groupby(["month", "visitor_home_cbgs", "poi_cbg"], as_index=False)
    .agg({"visitor": "sum"})
)
df["visitor_home_cbgs"] = df["visitor_home_cbgs"].astype(str) # 1,993,151 rows
df.to_csv(workspace + "1-processed/centrality/df.csv", index=False, encoding="utf-8-sig")

del df_raw


# =========================================
# 2. Monthly Network Analysis – Temporal
# =========================================
# Calculate centrality and flow diversity for each month
def calculate_monthly_centrality(df, month):
    # Filter data by month
    df_month = df[df["month"] == month].copy()

    # Create directed graph using visitors as edge weights
    G = nx.from_pandas_edgelist(
        df_month,
        source="visitor_home_cbgs",
        target="poi_cbg",
        edge_attr="visitor",
        create_using=nx.DiGraph()
    )

    # Compute degree centrality
    degree_centrality = nx.degree_centrality(G)

    # Use only origin nodes
    origin_nodes = df_month["visitor_home_cbgs"].unique()

    # Compute flow entropy (mobility diversity)
    flow = df_month.groupby(["visitor_home_cbgs", "poi_cbg"])["visitor"].sum().reset_index()
    flow["total"] = flow.groupby("visitor_home_cbgs")["visitor"].transform("sum")
    flow["p_ij"] = flow["visitor"] / flow["total"]

    # Avoid log(0)
    flow["entropy_component"] = -flow["p_ij"] * np.where(flow["p_ij"] > 0, np.log(flow["p_ij"]), 0)

    # Aggregate entropy by origin
    entropy_home = flow.groupby("visitor_home_cbgs")["entropy_component"].sum().reset_index()
    entropy_home.columns = ["GEOID", "entropy"]

    # Count number of destinations
    dest_count = flow.groupby("visitor_home_cbgs")["poi_cbg"].nunique().reset_index()
    dest_count.columns = ["GEOID", "num_dests"]

    entropy_home = entropy_home.merge(dest_count, on="GEOID", how="left")

    # Normalize entropy by log(number of destinations)
    entropy_home["entropy_norm"] = np.where(
        entropy_home["num_dests"] > 1,
        entropy_home["entropy"] / np.log(entropy_home["num_dests"]),
        np.nan
    )

    # Combine centrality data by origin
    df_cent = pd.DataFrame({
        "GEOID": origin_nodes,
        "month": month,
        "deg_cent": [degree_centrality.get(node, np.nan) for node in origin_nodes]
    })

    # Merge entropy results (keeping NaNs)
    df_cent = df_cent.merge(entropy_home[["GEOID", "entropy", "entropy_norm"]],
                            on="GEOID", how="left")

    return df_cent


# Compute monthly centralities
df_cent_june = calculate_monthly_centrality(df, "2023-06")
df_cent_july = calculate_monthly_centrality(df, "2023-07")
df_cent_aug = calculate_monthly_centrality(df, "2023-08")

# Combine results
df_results = pd.concat([df_cent_june, df_cent_july, df_cent_aug], ignore_index=True)


# =========================================
# 3. Plot monthly distribution comparisons
# =========================================
# (1) Plot distributions
save_dir = os.path.join(workspace, "map")
os.makedirs(save_dir, exist_ok=True)

# Figure 1: Degree Centrality distribution comparison (June–August)
plt.figure(figsize=(8, 6))
months = sorted(df_results["month"].unique())

for month in months:
    subset = df_results[df_results["month"] == month]["deg_cent"].dropna()
    if subset.empty:
        print(f"⚠️ {month}: no degree centrality data — skipped")
        continue

    kde = gaussian_kde(subset)
    x_vals = np.linspace(subset.min(), subset.max(), 500)
    y_vals = kde(x_vals)
    plt.plot(x_vals, y_vals, linewidth=2, label=f"{month}")

plt.xlabel("Degree Centrality")
plt.ylabel("Density")
plt.title("Degree Centrality Distribution (June–August 2023)")
plt.legend(title="Month")
plt.grid(True)

save_path1 = os.path.join(save_dir, "Figure1_degree_centrality_comparison.png")
plt.savefig(save_path1, dpi=300, bbox_inches="tight")
plt.close()
print(f"✅ Figure 1 saved → {save_path1}")

# Figure 2: Normalized Entropy distribution comparison (June–August)
plt.figure(figsize=(8, 6))

for month in months:
    subset = df_results[df_results["month"] == month]["entropy_norm"].dropna()
    if subset.empty:
        print(f"⚠️ {month}: no entropy data — skipped")
        continue

    kde = gaussian_kde(subset)
    x_vals = np.linspace(subset.min(), subset.max(), 500)
    y_vals = kde(x_vals)
    plt.plot(x_vals, y_vals, linewidth=2, label=f"{month}")

plt.xlabel("Normalized Entropy (Flow Diversity)")
plt.ylabel("Density")
plt.title("Flow Diversity (Entropy) Distribution (June–August 2023)")
plt.legend(title="Month")
plt.grid(True)

save_path2 = os.path.join(save_dir, "Figure2_entropy_comparison.png")
plt.savefig(save_path2, dpi=300, bbox_inches="tight")
plt.close()
print(f"✅ Figure 2 saved → {save_path2}")


# (2) Reshape results into wide format
# Extract month (MM) from YYYY-MM
df_results["month_str"] = df_results["month"].str[-2:]

# Pivot to wide format
df_wide = df_results.pivot_table(
    index="GEOID",
    columns="month_str",
    values=["deg_cent", "entropy", "entropy_norm"]
)

# Flatten multi-level column names
df_wide.columns = [f"{var}_{month}" for var, month in df_wide.columns]

# Restore index as column
df_wide = df_wide.reset_index()

# Preview
print(df_wide.head())


# (3) Jenks natural breaks calculation
deg_all = df_wide[[c for c in df_wide.columns if "deg_cent" in c]].values.flatten()
ent_all = df_wide[[c for c in df_wide.columns if "entropy_norm" in c]].values.flatten()

# Remove NaNs
deg_all = deg_all[~np.isnan(deg_all)]
ent_all = ent_all[~np.isnan(ent_all)]

# Compute min/max
deg_min, deg_max = deg_all.min(), deg_all.max()
ent_min, ent_max = ent_all.min(), ent_all.max()

print("Degree Centrality:", deg_min, deg_max)
print("Entropy:", ent_min, ent_max)

# Jenks natural breaks (5 classes)
jenks_deg = JenksCaspall(deg_all, k=5).bins
jenks_ent = JenksCaspall(ent_all, k=5).bins

print("Jenks breaks — Degree Centrality:", jenks_deg)
print("Jenks breaks — Entropy:", jenks_ent)


# (4) Merge with shapefile and export
# Merge spatial geometry with centrality results
cbg_with_centrality = cbg.merge(df_wide, on="GEOID", how="left")

# Export as GeoPackage
output_path_centrality = os.path.join(workspace, "1-processed", "centrality", "cbg_with_centrality.gpkg")
cbg_with_centrality.to_file(output_path_centrality, layer="centrality", driver="GPKG", encoding="utf-8")

print(f"✅ GeoPackage saved → {output_path_centrality}")
