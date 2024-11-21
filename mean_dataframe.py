#추출한 기업들의 데이터를 바탕으로 평균치를 계산하여 데이터프레임으로 만드는 코드
import pandas as pd

# CSV 파일 읽기 (파일 경로를 넣어야 함)
df = pd.read_csv('all_company_data.csv')

# NaN을 제외하고 평균 계산 (숫자형 데이터만 사용)
df = df.replace({'N/A': None, ',': ''}, regex=True)  # 'N/A'를 None으로, ',' 제거
df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')  # 숫자형으로 변환

# '기업명' 열을 제외하고, 각 항목별로 기업들의 평균 계산
averages = df.drop(columns='기업명').groupby('항목').mean()

# 평균값 출력 (결과를 DataFrame으로 만듦)
averages = averages.reset_index()  # 항목을 인덱스에서 컬럼으로 이동

# 원하는 항목 순서대로 리스트 생성
desired_order = [
    '매출액', '당기순이익', '영업활동현금흐름', '잉여현금흐름', '부채비율', 
    '유보율', 'ROE', '총자산회전율', '시가총액', 'PER', 'PBR', 'EV/EBITDA'
]

# 항목 순서를 원하는 대로 재정렬
averages = averages.set_index('항목').reindex([item for item in desired_order] ).reset_index()

# 출력
averages
