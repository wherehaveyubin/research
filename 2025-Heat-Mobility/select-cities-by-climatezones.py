import os
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# =========================
# User Settings
# =========================
# 1) Workspace path and input shapefile
workspace = "*"

# 2) Output paths (set to None if you don’t want to save)
OUT_GEOJSON = workspace + "selected_cities_by_class.geojson"
OUT_CSV     = workspace + "selected_cities_by_class.csv"

# 3) Parameters
K_PER_CLASS = 5              # Number of cities to select per climate class
POP_CLASS_MIN = 10           # Minimum POP_CLASS threshold
TOP_N_PER_CLASS = 500        # Consider top N cities by population within each class
MIN_SEPARATION_KM = 0        # Minimum separation between selected cities (0 = disabled)
POP_BONUS_KM = 0             # Optional: population bonus in km units (0 = pure farthest-first)
                             # Example: try 50–200 km if you want stronger population influence

# =========================
# Utility Functions
# =========================
def ensure_lonlat_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Ensure the CRS is WGS84 (EPSG:4326)."""
    if gdf.crs is None:
        gdf = gdf.set_crs(4326, allow_override=True)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)
    return gdf

def to_equal_area(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Project to US National Atlas Equal Area (EPSG:2163) for distance calculation."""
    return gdf.to_crs(2163)

def km_from_projected_distance(meters: np.ndarray) -> np.ndarray:
    return meters / 1000.0

def compute_min_dist_km(candidate_xy, picked_xy):
    """
    Compute minimum distance (km) from each candidate point to the set of already-picked points.
    """
    if picked_xy.shape[0] == 0:
        return np.full(candidate_xy.shape[0], np.inf)
    diff = candidate_xy[:, None, :] - picked_xy[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=2))  # distances in meters
    dmin_m = d.min(axis=1)
    return km_from_projected_distance(dmin_m)

def farthest_first_with_pop(
    df_class: gpd.GeoDataFrame,
    k=5,
    top_n=500,
    min_separation_km=0,
    pop_bonus_km=0,
):
    """
    Select k cities within one climate class using a farthest-first heuristic:
    - Start with the largest population city.
    - Iteratively add the city that maximizes minimum distance to the already selected set.
    - Optionally enforce a minimum separation (km).
    - Optionally add a population-based bonus to the distance score.
    """
    # Take top N by population
    dfc = df_class.sort_values("POPULATION", ascending=False).head(top_n).copy()

    # Project to equal-area CRS for distance computation
    dfc = ensure_lonlat_crs(dfc)
    dfp = to_equal_area(dfc)
    xy = np.vstack([dfp.geometry.x.values, dfp.geometry.y.values]).T

    # Population scaled to [0,1]
    pop = dfc["POPULATION"].values.astype(float)
    if pop.max() == pop.min():
        pop_scaled = np.zeros_like(pop)
    else:
        pop_scaled = (pop - pop.min()) / (pop.max() - pop.min())

    idx_all = np.arange(len(dfc))
    # Seed = most populous city
    seed_local_idx = 0
    picked_local_indices = [seed_local_idx]

    while len(picked_local_indices) < min(k, len(dfc)):
        picked_xy = xy[picked_local_indices, :]
        mask_unpicked = np.ones(len(dfc), dtype=bool)
        mask_unpicked[picked_local_indices] = False
        unpicked_idx = idx_all[mask_unpicked]
        if len(unpicked_idx) == 0:
            break

        un_xy = xy[mask_unpicked, :]
        min_dist_km = compute_min_dist_km(un_xy, picked_xy)

        # Apply separation constraint if specified
        valid = np.ones_like(min_dist_km, dtype=bool)
        if min_separation_km and min_separation_km > 0:
            valid &= (min_dist_km >= min_separation_km)
        if not valid.any():
            valid = np.ones_like(valid, dtype=bool)

        # Score = distance + optional population bonus
        scores = min_dist_km.copy()
        if pop_bonus_km and pop_bonus_km > 0:
            scores = scores + pop_scaled[mask_unpicked] * float(pop_bonus_km)

        best_pos = np.argmax(np.where(valid, scores, -np.inf))
        best_local_idx = unpicked_idx[best_pos]
        picked_local_indices.append(best_local_idx)

        if len(picked_local_indices) >= k:
            break

    selected = dfc.iloc[picked_local_indices].copy()
    return selected

# =========================
# Main Logic
# =========================
# 1) Load shapefile
cities = gpd.read_file(workspace + "cities_by_climatezones/City_by_climatezones.shp")

# 2) Check required columns
required_cols = {"NAME", "STATE_ABBR", "POPULATION", "POP_CLASS", "Class_1", "geometry"}
missing = required_cols - set(cities.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# 3) Clean geometry
cities = cities[~cities.geometry.is_empty & cities.geometry.notna()].copy()
cities = cities[cities.geometry.type.isin(["Point", "MultiPoint"])].copy()
cities.loc[cities.geometry.type == "MultiPoint", "geometry"] = cities.loc[
    cities.geometry.type == "MultiPoint", "geometry"
].centroid

# 4) Filter by POP_CLASS
cities_f = cities[cities["POP_CLASS"] >= POP_CLASS_MIN].copy()

# 5) Climate classes
classes = ["A", "B", "C", "D"]
classes_in_data = sorted(set(cities_f["Class_1"]) & set(classes))
if not classes_in_data:
    raise ValueError("No A/B/C/D classes remain after filtering. Try lowering POP_CLASS_MIN.")

# 6) Select per class
selected_list = []
for cc in classes:
    dfc = cities_f[cities_f["Class_1"] == cc].copy()
    if dfc.empty:
        print(f"[Warning] Class {cc}: no candidates, skipped.")
        continue

    k_pick = min(K_PER_CLASS, len(dfc))
    if k_pick < K_PER_CLASS:
        print(f"[Info] Class {cc}: only {len(dfc)} candidates, picking {k_pick}.")

    selected_cc = farthest_first_with_pop(
        dfc,
        k=k_pick,
        top_n=min(TOP_N_PER_CLASS, len(dfc)),
        min_separation_km=MIN_SEPARATION_KM,
        pop_bonus_km=POP_BONUS_KM,
    )
    selected_cc["__picked_rank"] = np.arange(1, len(selected_cc) + 1)
    selected_list.append(selected_cc)

# 7) Merge results
if len(selected_list) == 0:
    raise ValueError("No cities were selected for any class.")

selected_all = pd.concat(selected_list, ignore_index=True)
selected_all = selected_all.sort_values(
    by=["Class_1", "POPULATION"], ascending=[True, False]
).reset_index(drop=True)

# 8) Keep useful columns
keep_cols = [
    "Class_1", "NAME", "STATE_ABBR", "POPULATION", "POP_CLASS",
    "__picked_rank"
]
cities_ll = ensure_lonlat_crs(selected_all)
selected_all["lon"] = cities_ll.geometry.x
selected_all["lat"] = cities_ll.geometry.y
keep_cols += ["lon", "lat", "geometry"]
result_gdf = selected_all[keep_cols].copy()

# 9) Print preview
print("=== Selected Cities (summary) ===")
print(result_gdf[["Class_1", "NAME", "STATE_ABBR", "POPULATION", "lon", "lat"]])

# 10) Save outputs
if OUT_GEOJSON:
    result_gdf.to_file(OUT_GEOJSON, driver="GeoJSON")
    print(f"[Saved] GeoJSON -> {OUT_GEOJSON}")

if OUT_CSV:
    tmp = result_gdf.drop(columns=["geometry"]).copy()
    tmp.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"[Saved] CSV -> {OUT_CSV}")
