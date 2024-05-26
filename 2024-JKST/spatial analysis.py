import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import Point

file_path = '*'

# 시군구 shp 불러오기
shp_data = gpd.read_file(file_path + 'raw/_census_data_2022_4_bnd_sigungu_bnd_sigungu_00_2022_2022/bnd_sigungu_00_2022_2022_4Q.shp', encoding='utf-8')
shp_data = shp_data.to_crs(epsg=4326)
shp_data.to_file(file_path + 'shp/shp_data.shp', driver='ESRI Shapefile', encoding='utf-8')

# 코드명 조인
shp_data = shp_data[shp_data['SIGUNGU_CD'].astype(str).str.startswith(('11', '37'))]
join_key = pd.read_csv(file_path + 'raw/sgg_code.csv')
shp_data = pd.merge(shp_data, join_key, on='SIGUNGU_NM', how='inner')
shp_data.drop(columns=['SIGUNGU_CD_x', 'SIDO_NM'], inplace=True)
shp_data = shp_data.rename(columns={'SIGUNGU_CD_y':'SIGUNGU_CD'})

# 서울, 경북 shp 생성
shp_sl = shp_data[shp_data['SIGUNGU_CD'].astype(str).str.startswith('11')]
shp_sl.to_file(file_path + 'shp/shp_sl.shp', driver='ESRI Shapefile', encoding='utf-8')
shp_gb = shp_data[shp_data['SIGUNGU_CD'].astype(str).str.startswith('47')]
shp_gb.to_file(file_path + 'shp/shp_gb.shp', driver='ESRI Shapefile', encoding='utf-8')

# 시군구 중심점 추출
shp_data['centroid'] = shp_data['geometry'].centroid
shp_data['centroid_point'] = shp_data['centroid'].apply(lambda centroid: Point(centroid.x, centroid.y))
point_data = gpd.GeoDataFrame(shp_data[['SIGUNGU_NM', 'SIGUNGU_EN', 'SIGUNGU_CD', 'centroid_point']], geometry='centroid_point')
point_data.to_file(file_path + 'shp/point_data.shp')

# 시군구, 요일별 point 조인
pop_wd_sl = pd.read_csv(file_path + 'demand/pop_wd_sl.csv')
pop_we_sl = pd.read_csv(file_path + 'demand/pop_we_sl.csv')
pop_wd_gb = pd.read_csv(file_path + 'demand/pop_wd_gb.csv')
pop_we_gb = pd.read_csv(file_path + 'demand/pop_we_gb.csv')

point_pop_wd_sl = pd.merge(point_data, pop_wd_sl, on='SIGUNGU_CD', how='inner')
point_pop_we_sl = pd.merge(point_data, pop_we_sl, on='SIGUNGU_CD', how='inner')
point_pop_wd_gb = pd.merge(point_data, pop_wd_gb, on='SIGUNGU_CD', how='inner')
point_pop_we_gb = pd.merge(point_data, pop_we_gb, on='SIGUNGU_CD', how='inner')

point_pop_wd_sl.to_file(file_path + 'shp/point_pop_wd_sl.shp', encoding='euc-kr')
point_pop_we_sl.to_file(file_path + 'shp/point_pop_we_sl.shp', encoding='euc-kr')
point_pop_wd_gb.to_file(file_path + 'shp/point_pop_wd_gb.shp', encoding='euc-kr')
point_pop_we_gb.to_file(file_path + 'shp/point_pop_we_gb.shp', encoding='euc-kr')
