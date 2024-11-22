import pandas as pd
import numpy as np

# CSV 파일 읽기
file_path = "processed_company_data.csv"
data = pd.read_csv(file_path)

# 점수 계산 함수 (1 ~ 10 점수)
def assign_scores(df, column="최근값"):
    scores = list(range(1, 11))  # 점수는 1부터 10까지
    
    # NaN 값 제외하고 계산
    valid_values = df[column].dropna()
    if valid_values.empty:
        df["점수"] = np.nan
        return df
    
    # 각 값의 순위를 계산하여 점수 부여
    rank = valid_values.rank(pct=True)  # 값들을 0~1 사이로 정규화된 순위로 변환
    df["점수"] = pd.cut(rank, bins=np.linspace(0, 1, 11), labels=scores, include_lowest=True).astype(int)
    
    return df

# 항목별로 점수 계산
scored_data = []
for 항목 in data["항목"].unique():
    항목_data = data[data["항목"] == 항목].copy()
    항목_data = assign_scores(항목_data)

    # 반대로 계산할 항목 (예: 부채비율, PER, PBR, EV/EBITDA)
    if 항목 in ["부채비율", "PER", "PBR", "EV/EBITDA"]:
        항목_data["점수"] = 11 - 항목_data["점수"]  # 계산된 점수에서 11을 빼서 반전
    
    scored_data.append(항목_data)

# 결과 합치기
final_data = pd.concat(scored_data, ignore_index=True)

# 기업명 기준 정렬
final_data = final_data.sort_values(by=["기업명", "항목"], ignore_index=True)

# NaN 점수 기본 처리 (0점 할당)
final_data["점수"] = final_data["점수"].fillna(0).astype(int)

# 결과 확인
print(final_data)

# 결과를 CSV로 저장
final_data.to_csv("scored_company_data_sorted.csv", index=False, encoding="utf-8-sig")
