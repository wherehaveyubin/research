from tqdm import tqdm
import os
import glob
import numpy as np
import importlib
import matplotlib
import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.colors as mcolors
import community as community_louvain
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import torch
from torch_geometric.data import Data

import heat_utils
importlib.reload(heat_utils)
from heat_utils import *

workspace = "D:/heat/data/"

## Convert parguet data into csv format
# Set base folder
base_folder = os.path.join("data", "taxi", "summer")

# Find all yellow and green Parquet files based on filename
yellow_files = glob.glob(os.path.join(base_folder, "yellow*.parquet"))
green_files = glob.glob(os.path.join(base_folder, "green*.parquet"))

df_list = []

# Process yellow taxi files
for file in yellow_files:
    df = pd.read_parquet(file)

    # Standardize datetime columns
    rename_dict = {}
    if 'tpep_pickup_datetime' in df.columns:
        rename_dict['tpep_pickup_datetime'] = 'pep_pickup_datetime'
    if 'tpep_dropoff_datetime' in df.columns:
        rename_dict['tpep_dropoff_datetime'] = 'pep_dropoff_datetime'

    df = df.rename(columns=rename_dict)

    # Add yellow column
    df['yellow'] = 1
    df['green'] = 0
    df_list.append(df)

    df['yellow'] = df['yellow'].astype(int) #
    df['green'] = df['green'].astype(int) #
 
# Process green taxi files
for file in green_files:
    df = pd.read_parquet(file)
  
    # Standardize datetime columns
    rename_dict = {}
    if 'lpep_pickup_datetime' in df.columns:
        rename_dict['lpep_pickup_datetime'] = 'pep_pickup_datetime'
    if 'lpep_dropoff_datetime' in df.columns:
        rename_dict['lpep_dropoff_datetime'] = 'pep_dropoff_datetime'

    df = df.rename(columns=rename_dict)
 
    # Add green column
    df['yellow'] = 0
    df['green'] = 1
    df_list.append(df)

# Combine all data
df_all = pd.concat(df_list, ignore_index=True)

# Convert datetime column into datetime type
df_all['pep_pickup_datetime'] = pd.to_datetime(df_all['pep_pickup_datetime'], errors='coerce')
df_all['pep_dropoff_datetime'] = pd.to_datetime(df_all['pep_dropoff_datetime'], errors='coerce')
df_all = df_all[df_all['PULocationID'] != 263] # Outside of NYC
df_all = df_all[df_all['DOLocationID'] != 263] # Outside of NYC
df_all = df_all[df_all['pep_pickup_datetime'].notna()]
df_all = df_all[df_all['pep_dropoff_datetime'].notna()]
df_all = df_all[df_all['passenger_count'].notna()]


# Select summer period
df_all = df_all[
    (df_all['pep_pickup_datetime'] >= '2024-06-01') &
    (df_all['pep_pickup_datetime'] <= '2024-08-31 23:59:59')
]

# Preview
print(f"{len(df_all)} rows loaded from {len(yellow_files) + len(green_files)} files.")

# Save to CSV
output_path = os.path.join("data", "taxi", "nyc_taxi_od.csv")
df_all.to_csv(output_path, index=False)
print(f"CSV saved to: {output_path}")


# import taxi data
taxi = pd.read_csv(workspace + "taxi/nyc_taxi_od.csv", low_memory=False)
taxi # 8,484,325 rows

## node
# import taxi zone, census tract point shp file
taxi_zone = gpd.read_file("D:/heat/data/taxi/taxi_zones/taxi_zones.shp") # 263 rows
taxi_zone = taxi_zone.dissolve(by='LocationID', aggfunc='first').reset_index() # 260 rows
tract_point = gpd.read_file("D:/heat/data/boundary/tract_variables.shp") # 2,324 rows

# EPSG:2263 (NAD83 / New York Long Island ftUS)
taxi_zone = taxi_zone.to_crs(epsg=2263)
tract_point = tract_point.to_crs(epsg=2263)
