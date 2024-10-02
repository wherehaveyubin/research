from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
from time import time, sleep
import ast
from pandas import DataFrame

while True:
    gu_name = ['종로구', '중구', '용산구', '성동구', '광진구', 
           '동대문구', '중랑구', '성북구', '강북구', '도봉구', 
           '노원구', '은평구', '서대문구', '마포구', '양천구', 
           '강서구', '구로구', '금천구', '영등포구', '동작구', 
           '관악구', '서초구', '강남구', '송파구', '강동구', '기타']

    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y%m%d_%H%M')
    nowTime = now.strftime('%H%M')
    today = datetime.datetime.today()
    target_time = ['800', '1300', '1700', '2100', '1235', '1240']

    if nowTime in target_time:
        
        driver = webdriver.Chrome('*/chromedriver.exe')
        driver.implicitly_wait(3) #3초 대기
        driver.get("https://www.seoul.go.kr/coronaV/coronaStatus.do") #url 지정
        driver.implicitly_wait(3) #3초 대기
    
        ##실시간 추가 확진자수 크롤링
        html = driver.page_source #
        soup = BeautifulSoup(html, 'html.parser') #BeautifulSoup 사용하기
        today_cnt = soup.select('td') #
        line1 = today_cnt[13:26] #윗줄 []인덱싱 숫자 주의
        line2 = today_cnt[39:52] #아랫줄
        line_merge = line1 + line2 #두 줄 합치기
    
        #list to str, str 편집
        cnt_str = str(line_merge)
        rp1 = cnt_str.replace('"', "")
        rp2 = rp1.replace("<td class=today>", "")
        rp3 = rp2.replace("+", "")
        rp4 = rp3.replace("</td>", "")
    
        #str to list
        cnt_list = ast.literal_eval(rp4) 
    
        #df 생성
        cnt_df = DataFrame(gu_name, columns=['gu_name'])
        cnt_df['td_cnt'] = DataFrame(cnt_list)
        
        ##총 확진자수 크롤링
        line3 = today_cnt[0:13] #윗줄 []인덱싱 숫자 주의
        line4 = today_cnt[26:39] #아랫줄
        line_merge2 = line3 + line4 #두 줄 합치기
        
        #list to str, str 편집
        cnt_str2 = str(line_merge2)
        rp5 = cnt_str2.replace('"', "")
        rp6 = rp5.replace("<td>", "")
        rp7 = rp6.replace("</td>", "")
    
        #str to list
        cnt_list2 = ast.literal_eval(rp7) 
    
        #df 생성
        cnt_df['all_cnt'] = DataFrame(cnt_list2)
    
        #저장
        cnt_df.to_csv("*" + nowDatetime + "_COVID-19.csv",
                      encoding='euc-kr', index=False)
    
        #크롬 닫기
        driver.close()
        print(nowDatetime)
    
    sleep(61) #61초 대기
