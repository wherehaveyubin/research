"""
============================================================
ACS Socioeconomic Variable Download & Construction
============================================================
Downloads 2023 ACS 5-year estimates for LA, SD, SF census tracts.
Constructs 26 SES variables from detailed and subject tables.

Output: ACS_SES_tract.csv (GEOID + 26 variables)
============================================================
"""

import os
import requests
import pandas as pd
from functools import reduce

# ============================================================
# 1. User settings
# ============================================================
WORKSPACE = r"*\data"
API_KEY = "*"
YEAR = 2023

STATE_FIPS = "06"
COUNTIES = ["037", "073", "075"]  # Los Angeles, San Diego, San Francisco

TRACT_SHP = os.path.join(WORKSPACE, "tracts.shp")
OUTPUT_CSV = os.path.join(WORKSPACE, "ACS_SES_tract.csv")

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
        "B19013_001E"           # Median household income (USD)
    ],
    "race": [
        "B03002_001E",          # Total population
        "B03002_003E",          # Non-Hispanic White
        "B03002_004E",          # Non-Hispanic Black
        "B03002_005E",          # American Indian / Alaska Native
        "B03002_006E",          # Asian
        "B03002_007E",          # Native Hawaiian / Pacific Islander
        "B03002_012E"           # Hispanic or Latino
    ],
    "rent": [
        "B25003_001E",          # Total occupied housing units
        "B25003_003E"           # Renter-occupied housing units
    ],
    "gini": [
        "B19083_001E"           # Gini Index of Income Inequality (0~1)
    ],
    "living_alone": [
        "B11001_001E",          # Total households
        "B11001_008E"           # Householder living alone
    ],
    "single_parent": [
        "B11003_001E",          # Total families
        "B11003_010E",          # Male householder, no spouse, with children
        "B11003_016E"           # Female householder, no spouse, with children
    ],
    "foreign_born": [
        "B05002_001E",          # Total population
        "B05002_013E"           # Foreign born
    ],
    "vacancy": [
        "B25002_001E",          # Total housing units
        "B25002_003E"           # Vacant housing units
    ],
    "overcrowding": [
        "B25014_001E",          # Total occupied housing units
        "B25014_005E",          # Owner: 1.01 to 1.50 occupants per room
        "B25014_006E",          # Owner: 1.51 to 2.00 occupants per room
        "B25014_007E",          # Owner: 2.01 or more occupants per room
        "B25014_011E",          # Renter: 1.01 to 1.50 occupants per room
        "B25014_012E",          # Renter: 1.51 to 2.00 occupants per room
        "B25014_013E"           # Renter: 2.01 or more occupants per room
    ],
    "median_rent": [
        "B25064_001E"           # Median gross rent ($)
    ],
    "rent_burden": [
        "B25070_001E",          # Total renter households
        "B25070_007E",          # 30.0 ~ 34.9%
        "B25070_008E",          # 35.0 ~ 39.9%
        "B25070_009E",          # 40.0 ~ 49.9%
        "B25070_010E"           # 50.0% or more
    ]
}

# ---------- Subject tables ----------
SUBJECT_VARS = {
    "poverty": [
        "S1701_C03_001E"        # Poverty rate (% below poverty line)
    ],
    "education": [
        "S1501_C02_015E"        # % population age 25+ with college degree
    ],
    "age": [
        "S0101_C02_022E",       # % Population under 18 years
        "S0101_C02_030E"        # % population age 65+ (elderly)
    ],
    "employment": [
        "S2301_C04_001E"        # Unemployment rate (%)
    ],
    "insurance": [
        "S2701_C05_001E"        # % population without health insurance
    ],
    "language": [
        "S1601_C05_001E"        # % LEP among specified language speakers (5+)
    ],
    "disability": [
        "S1810_C03_001E"        # Percent with a disability
    ],
    "commute": [
        "S0801_C01_046E"        # Mean travel time to work (minutes)
    ],
    "internet": [
        "S2801_C02_019E"        # Percent without internet subscription
    ]
}

