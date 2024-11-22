# extracted_dict.py를 통해 추려낸 100개의 기업들의 주요데이터를 추출하여 dataframe을 형성하고 csv파일로 저장하는 코드
import pandas as pd
import re
import trafilatura
import requests
from bs4 import BeautifulSoup
import json

# JSON 파일에서 기업명과 고유 코드를 로드하는 함수
def load_company_codes(file_path="extracted_dict.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            company_codes = json.load(file)
        return company_codes
    except FileNotFoundError:
        print(f"{file_path} 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print(f"{file_path} 파일을 읽을 수 없습니다. 파일 형식이 올바른지 확인하세요.")
        return {}

# URL 생성 함수
def generate_urls(company_code):
    url_finance = f"https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode={company_code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701"
    url_ratio = f"https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode={company_code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701"
    url_invest = f"https://comp.fnguide.com/SVO2/ASP/SVD_Invest.asp?pGB=1&gicode={company_code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=105&stkGb=701"
    
    return url_finance, url_ratio, url_invest

# Trafilatura로 HTML 본문 추출
def fetch_data(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded, include_tables=True)
    else:
        print(f"URL에서 데이터를 가져올 수 없습니다: {url}")
        return ""

# 매출액, 당기순이익, 영업활동으로인한현금흐름 등 데이터 추출

def extract_finance_data(text):
    # 정규식 패턴: 매출액, 당기순이익, 영업활동현금흐름, 투자활동현금흐름, 재무활동현금흐름
    pattern = r"(매출액|당기순이익|영업활동으로인한현금흐름|투자활동으로인한현금흐름|재무활동으로인한현금흐름)\s*\|\s*(.*?)\n"
    matches = re.findall(pattern, text)

    # 항목 처리
    처리된_항목 = set()
    data = []
    columns = ["항목", "2021/12", "2022/12", "2023/12", "2024/09"]

    for match in matches:
        항목명 = match[0].replace("영업활동으로인한현금흐름", "영업활동현금흐름") \
                         .replace("투자활동으로인한현금흐름", "투자활동현금흐름") \
                         .replace("재무활동으로인한현금흐름", "재무활동현금흐름")

        if 항목명 in 처리된_항목:
            continue
        
        처리된_항목.add(항목명)
        row = [항목명] + [x.strip() for x in match[1].split("|")]
        
        if len(row) < len(columns):
            row += [None] * (len(columns) - len(row))
        elif len(row) > len(columns):
            row = row[:len(columns)]
        
        data.append(row)

    df = pd.DataFrame(data, columns=columns)
    
    # 잉여현금흐름(Final Cash Flow) 계산
    if {"영업활동현금흐름", "투자활동현금흐름", "재무활동현금흐름"}.issubset(df["항목"].values):
        # 쉼표를 제거하고 float으로 변환
        영업활동현금흐름 = df.loc[df["항목"] == "영업활동현금흐름"].iloc[:, 1:].replace({',': ''}, regex=True).values.astype(float)
        투자활동현금흐름 = df.loc[df["항목"] == "투자활동현금흐름"].iloc[:, 1:].replace({',': ''}, regex=True).values.astype(float)
        재무활동현금흐름 = df.loc[df["항목"] == "재무활동현금흐름"].iloc[:, 1:].replace({',': ''}, regex=True).values.astype(float)

        # 합산하여 잉여현금흐름 계산
        fcf = 영업활동현금흐름 + 투자활동현금흐름 + 재무활동현금흐름
        fcf_row = ["잉여현금흐름"] + fcf[0].tolist()

        # 잉여현금흐름 추가
        fcf_df = pd.DataFrame([fcf_row], columns=columns)
        df = pd.concat([df, fcf_df], ignore_index=True)

    # 매출액, 당기순이익, 영업활동현금흐름, 잉여현금흐름만 포함
    df = df[df["항목"].isin(["매출액", "당기순이익", "영업활동현금흐름", "잉여현금흐름"])]
    
    return df


def extract_row_data(soup, row_id, default_name):
    row = soup.find("tr", {"id": row_id})
    if row:
        item_name = row.select_one('th .txt_acd span').get_text(strip=True) if row.select_one('th .txt_acd span') else default_name
        values = [td.get_text(strip=True) for td in row.find_all("td", {"class": "r"})]
    else:
        item_name = default_name
        values = ["N/A"] * 5
    return item_name, values

def extract_ratio_data(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"페이지를 가져오지 못했습니다. 상태 코드: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", {"class": "us_table_ty1 h_fix zigbg_no"})
    if table:
        columns = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    else:
        print("테이블을 찾을 수 없습니다.")
        return pd.DataFrame()

    item_name1, values1 = extract_row_data(soup, "p_grid1_3", "부채비율")
    item_name2, values2 = extract_row_data(soup, "p_grid1_4", "유보율")
    item_name3, values3 = extract_row_data(soup, "p_grid1_18", "ROE")
    item_name4, values4 = extract_row_data(soup, "p_grid1_20", "총자산회전율")

    data = [
        [item_name1] + values1,
        [item_name2] + values2,
        [item_name3] + values3,
        [item_name4] + values4
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df.rename(columns={df.columns[0]: "항목"}, inplace=True)
    
    return df

def extract_invest_data(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"페이지를 가져오지 못했습니다. 상태 코드: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", {"class": "us_table_ty1 h_fix zigbg_no"})
    if table:
        columns = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    else:
        print("테이블을 찾을 수 없습니다.")
        return pd.DataFrame()

    market_cap_row = None
    for row in soup.find_all("tr"):
        th = row.find("th")
        if th and "시가총액" in th.get_text(strip=True):
            market_cap_row = row
            break

    if market_cap_row:
        market_cap_values = [td.get_text(strip=True) for td in market_cap_row.find_all("td", {"class": "r"})]
        market_cap_name = "시가총액"
    else:
        market_cap_values = ["N/A"] * 5
        market_cap_name = "시가총액"

    market_cap = market_cap_values[::2] if market_cap_values else ["N/A"] * 5

    item_name5, values5 = extract_row_data(soup, "p_grid1_9", "PER")
    item_name6, values6 = extract_row_data(soup, "p_grid1_12", "PBR")
    item_name7, values7 = extract_row_data(soup, "p_grid1_14", "EV/EBITDA")

    data = [
        [market_cap_name] + market_cap,
        [item_name5] + values5,
        [item_name6] + values6,
        [item_name7] + values7
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df.rename(columns={df.columns[0]: "항목"}, inplace=True)
    
    return df

def merge_dataframes(df_finance, df_ratio, df_invest, company_name):
    df_finance["기업명"] = company_name  # 기업명 열 추가
    df_ratio["기업명"] = company_name
    df_invest["기업명"] = company_name

    combined_df = pd.concat([df_finance, df_ratio, df_invest], ignore_index=True, sort=False)
    combined_df = combined_df.fillna("N/A")
    columns = ['기업명', '항목'] + sorted([col for col in combined_df.columns if col not in ['기업명', '항목']])
    combined_df = combined_df[columns]
    
    return combined_df

# 모든 기업에 대해 데이터 처리 및 저장
def process_and_save_all_data():
    company_codes = load_company_codes("extracted_dict.json")
    
    all_data = []  # 모든 데이터를 저장할 리스트

    for company_name, company_code in company_codes.items():
        print(f"데이터 처리 중: {company_name} ({company_code})")
        
        # URL 생성
        url_finance, url_ratio, url_invest = generate_urls(company_code)
        
        # Trafilatura로 금융 데이터 가져오기
        finance_data = fetch_data(url_finance)
        df_finance = extract_finance_data(finance_data)
        
        # 비율 데이터와 투자 데이터를 가져오기
        df_ratio = extract_ratio_data(url_ratio)
        df_invest = extract_invest_data(url_invest)

        # DataFrame들을 병합
        combined_df = merge_dataframes(df_finance, df_ratio, df_invest, company_name)
        
        # 기업명별로 데이터를 추가
        all_data.append(combined_df)

    # 모든 기업의 데이터를 하나의 DataFrame으로 합침
    final_df = pd.concat(all_data, ignore_index=True)

    # 하나의 CSV로 저장
    final_df.to_csv("all_company_data.csv", index=False, encoding="utf-8-sig")

# 실행
process_and_save_all_data()
