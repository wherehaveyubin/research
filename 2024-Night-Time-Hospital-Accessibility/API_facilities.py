import requests
import xml.etree.ElementTree as ET
import pandas as pd

url = 'http://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlMdcncListInfoInqire'
serviceKey = requests.utils.unquote('*')

# 서울
params = {
    'serviceKey': serviceKey,
    'Q0': '서울특별시',
    'pageNo': '1',
    'numOfRows': '100'
}

all_data = []

while True:
    response = requests.get(url, params=params)
    response.encoding = 'utf-8'
    root = ET.fromstring(response.text)

    items = root.findall('.//item')
    if not items:
        break

    for item in items:
        item_data = {child.tag: child.text for child in item}
        all_data.append(item_data)

    params['pageNo'] = str(int(params['pageNo']) + 1)

df = pd.DataFrame(all_data)
print(df)
file_path = './'
df.to_csv(file_path + 'supply/egen_sl.csv', index=False, encoding='euc-kr') # 6,901행

# 경북
params = {
    'serviceKey': serviceKey,
    'Q0': '경상북도',
    'pageNo': '1',
    'numOfRows': '100'
}

all_data = []

while True:
    response = requests.get(url, params=params)
    response.encoding = 'utf-8'
    root = ET.fromstring(response.text)

    items = root.findall('.//item')
    if not items:
        break

    for item in items:
        item_data = {child.tag: child.text for child in item}
        all_data.append(item_data)

    params['pageNo'] = str(int(params['pageNo']) + 1)

df = pd.DataFrame(all_data)
print(df)
file_path = './'
df.to_csv(file_path + 'supply/egen_gb.csv', index=False, encoding='euc-kr') # 3,331행
