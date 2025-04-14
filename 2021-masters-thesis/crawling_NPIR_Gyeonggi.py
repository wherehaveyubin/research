from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
from time import time, sleep
import ast
from pandas import DataFrame
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pyperclip
import pandas as pd

df_name = ['응급실_음압격리', '응급실_일반격리', '격리진료구역_음압격리', 
           '격리진료구역_일반격리', '응급전용_입원실 음압격리', 
           '응급전용_입원실 일반격리', '응급전용_중환자실 음압격리']
df_name2 = ['응급전용_중환자실 일반격리', '중환자실_음압격리', '입원실_음압격리']
rg_list = [3, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,
           1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2]
hpt_list = [3, 1, 1, 1, 1, 2, 2, 3, 4, 4, 2, 1, 1, 1, 1, 2, 3, 2, 1, 2, 1, 1, 1,
            1, 1, 1, 1, 2, 4, 1, 1, 4, 2, 3]

#빈 df 생성
hpt_df = pd.DataFrame()

hpt_df = pd.DataFrame()

now = datetime.datetime.now()
nowDatetime = now.strftime('%Y%m%d_%H%M')
nowTime = now.strftime('%H%M')
today = datetime.datetime.today()

driver = webdriver.Chrome('./chromedriver.exe')
driver.implicitly_wait(3)
driver.get("https://portal.nemc.or.kr:444/medi_info/dashboards/dash_total_emer_org_popup_for_egen.do")
driver.implicitly_wait(3)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# check box
driver.find_element_by_xpath('//*[@id="label_O003"]').click() #[응급실] 음압격리
driver.find_element_by_xpath('//*[@id="label_O004"]').click() #[응급실] 일반격리
driver.find_element_by_xpath('//*[@id="label_O046"]').click() #[격리진료구역] 음압격리
driver.find_element_by_xpath('//*[@id="label_O047"]').click() #[격리진료구역] 일반격리
driver.find_element_by_xpath('//*[@id="label_O052"]').click() #[응급전용] 입원실 음압격리
driver.find_element_by_xpath('//*[@id="label_O053"]').click() #[응급전용] 입원실 일반격리
driver.find_element_by_xpath('//*[@id="label_O050"]').click() #[응급실] 중환자실 음압격리
driver.find_element_by_xpath('//*[@id="label_O051"]').click() #[응급실] 중환자실 일반격리
driver.find_element_by_xpath('//*[@id="label_O025"]').click() #[입원실] 음압격리
driver.find_element_by_xpath('//*[@id="label_O018"]').click() #[중환자실] 음압격리

#세부지역 선택
driver.find_element_by_xpath('//*[@id="emogdstr"]').click() 
element = driver.find_element_by_xpath('//*[@id="emogdstr"]')

hpt_df = pd.DataFrame()
hpt_df

hpt_name = []
hpt_name2 = []
line1_df = pd.DataFrame()
line2_df = pd.DataFrame()
line1_df2 = pd.DataFrame()
line2_df2 = pd.DataFrame()

hpt_name = []

