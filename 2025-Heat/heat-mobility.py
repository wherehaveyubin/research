import pandas as pd
import geopandas as gpd
import glob
import os
from tqdm import tqdm
from shapely.geometry import Point
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

workspace = "D:/heat-mobility/data/"

# =====================================================================
# Import raw data and preprocessing
# =====================================================================
# Import tract boundary shp file
tract_boundary = gpd.read_file(workspace + "boundary/tl_2024_36_tract/tl_2024_36_tract.shp") # 5,411 rows
tract_boundary = tract_boundary[
    tract_boundary['GEOID'].str.startswith(('360050', '360470', '360471', '360610', '360810'))] # 2,091 rows
tract_boundary.to_crs(epsg=4326, inplace=True)

# Import weather data
weather = pd.read_csv("D:/heat/data/2022_2024_summer_heat_index.csv") # 8,541 rows
weather['DATE'] = pd.to_datetime(weather['DATE'])
weather = weather.sort_values('DATE')

# Import citibike data
folder_path = r"D:\heat-mobility\data\citibike"
csv_files = glob.glob(os.path.join(folder_path, "**", "*.csv"), recursive=True)

od_records = []
for file in tqdm(csv_files, desc="Processing files"):
    try:
        # Read and parse datetime
        df = pd.read_csv(file, low_memory=False)
        df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
        df['ended_at'] = pd.to_datetime(df['ended_at'], errors='coerce')

        # Drop missing critical fields
        df = df.dropna(subset=[
            'start_lat', 'start_lng', 'end_lat', 'end_lng',
            'started_at', 'ended_at'
        ])

        # Filter summer periods (2022–2024)
        df = df[
            ((df['started_at'] >= '2022-06-01') & (df['ended_at'] <= '2022-08-31')) |
            ((df['started_at'] >= '2023-06-01') & (df['ended_at'] <= '2023-08-31')) |
            ((df['started_at'] >= '2024-06-01') & (df['ended_at'] <= '2024-08-31'))
        ]
        if df.empty:
            continue

        # Weather merge (asof requires sort)
        df = df.sort_values('started_at')
        df = pd.merge_asof(
            df,
            weather[['DATE', 'heat_index', 'is_heat']],
            left_on='started_at',
            right_on='DATE',
            direction='nearest'
        )

        # Extract date and hour
        df['date'] = df['started_at'].dt.date
        df['hour'] = df['started_at'].dt.hour

        # Create GeoDataFrames
        gdf_start = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['start_lng'], df['start_lat']),
            crs='EPSG:4326'
        )
        gdf_end = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['end_lng'], df['end_lat']),
            crs='EPSG:4326'
        )

        # Spatial join with GEOIDFQ
        gdf_start = gpd.sjoin(gdf_start, tract_boundary[['GEOIDFQ', 'geometry']], how='left', predicate='intersects')
        gdf_end = gpd.sjoin(gdf_end, tract_boundary[['GEOIDFQ', 'geometry']], how='left', predicate='intersects')

        # Assign tract IDs
        df = df.assign(
            start_GEOIDFQ=gdf_start['GEOIDFQ'].values,
            end_GEOIDFQ=gdf_end['GEOIDFQ'].values
        ).dropna(subset=['start_GEOIDFQ', 'end_GEOIDFQ'])

        # Group by OD, date, hour
        od_group = df.groupby(
            ['start_GEOIDFQ', 'end_GEOIDFQ', 'date', 'hour']
        ).agg(
            trip_count=('start_GEOIDFQ', 'size'),
            heat_index=('heat_index', 'max'),
            is_heat=('is_heat', 'max')
        ).reset_index()

        od_records.append(od_group)

    except Exception as e:
        print(f"❌ Error in file {file}: {e}")

# Final aggregation of OD + time across all files
edge_df = pd.concat(od_records, ignore_index=True).groupby(
    ['start_GEOIDFQ', 'end_GEOIDFQ', 'date', 'hour']
).agg(
    trip_count=('trip_count', 'sum'),
    heat_index=('heat_index', 'max'),
    is_heat=('is_heat', 'max')
).reset_index()

# Save result
edge_df.to_csv(os.path.join(workspace, "edge_df.csv"), index=False)
del od_group
del od_records

edge_df.to_csv(workspace + "edge_df.csv") # 22,662,046 rows

# =====================================================================
# Mobility analysis – degree centrality
# =====================================================================
#edge_df = pd.read_csv(workspace + "edge_df.csv")

# Filter edges by heat condition
edge_normal = edge_df[edge_df["is_heat"] == 0]
edge_heat = edge_df[edge_df["is_heat"] == 1]

# Function to build directed graph from edge DataFrame
def build_graph(df, desc="Building Graph"):
    G = nx.DiGraph()
    for _, row in tqdm(df.iterrows(), total=len(df), desc=desc):
        G.add_edge(row["start_GEOIDFQ"], row["end_GEOIDFQ"])
    return G

# Create graphs for normal and heat days
G_normal = build_graph(edge_normal)
G_heat = build_graph(edge_heat)

# Function to compute degree centrality
def compute_degree_centrality(G, label):
    deg = nx.degree_centrality(G)
    return pd.DataFrame({
        "start_GEOIDFQ": list(deg.keys()),
        f"degree_{label}": list(deg.values())
    })

# Compute centrality for each graph
df_deg_normal = compute_degree_centrality(G_normal, "normal")
df_deg_heat = compute_degree_centrality(G_heat, "heat")

# Merge centrality values with tract geometries
gdf_normal = pd.merge(tract_boundary, df_deg_normal, left_on='GEOIDFQ', right_on="start_GEOIDFQ", how="right")
gdf_heat = pd.merge(tract_boundary, df_deg_heat, left_on='GEOIDFQ', right_on="start_GEOIDFQ", how="right")

# Set common color scale range
vmin = min(
    gdf_normal["degree_normal"].min(),
    gdf_heat["degree_heat"].min()
)
vmax = max(
    gdf_normal["degree_normal"].max(),
    gdf_heat["degree_heat"].max()
)

# Create subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 7))

# Define shared color scale
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
cmap = plt.cm.YlOrRd

# Plot: Normal Days
tract_boundary.plot(ax=axes[0], facecolor='none', edgecolor='lightgray', linewidth=0.5)  # base layer: tract outlines
gdf_normal.plot(column="degree_normal", cmap=cmap, linewidth=0.5, edgecolor='none',
                ax=axes[0], norm=norm)
axes[0].set_title("Degree Centrality (Normal Days)")
axes[0].axis("off")

# Plot: Heat Days
tract_boundary.plot(ax=axes[1], facecolor='none', edgecolor='lightgray', linewidth=0.5)  # base layer: tract outlines
gdf_heat.plot(column="degree_heat", cmap=cmap, linewidth=0.5, edgecolor='none',
              ax=axes[1], norm=norm)
axes[1].set_title("Degree Centrality (Heat Days)")
axes[1].axis("off")

# Adjust layout spacing and reserve space for colorbar
fig.subplots_adjust(right=0.85, wspace=0.05)

# Add shared colorbar
cbar_ax = fig.add_axes([0.88, 0.25, 0.015, 0.5])  # [left, bottom, width, height]
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm._A = []
fig.colorbar(sm, cax=cbar_ax, label="Degree Centrality")

plt.show()
plt.savefig('D:/heat-mobility/map/Degree centrality.png', bbox_inches='tight')
