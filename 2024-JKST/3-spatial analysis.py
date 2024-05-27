import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
import re

file_path = '*'

# STEP 1

# 의료시설 버퍼 불러오기
fac_buf_wd_sl = gpd.read_file(file_path + 'shp/shp_fac_wd_sl.shp')
fac_buf_we_sl = gpd.read_file(file_path + 'shp/shp_fac_we_sl.shp')
fac_buf_wd_gb = gpd.read_file(file_path + 'shp/shp_fac_wd_gb.shp')
fac_buf_we_gb = gpd.read_file(file_path + 'shp/shp_fac_we_gb.shp')

fac_buf_wd_sl['name'] = fac_buf_wd_sl['Name'].str.extract('([가-힣 ]+)')
fac_buf_we_sl['name'] = fac_buf_we_sl['Name'].str.extract('([가-힣 ]+)')
fac_buf_wd_gb['name'] = fac_buf_wd_gb['Name'].str.extract('([가-힣 ]+)')
fac_buf_we_gb['name'] = fac_buf_we_gb['Name'].str.extract('([가-힣 ]+)')

fac_buf_wd_sl['name'] = fac_buf_wd_sl['name'].str.replace(' ', '')
fac_buf_we_sl['name'] = fac_buf_we_sl['name'].str.replace(' ', '')
fac_buf_wd_gb['name'] = fac_buf_wd_gb['name'].str.replace(' ', '')
fac_buf_we_gb['name'] = fac_buf_we_gb['name'].str.replace(' ', '')

# 의료시설 불러오기
fac_wd_sl = gpd.read_file(file_path + 'shp/fac_sl_wd.shp', encoding='euc-kr') #124
fac_we_sl = gpd.read_file(file_path + 'shp/fac_sl_we.shp', encoding='euc-kr') #122
fac_wd_gb = gpd.read_file(file_path + 'shp/fac_gb_wd.shp', encoding='euc-kr') #38
fac_we_gb = gpd.read_file(file_path + 'shp/fac_gb_we.shp', encoding='euc-kr') #38

fac_wd_sl['Personnel'] = pd.to_numeric(fac_wd_sl['Personnel'])
fac_we_sl['Personnel'] = pd.to_numeric(fac_we_sl['Personnel'])
fac_wd_gb['Personnel'] = pd.to_numeric(fac_wd_gb['Personnel'])
fac_we_gb['Personnel'] = pd.to_numeric(fac_we_gb['Personnel'])

# 의료시설 버퍼와 의료시설 조인
selected_cols1 = ['name', 'ToBreak', 'geometry']
selected_cols2 = ['name', 'Personnel']
fac_buf_wd_sl = fac_buf_wd_sl[selected_cols1].merge(fac_wd_sl[selected_cols2], on='name', how='inner')
fac_buf_we_sl = fac_buf_we_sl[selected_cols1].merge(fac_we_sl[selected_cols2], on='name', how='inner')
fac_buf_wd_gb = fac_buf_wd_gb[selected_cols1].merge(fac_wd_gb[selected_cols2], on='name', how='inner')
fac_buf_we_gb = fac_buf_we_gb[selected_cols1].merge(fac_we_gb[selected_cols2], on='name', how='inner')

# 인구 불러오기
point_pop_wd_sl = gpd.read_file(file_path + 'shp/point_pop_wd_sl.shp')
point_pop_we_sl = gpd.read_file(file_path + 'shp/point_pop_we_sl.shp')
point_pop_wd_gb = gpd.read_file(file_path + 'shp/point_pop_wd_gb.shp')
point_pop_we_gb = gpd.read_file(file_path + 'shp/point_pop_we_gb.shp')

# 의료시설 버퍼와 인구 - 공간 조인
fac_buf_dfs = [fac_buf_wd_gb, fac_buf_we_gb, fac_buf_wd_sl, fac_buf_we_sl]
pop_dfs = [point_pop_wd_gb, point_pop_we_gb, point_pop_wd_sl, point_pop_we_sl]

