import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
import re

file_path = '*'

# Step 1

# Import facilities Buffer Data (Service Area analysis performed in ArcMap)
fac_buf_wd_sl = gpd.read_file(file_path + 'shp/shp_fac_wd_sl.shp')
fac_buf_we_sl = gpd.read_file(file_path + 'shp/shp_fac_we_sl.shp')
fac_buf_wd_gb = gpd.read_file(file_path + 'shp/shp_fac_wd_gb.shp')
fac_buf_we_gb = gpd.read_file(file_path + 'shp/shp_fac_we_gb.shp')

 # Keep only Korean characters in facilities buffer['Name']
fac_buf_wd_gb['name'] = fac_buf_wd_gb['Name'].str.extract('([가-힣 ]+)')
fac_buf_we_gb['name'] = fac_buf_we_gb['Name'].str.extract('([가-힣 ]+)')
fac_buf_wd_sl['name'] = fac_buf_wd_sl['Name'].str.extract('([가-힣 ]+)')
fac_buf_we_sl['name'] = fac_buf_we_sl['Name'].str.extract('([가-힣 ]+)')

 # Remove spaces from names
fac_buf_wd_gb['name'] = fac_buf_wd_gb['name'].str.replace(' ', '')
fac_buf_we_gb['name'] = fac_buf_we_gb['name'].str.replace(' ', '')
fac_buf_wd_sl['name'] = fac_buf_wd_sl['name'].str.replace(' ', '')
fac_buf_we_sl['name'] = fac_buf_we_sl['name'].str.replace(' ', '')


# 의료기관 불러오기
fac_wd_gb = gpd.read_file(file_path + 'shp/fac_gb_wd.shp', encoding='euc-kr') #38
fac_we_gb = gpd.read_file(file_path + 'shp/fac_gb_we.shp', encoding='euc-kr') #38
fac_wd_sl = gpd.read_file(file_path + 'shp/fac_sl_wd.shp', encoding='euc-kr') #124
fac_we_sl = gpd.read_file(file_path + 'shp/fac_sl_we.shp', encoding='euc-kr') #122

fac_wd_gb['Personnel'] = pd.to_numeric(fac_wd_gb['Personnel'])
fac_we_gb['Personnel'] = pd.to_numeric(fac_we_gb['Personnel'])
fac_wd_sl['Personnel'] = pd.to_numeric(fac_wd_sl['Personnel'])
fac_we_sl['Personnel'] = pd.to_numeric(fac_we_sl['Personnel'])

 # Join the 'Personnel' column to facilities buffer
selected_cols1 = ['name', 'ToBreak', 'geometry']
selected_cols2 = ['name', 'Personnel']
fac_buf_wd_gb = fac_buf_wd_gb[selected_cols1].merge(fac_wd_gb[selected_cols2], on='name', how='inner')
fac_buf_we_gb = fac_buf_we_gb[selected_cols1].merge(fac_we_gb[selected_cols2], on='name', how='inner')
fac_buf_wd_sl = fac_buf_wd_sl[selected_cols1].merge(fac_wd_sl[selected_cols2], on='name', how='inner')
fac_buf_we_sl = fac_buf_we_sl[selected_cols1].merge(fac_we_sl[selected_cols2], on='name', how='inner')

# Import Population Center Points
point_pop_wd_gb = gpd.read_file(file_path + 'shp/point_pop_wd_gb.shp')
point_pop_we_gb = gpd.read_file(file_path + 'shp/point_pop_we_gb.shp')
point_pop_wd_sl = gpd.read_file(file_path + 'shp/point_pop_wd_sl.shp')
point_pop_we_sl = gpd.read_file(file_path + 'shp/point_pop_we_sl.shp')

