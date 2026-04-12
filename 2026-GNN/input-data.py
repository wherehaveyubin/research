import os
import pandas as pd
import geopandas as gpd

# ============================================================
# 1. Set workspace and file paths
# ============================================================
workspace = r"*"

tracts_path = os.path.join(workspace, "LA_tracts.shp")
urbanwatch_path = os.path.join(workspace, "urbanwatch_tract_pct.csv")
acs_path = os.path.join(workspace, "ACS_tract_CA_selected.csv")
lst_path = os.path.join(workspace, "CA_tract_LST_NDVI_NDBI_NDWI_NDMI_SAVI_Albedo_2023summer.csv")
mhlth_path = os.path.join(workspace, "2023CA_MHLTH.csv")

output_gpkg = os.path.join(workspace, "tracts_merged.gpkg")
output_csv = os.path.join(workspace, "tracts_merged_attributes.csv")

# ============================================================
# 2. Read tract shapefile
# ============================================================
tracts = gpd.read_file(tracts_path)
tracts["GEOID"] = tracts["GEOID"].astype(str).str.zfill(11)

print("Tracts:", tracts.shape)
print(tracts[["GEOID", "NAME"]].head())

# ============================================================
# 3. Read UrbanWatch CSV
# ============================================================
urbanwatch = pd.read_csv(urbanwatch_path, dtype={"GEOID": str})
urbanwatch["GEOID"] = urbanwatch["GEOID"].astype(str).str.replace(r"\.0+$", "", regex=True).str.zfill(11)
urbanwatch = urbanwatch.rename(columns={"city": "UW_city"})

print("UrbanWatch:", urbanwatch.shape)
print(urbanwatch.head())

# ============================================================
# 4. Read ACS CSV
# ============================================================
acs = pd.read_csv(acs_path, dtype={"GEOID": str})
acs["GEOID"] = acs["GEOID"].astype(str).str.replace(r"\.0+$", "", regex=True).str.zfill(11)

if "NAME" in acs.columns:
    acs = acs.rename(columns={"NAME": "ACS_NAME"})

print("ACS:", acs.shape)
print(acs.head())

# ============================================================
# 5. Read Landsat/LST CSV
# ============================================================
lst = pd.read_csv(lst_path, dtype={"GEOID": str})
lst["GEOID"] = lst["GEOID"].astype(str).str.replace(r"\.0+$", "", regex=True).str.zfill(11)

if "NAME" in lst.columns:
    lst = lst.rename(columns={"NAME": "LST_NAME"})

print("LST:", lst.shape)
print(lst.head())

# ============================================================
# 6. Read Mental Health CSV
# ============================================================
mhlth = pd.read_csv(mhlth_path, dtype={"LocationName": str})

# LocationName is the tract FIPS code; zero-pad to 11 digits to match GEOID
mhlth["GEOID"] = mhlth["LocationName"].astype(str).str.zfill(11)

# Keep only GEOID and the outcome variable
mhlth = mhlth[["GEOID", "Data_Value"]].rename(columns={"Data_Value": "Mental_distress_pct"})

print("Mental Health:", mhlth.shape)
print(mhlth.head())

# ============================================================
# 7. Merge all attribute tables to tracts
# ============================================================
merged = tracts.merge(urbanwatch, on="GEOID", how="left")
merged = merged.merge(acs, on="GEOID", how="left")
merged = merged.merge(lst, on="GEOID", how="left")
merged = merged.merge(mhlth, on="GEOID", how="left")

# Drop unnecessary columns
drop_cols = [
    "STATEFP", "COUNTYFP", "TRACTCE", "GEOIDFQ", "NAME", "NAMELSAD",
    "MTFCC", "FUNCSTAT", "ALAND", "AWATER", "INTPTLAT", "INTPTLON",
    "GEOID_2", "UW_city", "total_pixels"
]
merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

print("Merged:", merged.shape)

# ============================================================
# 8. Check merge success
# ============================================================
print("\nNon-null counts for key variables:")
check_cols = ["UW_building_pct", "Median_income", "LST_mean", "Mental_distress_pct"]
for col in check_cols:
    if col in merged.columns:
        print(f"  {col}: {merged[col].notna().sum()}")

preview_cols = [c for c in [
    "GEOID", "NAME", "UW_city", "Median_income", "LST_mean", "Mental_distress_pct"
] if c in merged.columns]
print("\nPreview:")
print(merged[preview_cols].head())

# ============================================================
# 9. Handle missing values & Normalize
# ============================================================
from sklearn.preprocessing import MinMaxScaler

# Exclude non-numeric identifiers and metadata columns
exclude_cols = [
    "ALAND", "AWATER", "GEOID_2", "total_pixels",
    "GEOID", "NAME", "ACS_NAME", "LST_NAME", "UW_city", "geometry"
]
num_cols = [c for c in merged.columns
            if c not in exclude_cols and pd.api.types.is_numeric_dtype(merged[c])]

print(f"\nVariables to normalize ({len(num_cols)}):")
print(num_cols)

# Fill missing values with column median
merged[num_cols] = merged[num_cols].fillna(merged[num_cols].median())

# Min-Max scaling (0 to 1)
scaler = MinMaxScaler()
merged[num_cols] = scaler.fit_transform(merged[num_cols])

print("\nNormalization complete - range check:")
print(merged[num_cols].describe().loc[["min", "max"]])

# ============================================================
# 10. Save outputs
# ============================================================
merged.to_file(output_gpkg, layer="tracts_merged", driver="GPKG")
merged.drop(columns="geometry").to_csv(output_csv, index=False)

print("\nSaved files:")
print(output_gpkg)
print(output_csv)
print("Total tracts:", len(merged))
