import pandas as pd
import streamlit as st

def run_about():
    st.title("🌏 AI 기반 국가별 입국자 예측 & 맞춤 여행 서비스")
    st.header("✈️ 이 앱은 무엇을 하나요?")
    st.write(
        "AI 모델을 활용하여 2025~2026년 **국가별 예상 입국자 수를 예측**하고, "
        "각국 여행객의 방문 성향에 맞춘 **맞춤형 여행 패키지 기획**을 지원하는 플랫폼입니다."
    )
    
    st.header("🚀 주요 기능")
    st.markdown("""
    - **국가별 예상 입국자 예측** (Prophet + XGBoost 모델)
    - **한국 방방곡곡 즐거운 축제와 함께하는 사계절별 인기 여행지 추천**
    - **축제 & 관광 정보 실시간 제공 (한국관광공사 API)**
    - **맞춤형 호텔 & 관광지 추천** (네이버, 카카오 API)
    - **AI 여행 플래너 (Google Gemma-2-9b-it LLM API)**
    """)
    
    st.header("🔍 사용된 기술")
    st.markdown("""
    - **개발언어**: Python
    - **예측 모델**: Prophet, XGBoost Regressor
    - **자연어 처리 모델**: Google Gemma-2-9b-it LLM API
    - **데이터 출처**: 법무부_외국인 국적 및 월별 입국자 현황 "[데이터 출처: 공공데이터포털](https://www.data.go.kr/data/3074937/fileData.do)"
    - **웹 프레임워크**: Streamlit  
    - **한국관광공사 API, 네이버 블로그 API, 카카오 맵 API 활용**
    """)

    st.header("AI 모델 채택과정")
    st.markdown("""
    - 1. **Linear Regression** 모델로 접근(r2_score = 0.88): r2스코어는 높았으나 선형 회귀모델의 계절성 반영의 한계
    """)
    st.markdown("""
    - 2. **Prophet** 모델 적용 : 계절성 반영이 가능한 모델, 중국제외 MAPE(평균 절대 백분율 오차)도 4~15%대로 준수한 예측 수준을 보여 채택
    """)
    df=pd.read_csv("data/evaluation_df.csv")
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("image/prophet_China.png", use_container_width=True)
    with col2:
        st.image("image/XGB_China.png", use_container_width=True)
    st.markdown("""
    - 3. **XGBoost** 모델 적용(r2_score=0.98) : 계절성 규칙이 깨진 중국에 대해서만 트리 기반 회귀 XGBoost 모델 적용, 
                최대한의 계절성 반영을 위해 '월_sin', '월_cos’로 처리하여 1월과 12월간의 연속성을 반영할 수 있게 처리
    - 4. **Google Gemma-2-9b-it LLM API** 적용 : Hugging Face Inference API를 활용한 맞춤형 여행 일정 추천
    """)

    
    
    st.markdown("✨ AI 기반 맞춤 여행 예측 서비스와 함께 새로운 여행 트렌드를 만나보세요! ✨")