# ============================================================
# 4. Helper functions
# ============================================================
def fetch_acs(endpoint, variables):
    """Download ACS data for all counties from Census API."""
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
    """Convert all non-ID columns to numeric."""
    for col in df.columns:
        if col not in ["NAME", "state", "county", "tract", "GEOID"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def safe_pct(num, denom):
    """Calculate percentage safely, avoiding division by zero."""
    return (num / denom.replace({0: pd.NA})) * 100

# ============================================================
# 5. Download data
# ============================================================
print("=" * 60)
print("Downloading ACS data...")
print("=" * 60)

frames = []

# Detailed tables
for group_name, vars_list in DETAILED_VARS.items():
    print(f"  Downloading detailed table: {group_name} ({len(vars_list)} vars)")
    frames.append(fetch_acs(BASE_DETAILED, vars_list))

# Subject tables
for group_name, vars_list in SUBJECT_VARS.items():
    print(f"  Downloading subject table: {group_name} ({len(vars_list)} vars)")
    frames.append(fetch_acs(BASE_SUBJECT, vars_list))

print(f"  Downloaded {len(frames)} table groups")

# ============================================================
# 6. Merge all tables
# ============================================================
print("\nMerging tables...")

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

# Replace Census missing-value sentinels
acs = acs.replace({
    -666666666: pd.NA,
    -555555555: pd.NA,
    -333333333: pd.NA,
    -222222222: pd.NA,
    -888888888: pd.NA,
    -999999999: pd.NA
})

print(f"Total tracts downloaded: {len(acs)}")

# ============================================================
# 8. Variable construction
# ============================================================
print("\nConstructing variables...")

# --- Income & Inequality ---
acs["Median_income"] = acs["B19013_001E"]
acs["Gini_index"] = acs["B19083_001E"]

# --- Poverty ---
acs["Poverty_rate"] = acs["S1701_C03_001E"]

# --- Race / Ethnicity ---
acs["Pct_white"] = safe_pct(acs["B03002_003E"], acs["B03002_001E"])
acs["Pct_black"] = safe_pct(acs["B03002_004E"], acs["B03002_001E"])
acs["Pct_native"] = safe_pct(acs["B03002_005E"], acs["B03002_001E"])
acs["Pct_asian"] = safe_pct(acs["B03002_006E"], acs["B03002_001E"])
acs["Pct_pacific"] = safe_pct(acs["B03002_007E"], acs["B03002_001E"])
acs["Pct_hispanic"] = safe_pct(acs["B03002_012E"], acs["B03002_001E"])

# --- Education ---
acs["Pct_college"] = acs["S1501_C02_015E"]

# --- Age ---
acs["Pct_elderly"] = acs["S0101_C02_030E"]
acs["Pct_under18"] = acs["S0101_C02_022E"]

# --- Employment ---
acs["Unemployment_rate"] = acs["S2301_C04_001E"]

# --- Insurance ---
acs["Pct_uninsured"] = acs["S2701_C05_001E"]

# --- Housing ---
acs["Pct_renter"] = safe_pct(acs["B25003_003E"], acs["B25003_001E"])
acs["Median_rent"] = acs["B25064_001E"]
acs["Vacancy_rate"] = safe_pct(acs["B25002_003E"], acs["B25002_001E"])
acs["Rent_burden"] = safe_pct(
    acs["B25070_007E"] + acs["B25070_008E"] + acs["B25070_009E"] + acs["B25070_010E"],
    acs["B25070_001E"]
)

# --- Overcrowding (1.01+ occupants per room, owner + renter) ---
acs["Overcrowding"] = safe_pct(
    acs["B25014_005E"] + acs["B25014_006E"] + acs["B25014_007E"] +
    acs["B25014_011E"] + acs["B25014_012E"] + acs["B25014_013E"],
    acs["B25014_001E"]
)

# --- Language ---
acs["Pct_LEP"] = acs["S1601_C05_001E"]

# --- Social Isolation ---
acs["Pct_living_alone"] = safe_pct(acs["B11001_008E"], acs["B11001_001E"])

# --- Family Structure ---
acs["Pct_single_parent"] = safe_pct(
    acs["B11003_010E"] + acs["B11003_016E"],
    acs["B11003_001E"]
)

# --- Immigration ---
acs["Pct_foreign_born"] = safe_pct(acs["B05002_013E"], acs["B05002_001E"])

# --- Disability ---
acs["Pct_disability"] = acs["S1810_C03_001E"]

# --- Commute ---
acs["Commute_time"] = acs["S0801_C01_046E"]

# --- Digital Access ---
acs["Pct_no_internet"] = acs["S2801_C02_019E"]

# ============================================================
# 9. Final dataset
# ============================================================
final_columns = [
    "GEOID",
    "NAME",
    # Income & Inequality
    "Median_income",
    "Poverty_rate",
    "Gini_index",
    # Race / Ethnicity
    "Pct_white",
    "Pct_black",
    "Pct_native",
    "Pct_asian",
    "Pct_pacific",
    "Pct_hispanic",
    # Education
    "Pct_college",
    # Age
    "Pct_elderly",
    "Pct_under18",
    # Employment
    "Unemployment_rate",
    # Insurance
    "Pct_uninsured",
    # Housing
    "Pct_renter",
    "Median_rent",
    "Rent_burden",
    "Vacancy_rate",
    "Overcrowding",
    # Language
    "Pct_LEP",
    # Social Isolation
    "Pct_living_alone",
    # Family
    "Pct_single_parent",
    # Immigration
    "Pct_foreign_born",
    # Disability
    "Pct_disability",
    # Commute
    "Commute_time",
    # Digital Access
    "Pct_no_internet",
]

final = acs[final_columns].copy()

# ============================================================
# 10. Remove unreliable tracts
# ============================================================

# Total population is B03002_001E (already in acs)
final["total_pop"] = acs["B03002_001E"]
final["total_households"] = acs["B11001_001E"]

before = len(final)

# Remove tracts with population < 100 or households < 30
final = final[
    (final["total_pop"] >= 100) &
    (final["total_households"] >= 30)
].copy()

# Drop helper columns
final = final.drop(columns=["total_pop", "total_households"])

print(f"Removed {before - len(final)} unreliable tracts "
      f"(pop < 100 or households < 30)")
print(f"Remaining: {len(final)} tracts")

# ============================================================
# 11. Summary & Export
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"Total tracts: {len(final)}")
print(f"Variables: {len(final_columns) - 2} (excluding GEOID, NAME)")

# Count per county
for county, name in [("037", "Los Angeles"), ("073", "San Diego"), ("075", "San Francisco")]:
    n = final["GEOID"].str[2:5].eq(county).sum()
    print(f"  {name}: {n} tracts")

# Missing value check
print("\nMissing values per variable:")
num_cols = [c for c in final_columns if c not in ["GEOID", "NAME"]]
for col in num_cols:
    final[col] = pd.to_numeric(final[col], errors="coerce")
    n_miss = final[col].isna().sum()
    if n_miss > 0:
        print(f"  {col:25s}: {n_miss} missing ({n_miss/len(final)*100:.1f}%)")

# Quick stats
print("\nVariable ranges:")
stats = final[num_cols].agg(["min", "max", "mean"]).round(2)
print(stats.to_string())

# Save
final.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved: {OUTPUT_CSV}")
print("Done!")