for df, pop_df in zip(fac_buf_dfs, pop_dfs):
    result = gpd.sjoin(df, pop_df, how="inner", predicate="intersects")
    sum_pop_rate = result.groupby('name')['rate'].sum().reset_index()
    sum_pop_rate.rename(columns={'rate': 'rate_sum'}, inplace=True)
    df['rate_sum'] = df['name'].map(sum_pop_rate.set_index('name')['rate_sum'])
    df['rate_sum'] = pd.to_numeric(df['rate_sum'], errors='coerce')

# 거리별 가중치 부여
fac_buf_wd_sl['rate_sum_wgt'] = np.select([fac_buf_wd_sl['ToBreak'] == 11550.0, 
                                           fac_buf_wd_sl['ToBreak'] == 7700.0, 
                                           fac_buf_wd_sl['ToBreak'] == 3850.0], 
                                          [fac_buf_wd_sl['rate_sum'], 
                                           fac_buf_wd_sl['rate_sum'] * 0.68, 
                                           fac_buf_wd_sl['rate_sum'] * 0.22])
fac_buf_we_sl['rate_sum_wgt'] = np.select([fac_buf_we_sl['ToBreak'] == 11550.0, 
                                           fac_buf_we_sl['ToBreak'] == 7700.0, 
                                           fac_buf_we_sl['ToBreak'] == 3850.0], 
                                          [fac_buf_we_sl['rate_sum'], 
                                           fac_buf_we_sl['rate_sum'] * 0.68, 
                                           fac_buf_we_sl['rate_sum'] * 0.22])
fac_buf_wd_gb['rate_sum_wgt'] = np.select([fac_buf_wd_gb['ToBreak'] == 19550.0, 
                                           fac_buf_wd_gb['ToBreak'] == 13033.0, 
                                           fac_buf_wd_gb['ToBreak'] == 6517.0], 
                                          [fac_buf_wd_gb['rate_sum'], 
                                           fac_buf_wd_gb['rate_sum'] * 0.68, 
                                           fac_buf_wd_gb['rate_sum'] * 0.22])
fac_buf_we_gb['rate_sum_wgt'] = np.select([fac_buf_we_gb['ToBreak'] == 19550.0, 
                                           fac_buf_we_gb['ToBreak'] == 13033.0, 
                                           fac_buf_we_gb['ToBreak'] == 6517.0], 
                                          [fac_buf_we_gb['rate_sum'], 
                                           fac_buf_we_gb['rate_sum'] * 0.68, 
                                           fac_buf_we_gb['rate_sum'] * 0.22])

# 의료시설에 Personnel / rate_sum 값 입력
grouped = fac_buf_wd_sl.groupby('name')['rate_sum_wgt'].sum().reset_index()
fac_wd_sl = fac_wd_sl.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_wd_sl['Personnel'] = pd.to_numeric(fac_wd_sl['Personnel'], errors='coerce')
fac_wd_sl['ProToPop'] = fac_wd_sl['Personnel'] / fac_wd_sl['rate_sum_wgt']

grouped = fac_buf_we_sl.groupby('name')['rate_sum_wgt'].sum().reset_index()
fac_we_sl = fac_we_sl.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_we_sl['Personnel'] = pd.to_numeric(fac_we_sl['Personnel'], errors='coerce')
fac_we_sl['ProToPop'] = fac_we_sl['Personnel'] / fac_we_sl['rate_sum_wgt']

grouped = fac_buf_wd_gb.groupby('name')['rate_sum_wgt'].sum().reset_index()
fac_wd_gb = fac_wd_gb.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_wd_gb['Personnel'] = pd.to_numeric(fac_wd_gb['Personnel'], errors='coerce')
fac_wd_gb['ProToPop'] = fac_wd_gb['Personnel'] / fac_wd_gb['rate_sum_wgt']
fac_wd_gb['ProToPop'].replace([np.inf, -np.inf], np.nan, inplace=True)
fac_wd_gb['ProToPop'].fillna(0, inplace=True)

grouped = fac_buf_we_gb.groupby('name')['rate_sum_wgt'].sum().reset_index()
fac_we_gb = fac_we_gb.merge(grouped, on='name', suffixes=('_left', '_right'))
fac_we_gb['Personnel'] = pd.to_numeric(fac_we_gb['Personnel'], errors='coerce')
fac_we_gb['ProToPop'] = fac_we_gb['Personnel'] / fac_we_gb['rate_sum_wgt']
fac_we_gb['ProToPop'].replace([np.inf, -np.inf], np.nan, inplace=True)
fac_we_gb['ProToPop'].fillna(0, inplace=True)


