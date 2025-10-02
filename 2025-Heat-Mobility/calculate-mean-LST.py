import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, mapping
from tqdm import tqdm
import glob
import os

workspace = "D:/YUBIN/data/"
cbg_path = workspace + "0-raw/tl_2018_04_bg/tl_2018_04_bg_Maricopa_Pinal.shp"
raster_folder = workspace + "0-raw/LST_Weekly_MODIS/day/"
output_folder = workspace + "1-processed/lst-CBG/"

# Load CBG boundary
cbg = gpd.read_file(cbg_path).to_crs("EPSG:4326")

# Iterate through all .tif files in the folder
tif_files = glob.glob(os.path.join(raster_folder, "*.tif"))

for raster_path in tif_files:
    fname = os.path.splitext(os.path.basename(raster_path))[0]
    lst_cbg_path = os.path.join(output_folder, f"{fname}_mean.shp")

    print(f"▶️ Processing: {fname}")

    # Load raster and apply mask
    with rasterio.open(raster_path) as src:
        out_image, _ = mask(src, cbg.geometry.map(mapping), crop=True)
        arr = out_image[0]
        rows, cols = arr.shape
        xmin, ymin, xmax, ymax = src.bounds

    # Generate fishnet points + sampling loop
    multiplier = 6
    while True:
        xs = np.linspace(xmin, xmax, cols * multiplier)
        ys = np.linspace(ymin, ymax, rows * multiplier)

        gdf_points = gpd.GeoDataFrame(
            geometry=[Point(x, y) for x in xs for y in ys],
            crs="EPSG:4326"
        )

        with rasterio.open(raster_path) as src:
            coords = [(p.x, p.y) for p in gdf_points.geometry]
            values = []
            for val in tqdm(src.sample(coords), total=len(coords), desc=f"{fname} - Sampling"):
                values.append(val[0] if val[0] != src.nodata else np.nan)

        # Check for zero values
        if any(v == 0 for v in values if not np.isnan(v)):
            print(f"⚠️ {fname}: Found 0 values → multiplier {multiplier} → {multiplier+1}")
            multiplier += 1
            continue
        else:
            gdf_points["HEAT"] = values
            break

    # Spatial join between points and CBG polygons
    points_in_cbg = gpd.sjoin(gdf_points, cbg, how="inner", predicate="intersects")

    # Calculate mean HEAT per CBG
    cbg_mean = points_in_cbg.groupby("GEOID_int")["HEAT"].mean().reset_index()
    cbg_out = cbg.merge(cbg_mean, on="GEOID_int", how="left")

    lst_cbg = cbg_out[["GEOID_int", "HEAT", "geometry"]].copy()
    lst_cbg["GEOID_int"] = lst_cbg["GEOID_int"].astype(str)

    # Save final result
    lst_cbg.to_file(lst_cbg_path, driver="ESRI Shapefile")
    print(f"✅ Saved: {lst_cbg_path}")
