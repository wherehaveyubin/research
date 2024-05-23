import pandas as pd
import numpy as np
import geokakao as gk

file_path = 'D:/*'

# 1. supply

# data: 전국 병의원 현황 (2022.12 기준)
# http://opendata.hira.or.kr/op/opc/selectOpenData.do?sno=11925

# 데이터 불러오기 및 서울, 경북 추출
fac_info = pd.read_excel(file_path + 'raw/전국 병의원 및 약국 현황 2022.12/1.병원정보서비스 2022.12.xlsx') #76249행
fac_info2 = pd.read_excel(file_path + 'raw/전국 병의원 및 약국 현황 2022.12/4.의료기관별상세정보서비스_02_세부정보_2022.12.xlsx') #20805행
fac_merge = pd.merge(fac_info, fac_info2, on='암호화요양기호') #19364행
fac_merge.to_csv(file_path + 'supply/fac_merge.csv', index=False, encoding='euc-kr')

# 필요한 열만 추출
fac_merge = fac_merge[(fac_merge['종별코드명'] == '상급종합') | (fac_merge['종별코드명'] == '종합병원') | 
                      (fac_merge['종별코드명'] == '병원') | (fac_merge['종별코드명'] == '의원') | 
                      (fac_merge['종별코드명'] == '보건의료원')] #9058행
fac_hour = fac_merge.filter(regex='^진료')
fac_merge = pd.concat([fac_merge[['요양기관명_x', '종별코드명', '주소', '총의사수', '응급실 야간운영여부']], fac_hour], axis=1)
fac_merge = fac_merge[(fac_merge['주소'].str.startswith(('서울', '경상북도')))] #서울|경북 추출, 2574행
fac_merge.rename(columns={'요양기관명_x': '기관명'}, inplace=True)
fac_merge.replace(0, np.nan, inplace=True) #휴무일 제외 (0인 값을 nan로 대체)
fac_merge.fillna('', inplace=True)

# 지오 코딩을 위한 주소 가공
address_correction = {
    '서울특별시 중구 마른내로 9-9 (저동2가)': '서울특별시 중구 마른내로 9',
    '경상북도 경주시 원화로 315 315': '경상북도 경주시 원화로 315',
    '서울특별시 중구 다산로36길 11 3,4,5층 (신당동)': '서울특별시 중구 다산로36길 11',
    '서울특별시 영등포구 국회대로54길 10 305,306호 (영등포동7가, 아크로타워스퀘어)': '서울특별시 영등포구 국회대로54길 10',
    '서울특별시 강북구 도봉로 217 5,6,7층 (미아동, 25메디컬빌딩)': '서울특별시 강북구 도봉로 217',
    '경상북도 청송군 청송읍 의료원길 19 19': '경상북도 청송군 청송읍 의료원길 19'
}
fac_merge['주소'] = fac_merge['주소'].replace(address_correction)

# 진료 시간을 정수로 변경 
for col in fac_merge.columns:
    if '진료' in col:
        fac_merge[col] = pd.to_numeric(fac_merge[col], errors='coerce').astype('Int64')

# 주중 야간 진료 가능 병원
fac_weekday = fac_merge[(fac_merge['진료시작시간_월'] <= 600) & (fac_merge['진료시작시간_월'] != '') | 
                        (fac_merge['진료종료시간_월'] >= 2300) & (fac_merge['진료종료시간_월'] != '') |
                        (fac_merge['진료시작시간_화'] <= 600) & (fac_merge['진료시작시간_화'] != '') | 
                        (fac_merge['진료종료시간_화'] >= 2300) & (fac_merge['진료종료시간_화'] != '') |
                        (fac_merge['진료시작시간_수'] <= 600) & (fac_merge['진료시작시간_수'] != '') | 
                        (fac_merge['진료종료시간_수'] >= 2300) & (fac_merge['진료종료시간_수'] != '') |
                        (fac_merge['진료시작시간_목'] <= 600) & (fac_merge['진료시작시간_목'] != '') | 
                        (fac_merge['진료종료시간_목'] >= 2300) & (fac_merge['진료종료시간_목'] != '') |
                        (fac_merge['진료시작시간_금'] <= 600) & (fac_merge['진료시작시간_금'] != '') | 
                        (fac_merge['진료종료시간_금'] >= 2300) & (fac_merge['진료종료시간_금'] != '') |
                        (fac_merge['응급실 야간운영여부'] == 'Y')] #109행

# 주말 야간 진료 가능 병원
fac_weekend = fac_merge[(fac_merge['진료시작시간_토'] <= 600) & (fac_merge['진료시작시간_토'] != '') | 
                        (fac_merge['진료종료시간_토'] >= 2300) & (fac_merge['진료종료시간_토'] != '') |
                        (fac_merge['진료시작시간_일'] <= 600) & (fac_merge['진료시작시간_일'] != '') | 
                        (fac_merge['진료종료시간_일'] >= 2300) & (fac_merge['진료종료시간_일'] != '') |
                        (fac_merge['응급실 야간운영여부'] == 'Y')] # 107행

# 지오코딩
gk.add_coordinates_to_dataframe(fac_weekday, '주소')
fac_weekday.to_csv(file_path + 'supply/fac_weekday.csv', index=False, encoding='euc-kr')

gk.add_coordinates_to_dataframe(fac_weekend, '주소')
fac_weekend.to_csv(file_path + 'supply/fac_weekend.csv', index=False, encoding='euc-kr')

fac_sl_weekday = fac_weekday[(fac_weekday['주소'].str.startswith('서울'))] #79행
fac_sl_weekend = fac_weekend[(fac_weekend['주소'].str.startswith('서울'))] #77행
fac_sl_weekday.to_csv(file_path + 'supply/fac_sl_weekday.csv', index=False, encoding='euc-kr')
fac_sl_weekend.to_csv(file_path + 'supply/fac_sl_weekend.csv', index=False, encoding='euc-kr')

fac_gb_weekday = fac_weekday[(fac_weekday['주소'].str.startswith('경상북도'))] #30행
fac_gb_weekend = fac_weekend[(fac_weekend['주소'].str.startswith('경상북도'))] #30행
fac_gb_weekday.to_csv(file_path + 'supply/fac_gb_weekday.csv', index=False, encoding='euc-kr')
fac_gb_weekend.to_csv(file_path + 'supply/fac_gb_weekend.csv', index=False, encoding='euc-kr')
