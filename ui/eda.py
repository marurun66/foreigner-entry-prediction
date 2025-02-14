import streamlit as st
import pandas as pd
import plotly.express as px


def run_eda():
    st.title("데이터 탐색 (EDA)")
    st.write("18년\~24년까지 (20\~22년 코로나 펜데믹기간 제외) 15개국 입국자 수를 토대로 향후 2년간의 입국자수를 예측합니다.")
    # 데이터 로드
    df=pd.read_csv('data/df_total.csv')
    
    # 🍎 유저에게 예측희망 년, 월 입력
    st.title("입국자 예측 대시보드 🌍")
    # Streamlit UI 설정
    col1, col2 = st.columns([1, 1])  # 1:1 비율로 배치
    # 한 줄에 연도 & 월 선택
    with col1:
        year = st.selectbox("연도", [2025, 2026], key="year")  # 연도 선택
    with col2:
        month = st.selectbox("월", list(range(1, 13)), key="month")  # 월 선택
    

######
    # 🍎 지도로 해당 년월의 각국 예상 입국인원을 봅니다.
    # 유저가 선택한 year, month에 해당하는 데이터 필터링
    select_df = df[(df["년"]==year) & (df["월"]==month)]
    
    # 국가명을 ISO 코드로 변환
    country_to_iso = {
        "중국": "CHN", "일본": "JPN", "미국": "USA", "프랑스": "FRA", "독일": "DEU",
        "영국": "GBR", "캐나다": "CAN", "호주": "AUS", "태국": "THA", "베트남": "VNM",
        "필리핀": "PHL", "인도네시아": "IDN", "말레이시아": "MYS", "싱가포르": "SGP",
        "러시아": "RUS", "인도": "IND", "브라질": "BRA", "멕시코": "MEX", "이탈리아": "ITA",
        "스페인": "ESP", "대만": "TWN", "오스트레일리아": "AUS", "홍콩": "HKG"
    }
    select_df["iso_alpha"] = select_df["국적지역"].map(country_to_iso)

    #select_df 컬럼명 변경 국적지역 -> 국가, 입국자수 -> 예상 입국자수
    select_df.rename(columns={"국적지역": "국가", "입국자수": "예상 입국자수"}, inplace=True)

    # Choropleth 지도 생성
        # 년,월,국적지역,입국자수
    fig = px.choropleth(
        select_df, # 데이터프레임
        locations="iso_alpha",  # 국가 코드 (ISO 3166-1 alpha-3)
        color=f"예상 입국자수",  # 색상 기준 (입국자 수)
        hover_name="국가",  # 마우스 올릴 때 표시될 국가명
        hover_data={"iso_alpha": False},  # iso_alpha를 숨김
        color_continuous_scale="Blues",
        color_continuous_midpoint=select_df["예상 입국자수"].median(),  # 색상 스케일
        title=f"🌍 {year}년 {month}월 국가별 입국자 예측 지도",

    )
# 데이터 없는 국가의 색을 회색으로 변경 (윤곽선 검정 유지)
    fig.update_geos(
        projection_type="natural earth",  # 자연스러운 지도 표현
        showcoastlines=True,  # 해안선 표시
        coastlinecolor="black",  # 해안선 검정색 (기본값 유지)
        showland=True,  # 육지 표시
        landcolor="lightgray",  # ❗ 데이터 없는 국가는 회색으로 변경
        showocean=True,  # 바다 표시
        oceancolor="white"  # 바다 색상 유지
    )
    fig.update_geos(projection_type="natural earth")  # 지도를 자연스럽게 표현

    # Streamlit에 지도 출력
    st.plotly_chart(fig)
    # 🍎 해당 년월의 각 국가별 예상 입국자 수를 표로 출력합니다
    st.write(f"📊 {year}년 {month}월 각 국가별 예상 입국자 수")
    st.dataframe(
        select_df[["국가", "예상 입국자수"]]
        .sort_values("예상 입국자수", ascending=False)
        .reset_index(drop=True)  # 기존 인덱스 삭제
        .rename_axis("순위")  # 인덱스 이름 설정
        .reset_index()
        .assign(순위=lambda df: df.index + 1),  # 순위 1부터 시작
        hide_index=True  # Streamlit에서 인덱스 숨기기
    )

    st.write("방문자 수가 50k 이상 예상되는 국가")
    st.dataframe(
        select_df[select_df["예상 입국자수"] >= 50000][["국가", "예상 입국자수"]]
        .sort_values("예상 입국자수", ascending=False)
        .reset_index(drop=True)  # 기존 인덱스 삭제
        .rename_axis("순위")  # 인덱스 이름 설정
        .reset_index()
        .assign(순위=lambda df: df.index + 1),  # 순위 1부터 시작
        hide_index=True  # Streamlit에서 인덱스 숨기기 (최신 버전)
    )