# Perform spatial join of facilities buffer to population center points
fac_buf_dfs = [fac_buf_wd_gb, fac_buf_we_gb, fac_buf_wd_sl, fac_buf_we_sl]
pop_dfs = [point_pop_wd_gb, point_pop_we_gb, point_pop_wd_sl, point_pop_we_sl]
for df, pop_df in zip(fac_buf_dfs, pop_dfs):
    result = gpd.sjoin(df, pop_df, how="inner", predicate="intersects")
    sum_pop_rate = result.groupby('name')['Personnel'].sum().reset_index()
    sum_pop_rate.rename(columns={'Personnel': 'Personnel_sum'}, inplace=True)
    df['Personnel_sum'] = df['name'].map(sum_pop_rate.set_index('name')['Personnel_sum'])
    df['Personnel_sum'] = pd.to_numeric(df['Personnel_sum'], errors='coerce')


 # Assign weights to 'pop_rate_sum'
fac_buf_wd_gb['pop_rate_sum_wgt'] = np.select([fac_buf_wd_gb['ToBreak'] == 19550.0, 
                                               fac_buf_wd_gb['ToBreak'] == 13033.0, 
                                               fac_buf_wd_gb['ToBreak'] == 6517.0], 
                                              [fac_buf_wd_gb['Personnel_sum'], 
                                               fac_buf_wd_gb['Personnel_sum'] * 0.68, 
                                               fac_buf_wd_gb['Personnel_sum'] * 0.22],
                                               default=0)
fac_buf_we_gb['pop_rate_sum_wgt'] = np.select([fac_buf_we_gb['ToBreak'] == 19550.0, 
                                               fac_buf_we_gb['ToBreak'] == 13033.0, 
                                               fac_buf_we_gb['ToBreak'] == 6517.0], 
                                              [fac_buf_we_gb['Personnel_sum'], 
                                               fac_buf_we_gb['Personnel_sum'] * 0.68, 
                                               fac_buf_we_gb['Personnel_sum'] * 0.22], 
                                               default=0)
fac_buf_wd_sl['pop_rate_sum_wgt'] = np.select([fac_buf_wd_sl['ToBreak'] == 11550.0, 
                                               fac_buf_wd_sl['ToBreak'] == 7000.0, 
                                               fac_buf_wd_sl['ToBreak'] == 3850.0], 
                                              [fac_buf_wd_sl['Personnel_sum'], 
                                               fac_buf_wd_sl['Personnel_sum'] * 0.68, 
                                               fac_buf_wd_sl['Personnel_sum'] * 0.22], 
                                               default=0)
fac_buf_we_sl['pop_rate_sum_wgt'] = np.select([fac_buf_we_sl['ToBreak'] == 11550.0, 
                                               fac_buf_we_sl['ToBreak'] == 7000.0, 
                                               fac_buf_we_sl['ToBreak'] == 3850.0], 
                                              [fac_buf_we_sl['Personnel_sum'], 
                                               fac_buf_we_sl['Personnel_sum'] * 0.68, 
                                               fac_buf_we_sl['Personnel_sum'] * 0.22], 
                                               default=0)

 # Calculate the weighted sum of 'pop_rate_sum_wgt' for each hospital and 'ProToPop'
grouped = fac_buf_wd_gb.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_wd_gb = fac_wd_gb.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_wd_gb['Personnel'] = pd.to_numeric(fac_wd_gb['Personnel'], errors='coerce')
fac_wd_gb['ProToPop'] = fac_wd_gb['Personnel'] / fac_wd_gb['pop_rate_sum_wgt']

grouped = fac_buf_we_gb.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_we_gb = fac_we_gb.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_we_gb['Personnel'] = pd.to_numeric(fac_we_gb['Personnel'], errors='coerce')
fac_we_gb['ProToPop'] = fac_we_gb['Personnel'] / fac_we_gb['pop_rate_sum_wgt']

grouped = fac_buf_wd_sl.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_wd_sl = fac_wd_sl.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_wd_sl['Personnel'] = pd.to_numeric(fac_wd_sl['Personnel'], errors='coerce')
fac_wd_sl['ProToPop'] = fac_wd_sl['Personnel'] / fac_wd_sl['pop_rate_sum_wgt']

grouped = fac_buf_we_sl.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_we_sl = fac_we_sl.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_we_sl['Personnel'] = pd.to_numeric(fac_we_sl['Personnel'], errors='coerce')
fac_we_sl['ProToPop'] = fac_we_sl['Personnel'] / fac_we_sl['pop_rate_sum_wgt']


# Step 2

