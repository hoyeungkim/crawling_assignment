#순위표가 있는 웹페이지에서 기업들의 고유코드를 가져와 dictionary형태로 저장하는 코드
#여기서는 IT관련 주식들의 top100을 선정하고 있다.
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Chrome WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저 창을 열지 않음
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# WebDriver 실행 (webdriver_manager로 자동 설치)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL로 이동
url = "https://comp.fnguide.com/SVO2/asp/SVD_UJRank.asp?pGB=1&gicode=A000270&cID=&MenuYn=Y&ReportGB=&NewMenuID=301&stkGb=701"
driver.get(url)

# 페이지 로드 대기
time.sleep(3)

# selUpjong 드롭다운에서 IT 업종 선택
try:
    # ID가 'selUpjong'인 드롭다운 요소를 대기
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'selUpjong'))
    )
    select_element = Select(dropdown)  # Select 객체로 변환
    select_element.select_by_value("FI00.45")  # IT 업종의 value 값 선택

    time.sleep(2)  # 변경 내용 반영 대기

    # 조회 버튼 클릭
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'btnSearch'))
    )
    search_button.click()  # 조회 버튼 클릭

    time.sleep(5)  # 페이지 로드 대기
except Exception as e:
    print("업종 선택 또는 조회 버튼 클릭에 실패했습니다:", e)
    driver.quit()
    exit()

# class="l tbold"인 <td> 태그 찾기
td_elements = driver.find_elements(By.CLASS_NAME, "l.tbold")

# 딕셔너리 형태로 값들을 저장할 변수
extracted_dict = {}

# 각 <td> 태그 내에서 하이퍼링크 (a 태그) 추출
for td in td_elements:
    # <td> 안의 모든 <a> 태그 찾기
    a_tags = td.find_elements(By.TAG_NAME, 'a')
    
    # 각 <a> 태그의 href 속성(링크) 추출
    for a in a_tags:
        link = a.get_attribute('href')
        
        # 'javascript:ViewReport(...)'에서 인자값만 추출하는 정규 표현식
        match = re.search(r"javascript:ViewReport\('([^']+)'\)", link)
        
        if match:
            # a 태그의 텍스트를 키로, 추출한 인자값을 값으로 딕셔너리에 추가
            extracted_dict[a.text] = match.group(1)
            
            # 최대 100개만 추출
            if len(extracted_dict) >= 100:
                break

    # 100개 이상 추출되면 반복 종료
    if len(extracted_dict) >= 100:
        break

# 추출한 딕셔너리를 JSON 파일로 저장
with open("extracted_dict.json", "w", encoding="utf-8") as f:
    json.dump(extracted_dict, f, ensure_ascii=False, indent=4)

# WebDriver 종료
driver.quit()
