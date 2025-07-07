from simpledbf import Dbf
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

workspace = 'D:/heat/data/variables/'

# Import census tract shp file
gdf = gpd.read_file("D:/heat/data/boundary/nyc_tracts.shp") # 2,327 rows
variables = pd.DataFrame()
variables['Geography'] = gdf[['GEOIDFQ']].copy()

# =====================================================================
# RAW DATA                                                                            
# =====================================================================
age_sex = pd.read_csv(workspace + 'Age and sex/ACSST5Y2023.S0101-Data.csv', header=1, low_memory=False)
race = pd.read_csv(workspace + 'Race/DECENNIALPL2020.P1-Data.csv', header=1, low_memory=False)
income = pd.read_csv(workspace + 'ACSST5Y2023.S1903/ACSST5Y2023.S1903-Data.csv', header=1, low_memory=False)
hvi = DBF(workspace + 'hvi_by_tracts.dbf', load=True)
hvi = pd.DataFrame(iter(hvi))

# =====================================================================
# 1. SEX AND AGE                                                                           
# =====================================================================
# male ratio
age_sex['male'] = age_sex['Estimate!!Male!!Total population'] / age_sex['Estimate!!Total!!Total population'] * 100
male_ratio = age_sex[['Geography', 'male']]

# 65 and plus ratio
age_sex['age65plus'] = (
    age_sex['Estimate!!Total!!Total population!!SELECTED AGE CATEGORIES!!65 years and over'] /
    age_sex['Estimate!!Total!!Total population']
) * 100
age_65_plus_ratio = age_sex[['Geography','age65plus']]

# under 18 ratio
age_sex['under18'] = (
    age_sex['Estimate!!Total!!Total population!!SELECTED AGE CATEGORIES!!Under 18 years'] /
    age_sex['Estimate!!Total!!Total population']
) * 100
age_under18_ratio = age_sex[['Geography','under18']]

# =====================================================================
# 2. RACE                                                                               
# =====================================================================
# White ratio
race['white'] = race[' !!Total:!!Population of one race:!!White alone'] / race[' !!Total:'] * 100
white_ratio = race[['Geography', 'white']]

# Black ratio
race['black'] = race[' !!Total:!!Population of one race:!!Black or African American alone'] / race[' !!Total:'] * 100
black_ratio = race[['Geography', 'black']]

# Native ratio
race['native'] = race[' !!Total:!!Population of one race:!!American Indian and Alaska Native alone'] / race[' !!Total:'] * 100
native_ratio = race[['Geography', 'native']]

# Asian ratio
race['asian'] = race[' !!Total:!!Population of one race:!!Asian alone'] / race[' !!Total:'] * 100
asian_ratio = race[['Geography', 'asian']]

# =====================================================================
# 3. INCOME                                                                               
# =====================================================================
# Median income


# =====================================================================
# TABLE JOIN                                                                        
# =====================================================================
variables = variables.merge(male_ratio, on="Geography", how="left")
variables = variables.merge(age_under18_ratio, on="Geography", how="left")
variables = variables.merge(age_65_plus_ratio, on="Geography", how="left")
variables = variables.merge(white_ratio, on="Geography", how="left")
variables = variables.merge(black_ratio, on="Geography", how="left")
variables = variables.merge(native_ratio, on="Geography", how="left")
variables = variables.merge(asian_ratio, on="Geography", how="left")

variables = variables.drop_duplicates(subset='Geography')
variables = variables.rename(columns={'Geography': 'GEOIDFQ'})

# =====================================================================
# HEAT VULNERABILITY INDEX (HVI)                                                                             
# =====================================================================
hvi = hvi[['GEOIDFQ', 'HVI']]
variables = variables.merge(hvi, on="GEOIDFQ", how="left")
variables.to_csv(workspace + 'variables.csv')

# =====================================================================
# RESULTS: varialbes by census tract points        
# tracts_variables.shp
# =====================================================================
# Spatial join to census tract points
gdf_point = gpd.read_file("D:/heat/data/boundary/study_area_point.shp")
gdf_point = gdf_point[['GEOIDFQ', 'geometry']]
gdf_point = gdf_point.merge(variables, on="GEOIDFQ", how="left")
gdf_point.to_file("D:/heat/data/boundary/tract_variables.shp", driver="ESRI Shapefile")