# Load population data
point_pop_wd_gb = gpd.read_file(file_path + 'shp/point_pop_wd_gb.shp')
point_pop_we_gb = gpd.read_file(file_path + 'shp/point_pop_we_gb.shp')
point_pop_wd_sl = gpd.read_file(file_path + 'shp/point_pop_wd_sl.shp')
point_pop_we_sl = gpd.read_file(file_path + 'shp/point_pop_we_sl.shp')

# Convert 'SGG_CD' to string
point_pop_wd_gb['SIGUNGU_EN'] = point_pop_wd_gb['SIGUNGU_EN'].astype(str)
point_pop_we_gb['SIGUNGU_EN'] = point_pop_we_gb['SIGUNGU_EN'].astype(str)
point_pop_wd_sl['SIGUNGU_EN'] = point_pop_wd_sl['SIGUNGU_EN'].astype(str)
point_pop_we_sl['SIGUNGU_EN'] = point_pop_we_sl['SIGUNGU_EN'].astype(str)

# Load population buffer data (Performed Service Area analysis in ArcMap)
pop_buf_wd_gb = gpd.read_file(file_path + 'shp/shp_pop_wd_gb.shp')
pop_buf_we_gb = gpd.read_file(file_path + 'shp/shp_pop_we_gb.shp')
pop_buf_wd_sl = gpd.read_file(file_path + 'shp/shp_pop_wd_sl.shp')
pop_buf_we_sl = gpd.read_file(file_path + 'shp/shp_pop_we_sl.shp')

pop_buf_wd_gb['SIGUNGU_EN'] = pop_buf_wd_gb['Name'].astype(str)
pop_buf_we_gb['SIGUNGU_EN'] = pop_buf_we_gb['Name'].astype(str)
pop_buf_wd_sl['SIGUNGU_EN'] = pop_buf_wd_sl['Name'].astype(str)
pop_buf_we_sl['SIGUNGU_EN'] = pop_buf_we_sl['Name'].astype(str)


def extract_alphabets(text):
    return re.sub(r'[^a-zA-Z]', '', text)

pop_buf_wd_gb['SIGUNGU_EN'] = pop_buf_wd_gb['SIGUNGU_EN'].apply(extract_alphabets)
pop_buf_we_gb['SIGUNGU_EN'] = pop_buf_we_gb['SIGUNGU_EN'].apply(extract_alphabets)
pop_buf_wd_sl['SIGUNGU_EN'] = pop_buf_wd_sl['SIGUNGU_EN'].apply(extract_alphabets)
pop_buf_we_sl['SIGUNGU_EN'] = pop_buf_we_sl['SIGUNGU_EN'].apply(extract_alphabets)

