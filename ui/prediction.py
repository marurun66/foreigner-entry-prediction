import datetime
from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px

# 분기별 계절 매핑
def get_quarter_season(quarter):
    seasons = {"1분기 (봄 3~5월)": "봄", "2분기 (여름 6~8월)": "여름", "3분기 (가을 9~11월)": "가을", "4분기 (겨울 12~2월)": "겨울"}
    return seasons[quarter]
    
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rc('font', family='AppleGothic')

    
def run_prediction():
    st.title("Prediction")
    st.subheader("국가 그룹별 25,26년 입국자 예상 트렌드")
    # 클러스터링 완료 데이터 로드
    seasonal_df = pd.read_csv('data/seasonal_df.csv')
    # 프로펫 완료 데이터 로드
    prophet_df = pd.read_csv('data/prophet_df.csv')


    # 사용자 입력: 년, 분기 선택
    col1, col2 = st.columns(2)
    selected_year = col1.selectbox("년도를 선택하세요", list(range(2025, 2027)))
    selected_quarter = col2.selectbox("분기를 선택하세요", ["1분기 (봄 3~5월)", "2분기 (여름 6~8월)", "3분기 (가을 9~11월)", "4분기 (겨울 12~2월)"], index=0)
    selected_season = get_quarter_season(selected_quarter)

    # 해당 계절에 대한 클러스터별 평균 입국자 수 분석
    season_df = seasonal_df.groupby("클러스터")[[selected_season]].mean().reset_index()
    season_df = seasonal_df.sort_values(by=selected_season, ascending=False)

    # 데이터 시각화
    st.subheader(f"{selected_season}에 입국자 수가 많은 클러스터")
    fig, ax = plt.subplots()
    ax.bar(season_df["클러스터"].astype(str), season_df[selected_season], color='skyblue')
    ax.set_xlabel("클러스터")
    ax.set_ylabel("평균 입국자 수")
    ax.set_title(f"{selected_season} 계절별 클러스터 입국자 수 비교")
    st.pyplot(fig)

    # 클러스터별 국가 리스트 제공
    st.subheader("클러스터별 국가 정보")
    selected_cluster = st.selectbox("클러스터를 선택하세요", season_df["클러스터"].unique())
    cluster_countries = df[df["클러스터"] == selected_cluster][["국적지역", selected_season]].sort_values(by=selected_season, ascending=False)
    st.dataframe(cluster_countries)

    #예측 결과 출력
    #해당 국가의 클러스터 출력



    #계절 클릭시
    #어떤 클러스터가 많이 방문하는지 출력

    #해당 계절의 추천 여행 패키지 출력 - 트랜드반영할수있게
    

