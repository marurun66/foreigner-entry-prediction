import pandas as pd
import streamlit as st


def run_about():
    st.title("👩🏻‍💻 개발 프로세스")
    col1, col2 = st.columns([1, 1])
    st.header("📌 개발 툴")
    st.markdown(
        """
    ✔ 데이터 전처리 & 모델링: Jupyter Notebook  
    ✔ 개발 & 코드 통합: Visual Studio Code (코드 작성, 디버깅, API 연동)   
    ✔ 웹 애플리케이션 프레임워크: Streamlit  
    """
    )
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.header("🔍 사용된 기술")
    st.markdown(
        """
    - **개발언어**: Python
    - **예측 모델**: Prophet, XGBoost Regressor
    - **자연어 처리 모델**: Google Gemma-2-9b-it LLM API : Hugging Face Inference API를 활용한 맞춤형 여행 일정 추천
    - **데이터 출처**: 법무부_외국인 국적 및 월별 입국자 현황 18,19,20-24년 데이터 "[데이터 출처: 공공데이터포털](https://www.data.go.kr/data/3074937/fileData.do)"
    - **웹 프레임워크**: Streamlit  
    - **활용 API**:  
        - [한국관광공사 API](https://www.data.go.kr/data/15101578/openapi.do#/API)
        - [네이버 블로그 API](https://openapi.naver.com/v1/search/blog.json)  
        - [카카오 맵 API](https://developers.kakao.com/console/app/1196178/config/platform)
        - [gemma-2-9b-it LLM API](https://huggingface.co/gemma-2-9b-it)
    """
    )
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.header("데이터 전처리 과정과정👾")
    st.markdown(
        """
    #### 1. 22\~24년 데이터로 작업 시작:  
    **20년\~21년**까지는 **코로나 영향**으로 입국제한이 있어 입국자수가 크게 감소  
    코로나시즌을 데이터에 반영하기에는 포스트코로나 시대도 종료된지 오래인 이 시점에 부적절하다 판단  
                
    #### 2. **22년 6월** 까지도 코로나 영향으로 **입국자수가 회복되지 않음**:  
    한국 또한 2022년 6월 8일부터 모든 입국자에 대한 자가격리 의무가 해제, 출국자수가 서서히 회복되었기 때문에 **22년 6월까지의 데이터 또한 예측데이터에 사용할 수 없다 판단**  
    나라별로 차이가 있어 22년 하반기까지도 영향이 있는 나라가 많아 **22년 데이터를 제외**하기로 결정  
    23,24년간의 적은 데이터양으로는 계절성 반영이 어려울것으로 예상은 하였으나, **시험삼아 Prophet Regressor 모델을 적용**하여 예측 진행  
    => 문제점 : 23년 1,2월까지도 일부국가들은 입국인원이 적다가, 후반기에 코로나 이전 수준으로 회복된것을 모델은 입국자수가 폭발적으로 증가한거로 예측하여 **예측오차**가 커짐  
    - 해결을 위한 노력:
        - growth="logistic" : 일정 수치 이상으로 증가하지 못하도록 제한 (입국인원은 한정적이다.)
        - 상한값 = 최대 입국자 수의 **110%** 로 제한
        - 하한값 = 24년 최소 입국자 수에 1.5를 곱하여 조절
        - 과대 성장 방지를 위한 변곡점 민감도 조절 → changepoint_prior_scale=0.05
        - ⇒ 하지만 위 모델로도 23년 초 **30141명** 가량이였다가, 회복 후 **430303명** 로 폭발적으로 증가하는 중국 등의 국가를 예측하는데에 한계가 있었다.
                
    #### 3. **18,19년** 데이터 추가:  
    연속성이 깨질것이 염려되었으나, 23년, 24년 2년간의 데이터로는 계절특성을 반영하기 어렵다 판단되어  
    18,19년 데이터를 추가하여 4년간의 데이터로 모델링 진행  
    18년, 19년 데이터는 월별 컬럼이 따로 들어가는 양식이라 **피벗테이블**로 변환하여 23,24년 데이터와 양식을 맞춤               
    """
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("image/sc1.png", use_container_width=True)
        st.write("18,19년 Dataframe")
    with col2:
        st.image("image/sc2.png", width=235)
        st.write("23,24년 Dataframe")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            """
    #### 4. 국적 지역명 통일 및 개수 선정:  
    총 219개 국적지역 Value값 중  
    한국계 중국인, 터키, 체코공화국, 타이완 등 국적이 예전 이름이나 표기가 다른 경우가 있어 통일작업  
    201개국으로 정리
    모든 나라 데이터를 쓰는것보단  
    해당앱의 예상 사용자인 여행사 입장에서 **유효한 관광수요**로 보여지는 **입국자 총계 상위 15개국**으로 선정
    """
        )
        st.image(
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi6wU-_akiUF8dX0CIkUmAxyYdkN3HWxUFtYy6qbNeaxilKVqaJG6j6IUolj-zObVd_jk4he57Lm1RcMdPQ-8oaF8wRje8QvYLCJDJkxxGMP_qbIqoNY8MYzG60ng7r_LtnJmqEa1J9uYS1/s800/character_earth_chikyu.png",
            width=300,
        )
    with col2:
        st.image("image/sc3.png", width=400)

    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.header("Regressor 모델 채택과정👾")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            """
        ### 1. **Linear Regression** 모델로 접근(r2_score = 0.88):  
        r2스코어는 높았으나 **선형 회귀모델로는 계절성 반영의 한계**가 있었음
        """
        )
    with col2:
        st.image("image/linear.png", width=500)
    st.markdown("---")
    st.markdown(
        """
    ### 2. **Prophet** 모델 적용 :  
    계절성 반영이 가능한 모델, **중국제외 MAPE(평균 절대 백분율 오차)도 4~15%** 대로 준수한 예측 수준을 보여 채택
    """
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        df = pd.read_csv("data/evaluation_df.csv")
        st.dataframe(df, width=600)
    with col2:
        st.image("image/prophet.png", use_container_width=True)


    st.markdown("---")
    st.markdown(
        """
    ### 3. **XGBoost** 모델 적용(r2_score=0.98) :  
    계절성 규칙이 깨진 **중국에 대해서만 트리 기반 회귀 XGBoost 모델** 적용,  
    최대한의 계절성 반영을 위해 **'월_sin', '월_cos’** 로 처리하여 **1월과 12월간의 연속성을 반영** 할 수 있게 처리

    """
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("image/xgb1.png", use_container_width=True)
    with col2:
        st.image("image/xgb2.png", use_container_width=True)
    st.markdown("---")
    st.subheader("📌 최종 모델 선정-스위칭 기반 하이브리드 모델")
    st.markdown("""
✅ Prophet 모델: 전체적으로 계절별 트렌드를 반영하여 예측 가능한 모델, 대부분의 국가에 적용   
✅ XGBoost 모델: 코로나 회복 영향이 큰 국가의 경우 별도로 적용, 중국의 경우에만 적용
                """)
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.subheader("LLM 선정 기준👾")
    st.markdown(
        """
    **채택한 LLM** : google/gemma-2-9b-it  
    **API 형태** 로 제공: 별도의 학습 과정 없이 즉시 활용 가능  
    **사용자의 입력 정보** 를 종합적으로 분석하여 여행사 수준의 맞춤형 여행 계획을 자동 생성하는 데 최적화된것으로 판단하여 선정      
    **LLM이 처리하도록 세팅한 프롬프트** :             
    """
    )
    prompt = """
    나는 한국 여행사의 직원입니다. 
    {year}년 {month}월 {selected_country} 손님을 위한 한국 여행 코스를 준비해야 합니다. 
    {language}언어를 사용하는 {selected_country} 손님을 위해 사전에 준비하면 좋을 게 무엇인지 알려주세요.
    {selected_travel}를 중심으로 {selected_location}을 방문하며, 
    다음 관광지를 여행 코스에 포함하려고 합니다(다음 관광지중에 "호텔", "숙소", "펜션", "리조트"에서는 숙박합니다.숙박지에 대해서도 작성해주세요.)
    {", ".join(selected_places)}.
    
    고객이 한국에 입국해서 관광지들을 둘러보고, 귀국할 수 있는 여행 일정을 작성해주세요.
    또한, {travel_preference} 성향의 {selected_country} 고객에게 이 여행에서 어떤 부분이 어필될지도 작성해주세요.
    
    한글로 작성해주세요.
    """
    st.code(prompt, language="python")
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.subheader("StreamlitApp 배포 과정👾")
    st.markdown(
        """
    1. 로컬 컴퓨터 작업:  
    코드 개발 및 테스트
    **session_state**를 활용하여 유저가 입력한 정보를 유지하고, **navigate_to** 함수를 활용하여 페이지 이동 구현
    카카오맵 API에 접근 가능하도록 로컬 주소를 허용된 도메인으로 등록
    빠른 API처리를 위해 @st.cache_data(ttl=3600) 캐싱 처리
    2. 스트림릿 배포:  
    **requirements.txt**으로 필요한 라이브러리 목록 관리
    GitHub에 최종 푸쉬 후 스트림릿에 연동
    카카오맵 API에 접근 가능하도록 앱 주소를 허용된 도메인으로 변경
    3. 로컬 작업 결과와 달리 스트림릿 앱에서는 카카오맵API Mixed Content 에러가 발생
    """
    )
    st.error(
        "🚨**Mixed Content란?** 보안상의 이유로 HTTPS 환경에서 HTTP 리소스를 불러오는 것을 막는 것."
    )
    st.markdown(
        """
    카카오 API가 내가 코드에서 **https**를 사용했어도, API 내부에서 **http**를 호출하여 발생하는 문제로 보여짐
    **해결시도**:  
    - 챗지비티의 조언에 따라 카카오맵 API를 기존 코드 v3.js대신 v2.js로 변경 -> 실패 
    - 카카오 지도 HTML을 별도 파일로 만들고, Streamlit에서 iframe으로 카카오 지도 삽입시도 -> 실패
    - 코드 중 유일하게 http를 사용하는 공공데이터포털 API를 https로 변경 -> 공공데이터API는 http만 지원하여 실패
    - **최종 해결**:  
        <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">  
        카카오 API 내부 http 호출 방식을 https로 강제 변경하여 해결 [🔗출처](https://web.dev/articles/fixing-mixed-content?hl=ko)
    """
    )
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    수많은 시행착오와 데이터 정제과정, 그리고 모델 선택 고민 끝에 최적의 예측모델과 LLM을 적용한 여행 추천 앱을 만들었습니다.  
    처음에는 단순히 입국자 예측에서 시작했지만,  
    코로나 기간을 고려한 데이터의 계절성 반영, 모델 스위칭 기반 하이브리드 모델 선정,  
    LLM API를 통해 편리한 여행계획서 작성, API 연동 문제 해결까지 다양한 난관을 하나씩 해결해 나가며 완성도를 높일 수 있었습니다.  
    개발 과정에서 얻은 경험과 해결 방법들을 바탕으로 앞으로 더 발전된 기능을 추가할 수 있도록 노력하겠습니다.😄  
    """
    )
