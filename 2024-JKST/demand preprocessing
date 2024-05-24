import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import Point

file_path = 'D:/*'

# 카드 이용인구
## 카드 이용인구 전처리
card_sl = pd.read_csv(file_path + 'raw/sh_sl.csv')
card_sl = card_sl.rename(columns={'shop.gungu':'SIGUNGU_CD'})
card_sl = card_sl[(card_sl['time.day'] == 1) | (card_sl['time.day'] == 6)] #야간 시간대 추출, 6868행
card_sl_group = card_sl.groupby(['date', 'SIGUNGU_CD']).agg({'medi.flows': 'sum'}).reset_index() #일, 구별 합

card_gb = pd.read_csv(file_path + 'raw/sh_gb.csv')
card_gb = card_gb.rename(columns={'shop.gungu':'SIGUNGU_CD'})
card_gb = card_gb[(card_gb['time.day'] == 1) | (card_gb['time.day'] == 6)] #야간 시간대 추출, 591행
card_gb_group = card_gb.groupby(['date', 'SIGUNGU_CD']).agg({'medi.flows': 'sum'}).reset_index() #일, 구별 합

## 카드 이용인구 일별 평균 (for figure)
card_daily_sl = card_sl_group.groupby(['date']).agg({'medi.flows': 'mean'}).reset_index() #일별 평균
card_daily_sl.to_csv(file_path + 'demand/card_daily_sl.csv')

card_daily_gb = card_gb_group.groupby(['date']).agg({'medi.flows': 'mean'}).reset_index() #일별 평균
card_daily_gb.to_csv(file_path + 'demand/card_daily_gb.csv')

## 카드 이용인구 주중, 주말 평균
card_sl_group['date'] = pd.to_datetime(card_sl_group['date'])
card_sl_group['weekday'] = card_sl_group['date'].dt.weekday
card_sl_group['weekend'] = card_sl_group['weekday'].isin([5, 6]).astype(int)
card_sl_weekday = card_sl_group[card_sl_group['weekend'] == 0].groupby('SIGUNGU_CD')['medi.flows'].mean().reset_index()
card_sl_weekend = card_sl_group[card_sl_group['weekend'] == 1].groupby('SIGUNGU_CD')['medi.flows'].mean().reset_index()

card_gb_group['date'] = pd.to_datetime(card_gb_group['date'])
card_gb_group['weekday'] = card_gb_group['date'].dt.weekday
card_gb_group['weekend'] = card_gb_group['weekday'].isin([5, 6]).astype(int)
card_gb_weekday = card_gb_group[card_gb_group['weekend'] == 0].groupby('SIGUNGU_CD')['medi.flows'].mean().reset_index()
card_gb_weekend = card_gb_group[card_gb_group['weekend'] == 1].groupby('SIGUNGU_CD')['medi.flows'].mean().reset_index()

# 유동인구
## 유동인구 전처리
skt_sl = pd.read_csv(file_path + 'raw/skt_sl.csv')
skt_sl = skt_sl.rename(columns={'DEST_CD':'SIGUNGU_CD'})
skt_sl = skt_sl[(skt_sl['HH'] <= 6) | (skt_sl['HH'] >= 23)] #야간 시간대 추출
skt_sl['pop'] = skt_sl['M_1019'] + skt_sl['M_2034'] + skt_sl['M_3564'] + skt_sl['M_65U'] + skt_sl['W_1019'] + skt_sl['W_2034'] + skt_sl['W_3564'] + skt_sl['W_65U']
skt_sl_group = skt_sl.groupby(['STD_YMD', 'SIGUNGU_CD', 'HH']).agg({'pop': 'sum'}).reset_index() #시간대별 합

