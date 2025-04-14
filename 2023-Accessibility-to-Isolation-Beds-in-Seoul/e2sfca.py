# Title : E2SFCA Analysis
# Author : Yubin Lee
# Date : 2023-10-13

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point

file_path = './data/shp/arc/'

# Step 1

# Facilities ID
 # Hospital List Data
hospital_list = [
    '의료법인왜관병원', '맘존 여성병원', '현대병원', '한성의원', '서울힐링요양병원', '송파그랜드요양병원',
    '서울제일요양병원', '에스엠씨요양병원', '코리아병원', '빠른병원', '닥터김앤박요양병원', '강동우리들요양병원',
    '송파365의원', '아이엠유의원', '다민한의원', '서울한성의원', '자곡365의원', '24시열린의원', '봄날애의원',
    '편한내일마취통증의학과의원', '연세바움치과의원', '구의센트럴내과의원', '미톡스외과의원', '숲길신경과의원',
    '조아성형외과의원', '서울하트내과의원', '365코이이비인후과의원', '성북성심의원', '연세곰돌이소아청소년과의원'
]
 # Create a DataFrame
id_list = pd.DataFrame({'ID': range(1, len(hospital_list) + 1), 'name': hospital_list})
id_list['name'] = id_list['name'].str.replace(' ', '') # 띄어쓰기 제거

# Facilities Location Data
fac_wd_gb = gpd.read_file(file_path + 'fac_wd_gb.shp')
fac_we_gb = gpd.read_file(file_path + 'fac_we_gb.shp')
fac_wd_sl = gpd.read_file(file_path + 'fac_wd_sl.shp')
fac_we_sl = gpd.read_file(file_path + 'fac_we_sl.shp')

 # Rename '한성의원' to '서울한성의원'
fac_wd_sl['name'] = fac_wd_sl['name'].replace('한성의원', '서울한성의원')
fac_we_sl['name'] = fac_we_sl['name'].replace('한성의원', '서울한성의원')

 # Remove spaces from names
fac_wd_gb['name'] = fac_wd_gb['name'].str.replace(' ', '')
fac_we_gb['name'] = fac_we_gb['name'].str.replace(' ', '')
fac_wd_sl['name'] = fac_wd_sl['name'].str.replace(' ', '')
fac_we_sl['name'] = fac_we_sl['name'].str.replace(' ', '')

 # Facilities Location + ID Join
