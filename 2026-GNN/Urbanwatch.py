"""
UrbanWatch LCLU → Census Tract Zonal Statistics
=================================================
Input:  UrbanWatch RGB GeoTIFFs (LA_1_LULC.tif, LA_2_LULC.tif, ...)
        Census tract shapefile (tl_2023_06_tract.shp)
Output: CSV with GEOID + 7 LCLU percentages per tract
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ================================================================
# 1. CONFIGURATION
# ================================================================

# Path to folder containing UrbanWatch tiles
UW_DIR = Path(r"*\urbanwatch")

# Path to Census tract shapefile
TRACT_SHP = Path(r"*\tracts.shp")

# Output CSV path
OUTPUT_CSV = Path(r"*\urbanwatch_tract_pct.csv")

# Tile patterns by city
CITY_PATTERNS = {
    "LA": "LA_*_LULC*.tif",
    "SD": "SD_*_LULC*.tif",
    "SF": "SF_*_LULC*.tif",
}

# Target county FIPS codes (first 5 digits of GEOID)
TARGET_COUNTIES = ["06037", "06073", "06075"]  # LA, SD, SF


# ================================================================
# 2. RGB → CLASS conversion lookup table
# ================================================================
# UrbanWatch RGB color scheme (based on official documentation)

CLASS_INFO = {
    0: {"name": "building",    "rgb": (255, 0,   0  )},
    1: {"name": "road",        "rgb": (133, 133, 133)},
    2: {"name": "parking_lot", "rgb": (255, 0,   192)},
    3: {"name": "tree_canopy", "rgb": (34,  139, 34 )},
    4: {"name": "grass_shrub", "rgb": (128, 236, 104)},
    5: {"name": "agriculture", "rgb": (255, 193, 37 )},
    6: {"name": "water",       "rgb": (0,   0,   255)},
    7: {"name": "barren",      "rgb": (128, 0,   0  )},
    8: {"name": "others",      "rgb": (255, 255, 255)},
}

# Target classes for analysis
TARGET_CLASSES = [0, 1, 2, 3, 4, 6, 7]  # building ~ barren (7 classes)


def build_rgb_lookup():
    """Create RGB → class_id lookup dictionary"""
    lookup = {}
    for cid, info in CLASS_INFO.items():
        lookup[info["rgb"]] = cid
    return lookup


def rgb_to_class_nearest(r, g, b, lookup):
    """
    Convert RGB values to the nearest class.
    Exact RGB matching may fail due to compression/resampling artifacts,
    so nearest-neighbor matching based on Euclidean distance is used.
    """
    ref_rgbs = np.array([info["rgb"] for info in CLASS_INFO.values()])
    ref_ids = np.array(list(CLASS_INFO.keys()))

    # Flatten spatial dimensions
    shape = r.shape
    r_flat = r.ravel().astype(np.int32)
    g_flat = g.ravel().astype(np.int32)
    b_flat = b.ravel().astype(np.int32)

    # Stack into (N, 3)
    pixels = np.stack([r_flat, g_flat, b_flat], axis=1)

    # Compute distances to each reference color
    # Shape: (N, num_classes)
    dists = np.sqrt(
        ((pixels[:, np.newaxis, :] - ref_rgbs[np.newaxis, :, :]) ** 2)
        .sum(axis=2)
    )
    class_map = ref_ids[np.argmin(dists, axis=1)]
    return class_map.reshape(shape)


# ================================================================
# 3. Load tiles & mosaic
# ================================================================

def load_and_mosaic_tiles(uw_dir, patterns):
    """Load tiles by city and merge into a single mosaic"""
    all_files = []
    for city, pattern in patterns.items():
        files = sorted(uw_dir.glob(pattern))
        print(f"  {city}: {len(files)} tiles found")
        all_files.extend(files)

    if not all_files:
        raise FileNotFoundError(
            f"No tiles found in {uw_dir}. Check CITY_PATTERNS."
        )

    print(f"  Total tiles: {len(all_files)}")

    # Open all tiles
    src_files = [rasterio.open(f) for f in all_files]

    # Mosaic
    mosaic_arr, mosaic_transform = merge(src_files)
    profile = src_files[0].profile.copy()
    profile.update({
        "height": mosaic_arr.shape[1],
        "width": mosaic_arr.shape[2],
        "transform": mosaic_transform,
    })

    # Close source files
    for src in src_files:
        src.close()

    return mosaic_arr, profile


# ================================================================
# 4. Memory-efficient tract-level zonal statistics
# ================================================================

def compute_tract_stats_chunked(uw_dir, patterns, tracts_gdf):
    """
    Process data city-by-city to reduce memory usage.
    Mosaic tiles for each city → clip by tract → compute class proportions.
    """
    results = []
    class_names = {cid: info["name"] for cid, info in CLASS_INFO.items()}

    for city, pattern in patterns.items():
        print(f"\n{'='*50}")
        print(f"Processing {city}...")
        print(f"{'='*50}")

        files = sorted(uw_dir.glob(pattern))
        if not files:
            print(f"  WARNING: No tiles for {city}, skipping.")
            continue

        print(f"  Loading {len(files)} tiles...")

        # Open tiles
        src_files = [rasterio.open(f) for f in files]

        # Mosaic
        mosaic_arr, mosaic_transform = merge(src_files)
        profile = src_files[0].profile.copy()
        profile.update({
            "height": mosaic_arr.shape[1],
            "width": mosaic_arr.shape[2],
            "transform": mosaic_transform,
            "count": mosaic_arr.shape[0],
        })

        # Match CRS
        raster_crs = profile.get("crs")
        if raster_crs and tracts_gdf.crs != raster_crs:
            tracts_proj = tracts_gdf.to_crs(raster_crs)
        else:
            tracts_proj = tracts_gdf

        from rasterio.io import MemoryFile
        memfile = MemoryFile()

        with memfile.open(**profile) as mem_dst:
            mem_dst.write(mosaic_arr)

        # Free memory
        del mosaic_arr

        dataset = memfile.open()
        raster_bounds = dataset.bounds

        # Filter tracts within raster bounds
        from shapely.geometry import box
        raster_box = box(
            raster_bounds.left, raster_bounds.bottom,
            raster_bounds.right, raster_bounds.top
        )

        tracts_in_bounds = tracts_proj[
            tracts_proj.geometry.intersects(raster_box)
        ]

        print(f"  Tracts in {city} bounds: {len(tracts_in_bounds)}")

        # Process each tract
        for idx, row in tracts_in_bounds.iterrows():
            geoid = row["GEOID"]
            geom = row.geometry

            if geom is None or geom.is_empty:
                continue

            try:
                out_image, _ = mask(
                    dataset, [geom], crop=True, nodata=0
                )
            except Exception:
                continue

            if out_image.shape[0] < 3:
                continue

            r_band = out_image[0]
            g_band = out_image[1]
            b_band = out_image[2]

            valid = ~((r_band == 0) & (g_band == 0) & (b_band == 0))
            total_valid = valid.sum()

            if total_valid == 0:
                continue

            class_map = rgb_to_class_nearest(
                r_band[valid],
                g_band[valid],
                b_band[valid],
                build_rgb_lookup()
            )

            counts = Counter(class_map.ravel())

            row_data = {
                "GEOID": geoid,
                "city": city,
                "total_pixels": int(total_valid)
            }

            for cid in range(9):
                col_name = f"UW_{class_names[cid]}_pct"
                count = counts.get(cid, 0)
                pct = (count / total_valid) * 100
                row_data[col_name] = round(pct, 4)

            results.append(row_data)

        # Cleanup
        dataset.close()
        memfile.close()

        for src in src_files:
            src.close()

        print(f"  Done: {len([r for r in results if r['city']==city])} tracts processed")

    return pd.DataFrame(results)


# ================================================================
# 5. RGB validation utility
# ================================================================

def verify_rgb(uw_dir, patterns, n_samples=100000):
    """
    Sample random pixels from tiles to inspect actual RGB distributions.
    If UrbanWatch RGB values differ from expectations,
    CLASS_INFO should be updated.
    """
    print("\n=== RGB Value Verification ===")

    for city, pattern in patterns.items():
        files = sorted(uw_dir.glob(pattern))
        if not files:
            continue

        with rasterio.open(files[0]) as src:
            data = src.read()  # (3, H, W)

            # Random sampling
            h, w = data.shape[1], data.shape[2]
            np.random.seed(42)
            sample_y = np.random.randint(0, h, n_samples)
            sample_x = np.random.randint(0, w, n_samples)

            r = data[0, sample_y, sample_x]
            g = data[1, sample_y, sample_x]
            b = data[2, sample_y, sample_x]

            # Unique RGB combinations (top 15)
            rgbs = list(zip(r.tolist(), g.tolist(), b.tolist()))
            counts = Counter(rgbs)

            print(f"\n{city} — Top 15 RGB values (from {files[0].name}):")
            print(f"  {'RGB':<25} {'Count':<10} {'Possible class'}")
            print(f"  {'-'*55}")
            for rgb, cnt in counts.most_common(15):
                # Find closest class
                min_dist = float('inf')
                best_class = "unknown"
                for cid, info in CLASS_INFO.items():
                    dist = sum((a-b)**2 for a,b in zip(rgb, info["rgb"]))
                    if dist < min_dist:
                        min_dist = dist
                        best_class = info["name"]
                        best_dist = dist

                match = "✓" if best_dist == 0 else f"(dist={int(best_dist**0.5)})"
                print(f"  {str(rgb):<25} {cnt:<10} {best_class} {match}")
