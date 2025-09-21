# =========================================
# 0. Import libraries
# =========================================
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# =========================================
# 1. Load mobility data
# =========================================
# Set workspace path
workspace = "*/data/"

# Import raw mobility data
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

# =========================================
# 2. Analysis with 2023 Summer LST
# =========================================
lst = pd.read_csv(workspace + "1 processed/image/aggregated_lst.csv")
lst["K_MEAN"] = lst["MEAN"]                   # keep Kelvin
lst["MEAN"] = lst["MEAN"] - 273.15            # convert to Celsius
lst["MEAN_GROUP"] = pd.qcut(lst["MEAN"], q=3, labels=["Low", "Median", "High"]) # 901 CBGs each

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

# Summarize visitors by mobility type
mobility_summary_lst = (
    df_lst.groupby("mobility")["visitor"]
    .sum()
    .reset_index()
    .sort_values("visitor", ascending=False)
)
print("=== Mobility Summary (2023 Summer LST) ===")
print(mobility_summary_lst)

'''
=== Mobility Summary (2023 Summer LST) ===
  mobility   visitor
0       HH  30845351
8       MM  25800937
6       MH  24161518
4       LL  21302219
5       LM  19125274
2       HM  18897957
3       LH  16106777
7       ML  15976645
'''

# Heat vs Non-heat comparison (top 10% vs bottom 10%)
threshold_heat = lst["MEAN"].quantile(0.9)
threshold_nonheat = lst["MEAN"].quantile(0.1)
df_heat = df_lst[df_lst["home_lst"] >= threshold_heat]       # 327,518 rows
df_nonheat = df_lst[df_lst["home_lst"] <= threshold_nonheat] # 259,997 rows

# T-test and effect size
t_stat, p_val = stats.ttest_ind(df_heat["visitor"], df_nonheat["visitor"], equal_var=False)
mean_diff = df_heat["visitor"].mean() - df_nonheat["visitor"].mean()
pooled_std = np.sqrt((df_heat["visitor"].var(ddof=1) + df_nonheat["visitor"].var(ddof=1)) / 2)
cohens_d = mean_diff / pooled_std

print("\n=== Heat vs Non-heat (LST) ===")
print(f"T-stat: {t_stat}, P-value: {p_val}")
print(f"Cohen's d: {cohens_d}")

'''
=== Heat vs Non-heat (LST) ===
T-stat: -6.391228160552242, P-value: 1.646812720691379e-10
Cohen's d: -0.016595520613224047
'''

# =========================================
# 3. Analysis with Sen's Slope (2000–2023)
# =========================================
senslope = pd.read_csv(workspace + "1 processed/image/aggregated_senslope.csv")
senslope["MEAN_GROUP"] = pd.qcut(senslope["MEAN"], q=3, labels=["Low", "Median", "High"])

# Merge mobility with Sen's slope (home & poi)
df_sens = df.merge(
    senslope[["GEOID", "MEAN", "MEAN_GROUP"]].rename(columns={"GEOID": "home_cbg", "MEAN": "home_sens", "MEAN_GROUP": "home_trend"}),
    left_on="visitor_home_cbgs",
    right_on="home_cbg",
    how="left"
)
df_sens = df_sens.merge(
    senslope[["GEOID", "MEAN", "MEAN_GROUP"]].rename(columns={"GEOID": "poi_cbg", "MEAN": "poi_sens", "MEAN_GROUP": "poi_trend"}),
    left_on="poi_cbg",
    right_on="poi_cbg",
    how="left"
)
df_sens = df_sens.rename(columns={"date_range_start": "date"})

# Create mobility category based on Sen's slope
df_sens["mobility"] = df_sens["home_trend"].str[0] + df_sens["poi_trend"].str[0]

# Summarize visitors by mobility type
mobility_summary_sens = (
    df_sens.groupby("mobility")["visitor"]
    .sum()
    .reset_index()
    .sort_values("visitor", ascending=False)
)
print("\n=== Mobility Summary (Sen's slope) ===")
print(mobility_summary_sens)