# Step 2

# 인구 버퍼 불러오기
pop_buf_wd_sl = gpd.read_file(file_path + 'shp/shp_pop_wd_sl.shp')
pop_buf_we_sl = gpd.read_file(file_path + 'shp/shp_pop_we_sl.shp')
pop_buf_wd_gb = gpd.read_file(file_path + 'shp/shp_pop_wd_gb.shp')
pop_buf_we_gb = gpd.read_file(file_path + 'shp/shp_pop_we_gb.shp')

def extract_alphabets(text):
    return re.sub(r'[^a-zA-Z]', '', text)

pop_buf_wd_sl['SIGUNGU_EN'] = pop_buf_wd_sl['Name'].apply(extract_alphabets)
pop_buf_we_sl['SIGUNGU_EN'] = pop_buf_we_sl['Name'].apply(extract_alphabets)
pop_buf_wd_gb['SIGUNGU_EN'] = pop_buf_wd_gb['Name'].apply(extract_alphabets)
pop_buf_we_gb['SIGUNGU_EN'] = pop_buf_we_gb['Name'].apply(extract_alphabets)

pop_buf_wd_gb['SIGUNGU_EN'] = pop_buf_wd_gb['SIGUNGU_EN'].replace({'SouthPohang': 'South Pohang', 'NorthPohang': 'North Pohang'})
pop_buf_we_gb['SIGUNGU_EN'] = pop_buf_we_gb['SIGUNGU_EN'].replace({'SouthPohang': 'South Pohang', 'NorthPohang': 'North Pohang'})


# 인구 버퍼와 인구 조인
selected_cols1 = ['SIGUNGU_EN', 'ToBreak', 'geometry']
selected_cols2 = ['SIGUNGU_EN', 'rate']