selected_cols1 = ['name', 'Personnel', 'geometry']
selected_cols2 = ['name', 'ID']
fac_wd_gb = fac_wd_gb[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_we_gb = fac_we_gb[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_wd_sl = fac_wd_sl[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_we_sl = fac_we_sl[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')

# Import facilities Buffer Data (Service Area analysis performed in ArcMap)
fac_buf_wd_gb = gpd.read_file(file_path + 'sfca/fac_buf_wd_gb.shp')
fac_buf_we_gb = gpd.read_file(file_path + 'sfca/fac_buf_we_gb.shp')
fac_buf_wd_sl = gpd.read_file(file_path + 'sfca/fac_buf_wd_sl.shp')
fac_buf_we_sl = gpd.read_file(file_path + 'sfca/fac_buf_we_sl.shp')

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

 # Rename '한성의원' to '서울한성의원'
fac_buf_wd_sl['name'] = fac_buf_wd_sl['name'].replace('한성의원', '서울한성의원')
fac_buf_we_sl['name'] = fac_buf_we_sl['name'].replace('한성의원', '서울한성의원')

 # facilities buffer + ID join
selected_cols1 = ['name', 'ToBreak', 'geometry']
selected_cols2 = ['name', 'ID']
fac_buf_wd_gb = fac_buf_wd_gb[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_buf_we_gb = fac_buf_we_gb[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_buf_wd_sl = fac_buf_wd_sl[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')
fac_buf_we_sl = fac_buf_we_sl[selected_cols1].merge(id_list[selected_cols2], on='name', how='inner')

 # Join the 'Personnel' column to facilities buffer
selected_cols1 = ['name', 'ToBreak', 'geometry']
selected_cols2 = ['name', 'Personnel']
fac_buf_wd_gb = fac_buf_wd_gb[selected_cols1].merge(fac_wd_gb[selected_cols2], on='name', how='inner')
fac_buf_we_gb = fac_buf_we_gb[selected_cols1].merge(fac_we_gb[selected_cols2], on='name', how='inner')
fac_buf_wd_sl = fac_buf_wd_sl[selected_cols1].merge(fac_wd_sl[selected_cols2], on='name', how='inner')
fac_buf_we_sl = fac_buf_we_sl[selected_cols1].merge(fac_we_sl[selected_cols2], on='name', how='inner')

# Import Population Center Points
point_pop_wd_gb = gpd.read_file(file_path + 'point_pop_wd_gb.shp')
point_pop_we_gb = gpd.read_file(file_path + 'point_pop_we_gb.shp')
point_pop_wd_sl = gpd.read_file(file_path + 'point_pop_wd_sl.shp')
point_pop_we_sl = gpd.read_file(file_path + 'point_pop_we_sl.shp')

# Perform spatial join of facilities buffer to population center points
fac_buf_dfs = [fac_buf_wd_gb, fac_buf_we_gb, fac_buf_wd_sl, fac_buf_we_sl]
pop_dfs = [point_pop_wd_gb, point_pop_we_gb, point_pop_wd_sl, point_pop_we_sl]
for df, pop_df in zip(fac_buf_dfs, pop_dfs):
    result = gpd.sjoin(df, pop_df, how="inner", predicate="intersects")
    sum_pop_rate = result.groupby('name')['pop_rate'].sum().reset_index()
    sum_pop_rate.rename(columns={'pop_rate': 'pop_rate_sum'}, inplace=True)
    df['pop_rate_sum'] = df['name'].map(sum_pop_rate.set_index('name')['pop_rate_sum'])

 # Assign weights to 'pop_rate_sum'
fac_buf_wd_gb['pop_rate_sum_wgt'] = np.select([fac_buf_wd_gb['ToBreak'] == 19550.0, fac_buf_wd_gb['ToBreak'] == 13030.0, fac_buf_wd_gb['ToBreak'] == 6520.0], [fac_buf_wd_gb['pop_rate_sum'], fac_buf_wd_gb['pop_rate_sum'] * 0.68, fac_buf_wd_gb['pop_rate_sum'] * 0.22], default=0)
fac_buf_we_gb['pop_rate_sum_wgt'] = np.select([fac_buf_we_gb['ToBreak'] == 19550.0, fac_buf_we_gb['ToBreak'] == 13030.0, fac_buf_we_gb['ToBreak'] == 6520.0], [fac_buf_we_gb['pop_rate_sum'], fac_buf_we_gb['pop_rate_sum'] * 0.68, fac_buf_we_gb['pop_rate_sum'] * 0.22], default=0)
fac_buf_wd_sl['pop_rate_sum_wgt'] = np.select([fac_buf_wd_sl['ToBreak'] == 11550.0, fac_buf_wd_sl['ToBreak'] == 7000.0, fac_buf_wd_sl['ToBreak'] == 3850.0], [fac_buf_wd_sl['pop_rate_sum'], fac_buf_wd_sl['pop_rate_sum'] * 0.68, fac_buf_wd_sl['pop_rate_sum'] * 0.22], default=0)
fac_buf_we_sl['pop_rate_sum_wgt'] = np.select([fac_buf_we_sl['ToBreak'] == 11550.0, fac_buf_we_sl['ToBreak'] == 7000.0, fac_buf_we_sl['ToBreak'] == 3850.0], [fac_buf_we_sl['pop_rate_sum'], fac_buf_we_sl['pop_rate_sum'] * 0.68, fac_buf_we_sl['pop_rate_sum'] * 0.22], default=0)

 # Calculate the weighted sum of 'pop_rate_sum_wgt' for each hospital and 'ProToPop'
grouped = fac_buf_wd_gb.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_wd_gb = fac_wd_gb.merge(grouped, on='name')
fac_wd_gb['ProToPop'] = fac_wd_gb['Personnel'] / fac_wd_gb['pop_rate_sum_wgt']

grouped = fac_buf_we_gb.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_we_gb = fac_we_gb.merge(grouped, on='name')
fac_we_gb['ProToPop'] = fac_we_gb['Personnel'] / fac_we_gb['pop_rate_sum_wgt']

grouped = fac_buf_wd_sl.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_wd_sl = fac_wd_sl.merge(grouped, on='name')
fac_wd_sl['ProToPop'] = fac_wd_sl['Personnel'] / fac_wd_sl['pop_rate_sum_wgt']

grouped = fac_buf_we_sl.groupby('name')['pop_rate_sum_wgt'].sum().reset_index()
fac_we_sl = fac_we_sl.merge(grouped, on='name')
fac_we_sl['ProToPop'] = fac_we_sl['Personnel'] / fac_we_sl['pop_rate_sum_wgt']


# Step 2

# Load population data
point_pop_wd_gb = gpd.read_file(file_path + 'point_pop_wd_gb.shp')
point_pop_we_gb = gpd.read_file(file_path + 'point_pop_we_gb.shp')
point_pop_wd_sl = gpd.read_file(file_path + 'point_pop_wd_sl.shp')
point_pop_we_sl = gpd.read_file(file_path + 'point_pop_we_sl.shp')

# Convert 'SGG_CD' to string
point_pop_wd_gb['SGG_CD'] = point_pop_wd_gb['SGG_CD'].astype(str)
point_pop_we_gb['SGG_CD'] = point_pop_we_gb['SGG_CD'].astype(str)
point_pop_wd_sl['SGG_CD'] = point_pop_wd_sl['SGG_CD'].astype(str)
point_pop_we_sl['SGG_CD'] = point_pop_we_sl['SGG_CD'].astype(str)

# Remove spaces from 'SGG_CD'
point_pop_wd_gb['SGG_CD'] = point_pop_wd_gb['SGG_CD'].str.replace(' ', '')
point_pop_we_gb['SGG_CD'] = point_pop_we_gb['SGG_CD'].str.replace(' ', '')
point_pop_wd_sl['SGG_CD'] = point_pop_wd_sl['SGG_CD'].str.replace(' ', '')
point_pop_we_sl['SGG_CD'] = point_pop_we_sl['SGG_CD'].str.replace(' ', '')

# Load population buffer data (Performed Service Area analysis in ArcMap)
pop_buf_wd_gb = gpd.read_file(file_path + 'sfca/pop_buf_wd_gb.shp')
pop_buf_we_gb = gpd.read_file(file_path + 'sfca/pop_buf_we_gb.shp')
pop_buf_wd_sl = gpd.read_file(file_path + 'sfca/pop_buf_wd_sl.shp')
pop_buf_we_sl = gpd.read_file(file_path + 'sfca/pop_buf_we_sl.shp')

# Extract 'SGG_CD' from ['Name']
pop_buf_wd_gb['SGG_CD'] = pop_buf_wd_gb['Name'].str.extract(r'(\d+) :')
pop_buf_we_gb['SGG_CD'] = pop_buf_we_gb['Name'].str.extract(r'(\d+) :')
pop_buf_wd_sl['SGG_CD'] = pop_buf_wd_sl['Name'].str.extract(r'(\d+) :')
pop_buf_we_sl['SGG_CD'] = pop_buf_we_sl['Name'].str.extract(r'(\d+) :')

# Join 'SGG_CD' and 'pop_rate' to population buffer data
selected_cols1 = ['SGG_CD', 'ToBreak', 'geometry']
selected_cols2 = ['SGG_CD', 'pop_rate']
pop_buf_wd_gb = pop_buf_wd_gb[selected_cols1].merge(point_pop_wd_gb[selected_cols2], on='SGG_CD', how='inner')
pop_buf_we_gb = pop_buf_we_gb[selected_cols1].merge(point_pop_we_gb[selected_cols2], on='SGG_CD', how='inner')
pop_buf_wd_sl = pop_buf_wd_sl[selected_cols1].merge(point_pop_wd_sl[selected_cols2], on='SGG_CD', how='inner')
pop_buf_we_sl = pop_buf_we_sl[selected_cols1].merge(point_pop_we_sl[selected_cols2], on='SGG_CD', how='inner')

# Join hospital 'ProToPop' to population buffer data
dfs = [pop_buf_wd_gb, pop_buf_we_gb, pop_buf_wd_sl, pop_buf_we_sl]
fac_dfs = [fac_wd_gb, fac_we_gb, fac_wd_sl, fac_we_sl]
for df, fac_df in zip(dfs, fac_dfs):
    result = gpd.sjoin(df, fac_df, how="inner", predicate="intersects")
    sum_ProToPop = result.groupby('SGG_CD')['ProToPop'].sum().reset_index()
    sum_ProToPop.rename(columns={'ProToPop': 'ProToPop_sum'}, inplace=True)
    df['ProToPop_sum'] = df['SGG_CD'].map(sum_ProToPop.set_index('SGG_CD')['ProToPop_sum'])

# Assign weights to 'e2sfca' in population buffer data
pop_buf_wd_gb['e2sfca'] = np.select(
    [pop_buf_wd_gb['ToBreak'] == 19550.0, pop_buf_wd_gb['ToBreak'] == 13030.0, pop_buf_wd_gb['ToBreak'] == 6520.0],
    [pop_buf_wd_gb['ProToPop_sum'], pop_buf_wd_gb['ProToPop_sum'] * 0.68, pop_buf_wd_gb['ProToPop_sum'] * 0.22],
    default=0
)
pop_buf_we_gb['e2sfca'] = np.select(
    [pop_buf_we_gb['ToBreak'] == 19550.0, pop_buf_we_gb['ToBreak'] == 13030.0, pop_buf_we_gb['ToBreak'] == 6520.0],
    [pop_buf_we_gb['ProToPop_sum'], pop_buf_we_gb['ProToPop_sum'] * 0.68, pop_buf_we_gb['ProToPop_sum'] * 0.22],
    default=0
)
pop_buf_wd_sl['e2sfca'] = np.select(
    [pop_buf_wd_sl['ToBreak'] == 11550.0, pop_buf_wd_sl['ToBreak'] == 7000.0, pop_buf_wd_sl['ToBreak'] == 3850.0],
    [pop_buf_wd_sl['ProToPop_sum'], pop_buf_wd_sl['ProToPop_sum'] * 0.68, pop_buf_wd_sl['ProToPop_sum'] * 0.22],
    default=0
)
pop_buf_we_sl['e2sfca'] = np.select(
    [pop_buf_we_sl['ToBreak'] == 11550.0, pop_buf_we_sl['ToBreak'] == 7000.0, pop_buf_we_sl['ToBreak'] == 3850.0],
    [pop_buf_we_sl['ProToPop_sum'], pop_buf_we_sl['ProToPop_sum'] * 0.68, pop_buf_we_sl['ProToPop_sum'] * 0.22],
    default=0
)

# Sum 'e2sfca' for each 'SGG_CD'
pop_buf_wd_gb = pop_buf_wd_gb.groupby(['SGG_CD'])[['e2sfca']].sum().reset_index()
pop_buf_we_gb = pop_buf_we_gb.groupby(['SGG_CD'])[['e2sfca']].sum().reset_index()
pop_buf_wd_sl = pop_buf_wd_sl.groupby(['SGG_CD'])[['e2sfca']].sum().reset_index()
pop_buf_we_sl = pop_buf_we_sl.groupby(['SGG_CD'])[['e2sfca']].sum().reset_index()

# Load municipal boundary data
shp_gb = gpd.read_file(file_path + 'shp_gb.shp', encoding='euc-kr')
shp_sl = gpd.read_file(file_path + 'shp_sl.shp', encoding='euc-kr')

# Convert municipal code to string
shp_gb['SGG_CD'] = shp_gb['SGG_CD'].astype(str)
shp_sl['SGG_CD'] = shp_sl['SGG_CD'].astype(str)

# Join 'e2sfca' to municipal boundaries
selected_cols1 = ['SGG_CD', 'SIGUNGU_NM', 'geometry']
selected_cols2 = ['SGG_CD', 'e2sfca']
shp_wd_gb = shp_gb[selected_cols1].merge(pop_buf_wd_gb[selected_cols2], on='SGG_CD', how='left')
shp_we_gb = shp_gb[selected_cols1].merge(pop_buf_we_gb[selected_cols2], on='SGG_CD', how='left')
shp_wd_sl = shp_sl[selected_cols1].merge(pop_buf_wd_sl[selected_cols2], on='SGG_CD', how='left')
shp_we_sl = shp_sl[selected_cols1].merge(pop_buf_we_sl[selected_cols2], on='SGG_CD', how='left')

# Export shapefiles
#shp_wd_gb.to_file(file_path + 'shp_wd_gb.shp')
#shp_we_gb.to_file(file_path + 'shp_we_gb.shp')
##shp_we_sl.to_file(file_path + 'shp_we_sl.shp')
