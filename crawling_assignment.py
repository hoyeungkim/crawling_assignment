import pandas as pd
import re
import trafilatura

# URL 설정
url = "https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A005930&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701"

# Trafilatura로 HTML 본문 추출
downloaded = trafilatura.fetch_url(url)

if downloaded:
    text = trafilatura.extract(downloaded, include_tables=True)
else:
    print("URL에서 데이터를 가져올 수 없습니다.")
    text = ""

# 매출액, 당기순이익, 영업활동으로인한현금흐름, 투자활동으로인한현금흐름, 재무활동으로인한현금흐름 데이터 추출
pattern = r"(매출액|당기순이익|영업활동으로인한현금흐름|투자활동으로인한현금흐름|재무활동으로인한현금흐름)\s*\|\s*(.*?)\n"
matches = re.findall(pattern, text)

# 데이터 정리
data = []
columns = ["항목", "2021/12", "2022/12", "2023/12", "2024/06", "전년동기", "전년동기(%)"]

# 항목 이름 변경: 영업활동으로인한현금흐름 -> 영업활동현금흐름, 투자활동으로인한현금흐름 -> 투자활동현금흐름, 재무활동으로인한현금흐름 -> 재무활동현금흐름
matches = [(항목명.replace("영업활동으로인한현금흐름", "영업활동현금흐름")
            .replace("투자활동으로인한현금흐름", "투자활동현금흐름")
            .replace("재무활동으로인한현금흐름", "재무활동현금흐름"), 값) 
           for 항목명, 값 in matches]

# 항목을 연간, 분기로 나누기 위한 처리
항목_카운트 = {}

for match in matches:
    항목명 = match[0]
    
    # 항목의 등장 횟수에 따라 연간, 분기 구분
    if 항목명 not in 항목_카운트:
        항목_카운트[항목명] = 1
        항목명_변경 = f"{항목명}(연간)"
    else:
        항목_카운트[항목명] += 1
        항목명_변경 = f"{항목명}(분기)"
    
    # 해당 항목 데이터를 처리
    row = [항목명_변경] + [x.strip() for x in match[1].split("|")]
    # 열 수 맞추기: 데이터가 부족하면 NaN으로 채움
    if len(row) < len(columns):
        row += [None] * (len(columns) - len(row))
    # 데이터 초과 시, 필요한 만큼만 사용
    elif len(row) > len(columns):
        row = row[:len(columns)]
    
    data.append(row)

# pandas DataFrame 생성
df = pd.DataFrame(data, columns=columns)

# 숫자로 변환할 수 있는 항목들만 추출 (쉼표 제거 후)
def clean_and_convert(value):
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None

# 숫자 데이터로 변환
for col in df.columns[1:]:
    df[col] = df[col].apply(clean_and_convert)

# 영업활동, 투자활동, 재무활동의 현금흐름 합을 계산하여 새로운 "잉여현금흐름" 행 추가
영업활동_col = "영업활동현금흐름"
투자활동_col = "투자활동현금흐름"
재무활동_col = "재무활동현금흐름"

# "영업활동현금흐름", "투자활동현금흐름", "재무활동현금흐름"이 존재할 때만 처리
if 영업활동_col in df["항목"].values and 투자활동_col in df["항목"].values and 재무활동_col in df["항목"].values:
    영업활동 = df[df["항목"] == 영업활동_col].iloc[0, 1:]
    투자활동 = df[df["항목"] == 투자활동_col].iloc[0, 1:]
    재무활동 = df[df["항목"] == 재무활동_col].iloc[0, 1:]
    
    # 잉여현금흐름 계산 (영업활동 + 투자활동 + 재무활동)
    잉여현금흐름 = 영업활동 + 투자활동 + 재무활동

    # 잉여현금흐름을 새로운 행으로 추가
    new_row = ["잉여현금흐름"] + 잉여현금흐름.tolist()
    df.loc[len(df)] = new_row

# 결과 출력
df