'''
=== Mobility Summary (Sen's slope) ===
  mobility   visitor
4       LL  38580740
7       ML  23621807
8       MM  21166479
1       HL  20555947
0       HH  19050309
5       LM  17993256
2       HM  17236908
6       MH  14035191
3       LH  13226954
'''

# Heat vs Non-heat comparison (Sen's slope: top 10% vs bottom 10%)
threshold_sens_high = senslope["MEAN"].quantile(0.9)
threshold_sens_low = senslope["MEAN"].quantile(0.1)
df_heat_sens = df_sens[df_sens["home_sens"] >= threshold_sens_high]
df_nonheat_sens = df_sens[df_sens["home_sens"] <= threshold_sens_low]

t_stat_sens, p_val_sens = stats.ttest_ind(df_heat_sens["visitor"], df_nonheat_sens["visitor"], equal_var=False)
mean_diff_sens = df_heat_sens["visitor"].mean() - df_nonheat_sens["visitor"].mean()
pooled_std_sens = np.sqrt((df_heat_sens["visitor"].var(ddof=1) + df_nonheat_sens["visitor"].var(ddof=1)) / 2)
cohens_d_sens = mean_diff_sens / pooled_std_sens

print("\n=== Heat vs Non-heat (Sen's slope) ===")
print(f"T-stat: {t_stat_sens}, P-value: {p_val_sens}")
print(f"Cohen's d: {cohens_d_sens}")

'''
=== Heat vs Non-heat (Sen's slope) ===
T-stat: -22.400376855335267, P-value: 4.322592327481363e-111
Cohen's d: -0.05268154125687771
'''

# =========================================
# 4. Save outputs for mapping
# =========================================
cbg = gpd.read_file(workspace + "0 raw/tl_2018_04_bg/tl_2018_04_bg_Maricopa_Pinal.shp")
cbg["home_cbg"] = cbg["GEOID"].str[1:]  # align with GEOID format

# Dominant mobility (LST)
tmp_lst = (
    df_lst.groupby(["home_cbg", "mobility"], as_index=False)["visitor"]
    .sum()
    .rename(columns={"visitor": "vis_sum"})
)
tmp_lst_sorted = tmp_lst.sort_values(["home_cbg", "vis_sum"], ascending=[True, False])
home_mobility_lst = tmp_lst_sorted.drop_duplicates("home_cbg").astype(str)
gdf_lst = cbg.merge(home_mobility_lst, on="home_cbg", how="left")
gdf_lst = gdf_lst.astype({'GEOID_int': 'string'})
gdf_lst.to_file(workspace + "1 processed/mobility/home_mobility_map_lst.shp", driver="ESRI Shapefile")

# Dominant mobility (Sen's slope)
tmp_sens = (
    df_sens.groupby(["home_cbg", "mobility"], as_index=False)["visitor"]
    .sum()
    .rename(columns={"visitor": "vis_sum"})
)
tmp_sens_sorted = tmp_sens.sort_values(["home_cbg", "vis_sum"], ascending=[True, False])
home_mobility_sens = tmp_sens_sorted.drop_duplicates("home_cbg").astype(str)
gdf_sens = cbg.merge(home_mobility_sens, on="home_cbg", how="left")
gdf_sens = gdf_sens.astype({'GEOID_int': 'string'})
gdf_sens.to_file(workspace + "1 processed/mobility/home_mobility_map_senslope.shp", driver="ESRI Shapefile")

# =========================================
# 4. Cross-classification
# =========================================
# Cross-classification: Short-term LST vs Long-term Sen's slope
def classify(row):
    if row["home_lst"] >= threshold_heat and row["home_sens"] >= threshold_sens_high:
        return "High LST + High Trend"   # continuously hot (potential adaptation)
    elif row["home_lst"] >= threshold_heat and row["home_sens"] < threshold_sens_high:
        return "High LST + Low Trend"    # recently hot (less adapted)
    elif row["home_lst"] < threshold_heat and row["home_sens"] >= threshold_sens_high:
        return "Low LST + High Trend"    # future risk (warming fast but not hot yet)
    else:
        return "Low LST + Low Trend"     # baseline (cool & stable)