for i in range(34): #총 시/구 개수 -34개라서 35로 입력
    driver.find_element_by_xpath('//*[@id="emogloca"]').click() 
    element = driver.find_element_by_xpath('//*[@id="emogloca"]')
    for a in range(8): #화살표 아래로 8칸
        element.send_keys(Keys.ARROW_DOWN)
    if rg_list[i] == 2: #만약 2칸 내려야한다면
        for j in range(2): #2번 화살표 아래로
            driver.find_element_by_xpath('//*[@id="emogdstr"]').click()
            element = driver.find_element_by_xpath('//*[@id="emogdstr"]')
            element.send_keys(Keys.ARROW_DOWN)
    elif rg_list[i] == 1:
        driver.find_element_by_xpath('//*[@id="emogdstr"]').click()
        element = driver.find_element_by_xpath('//*[@id="emogdstr"]')
        element.send_keys(Keys.ARROW_DOWN)
    elif rg_list[i] == 3:
        for z in range(3): #3번 화살표 아래로
            driver.find_element_by_xpath('//*[@id="emogdstr"]').click()
            element = driver.find_element_by_xpath('//*[@id="emogdstr"]')
            element.send_keys(Keys.ARROW_DOWN)
        
    #조회하기 클릭
    driver.find_element_by_xpath('//*[@id="btn_search"]').click()
    
    #각 페이지 병원 개수에 따라
    ##병원이 1개일때
    if hpt_list[i] == 1:
        for k in range(1):
            hpt_nm = driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[1]/div/div[1]/div/span/a")
            hpt_nm = hpt_nm.text #텍스트화
            hpt_nm = hpt_nm.replace("[권역]", "")
            hpt_nm = hpt_nm.replace("[소아]", "")
            hpt_nm = hpt_nm.replace("[중증]", "")
            hpt_nm = hpt_nm.replace("[외상]", "")
            hpt_nm = hpt_nm.replace("[센터]", "")
            hpt_nm = hpt_nm.replace("[기관]", "")
            hpt_nm = hpt_nm.replace("   ", "")
            hpt_nm = hpt_nm.replace("  ", "")
            hpt_nm = hpt_nm.replace(" ", "")
            hpt_name.append(hpt_nm)
            
    ##병원이 2개 이상일때
    elif hpt_list[i] > 1:
        for k in range(1, hpt_list[i]+1):
            hpt_nm = driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[" + str(k)+ "]/div/div[1]/div/span/a")
            hpt_nm = hpt_nm.text #텍스트화
            hpt_nm = hpt_nm.replace("[권역]", "")
            hpt_nm = hpt_nm.replace("[소아]", "")
            hpt_nm = hpt_nm.replace("[중증]", "")
            hpt_nm = hpt_nm.replace("[외상]", "")
            hpt_nm = hpt_nm.replace("[센터]", "")
            hpt_nm = hpt_nm.replace("[기관]", "")
            hpt_nm = hpt_nm.replace("   ", "")
            hpt_nm = hpt_nm.replace("  ", "")
            hpt_nm = hpt_nm.replace(" ", "")
            hpt_name.append(hpt_nm)
            
    hpt_df = DataFrame(hpt_name, columns=['hpt_name'])

    #첫번째 줄
    for m in range(1, 8):
        a1 = []
        for n in range(1, hpt_list[i]+1):
            try:
                tmp = driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[" + str(n)+  "]/div/div[2]/div[2]/table/tbody/tr[1]/td[" + str(m) + "]/div[2]")
                tmp2 = tmp.text #텍스트화
            except:
                    tmp2 = 0
        
            if tmp2 == '': #만약 아무 내용 없으면 0으로 반환
                tmp2 = 0
                a1.append(tmp2)
        
            elif tmp2 == "임시 운영 중단":
                tmp2 = 0
                a1.append(tmp2)
            
            elif tmp2 == 0:
                a1.append(tmp2)
        
            else:
                tmp3 = tmp2.partition('/')
                tmp4 = int(tmp3[0]) #가용 병상
                if tmp4 < 0:
                    tmp4 = 0
                    a1.append(tmp4)
                else:
                    a1.append(tmp4)
                
        #병상 이름 df 생성
        hpt_df[df_name[m-1]] = DataFrame(a1)
    
    #펼치기 클릭
    driver.find_element_by_xpath('/html/body/div[4]/div/div[1]/div[2]/p/span').click()

hpt_df

#격리실 수 합
hpt_df['총_일반격리'] = hpt_df['응급실_일반격리'] + hpt_df['격리진료구역_일반격리'] + hpt_df['응급전용_입원실 일반격리']+hpt_df['응급전용_중환자실 일반격리']

hpt_df['총_음압격리'] = hpt_df['응급실_음압격리'] + hpt_df['격리진료구역_음압격리'] + hpt_df['응급전용_입원실 음압격리'] + hpt_df['응급전용_중환자실 음압격리'] + hpt_df['중환자실_음압격리'] + hpt_df['입원실_음압격리']

hpt_df['총_격리실'] = hpt_df['총_일반격리'] + hpt_df['총_음압격리']

hpt_df['병원명'] = hpt_name

hpt_df = hpt_df[['병원명', '응급실_음압격리', '응급실_일반격리', 
                 '격리진료구역_음압격리', '격리진료구역_일반격리', 
                 '응급전용_입원실 음압격리', '응급전용_입원실 일반격리',
                 '응급전용_중환자실 음압격리', '응급전용_중환자실 일반격리', 
                 '중환자실_음압격리', '입원실_음압격리', '총_일반격리', 
                 '총_음압격리', '총_격리실']]

#export to csv
hpt_df.to_csv("." + nowDatetime + "_경기_병상수.csv", encoding='euc-kr', 
              index=False)
print(nowDatetime)
driver.close()
