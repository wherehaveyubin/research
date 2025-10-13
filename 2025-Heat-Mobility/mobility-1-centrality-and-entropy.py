import os

import pandas as pd
import geopandas as gpd
import networkx as nx

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

# Aggregate visitors
df = (
    df_raw.groupby(["visitor_home_cbgs", "poi_cbg"], as_index=False)
    .agg({"visitor": "sum"})
)
df["visitor_home_cbgs"] = df["visitor_home_cbgs"].astype(str)
df["poi_cbg"] = df["poi_cbg"].astype(str)
df.to_csv(workspace + "1-processed/centrality/df.csv", index=False, encoding="utf-8-sig") # 1,287,615 rows

del df_raw


# =========================================
# 2. Network Analysis – Summer Combined
# =========================================
# Calculate degree centrality and flow entropy for the entire summer (June–August)

def calculate_summer_centrality(df):
    # Create directed graph using visitors as edge weights
    G = nx.from_pandas_edgelist(
        df,
        source="visitor_home_cbgs",
        target="poi_cbg",
        edge_attr="visitor",
        create_using=nx.DiGraph()
    )

    # Compute degree centrality
    degree_centrality = nx.degree_centrality(G)

    # List of origin nodes
    origin_nodes = df["visitor_home_cbgs"].unique()

    # Compute flow entropy (mobility diversity)
    flow = df.groupby(["visitor_home_cbgs", "poi_cbg"])["visitor"].sum().reset_index()
    flow["total"] = flow.groupby("visitor_home_cbgs")["visitor"].transform("sum")
    flow["p_ij"] = flow["visitor"] / flow["total"]

    # Calculate entropy component: -p * log(p)
    flow["entropy_component"] = -flow["p_ij"] * np.where(flow["p_ij"] > 0, np.log(flow["p_ij"]), 0)

    # Aggregate entropy by origin CBG
    entropy_home = flow.groupby("visitor_home_cbgs")["entropy_component"].sum().reset_index()
    entropy_home.columns = ["GEOID", "entropy"]

    # Count number of unique destinations for each origin
    dest_count = flow.groupby("visitor_home_cbgs")["poi_cbg"].nunique().reset_index()
    dest_count.columns = ["GEOID", "num_dests"]

    # Merge destination counts
    entropy_home = entropy_home.merge(dest_count, on="GEOID", how="left")

    # Normalize entropy by log(number of destinations)
    entropy_home["entropy_norm"] = np.where(
        entropy_home["num_dests"] > 1,
        entropy_home["entropy"] / np.log(entropy_home["num_dests"]),
        np.nan
    )

    # Combine degree centrality and entropy results
    df_cent = pd.DataFrame({
        "GEOID": origin_nodes,
        "deg_cent": [degree_centrality.get(node, np.nan) for node in origin_nodes]
    })

    df_cent = df_cent.merge(entropy_home[["GEOID", "entropy", "entropy_norm"]],
                            on="GEOID", how="left")

    return df_cent


# Run the analysis for the summer-combined dataset
df_results = calculate_summer_centrality(df)

# Save output
output_path_centrality = os.path.join(workspace, "1-processed", "centrality", "cbg_centrality_summer.csv")
df_results.to_csv(output_path_centrality, index=False, encoding="utf-8-sig")
print(f"Centrality and entropy metrics saved to: {output_path_centrality}")


# =========================================
# 3. Distribution Analysis – Summer Combined
# =========================================
import os
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np
from mapclassify import JenksCaspall

# Create directory for figures
save_dir = os.path.join(workspace, "map")
os.makedirs(save_dir, exist_ok=True)

# (1) Plot distribution of degree centrality and normalized entropy
plt.figure(figsize=(8, 6))
subset = df_results["deg_cent"].dropna()

kde = gaussian_kde(subset)
x_vals = np.linspace(subset.min(), subset.max(), 500)
y_vals = kde(x_vals)
plt.plot(x_vals, y_vals, linewidth=2, color="steelblue")

plt.xlabel("Degree Centrality")
plt.ylabel("Density")
plt.title("Degree Centrality Distribution (June–August 2023)")
plt.grid(True)

save_path1 = os.path.join(save_dir, "Figure1_degree_centrality_summer.png")
plt.savefig(save_path1, dpi=300, bbox_inches="tight")
plt.close()
print(f"Figure 1 saved to: {save_path1}")

# Plot normalized entropy distribution
plt.figure(figsize=(8, 6))
subset = df_results["entropy_norm"].dropna()

kde = gaussian_kde(subset)
x_vals = np.linspace(subset.min(), subset.max(), 500)
y_vals = kde(x_vals)
plt.plot(x_vals, y_vals, linewidth=2, color="darkorange")

plt.xlabel("Normalized Entropy (Flow Diversity)")
plt.ylabel("Density")
plt.title("Flow Diversity (Entropy) Distribution (June–August 2023)")
plt.grid(True)

save_path2 = os.path.join(save_dir, "Figure2_entropy_summer.png")
plt.savefig(save_path2, dpi=300, bbox_inches="tight")
plt.close()
print(f"Figure 2 saved to: {save_path2}")

# (2) Merge with shapefile and export
cbg_with_centrality = cbg.merge(df_results, on="GEOID", how="left")

output_path_centrality = os.path.join(
    workspace, "1-processed", "centrality", "cbg_with_centrality_summer.gpkg"
)

cbg_with_centrality.to_file(
    output_path_centrality, layer="centrality", driver="GPKG", encoding="utf-8"
)

print(f"GeoPackage saved to: {output_path_centrality}")