############################################################################################################

    # 날짜 컬럼 생성
    df['일'] = 1
    df = df.rename(columns={"년": "year", "월": "month", "일": "day"})
    df["ds"] = pd.to_datetime(df[["year", "month", "day"]])

    # 날짜 범위 설정
    selected_date = pd.to_datetime(f"{year}-{month}-01")
    start_date = selected_date - pd.DateOffset(months=3)
    end_date = selected_date + pd.DateOffset(months=3)

    # ✅ 해당 기간 데이터 필터링
    filtered_df = df[(df["ds"] >= start_date) & (df["ds"] <= end_date)]
    filtered_df = filtered_df.rename(columns={"입국자수": "yhat"})

    # ✅ 상위 5개국 선정 (선택한 연/월 기준)
    top_countries = (
        filtered_df[filtered_df["ds"] == selected_date]  # 선택한 연/월 기준 필터링
        .groupby("국적지역")["yhat"].sum()  # 입국자 수 합산
        .nlargest(5)  # 상위 5개국
        .index.tolist()
    )

    # ✅ 상위 5개국 데이터프레임 생성
    top_5_df = filtered_df[filtered_df["국적지역"].isin(top_countries)]

    # ✅ 그 외 국가 중 입국자 수 상위 10개국 선정
    other_countries_df = filtered_df[~filtered_df["국적지역"].isin(top_countries)]
    top_10_others = (
        other_countries_df[other_countries_df["ds"] == selected_date]  # 선택한 연/월 기준 필터링
        .groupby("국적지역")["yhat"].sum()  # 입국자 수 합산
        .nlargest(10)  # 상위 10개국
        .index.tolist()
    )

    # ✅ 그 외 국가 중 상위 10개국 데이터프레임 생성
    top_10_others_df = filtered_df[filtered_df["국적지역"].isin(top_10_others)]

    # ✅ Streamlit UI 출력
    st.subheader(f"📊 {year}년 {month}월 기준 상위 5개국 ±3개월 입국자 수 추이")
    #✅ 상위 5개국 차트    
    fig1 = px.line(top_5_df, x="ds", y="yhat", color="국적지역", markers=True)
    fig1.update_layout(
        xaxis=dict(range=[start_date, end_date]),
        xaxis_title="",
        yaxis_title="예측 입국자 수"
    )
    st.plotly_chart(fig1)  # ✅ 첫 번째 차트 출력

    st.subheader(f"📊 {year}년 {month}월 기준 그 외 10개국 ±3개월 입국자 수")
    # ✅ 그 외 국가 차트
    fig2 = px.line(top_10_others_df, x="ds", y="yhat", color="국적지역", markers=True)
    fig2.update_layout(
        xaxis=dict(range=[start_date, end_date]),
        xaxis_title="",
        yaxis_title="예측 입국자 수"
    )
    st.plotly_chart(fig2)  # ✅ 두 번째 차트 출력


    ############################################################################################################
    #추천하기

    


   
   
   
   
   
   
   
   
   
  ############################################################################################################ 
    # 🍎 클러스터별 선호 관광 특수기 출력
    #클러스터별 선호 관광 특수기 그래프 출력
    #클러스터분석 결과 출력


