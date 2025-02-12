import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

def run_prediction():
    st.title("Prediction")

    st.subheader("국가 그룹별 25,26년 입국자 예상 트렌드")

    #예측 희망 년 월 선택
    #예측 희망 국가 지도에서 선택
    df=pd.read_csv("data/seasonal_df.csv")
    countries = df['국적지역'].unique().tolist()
    st.write(countries)
    # 국가별 지도 데이터 로드
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))



    #예측 결과 출력
    #해당 국가의 클러스터 출력



    #계절 클릭시
    #어떤 클러스터가 많이 방문하는지 출력

    #해당 계절의 추천 여행 패키지 출력 - 트랜드반영할수있게
    