skt_gb = pd.read_csv(file_path + 'raw/skt_gb.csv')
skt_gb = skt_gb.rename(columns={'DEST_CD':'SIGUNGU_CD'})
skt_gb = skt_gb[(skt_gb['HH'] <= 6) | (skt_gb['HH'] >= 23)] #야간 시간대 추출
skt_gb['pop'] = skt_gb['M_1019'] + skt_gb['M_2034'] + skt_gb['M_3564'] + skt_gb['M_65U'] + skt_gb['W_1019'] + skt_gb['W_2034'] + skt_gb['W_3564'] + skt_gb['W_65U']
skt_gb_group = skt_gb.groupby(['STD_YMD', 'SIGUNGU_CD', 'HH']).agg({'pop': 'sum'}).reset_index() #시간대별 합

## 유동인구 일별 평균 (for figure)
skt_sl_group = skt_sl_group.groupby(['STD_YMD', 'SIGUNGU_CD']).agg({'pop': 'mean'}).reset_index() #일, 구별 평균
skt_daily_sl = skt_sl_group.groupby(['STD_YMD']).agg({'pop': 'mean'}).reset_index() #일별 평균
skt_daily_sl.to_csv(file_path + 'demand/skt_daily_sl.csv')

skt_gb_group = skt_gb_group.groupby(['STD_YMD', 'SIGUNGU_CD']).agg({'pop': 'mean'}).reset_index() #일, 구별 평균
skt_daily_gb = skt_gb_group.groupby(['STD_YMD']).agg({'pop': 'mean'}).reset_index() #일별 평균
skt_daily_gb.to_csv(file_path + 'demand/skt_daily_gb.csv')

## 유동인구 주중, 주말 평균
skt_sl_group['STD_YMD'] = pd.to_datetime(skt_sl_group['STD_YMD'], format='%Y%m%d')
skt_sl_group['weekday'] = skt_sl_group['STD_YMD'].dt.weekday
skt_sl_group['weekend'] = skt_sl_group['weekday'].isin([5, 6]).astype(int)
skt_sl_weekday = skt_sl_group[skt_sl_group['weekend'] == 0].groupby('SIGUNGU_CD')['pop'].mean().reset_index()
skt_sl_weekend = skt_sl_group[skt_sl_group['weekend'] == 1].groupby('SIGUNGU_CD')['pop'].mean().reset_index()

skt_gb_group['STD_YMD'] = pd.to_datetime(skt_gb_group['STD_YMD'], format='%Y%m%d')
skt_gb_group['weekday'] = skt_gb_group['STD_YMD'].dt.weekday
skt_gb_group['weekend'] = skt_gb_group['weekday'].isin([5, 6]).astype(int)
skt_gb_weekday = skt_gb_group[skt_gb_group['weekend'] == 0].groupby('SIGUNGU_CD')['pop'].mean().reset_index()
skt_gb_weekend = skt_gb_group[skt_gb_group['weekend'] == 1].groupby('SIGUNGU_CD')['pop'].mean().reset_index()

# 의료 수요 인구 계산
pop_wd_sl = pd.merge(card_sl_weekday, skt_sl_weekday, on='SIGUNGU_CD')
pop_wd_sl['pop_1k'] = pop_wd_sl['pop']/1000
pop_wd_sl['rate'] = pop_wd_sl['medi.flows']/pop_wd_sl['pop_1k']

pop_we_sl = pd.merge(card_sl_weekend, skt_sl_weekend, on='SIGUNGU_CD')
pop_we_sl['pop_1k'] = pop_we_sl['pop']/1000
pop_we_sl['rate'] = pop_we_sl['medi.flows']/pop_we_sl['pop_1k']

pop_wd_gb = pd.merge(card_gb_weekday, skt_gb_weekday, on='SIGUNGU_CD')
pop_wd_gb['pop_1k'] = pop_wd_gb['pop']/1000
pop_wd_gb['rate'] = pop_wd_gb['medi.flows']/pop_wd_gb['pop_1k']

pop_we_gb = pd.merge(card_gb_weekend, skt_gb_weekend, on='SIGUNGU_CD')
pop_we_gb['pop_1k'] = pop_we_gb['pop']/1000
pop_we_gb['rate'] = pop_we_gb['medi.flows']/pop_we_gb['pop_1k']