pop_buf_wd_sl = pop_buf_wd_sl[selected_cols1].merge(point_pop_wd_sl[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_we_sl = pop_buf_we_sl[selected_cols1].merge(point_pop_we_sl[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_wd_gb = pop_buf_wd_gb[selected_cols1].merge(point_pop_wd_gb[selected_cols2], on='SIGUNGU_EN', how='inner')
pop_buf_we_gb = pop_buf_we_gb[selected_cols1].merge(point_pop_we_gb[selected_cols2], on='SIGUNGU_EN', how='inner')

# 인구 버퍼와 의료시설 - 공간 조인
dfs = [pop_buf_wd_gb, pop_buf_we_gb, pop_buf_wd_sl, pop_buf_we_sl]
fac_dfs = [fac_wd_gb, fac_we_gb, fac_wd_sl, fac_we_sl]

for df, fac_df in zip([pop_buf_wd_sl, pop_buf_we_sl, pop_buf_wd_gb, pop_buf_we_gb], 
                      [fac_wd_sl, fac_we_sl, fac_wd_gb, fac_we_gb]):
    result = gpd.sjoin(df, fac_df, how="inner", predicate="intersects")
    sum_ProToPop = result.groupby('SIGUNGU_EN')['ProToPop'].sum().reset_index()
    sum_ProToPop.rename(columns={'ProToPop': 'ProToPop_sum'}, inplace=True)
    df['ProToPop_sum'] = df['SIGUNGU_EN'].map(sum_ProToPop.set_index('SIGUNGU_EN')['ProToPop_sum'])
    df['ProToPop_sum'].fillna(0, inplace=True)

# 거리별 가중치 부여
pop_buf_wd_sl['e2sfca'] = np.select([pop_buf_wd_sl['ToBreak'] == 11550.0, 
                                     pop_buf_wd_sl['ToBreak'] == 7700.0, 
                                     pop_buf_wd_sl['ToBreak'] == 3850.0],
                                    [pop_buf_wd_sl['ProToPop_sum'], 
                                     pop_buf_wd_sl['ProToPop_sum'] * 0.68, 
                                     pop_buf_wd_sl['ProToPop_sum'] * 0.22])
pop_buf_we_sl['e2sfca'] = np.select([pop_buf_we_sl['ToBreak'] == 11550.0, 
                                     pop_buf_we_sl['ToBreak'] == 7700.0, 
                                     pop_buf_we_sl['ToBreak'] == 3850.0],
                                    [pop_buf_we_sl['ProToPop_sum'], 
                                     pop_buf_we_sl['ProToPop_sum'] * 0.68, 
                                     pop_buf_we_sl['ProToPop_sum'] * 0.22])
pop_buf_wd_gb['e2sfca'] = np.select([pop_buf_wd_gb['ToBreak'] == 19550.0, 
                                     pop_buf_wd_gb['ToBreak'] == 13033.0, 
                                     pop_buf_wd_gb['ToBreak'] == 6517.0],
                                    [pop_buf_wd_gb['ProToPop_sum'], 
                                     pop_buf_wd_gb['ProToPop_sum'] * 0.68, 
                                     pop_buf_wd_gb['ProToPop_sum'] * 0.22])
pop_buf_we_gb['e2sfca'] = np.select([pop_buf_we_gb['ToBreak'] == 19550.0, 
                                     pop_buf_we_gb['ToBreak'] == 13033.0, 
                                     pop_buf_we_gb['ToBreak'] == 6517.0],
                                    [pop_buf_we_gb['ProToPop_sum'], 
                                     pop_buf_we_gb['ProToPop_sum'] * 0.68, 
                                     pop_buf_we_gb['ProToPop_sum'] * 0.22])

# 접근성 값 합산
pop_buf_wd_sl = pop_buf_wd_sl.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_we_sl = pop_buf_we_sl.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_wd_gb = pop_buf_wd_gb.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()
pop_buf_we_gb = pop_buf_we_gb.groupby(['SIGUNGU_EN'])[['e2sfca']].sum().reset_index()

# 시군구 경계 불러오기
shp_sl = gpd.read_file(file_path + 'shp/shp_sl.shp', encoding='utf-8')
shp_gb = gpd.read_file(file_path + 'shp/shp_gb.shp', encoding='utf-8')

# E2SFCA 값을 시군구 경계에 조인
selected_cols1 = ['SIGUNGU_EN', 'SIGUNGU_CD', 'geometry']
selected_cols2 = ['SIGUNGU_EN', 'e2sfca']

shp_wd_sl = shp_sl[selected_cols1].merge(pop_buf_wd_sl[selected_cols2], on='SIGUNGU_EN', how='left')
shp_we_sl = shp_sl[selected_cols1].merge(pop_buf_we_sl[selected_cols2], on='SIGUNGU_EN', how='left')
shp_wd_gb = shp_gb[selected_cols1].merge(pop_buf_wd_gb[selected_cols2], on='SIGUNGU_EN', how='left')
shp_we_gb = shp_gb[selected_cols1].merge(pop_buf_we_gb[selected_cols2], on='SIGUNGU_EN', how='left')

# 서울 평일
e2sfca_mean_wd_sl = shp_wd_sl['e2sfca'].mean()
shp_wd_sl['SPAR'] = shp_wd_sl['e2sfca'] / e2sfca_mean_wd_sl
shp_wd_sl.to_file(file_path + 'shp/shp_e2sfca_wd_sl.shp')

# 서울 주말
e2sfca_mean_we_sl = shp_we_sl['e2sfca'].mean()
shp_we_sl['SPAR'] = shp_we_sl['e2sfca'] / e2sfca_mean_we_sl
shp_we_sl.to_file(file_path + 'shp/shp_e2sfca_we_sl.shp')

# 경북 평일
e2sfca_mean_wd_gb = shp_wd_gb['e2sfca'].mean()
shp_wd_gb['SPAR'] = shp_wd_gb['e2sfca'] / e2sfca_mean_wd_gb
shp_wd_gb.to_file(file_path + 'shp/shp_e2sfca_wd_gb.shp')
# 경북 주말
e2sfca_mean_we_gb = shp_we_gb['e2sfca'].mean()
shp_we_gb['SPAR'] = shp_we_gb['e2sfca'] / e2sfca_mean_we_gb
shp_we_gb.to_file(file_path + 'shp/shp_e2sfca_we_gb.shp')