# Merge both LST and Sen's slope into one mobility dataset
df_mobility = df.merge(
    lst[["GEOID", "MEAN"]].rename(columns={"GEOID": "home_cbg", "MEAN": "home_lst"}),
    left_on="visitor_home_cbgs", right_on="home_cbg", how="left"
)
df_mobility = df_mobility.merge(
    senslope[["GEOID", "MEAN"]].rename(columns={"GEOID": "home_cbg", "MEAN": "home_sens"}),
    left_on="visitor_home_cbgs", right_on="home_cbg", how="left"
)
df_mobility = df_mobility.rename(columns={"date_range_start": "date"})
df_mobility = df_mobility.drop(columns=["home_cbg_y"], errors="ignore")
df_mobility = df_mobility.rename(columns={"home_cbg_x": "home_cbg"})
df_mobility = df_mobility[["home_cbg", "poi_cbg", "visitor", "date", "home_lst", "home_sens"]]

# Assign heat category
df_mobility["heat_category"] = df_mobility.apply(classify, axis=1)

# Aggregate mobility by category
category_summary = (
    df_mobility.groupby("heat_category")["visitor"]
    .agg(["sum", "mean", "count"])
    .reset_index()
    .sort_values("sum", ascending=False)
)
print("\n=== Mobility by Heat Category (LST × Sen's slope) ===")
print(category_summary)

'''
=== Mobility by Heat Category (LST × Sen's slope) ===
           heat_category        sum       mean    count
3    Low LST + Low Trend  152952263  55.709599  2745528
2   Low LST + High Trend   15553515  55.793360   278770
1   High LST + Low Trend   12209110  54.702764   223190
0  High LST + High Trend    4752703  45.555393   104328
'''

# ANOVA test across the four categories
groups = [
    df_mobility[df_mobility["heat_category"] == cat]["visitor"]
    for cat in df_mobility["heat_category"].unique()
]
f_stat, p_val = stats.f_oneway(*groups)
print("\nANOVA F:", f_stat, "p-value:", p_val)
# Example result: ANOVA F: 54.03, p-value: 6.52e-35

# Tukey HSD post-hoc test
tukey = pairwise_tukeyhsd(
    endog=df_mobility["visitor"],        # dependent variable
    groups=df_mobility["heat_category"], # group variable
    alpha=0.05
)
print(tukey)
'''
               Multiple Comparison of Means - Tukey HSD, FWER=0.05               
=================================================================================
        group1               group2        meandiff   p-adj   lower   upper  reject
---------------------------------------------------------------------------------
High LST + High Trend  High LST + Low Trend   9.1474  0.0     6.6938 11.601   True
High LST + High Trend  Low LST + High Trend  10.238   0.0     7.8636 12.6124  True
High LST + High Trend  Low LST + Low Trend   10.1542  0.0     8.0906 12.2178  True
High LST + Low Trend   Low LST + High Trend   1.0906  0.4328 -0.7676  2.9488  False
High LST + Low Trend   Low LST + Low Trend    1.0068  0.2751 -0.4332  2.4468  False
Low LST + High Trend   Low LST + Low Trend   -0.0838  0.9984 -1.3842  1.2167  False
---------------------------------------------------------------------------------

# Interpretation:
# High LST + High Trend (HH): Significantly higher mobility than all other categories.
# → Suggests adaptation: areas continuously exposed to heat maintain mobility levels.
#
# High LST + Low Trend (HL) vs Low LST groups (LH, LL): No significant difference.
# → Suggests recently heated areas may lack adaptation, showing mobility reduction.
#
# Low LST groups (LH vs LL): No difference.
# → Suggests limited short-term impact, but LH areas remain at future risk.
'''
