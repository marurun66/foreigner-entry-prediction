import streamlit as st
import pandas as pd
import plotly.express as px

from navigation import navigate_to


def get_top_country(df, year, month):
    """사용자가 선택한 연도와 월을 기준으로 입국자 수 증가량이 가장 큰 1개 국가를 반환하는 함수"""
    df1 = pd.read_csv("data/df_total.csv")
    # 1월이면 작년 12월과 비교
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    # 현재 월과 이전 월 데이터 분리
    df_latest = df1[(df1["년"] == year) & (df1["월"] == month)]
    df_previous = df1[(df1["년"] == prev_year) & (df1["월"] == prev_month)]

    if df_latest.empty or df_previous.empty:
        st.warning("선택한 연도와 월에 대한 충분한 데이터가 없습니다.")
        return None

    # 입국자 수 차이 계산
    df_merge = df_latest.merge(
        df_previous, on="국적지역", suffixes=("_latest", "_previous")
    )
    df_merge["입국자수_증가"] = (
        df_merge["입국자수_latest"] - df_merge["입국자수_previous"]
    )

    # 증가량이 가장 큰 상위 3개 국가 선택
    return df_merge.nlargest(1, "입국자수_증가")


def run_country():
    st.title("🌍 25,26년 국가별 예상입국인원과 국가 선택 가이드")
    st.html(
        """
        <div style="
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 5px solid #28a745;
            color: #333;
            font-size: 16px;
            line-height: 1.6;">
            <p>📊 <b>외교부 제공 데이터 + AI 예측 모델 (Prophet, XGBRegressor)</b> 이<br>
            2018년~2024년까지의 각국 입국 데이터를 분석하여,<br>
            <span style="color: #28a745;"><b>향후 2년간의 예상 입국 인원</b></span>을 제공합니다.</p>

            <ul>
                <li>✅ <b style="color: #28a745;">성공 가능성이 높은 상위 5개 국가</b></li>
                <li>🚀 <b style="color: #28a745;">새롭게 떠오르는 주목할 5개 국가</b></li>
                <li>선택한 달을 기준으로 <b>3개월 전후의 입국자 수 추이</b></li>
            </ul>

            <p>입국자들의 <span style="color: #28a745;"><b>사계절별 한국 방문 선호도</b></span>를 파악하고,</p>
            
            <p><b>각국 여행객들이 원하는 특별한 경험을 준비해보세요!</b></p>
            
            <p>한국의 <span style="color: #28a745;"><b>다채로운 축제</b></span>와 
            <span style="color: #28a745;"><b>사계절 맞춤형 여행 패키지</b></span>를 기획하여,<br>
            더 많은 글로벌 여행객을 매료시킬 기회를 만들어보세요. ✨✈️</p>

        </div>
    """
    )

    # 데이터 로드
    df = pd.read_csv("data/df_total.csv")
    seasonal_growth_df = pd.read_csv("data/df_seasonal_growth.csv")

    # 🍎 유저에게 예측희망 년, 월 입력
    st.subheader("예측 희망 년, 월을 입력하세요.🌍")
    # Streamlit UI 설정
    col1, col2 = st.columns([1, 1])  # 1:1 비율로 배치
    # 한 줄에 연도 & 월 선택
    with col1:
        year = st.selectbox(
            "연도", [2025, 2026], key="year", placeholder="연도를 선택하세요"
        )  # 연도 선택
    with col2:
        month = st.selectbox(
            "월", list(range(1, 13)), key="month", placeholder="월을 선택하세요"
        )  # 월 선택

    ######
    # 🍎 지도로 해당 년월의 각국 예상 입국인원을 봅니다.
    # 유저가 선택한 year, month에 해당하는 데이터 필터링
    select_df = df[(df["년"] == year) & (df["월"] == month)]

    # 국가명을 ISO 코드로 변환
    country_to_iso = {
        "중국": "CHN",
        "일본": "JPN",
        "미국": "USA",
        "프랑스": "FRA",
        "독일": "DEU",
        "영국": "GBR",
        "캐나다": "CAN",
        "호주": "AUS",
        "태국": "THA",
        "베트남": "VNM",
        "필리핀": "PHL",
        "인도네시아": "IDN",
        "말레이시아": "MYS",
        "싱가포르": "SGP",
        "러시아": "RUS",
        "인도": "IND",
        "브라질": "BRA",
        "멕시코": "MEX",
        "이탈리아": "ITA",
        "스페인": "ESP",
        "대만": "TWN",
        "오스트레일리아": "AUS",
        "홍콩": "HKG",
    }
    select_df = select_df.copy()
    select_df["iso_alpha"] = select_df["국적지역"].map(country_to_iso)

    # select_df 컬럼명 변경 국적지역 -> 국가, 입국자수 -> 예상 입국자수
    select_df.rename(
        columns={"국적지역": "국가", "입국자수": "예상 입국자수"}, inplace=True
    )

    # Choropleth 지도 생성
    # 년,월,국적지역,입국자수
    fig = px.choropleth(
        select_df,  # 데이터프레임
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
        oceancolor="white",  # 바다 색상 유지
    )
    fig.update_geos(projection_type="natural earth")  # 지도를 자연스럽게 표현

    # Streamlit에 지도 출력
    st.plotly_chart(fig)

    col1, col2 = st.columns(2)
    with col1:
        # 🍎 해당 년월의 각 국가별 예상 입국자 수를 표로 출력합니다
        st.write(f"📊 {year}년 {month}월 각 국가별 예상 입국자 수")
        st.dataframe(
            select_df[["국가", "예상 입국자수"]]
            .sort_values("예상 입국자수", ascending=False)
            .reset_index(drop=True)  # 기존 인덱스 삭제
            .rename_axis("순위")  # 인덱스 이름 설정
            .reset_index()
            .assign(순위=lambda df: df.index + 1),  # 순위 1부터 시작
            hide_index=True,  # Streamlit에서 인덱스 숨기기
            use_container_width=True,
        )
    with col2:
        st.write("방문자 수가 3k 이상 예상되는 국가")
        st.dataframe(
            select_df[select_df["예상 입국자수"] >= 30000][["국가", "예상 입국자수"]]
            .sort_values("예상 입국자수", ascending=False)
            .reset_index(drop=True)  # 기존 인덱스 삭제
            .rename_axis("순위")  # 인덱스 이름 설정
            .reset_index()
            .assign(순위=lambda df: df.index + 1),  # 순위 1부터 시작
            hide_index=True,  # Streamlit에서 인덱스 숨기기 (최신 버전)
            use_container_width=True,
        )
        # 계절 판별
        high_visitor_countries = select_df[select_df["예상 입국자수"] >= 30000][
            ["국가", "예상 입국자수"]
        ]

        if month in [3, 4, 5]:
            season_col = "봄철 증가율"
            season_name = "봄"
        elif month in [6, 7, 8]:
            season_col = "여름철 증가율"
            season_name = "여름"
        elif month in [9, 10, 11]:
            season_col = "가을철 증가율"
            season_name = "가을"
        else:
            season_col = "겨울철 증가율"
            season_name = "겨울"
        # 방문자 30K 이상 국가 중 계절 증가율이 가장 높은 나라 찾기
        if not high_visitor_countries.empty:
            # 계절별 증가율 데이터를 합침
            merged_df = high_visitor_countries.merge(
                seasonal_growth_df, left_on="국가", right_on="국적지역", how="left"
            )

            # 해당 계절 증가율이 가장 높은 나라 찾기
            top_season_country = merged_df.nlargest(5, season_col)

            if not top_season_country.empty:
                country_name = top_season_country["국가"].values[0]
                growth_rate = top_season_country[season_col].values[0]

                # ✅ 계절별 추천 안내 문구 추가
                st.html(
                    f"""
                        <div style="
                            background-color: #d4edda; 
                            padding: 15px; 
                            border-radius: 10px; 
                            border-left: 5px solid #155724;
                            color: #155724;
                            font-size: 16px;
                            padding-bottom: 10px;">
                            💡 <b>Tip:</b><br>

                            <span style="display: block; border-top: 1px solid #28a745; margin: 10px 0;"></span>  <!-- 초록색 얇은 줄 -->

                            <b>{country_name}</b> (사계절 대비 {season_name}철 입국 증가율 {growth_rate:.2f}%)은<br>
                            한국 사계절 중 {season_name}을 사랑하는 나라예요! 🌸🌞🍂❄️
                        </div>
                    """
                )
    ############################################################################################################
    # 🍎 ±3개월 입국자 수 추이
    # 날짜 컬럼 생성
    df["일"] = 1
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
        .groupby("국적지역")["yhat"]
        .sum()  # 입국자 수 합산
        .nlargest(5)  # 상위 5개국
        .index.tolist()
    )
    # 다음 5개국 (6~10위) 가져오기
    top_countries_next = (
        filtered_df[filtered_df["ds"] == selected_date]
        .groupby("국적지역")["yhat"]
        .sum()
        .nlargest(10)  # 상위 10개국 중에서
        .index.tolist()[5:]  # 6~10위
    )

    # 다음 5개국 (11~15위) 가져오기
    bottom_countries = (
        filtered_df[filtered_df["ds"] == selected_date]
        .groupby("국적지역")["yhat"]
        .sum()
        .nsmallest(5)  # ✅ 가장 작은 값 5개 가져오기
        .index.tolist()
    )

    # ✅ 상위 5개국 데이터프레임 생성
    top_5_df = filtered_df[filtered_df["국적지역"].isin(top_countries)]

    # ✅ 그 외 국가 중 입국자 수 상위 10개국 선정
    other_countries_df = filtered_df[~filtered_df["국적지역"].isin(top_countries)]
    top_10_others = (
        other_countries_df[
            other_countries_df["ds"] == selected_date
        ]  # 선택한 연/월 기준 필터링
        .groupby("국적지역")["yhat"]
        .sum()  # 입국자 수 합산
        .nlargest(10)  # 상위 10개국
        .index.tolist()
    )

    # ✅ 그 외 국가 10개국 데이터프레임 생성
    top_10_others_df = filtered_df[filtered_df["국적지역"].isin(top_10_others)]

    # ✅ Streamlit UI 출력
    st.subheader(f"📊 {year}년 {month}월 기준 상위 5개국 ±3개월 입국자 수 추이")
    # ✅ 상위 5개국 차트
    fig1 = px.line(top_5_df, x="ds", y="yhat", color="국적지역", markers=True)
    fig1.update_layout(
        xaxis=dict(range=[start_date, end_date]),
        xaxis_title="",
        yaxis_title="예측 입국자 수",
    )
    st.plotly_chart(fig1)  # ✅ 첫 번째 차트 출력

    st.subheader(f"📊 {year}년 {month}월 기준 그 외 10개국 ±3개월 입국자 수")
    # ✅ 그 외 국가 차트
    fig2 = px.line(top_10_others_df, x="ds", y="yhat", color="국적지역", markers=True)
    fig2.update_layout(
        xaxis=dict(range=[start_date, end_date]),
        xaxis_title="",
        yaxis_title="예측 입국자 수",
    )
    st.plotly_chart(fig2)  # ✅ 두 번째 차트 출력

    # 분석 실행
    top_country = get_top_country(df, year, month)

    if top_country is not None and not top_country.empty:
        row = top_country.iloc[0]
        country_name = row["국적지역"]
        growth_rate = (
            (row["입국자수_증가"] / row["입국자수_previous"]) * 100
            if row["입국자수_previous"] > 0
            else 0
        )

        st.html(
            f"""
            <div style="
                background-color: #d4edda; 
                padding: 15px; 
                border-radius: 10px; 
                border-left: 5px solid #155724;
                color: #155724;
                font-size: 16px;
                padding-bottom: 10px;">
                💡 <b>월별 입국 증가 데이터</b><br>

                <span style="display: block; border-top: 1px solid #28a745; margin: 10px 0;"></span>  <!-- 초록색 얇은 줄 -->

                <b>{country_name}</b> (전월 대비 입국 증가율 {growth_rate:.2f}%)<br>
                {month}월 기준으로 입국자 수가 가장 많이 증가한 국가입니다! 📈✈️
            </div>
        """
        )

    #####################################################

    # 여행성향 예시파일 로드
    country_info_df = pd.read_csv(
        "data/example_travel_preference.csv", index_col="국가"
    )
    # 🍎  상위 5개국, 레드오션 추천

    col1, col2, col3 = st.columns(3)
    # ✅ 2개의 컬럼 생성 (좌측: 1~5위 / 중간: 6~10위 / 우측: 11~15위)

    # ✅ session_state 초기화 (없으면 기본값 설정)
    if "selected_country" not in st.session_state:
        st.session_state["selected_country"] = None
    if "selected_country_1" not in st.session_state:
        st.session_state["selected_country_1"] = None
    if "selected_country_2" not in st.session_state:
        st.session_state["selected_country_2"] = None
    if "selected_country_3" not in st.session_state:
        st.session_state["selected_country_3"] = (
            None  # ✅ 숨은 보석(11~15위) 선택지 추가
        )

    # ✅ 선택된 국가 업데이트 함수 (선택하면 나머지 2개 선택 해제)
    def update_selected_country(selected_key):
        selected_value = st.session_state[selected_key]
        if selected_value:  # 선택된 값이 있으면
            st.session_state["selected_country"] = selected_value
            # ✅ 다른 선택지 해제
            for key in [
                "selected_country_1",
                "selected_country_2",
                "selected_country_3",
            ]:
                if key != selected_key:
                    st.session_state[key] = None

    # ✅ 라디오 버튼 (값 변경 시 자동 반영)
    with col1:
        st.radio(
            "🔹 따논당상 입국자 1~5위 국가 중 선택",
            top_countries,
            index=None,  # 기본 선택 없음
            key="selected_country_1",
            on_change=update_selected_country,
            args=("selected_country_1",),  # ✅ 한 개의 인자만 전달하도록 수정
        )

    with col2:
        st.radio(
            "🔹 블루오션 입국자 6~10위 국가 중 선택",
            top_countries_next,
            index=None,  # 기본 선택 없음
            key="selected_country_2",
            on_change=update_selected_country,
            args=("selected_country_2",),  # ✅ 한 개의 인자만 전달하도록 수정
        )

    with col3:
        st.radio(
            "🔹 숨은 보석 입국자 11~15위 국가 중 선택",
            bottom_countries,
            index=None,  # 기본 선택 없음
            key="selected_country_3",
            on_change=update_selected_country,
            args=("selected_country_3",),  # ✅ 한 개의 인자만 전달하도록 수정
        )

    selected_country = st.session_state["selected_country"]

    # ✅ 선택한 국가의 정보 출력
    st.subheader(f"🔎 {selected_country if selected_country else ''} 여행 정보")
    if selected_country and selected_country in country_info_df.index:
        info = country_info_df.loc[selected_country]
        st.write(f"**🗣️ 사용 언어:** {info['언어']}")
        st.write(
            f"""**🎒 여행 성향:** {info['여행 성향']}  
                 * 여행 성향 분석은 예시 입니다."""
        )

        # ✅ 예상 입국 인원 가져오기
        filtered_values = filtered_df[filtered_df["국적지역"] == selected_country][
            "yhat"
        ]
        if not filtered_values.empty:  # 값이 존재하는 경우
            expected_visitors = int(filtered_values.sum())  # 총합을 정수로 변환
            st.write(f"**🙂 예상 입국인원:** {expected_visitors:,} 명")
            st.write(
                f"{year}년 {month}월, {selected_country} 관광객을 위한 여행패키지 구상을 시작합니다.✈️🎉"
            )  # 천 단위 콤마 표시
            st.session_state["selected_year"] = year
            st.session_state["selected_month"] = month
            st.session_state["selected_country"] = selected_country
            st.session_state["info"] = info
            st.session_state["expected_visitors"] = expected_visitors
            if st.button("➡ 축제 정보 보기"):
                navigate_to("Festival")
                # ✅ `Festival`으로 이동

        else:
            st.write("🚫 예상 입국자 수 데이터가 없습니다.")
    else:
        st.write("⚠️ 국가를 선택해 주세요.")

    ############################################################################################################


############################################################################################################
# 🍎 클러스터별 선호 관광 특수기 출력
# 클러스터별 선호 관광 특수기 그래프 출력
# 클러스터분석 결과 출력
