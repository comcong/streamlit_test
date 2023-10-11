import requests
# from bs4 import BeautifulSoup
import re
# import json
import math
import pandas as pd

city = '서구 원당동'

url = 'https://m.land.naver.com/search/result/'
url += city
hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
response = requests.get(url, headers=hdr)



pattern = re.compile(r"filter:\s*{([^}]*)}")
match = pattern.search(response.text)
print((match))

if match:
    result = dict(re.findall(r"(\w+):\s*'([^']*)'", match.group(1)))
lat = result['lat'] # 위도
lon = result['lon'] # 경도
z = result['z']
cortarNo = result['cortarNo']  # 지역코드
search_type = 'APT' #건물 유형
building_type = 'A1:B1:B2' #평형 타입

# 검색 지역안의 단지들의 정보를 담고 있는 주소
url = f'https://m.land.naver.com/cluster/clusterList?cortarNo={cortarNo}&' \
      f'rletTpCd={search_type}&tradTpCd={building_type}&z={z}&lat={lat}&' \
      f'lon={lon}&addon=COMPLEX&isOnlyIsale=false'

# 단지 리스트 정보를 json 형태로 담는다.
response = ''
response = requests.get(url, headers=hdr)
response = response.json()

# 단지들 리스트
result = []
cnt = 0
for item in response['data']['COMPLEX']:
    result.append({'lgeo': item['lgeo'], 'lat': item['lat'], 'lon': item['lon'], 'count': item['count']})

maemul = []
count = 0
img_url = 'https://landthumb-phinf.pstatic.net'
for i in enumerate(result):
    page = math.ceil(i[1]['count']/20)
    lgeo = i[1]['lgeo']
    lat  = i[1][ 'lat']
    lon  = i[1][ 'lon']
    for j in range(page):
        url = f'https://m.land.naver.com/cluster/ajax/complexList?itemId={lgeo}&lgeo={lgeo}&rletTpCd={search_type}&tradTpCd={building_type}&z={z}&lat={lat}&lon={lon}&cortarNo={cortarNo}&isOnlyIsale=false&poiType=CC&preSaleComplexNumber=2120233332&sort=readRank&page={j+1}'
        data = requests.get(url, headers=hdr).json()['result']
        for k in data:
            if "repImgUrl" in k:
                k['repImgUrl'] = img_url + k['repImgUrl']
            else:
                k['repImgUrl'] = 'N'
            k['검색지역'] = city
            maemul.append(k)

# 영어로 된 컬럼명 한글로 수정
df = pd.DataFrame(maemul).rename(columns={'hscpNm':'단지명', 'useAprvYmd':'사용승인일', 'hscpTypeCd':'건물타입', 'hscpNo':'단지ID',
                                          'totDongCnt':'동수', 'hscpTypeNm':'빌딩타입', 'totHsehCnt':'세대수', 'repImgUrl':'대표이미지',
                                          'dealCnt':'매매', 'leaseCnt':'전세', 'rentCnt':'월세', 'totalAtclCnt':'총잔량', 'minSpc':'최소면적',
                                          'maxSpc':'최대면적', 'dealPrcMin':'최소매매가', 'dealPrcMax':'최대매매가', 'leasePrcMin':'최소전세가',
                                          'leasePrcMax':'최대전세가', 'strmRentCnt':'단기',
                                          })

# 데이터 전처리
df['최소매매가'] = df['최소매매가'].str.replace('<em class=\'txt_unit\'>', '').str.replace('</em>', '')
df['최대매매가'] = df['최대매매가'].str.replace('<em class=\'txt_unit\'>', '').str.replace('</em>', '')
df['최대전세가'] = df['최대전세가'].str.replace('<em class=\'txt_unit\'>', '').str.replace('</em>', '')
df['최소전세가'] = df['최소전세가'].str.replace('<em class=\'txt_unit\'>', '').str.replace('</em>', '')


#  컬럼 순서 지정
df = df[['검색지역', '단지명', '단지ID', '건물타입', '빌딩타입', '동수', '세대수', 'genHsehCnt', '사용승인일',
       '대표이미지', '매매', '전세', '월세', '단기', '총잔량', '최소면적', '최대면적',
       '최소매매가', '최대매매가', '최소전세가', '최대전세가', 'isalePrcMin', 'isalePrcMax',
       'isaleNotifSeq', 'isaleScheLabel', 'isaleScheLabelPre' ]]

df
