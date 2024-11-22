#제일 좋은 기업과 기업들 평균치를 방사형 차트로 보여주는 코드
import pandas as pd
import plotly.graph_objects as go

# CSV 파일 읽기
file_path = "scored_company_data_sorted.csv"
data = pd.read_csv(file_path)

# 점수 컬럼이 없으면 처리
if "점수" not in data.columns:
    print("점수 컬럼이 데이터에 없습니다. 점수를 먼저 계산해주세요.")
else:
    # 제일 좋은 기업 (점수 합계가 가장 높은 기업 1개)
    best_company = data.groupby('기업명')['점수'].sum().idxmax()

    # "average" 기업 데이터 필터링
    average_data = data[data['기업명'] == "average"]

    # 색상 리스트 (RGBA 값을 사용하여 투명도 설정)
    colors = [
        'rgba(0, 0, 255, 0.4)',  # 제일 좋은 기업 파란색
        'rgba(255, 0, 0, 0.4)'   # "average" 기업 빨간색
    ]

    # 방사형 차트 그리기
    def plot_radar_chart():
        # Plotly를 사용하여 빈 차트 생성
        fig = go.Figure()

        # 제일 좋은 기업에 대해 그래프 추가
        best_company_data = data[data['기업명'] == best_company]
        if not best_company_data.empty:
            categories = best_company_data['항목'].tolist()
            values = best_company_data['점수'].tolist()
            recent_values = best_company_data['최근값'].tolist()

            # 시작점과 끝점을 이어주기 위해 첫 번째 값을 마지막에 추가
            categories += categories[:1]
            values += values[:1]
            recent_values += recent_values[:1]

            # 호버 텍스트 생성
            hover_text = [f"{categories[i]}: {recent_values[i]}" for i in range(len(categories))]

            # 제일 좋은 기업 차트 추가
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                mode='lines+markers',  # 선과 점 표시
                line=dict(color=colors[0], width=2),  # 선 색상과 두께 설정
                marker=dict(size=6),  # 점 크기 설정
                text=hover_text,  # 호버 텍스트 설정
                hoverinfo="text",  # 텍스트를 호버 정보로 표시
                name=best_company,
            ))

        # "average" 기업에 대해 그래프 추가
        if not average_data.empty:
            categories = average_data['항목'].tolist()
            values = average_data['점수'].tolist()
            recent_values = average_data['최근값'].tolist()

            # 시작점과 끝점을 이어주기 위해 첫 번째 값을 마지막에 추가
            categories += categories[:1]
            values += values[:1]
            recent_values += recent_values[:1]

            # 호버 텍스트 생성
            hover_text = [f"{categories[i]}: {recent_values[i]}" for i in range(len(categories))]

            # "average" 기업 차트 추가
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                mode='lines+markers',  # 선과 점 표시
                line=dict(color=colors[1], width=2),  # 선 색상과 두께 설정
                marker=dict(size=6),  # 점 크기 설정
                text=hover_text,  # 호버 텍스트 설정
                hoverinfo="text",  # 텍스트를 호버 정보로 표시
                name="average",
            ))

        # 레이아웃 설정
        fig.update_layout(
            title="제일 좋은 기업과 Average 기업 방사형 차트",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]  # 최대 점수 10으로 설정
                ),
            ),
            showlegend=True,  # 범례 표시
        )

        # 그래프 표시
        fig.show()

    # 방사형 차트 그리기
    plot_radar_chart()