# Join 'SGG_CD' and 'pop_rate' to population buffer data
selected_cols1 = ['SIGUNGU_EN', 'ToBreak', 'geometry']
selected_cols2 = ['SIGUNGU_EN', 'rate']
pop_buf_wd_gb = pop_buf_wd_gb[selected_cols1].merge(point_pop_wd_gb[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_we_gb = pop_buf_we_gb[selected_cols1].merge(point_pop_we_gb[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_wd_sl = pop_buf_wd_sl[selected_cols1].merge(point_pop_wd_sl[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_we_sl = pop_buf_we_sl[selected_cols1].merge(point_pop_we_sl[selected_cols2], on='SIGUNGU_EN', how='inner')

# Join hospital 'ProToPop' to population buffer data
dfs = [pop_buf_wd_gb, pop_buf_we_gb, pop_buf_wd_sl, pop_buf_we_sl]
fac_dfs = [fac_wd_gb, fac_we_gb, fac_wd_sl, fac_we_sl]
for df, fac_df in zip(dfs, fac_dfs):
    result = gpd.sjoin(df, fac_df, how="inner", predicate="intersects")
    sum_ProToPop = result.groupby('SIGUNGU_EN')['ProToPop'].sum().reset_index()
    sum_ProToPop.rename(columns={'ProToPop': 'ProToPop_sum'}, inplace=True)
    df['ProToPop_sum'] = df['SIGUNGU_EN'].map(sum_ProToPop.set_index('SIGUNGU_EN')['ProToPop_sum'])

# Assign weights to 'e2sfca' in population buffer data
pop_buf_wd_gb['e2sfca'] = np.select(
    [pop_buf_wd_gb['ToBreak'] == 19550.0, 
     pop_buf_wd_gb['ToBreak'] == 13030.0, 
     pop_buf_wd_gb['ToBreak'] == 6520.0],
    [pop_buf_wd_gb['ProToPop_sum'], 
     pop_buf_wd_gb['ProToPop_sum'] * 0.68, 
     pop_buf_wd_gb['ProToPop_sum'] * 0.22],
     default=0
)
pop_buf_we_gb['e2sfca'] = np.select(
    [pop_buf_we_gb['ToBreak'] == 19550.0, 
     pop_buf_we_gb['ToBreak'] == 13030.0, 
     pop_buf_we_gb['ToBreak'] == 6520.0],
    [pop_buf_we_gb['ProToPop_sum'], 
     pop_buf_we_gb['ProToPop_sum'] * 0.68, 
     pop_buf_we_gb['ProToPop_sum'] * 0.22],
     default=0
)
pop_buf_wd_sl['e2sfca'] = np.select(
    [pop_buf_wd_sl['ToBreak'] == 11550.0, 
     pop_buf_wd_sl['ToBreak'] == 7000.0, 
     pop_buf_wd_sl['ToBreak'] == 3850.0],
    [pop_buf_wd_sl['ProToPop_sum'], 
     pop_buf_wd_sl['ProToPop_sum'] * 0.68, 
     pop_buf_wd_sl['ProToPop_sum'] * 0.22],
     default=0
)
pop_buf_we_sl['e2sfca'] = np.select(
    [pop_buf_we_sl['ToBreak'] == 11550.0, 
     pop_buf_we_sl['ToBreak'] == 7000.0, 
     pop_buf_we_sl['ToBreak'] == 3850.0],
    [pop_buf_we_sl['ProToPop_sum'], 
     pop_buf_we_sl['ProToPop_sum'] * 0.68, 
     pop_buf_we_sl['ProToPop_sum'] * 0.22],
     default=0
)

# Sum 'e2sfca' for each 'SGG_CD'
pop_buf_wd_gb = pop_buf_wd_gb.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_we_gb = pop_buf_we_gb.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_wd_sl = pop_buf_wd_sl.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_we_sl = pop_buf_we_sl.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()

# Load municipal boundary data
shp_gb = gpd.read_file(file_path + 'shp/shp_gb.shp', encoding='euc-kr')
shp_sl = gpd.read_file(file_path + 'shp/shp_sl.shp', encoding='euc-kr')

# Convert municipal code to string
shp_gb['SIGUNGU_EN'] = shp_gb['SIGUNGU_EN'].astype(str)
shp_sl['SIGUNGU_EN'] = shp_sl['SIGUNGU_EN'].astype(str)

# Join 'e2sfca' to municipal boundaries
selected_cols1 = ['SIGUNGU_EN', 'SIGUNGU_CD', 'geometry']
selected_cols2 = ['SIGUNGU_EN', 'e2sfca']
shp_wd_gb = shp_gb[selected_cols1].merge(pop_buf_wd_gb[selected_cols2], on='SIGUNGU_EN', how='left')
shp_we_gb = shp_gb[selected_cols1].merge(pop_buf_we_gb[selected_cols2], on='SIGUNGU_EN', how='left')
shp_wd_sl = shp_sl[selected_cols1].merge(pop_buf_wd_sl[selected_cols2], on='SIGUNGU_EN', how='left')
shp_we_sl = shp_sl[selected_cols1].merge(pop_buf_we_sl[selected_cols2], on='SIGUNGU_EN', how='left')

# Export shapefiles
shp_wd_gb.to_file(file_path + 'shp/shp_e2sfca_wd_gb.shp')
shp_we_gb.to_file(file_path + 'shp/shp_e2sfca_we_gb.shp')
shp_wd_sl.to_file(file_path + 'shp/shp_e2sfca_wd_sl.shp')
shp_we_sl.to_file(file_path + 'shp/shp_e2sfca_we_sl.shp')



