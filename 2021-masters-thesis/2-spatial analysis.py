import pandas as pd
import geopandas as gpd

file_path = '*'

# STEP 1

# 의료시설 불러오기
fac_point = gpd.read_file(file_path + 'fac_point.shp', encoding='euc-kr')
fac_point['name'] = fac_point['name'].str.replace(' ', '')

# 의료시설 버퍼 불러오기
fac_buffer = gpd.read_file(file_path + 'fac_buffer.shp')
fac_buffer['name'] = [name.split(' :')[0] for name in fac_buffer['Name']]
fac_buffer['name'] = fac_buffer['name'].str.replace(' ', '')

# 의료시설 버퍼에 의료시설 조인
fac_buffer1 = gpd.GeoDataFrame(fac_buffer[['name', 'geometry']]).merge(fac_point[['name', 'type', 'num']], on='name', how='inner')
fac_buffer1 = gpd.GeoDataFrame(fac_buffer1, geometry='geometry')

fac_buffer2 = fac_buffer1.copy()
fac_buffer2 = gpd.GeoDataFrame(fac_buffer2, geometry='geometry')

fac_buffer3 = fac_buffer1.copy()
fac_buffer3 = gpd.GeoDataFrame(fac_buffer3, geometry='geometry')

"""
if isinstance(fac_point3, gpd.GeoDataFrame):
    print("gdf is a GeoDataFrame")
else:
    print("gdf is not a GeoDataFrame")
"""

# 인구 불러오기
den_point = gpd.read_file(file_path + 'den_point.shp')
den_point = den_point.to_crs(fac_buffer.crs)

point_pop = den_point[['SGGNM', 'P_den', 'geometry']]
point_pop.rename(columns={'P_den': 'den'}, inplace=True)

point_65 = den_point[['SGGNM', 'E_den', 'geometry']]
point_65.rename(columns={'E_den': 'den'}, inplace=True)

point_covid = den_point[['SGGNM', 'C_den', 'geometry']]
point_covid.rename(columns={'C_den': 'den'}, inplace=True)

# 의료시설 버퍼와 인구 spatial join
fac_dfs = [fac_buffer1, fac_buffer2, fac_buffer3]
pop_dfs = [point_pop, point_65, point_covid]

for fac_df, pop_df in zip(fac_dfs, pop_dfs):
    result = gpd.sjoin(fac_df, pop_df, how="inner", predicate="intersects") 
    sum_pop_rate = result.groupby('name')['den'].sum().reset_index()
    sum_pop_rate.rename(columns={'den': 'den_sum'}, inplace=True)
    fac_df['den_sum'] = fac_df['name'].map(sum_pop_rate.set_index('name')['den_sum']).fillna(0)

# 의료시설에 의료시설 버퍼 join
fac_point1 = gpd.GeoDataFrame(fac_buffer1[['name', 'den_sum']]).merge(fac_point[['name', 'type', 'geometry']], on='name', how='inner')
fac_point1 = gpd.GeoDataFrame(fac_point1, geometry='geometry')

fac_point2 = gpd.GeoDataFrame(fac_buffer2[['name', 'den_sum']]).merge(fac_point[['name', 'type', 'geometry']], on='name', how='inner')
fac_point2 = gpd.GeoDataFrame(fac_point2, geometry='geometry')

fac_point3 = gpd.GeoDataFrame(fac_buffer3[['name', 'den_sum']]).merge(fac_point[['name', 'type', 'geometry']], on='name', how='inner')
fac_point3 = gpd.GeoDataFrame(fac_point3, geometry='geometry')


# Step 2

# 인구 버퍼 불러오기
den_buffer = gpd.read_file(file_path + 'den_buffer.shp')
den_buffer['den_name'] = [name.split(' :')[0] for name in den_buffer['Name']]

# 인구 버퍼에 인구 조인
den_buffer = den_buffer[['den_name', 'geometry']].merge(point_pop[['SGGNM', 'den']], left_on='den_name', right_on='SGGNM', how='inner')
den_buffer.drop(columns=['SGGNM'], inplace=True)

eld_buffer = den_buffer[['den_name', 'geometry']].merge(point_65[['SGGNM', 'den']], left_on='den_name', right_on='SGGNM', how='inner')
eld_buffer.drop(columns=['SGGNM'], inplace=True)

cov_buffer = den_buffer[['den_name', 'geometry']].merge(point_covid[['SGGNM', 'den']], left_on='den_name', right_on='SGGNM', how='inner')
cov_buffer.drop(columns=['SGGNM'], inplace=True)

# 인구 버퍼와 의료시설(den_sum) - 공간 조인
pop_dfs = [den_buffer, eld_buffer, cov_buffer]
fac_dfs = [fac_point1, fac_point2, fac_point3]

for pop_df, fac_df in zip(pop_dfs, fac_dfs):
    result = gpd.sjoin(pop_df, fac_df, how="inner", predicate="intersects") 
    sum_ProToPop = result.groupby('den_name')['den_sum'].sum().reset_index()
    sum_ProToPop.rename(columns={'den_sum': 'sfca'}, inplace=True)
    pop_df['sfca'] = pop_df['den_name'].map(sum_ProToPop.set_index('den_name')['sfca']).fillna(0)

# 평균값으로 나누기
den_buffer['spar'] = den_buffer['sfca'] / den_buffer['sfca'].mean()
eld_buffer['spar'] = eld_buffer['sfca'] / eld_buffer['sfca'].mean()
cov_buffer['spar'] = cov_buffer['sfca'] / cov_buffer['sfca'].mean()

# 2SFCA 값을 시군구 경계에 조인
spar_den = den_buffer[['den_name', 'geometry', 'den', 'sfca', 'spar']].merge(den['SGGNM'], left_on='den_name', right_on='SGGNM', how='right')
spar_eld = eld_buffer[['den_name', 'geometry', 'den', 'sfca', 'spar']].merge(den['SGGNM'], left_on='den_name', right_on='SGGNM', how='right')
spar_cov = cov_buffer[['den_name', 'geometry', 'den', 'sfca', 'spar']].merge(den['SGGNM'], left_on='den_name', right_on='SGGNM', how='right')

spar_den.to_file(file_path + 'spar_den.shp', encoding='euc-kr')
spar_eld.to_file(file_path + 'spar_eld.shp', encoding='euc-kr')
spar_cov.to_file(file_path + 'spar_cov.shp', encoding='euc-kr')
