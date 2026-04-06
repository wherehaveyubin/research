import os
import requests
import pandas as pd
import geopandas as gpd
from functools import reduce

# ============================================================
# 1. User settings
# ============================================================
WORKSPACE = "*"
API_KEY = "*"
YEAR = 2023

STATE_FIPS = "06"
COUNTIES = ["037", "073", "075"]  # Los Angeles, San Diego, San Francisco

TRACT_SHP = WORKSPACE + "data/tl_2023_06_tract/tl_2023_06_tract.shp"
OUTPUT_CSV = WORKSPACE + "data/ACS_tract_CA_selected.csv"

# ============================================================
# 2. Census API endpoints
# ============================================================
BASE_DETAILED = f"https://api.census.gov/data/{YEAR}/acs/acs5"
BASE_SUBJECT = f"https://api.census.gov/data/{YEAR}/acs/acs5/subject"

# ============================================================
# 3. Variable definitions
# ============================================================

# ---------- Detailed tables ----------
DETAILED_VARS = {
    "income": [
        "B19013_001E"  # Median household income (USD)
    ],
    "race": [
        "B03002_001E",  # Total population
        "B03002_003E",  # Non-Hispanic White population
        "B03002_004E",  # Non-Hispanic Black population
        "B03002_005E",  # American Indian and Alaska Native population (non-Hispanic)
        "B03002_006E",  # Asian population (non-Hispanic)
        "B03002_007E",  # Native Hawaiian and Other Pacific Islander population (non-Hispanic)
        "B03002_012E"   # Hispanic or Latino population
    ],
    "rent": [
        "B25003_001E",  # Total occupied housing units
        "B25003_003E"   # Renter-occupied housing units
    ]
}

# ---------- Subject tables ----------
SUBJECT_VARS = {
    "poverty": [
        "S1701_C03_001E"  # Poverty rate (% below poverty line)
    ],
    "education": [
        "S1501_C02_015E"  # % population age 25+ with a college degree
    ],
    "age": [
        "S0101_C01_001E",  # Total population (count)
        "S0101_C01_022E",  # Population under 18 years (count)
        "S0101_C02_030E"   # % population age 65+ (elderly)
    ],
    "employment": [
        "S2301_C04_001E"  # Unemployment rate (%)
    ],
    "insurance": [
        "S2701_C05_001E"  # % population without health insurance
    ],
    "language": [
        "S1601_C01_001E", # population age 5+
        "S1601_C05_001E"  # population age 5+ with limited English proficiency
    ]
}

# ============================================================
# 4. Helper functions
# ============================================================
def fetch_acs(endpoint, variables):
    frames = []

    for county in COUNTIES:
        params = {
            "get": ",".join(["NAME"] + variables),
            "for": "tract:*",
            "in": f"state:{STATE_FIPS} county:{county}",
            "key": API_KEY
        }

        response = requests.get(endpoint, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def clean_numeric(df):
    for col in df.columns:
        if col not in ["NAME", "state", "county", "tract", "GEOID"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def safe_pct(num, denom):
    return (num / denom.replace({0: pd.NA})) * 100


def load_area(shp_path):
    gdf = gpd.read_file(shp_path)
    gdf = gdf[gdf["COUNTYFP"].isin(COUNTIES)].copy()

    # Reproject to California Albers for area calculation
    gdf_proj = gdf.to_crs(epsg=3310)
    gdf["area_km2"] = gdf_proj.geometry.area / 1_000_000

    return gdf[["GEOID", "area_km2"]]


# ============================================================
# 5. Download data
# ============================================================
frames = []

for vars_list in DETAILED_VARS.values():
    frames.append(fetch_acs(BASE_DETAILED, vars_list))

for vars_list in SUBJECT_VARS.values():
    frames.append(fetch_acs(BASE_SUBJECT, vars_list))

# ============================================================
# 6. Merge all tables
# ============================================================
acs = reduce(
    lambda left, right: pd.merge(
        left,
        right.drop(columns=["NAME"], errors="ignore"),
        on=["state", "county", "tract"],
        how="outer"
    ),
    frames
)

# ============================================================
# 7. GEOID and cleaning
# ============================================================
acs["state"] = acs["state"].astype(str).str.zfill(2)
acs["county"] = acs["county"].astype(str).str.zfill(3)
acs["tract"] = acs["tract"].astype(str).str.zfill(6)
acs["GEOID"] = acs["state"] + acs["county"] + acs["tract"]

acs = clean_numeric(acs)

# Optional: replace common Census missing-value sentinels
acs = acs.replace({
    -666666666: pd.NA,
    -555555555: pd.NA,
    -333333333: pd.NA,
    -222222222: pd.NA,
    -888888888: pd.NA
})

# ============================================================
# 8. Variable construction
# ============================================================

# Income
acs["Median_income"] = acs["B19013_001E"]

# Poverty
acs["Poverty_rate"] = acs["S1701_C03_001E"]

# Race / ethnicity
acs["Pct_white"] = safe_pct(acs["B03002_003E"], acs["B03002_001E"])     # Non-Hispanic White
acs["Pct_black"] = safe_pct(acs["B03002_004E"], acs["B03002_001E"])     # Non-Hispanic Black
acs["Pct_native"] = safe_pct(acs["B03002_005E"], acs["B03002_001E"])    # American Indian / Alaska Native
acs["Pct_asian"] = safe_pct(acs["B03002_006E"], acs["B03002_001E"])     # Asian
acs["Pct_pacific"] = safe_pct(acs["B03002_007E"], acs["B03002_001E"])   # Pacific Islander
acs["Pct_hispanic"] = safe_pct(acs["B03002_012E"], acs["B03002_001E"])  # Hispanic
acs["Pct_minority"] = safe_pct(
    acs["B03002_001E"] - acs["B03002_003E"],
    acs["B03002_001E"]
)

# Education
acs["Pct_college"] = acs["S1501_C02_015E"]

# Age
acs["Pct_elderly"] = acs["S0101_C02_030E"]

acs["Pct_under18"] = safe_pct(
    acs["S0101_C01_022E"],  # Population under 18 years (count)
    acs["S0101_C01_001E"]   # Total population (count)
)

# Employment
acs["Unemployment"] = acs["S2301_C04_001E"]

# Insurance
acs["Pct_no_insurance"] = acs["S2701_C05_001E"]

# Housing
acs["Pct_renter"] = safe_pct(acs["B25003_003E"], acs["B25003_001E"])

# Language
acs["Pct_limited_eng"] = safe_pct(acs["S1601_C05_001E"], acs["S1601_C01_001E"])

# ============================================================
# 9. Population density
# ============================================================
area_df = load_area(TRACT_SHP)
acs = acs.merge(area_df, on="GEOID", how="left")

acs["Pop_density"] = acs["B03002_001E"] / acs["area_km2"].replace({0: pd.NA})

# ============================================================
# 10. Final dataset
# ============================================================
final = acs[
    [
        "GEOID",
        "NAME",
        "Median_income",
        "Poverty_rate",
        "Pct_white",
        "Pct_black",
        "Pct_native",
        "Pct_asian",
        "Pct_pacific",
        "Pct_hispanic",
        "Pct_minority",
        "Pct_college",
        "Pct_elderly",
        "Pct_under18",
        "Unemployment",
        "Pct_no_insurance",
        "Pct_renter",
        "Pop_density",
        "Pct_limited_eng"
    ]
].copy()

# ============================================================
# 11. Export
# ============================================================
final.to_csv(OUTPUT_CSV, index=False)

print(final.head())
print("Saved:", OUTPUT_CSV)
print("Number of tracts:", len(final))
