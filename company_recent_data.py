#추출된 데이터에서 가장 최근 값만을 추출하는 코드
import pandas as pd

# CSV 파일 읽기
file_path = "all_company_data.csv"
data = pd.read_csv(file_path)

# NaN 값을 채우기 위한 함수
def get_filled_latest_value(row):
    # NaN 값을 가장 최근 데이터로 채움
    for column in reversed(row.index[2:]):  # "2020/12" 이후 컬럼만 탐색
        if pd.notna(row[column]):
            return row[column]
    return None  # 모든 값이 NaN일 경우

# 기업별로 데이터 변형
result_dfs = []  # 각 기업별 결과를 저장할 리스트
for company in data["기업명"].unique():
    # 해당 기업 데이터 필터링
    company_data = data[data["기업명"] == company]
    
    # NaN 없이 최근 값 추출
    filled_values = company_data.apply(get_filled_latest_value, axis=1)
    
    # 새로운 데이터프레임 생성
    result_df = pd.DataFrame({
        "기업명": company_data["기업명"],
        "항목": company_data["항목"],
        "최근값": filled_values
    })
    
    result_dfs.append(result_df)

# 모든 기업 데이터 합치기
final_result = pd.concat(result_dfs, ignore_index=True)

# 결과를 CSV로 저장
final_result.to_csv("processed_company_data.csv", index=False, encoding="utf-8-sig")
