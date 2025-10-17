import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.stats import chisquare
import numpy as np

workspace = "*"

df_raw = pd.read_csv(
    workspace + "0 raw/mobility_phoenix/od_flow-visitor_home_cbgs-poi_cbg-Maricopa_Pinal_County-2023-01-02_2023-12-25.csv.gz",
    compression="gzip"
)

# Filter data for summer period (June 5 – August 28, 2023)
df_raw["date_range_start"] = pd.to_datetime(df_raw["date_range_start"])
df = df_raw[
    (df_raw["date_range_start"] >= "2023-06-01") &
    (df_raw["date_range_start"] <= "2023-08-28")
]

df.loc[:, "visitor_home_cbgs"] = df["visitor_home_cbgs"].astype(str)
df.loc[:, "poi_cbg"] = df["poi_cbg"].astype(str)

cbg = gpd.read_file(workspace + "1 processed/boundary/phoenix_boundary.shp")
cbg["GEOID"] = cbg["GEOID"].str[1:]

# Filter df_raw so both home and POI CBGs exist in cbg
df = df[
    df["visitor_home_cbgs"].isin(cbg["GEOID"]) &
    df["poi_cbg"].isin(cbg["GEOID"])
] # 717713 rows

cbg = gpd.read_file(workspace + "1 processed/boundary/phoenix_boundary.shp")
cbg["GEOID"] = cbg["GEOID"].str[1:]  # align with GEOID format

# ------------------------------------------------------------------------------
# 1. Mobility only
# ------------------------------------------------------------------------------
# 1. Filter only outflow records (exclude self-flows)
flow_df = df[df['visitor_home_cbgs'] != df['poi_cbg']]

# 2. Calculate total outflow per home CBG
outflow_sum = (
    flow_df.groupby('visitor_home_cbgs')['visitor']
    .sum()
    .reset_index(name='outflow')
)

# Normalize outflow values
outflow_sum['outflow_norm'] = (
    (outflow_sum['outflow'] - outflow_sum['outflow'].min()) /
    (outflow_sum['outflow'].max() - outflow_sum['outflow'].min())
)

# Merge with CBG geometry
cbg_out = cbg.merge(
    outflow_sum,
    how='left',
    left_on='GEOID',
    right_on='visitor_home_cbgs'
)

# 3. Calculate total inflow per POI CBG
inflow_sum = (
    flow_df.groupby('poi_cbg')['visitor']
    .sum()
    .reset_index(name='inflow')
)

# Normalize inflow values
inflow_sum['inflow_norm'] = (
    (inflow_sum['inflow'] - inflow_sum['inflow'].min()) /
    (inflow_sum['inflow'].max() - inflow_sum['inflow'].min())
)

# Merge with CBG geometry
cbg_in = cbg.merge(
    inflow_sum,
    how='left',
    left_on='GEOID',
    right_on='poi_cbg'
)

# ------------------------------------------------------------------------------
# 2. Mobility with heat
# ------------------------------------------------------------------------------
# 1. LST
lst = pd.read_csv(workspace + "1 processed/image/aggregated_lst.csv")
lst.loc[:, "GEOID"] = lst["GEOID"].astype(str)

lst["K_MEAN"] = lst["MEAN"]                   # keep Kelvin
lst["MEAN"] = lst["MEAN"] - 273.15            # convert to Celsius
lst["MEAN_GROUP"] = pd.qcut(lst["MEAN"], q=3, labels=["Low", "Median", "High"]) # 2704 rows

# Merge mobility with LST (home & poi)
df_lst = df.merge(
    lst[["GEOID", "MEAN", "MEAN_GROUP"]].rename(columns={"GEOID": "home_cbg", "MEAN": "home_lst", "MEAN_GROUP": "home_heat"}),
    left_on="visitor_home_cbgs",
    right_on="home_cbg",
    how="left"
)
df_lst = df_lst.merge(
    lst[["GEOID", "MEAN", "MEAN_GROUP"]].rename(columns={"GEOID": "poi_cbg", "MEAN": "poi_lst", "MEAN_GROUP": "poi_heat"}),
    left_on="poi_cbg",
    right_on="poi_cbg",
    how="left"
)
df_lst = df_lst.rename(columns={"date_range_start": "date"})

# Create mobility category (e.g., HH, HL, etc.)
df_lst["mobility"] = df_lst["home_heat"].str[0] + df_lst["poi_heat"].str[0]


# 2. Sen's slope
sens = gpd.read_file(workspace + "1 processed/sens-CBG/sensSlope_LST_2000_2023_Senslope_mean.shp")
sens = sens.rename(columns={"HEAT": "HEAT_SENS"})

sens["SENS_GROUP"] = pd.qcut(sens["HEAT_SENS"], q=3, labels=["Low", "Median", "High"]) # 2704 rows

# Merge mobility with LST (home & poi)
df_sens = df.merge(
    sens[["GEOID", "HEAT_SENS", "SENS_GROUP"]]
    .rename(columns={"GEOID": "home_cbg", "HEAT_SENS": "home_sens_value", "SENS_GROUP": "home_sens"}),
    left_on="visitor_home_cbgs",
    right_on="home_cbg",
    how="left"
)

df_sens = df_sens.merge(
    sens[["GEOID", "HEAT_SENS", "SENS_GROUP"]]
    .rename(columns={"GEOID": "poi_cbg", "HEAT_SENS": "poi_sens_value", "SENS_GROUP": "poi_sens"}),
    left_on="poi_cbg",
    right_on="poi_cbg",
    how="left"
)
df_sens = df_sens.rename(columns={"date_range_start": "date"})
