import pandas as pd
import numpy as np

file_path = '*'

# 데이터 불러오기
fac_info = pd.read_excel(file_path + 'raw/1.병원정보서비스 2024.3.xlsx') 
fac_info2 = pd.read_excel(file_path + 'raw/4.의료기관별상세정보서비스_02_세부정보 2024.3.xlsx')

# 데이터 병합
fac_merge = pd.merge(fac_info, fac_info2, on='암호화요양기호')

# 필요한 열 추출
fac_merge = fac_merge[(fac_merge['종별코드명'].isin(['상급종합', '종합병원', '병원', '의원', '보건의료원']))]
fac_hour = fac_merge.filter(regex='^진료')
fac_merge = pd.concat([fac_merge[['요양기관명_x', '종별코드명', '주소', '총의사수', '응급실_야간_운영여부']], fac_hour], axis=1)

# 서울, 경북 추출
fac_merge = fac_merge[(fac_merge['주소'].str.startswith(('서울', '경상북도')))]
fac_merge.rename(columns={'요양기관명_x': '기관명'}, inplace=True)

# 0인 값을 NaN으로 대체하고 NaN을 빈 문자열로 대체
fac_merge.replace(0, np.nan, inplace=True)
fac_merge.fillna('', inplace=True)

# 진료 시간을 정수로 변경
for col in fac_merge.columns:
    if '진료' in col:
        fac_merge[col] = pd.to_numeric(fac_merge[col], errors='coerce').astype('Int64')

# 주중 야간 진료 가능 병원
fac_weekday = fac_merge[(fac_merge['진료시작시간_월요일'] <= 600) & (fac_merge['진료시작시간_월요일'] != '') | 
                        (fac_merge['진료종료시간_월요일'] >= 2300) & (fac_merge['진료종료시간_월요일'] != '') |
                        (fac_merge['진료시작시간_화요일'] <= 600) & (fac_merge['진료시작시간_화요일'] != '') | 
                        (fac_merge['진료종료시간_화요일'] >= 2300) & (fac_merge['진료종료시간_화요일'] != '') |
                        (fac_merge['진료시작시간_수요일'] <= 600) & (fac_merge['진료시작시간_수요일'] != '') | 
                        (fac_merge['진료종료시간_수요일'] >= 2300) & (fac_merge['진료종료시간_수요일'] != '') |
                        (fac_merge['진료시작시간_목요일'] <= 600) & (fac_merge['진료시작시간_목요일'] != '') | 
                        (fac_merge['진료종료시간_목요일'] >= 2300) & (fac_merge['진료종료시간_목요일'] != '') |
                        (fac_merge['진료시작시간_금요일'] <= 600) & (fac_merge['진료시작시간_금요일'] != '') | 
                        (fac_merge['진료종료시간_금요일'] >= 2300) & (fac_merge['진료종료시간_금요일'] != '') |
                        (fac_merge['응급실_야간_운영여부'] == 'Y')]

fac_weekday.to_csv(file_path + 'supply/fac_weekday.csv', index=False, encoding='euc-kr')

fac_sl_weekday = fac_weekday[(fac_weekday['주소'].str.startswith('서울'))]
fac_sl_weekday.to_csv(file_path + 'supply/fac_sl_weekday.csv', index=False, encoding='euc-kr')

fac_gb_weekday = fac_weekday[(fac_weekday['주소'].str.startswith('경상북도'))]
fac_gb_weekday.to_csv(file_path + 'supply/fac_gb_weekday.csv', index=False, encoding='euc-kr')

# 주말 야간 진료 가능 병원
fac_weekend = fac_merge[(fac_merge['진료시작시간_토요일'] <= 600) & (fac_merge['진료시작시간_토요일'] != '') | 
                        (fac_merge['진료종료시간_토요일'] >= 2300) & (fac_merge['진료종료시간_토요일'] != '') |
                        (fac_merge['진료시작시간_일요일'] <= 600) & (fac_merge['진료시작시간_일요일'] != '') | 
                        (fac_merge['진료종료시간_일요일'] >= 2300) & (fac_merge['진료종료시간_일요일'] != '') |
                        (fac_merge['응급실_야간_운영여부'] == 'Y')]

fac_weekend.to_csv(file_path + 'supply/fac_weekend.csv', index=False, encoding='euc-kr')

fac_sl_weekend = fac_weekend[(fac_weekend['주소'].str.startswith('서울'))]
fac_sl_weekend.to_csv(file_path + 'supply/fac_sl_weekend.csv', index=False, encoding='euc-kr')

fac_gb_weekend = fac_weekend[(fac_weekend['주소'].str.startswith('경상북도'))]
fac_gb_weekend.to_csv(file_path + 'supply/fac_gb_weekend.csv', index=False, encoding='euc-kr')
