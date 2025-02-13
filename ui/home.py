import streamlit as st

def run_home():
    st.title("Home")
    st.text("""50개국 22-24년 입국자 수를 토대로 관광 특수기를 예측하는 프로젝트입니다.  
            Prophet을 통한 시계열 예측 모델로 25,26년 입국자 수를 예측합니다. 
            예측 입국자수를 Hierarchy clustering을 통해 군집화하고, 군집별 선호 관광 특수기를 분석합니다.
            """)