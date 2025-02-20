# 📌 AI 기반 국가별 입국자 예측 및 맞춤 여행 서비스  
[StreamlitAPP](https://foreigner-entry-prediction-marurun66.streamlit.app/)

## 🌍 프로젝트 개요
**AI 모델을 활용한 국가별 입국자 예측 및 맞춤 여행 기획 서비스**입니다.  
2018년\~2024년(코로나 특수기 제외)간의 데이터를 토대로 2025\~2026년의 **국가별 예상 입국자 수를 예측**하고,
각국 여행객에게 **축제, 사계절 테마 여행 패키지**를 쉽고 편하게 기획할 수 있도록 돕는 플랫폼입니다.  

## 🚀 주요 기능

### 🗺️ **국가별 입국자 예측 (Country 메뉴)**
- **Prophet + XGBRegressor 모델**을 활용하여 **15개국의 2025~2026년 예상 입국자 수** 제공
- 특정 계절 방문도가 높은 나라를 **계절별 입국 증가율(%) 계산**을 통해 제시
- **입국 예정자 상위 1\~5위 국가 & 블루오션을 위한 6\~10위 국가 추천**

### 🎉 **축제 정보 (Festival 메뉴)**
- **한국관광공사 API**에서 실시간 축제 정보 반영
- **네이버 블로그 연관 상위 블로그 데이터**를 통해 최신 축제 정보 제공
- **희망하는 축제 테마 기반으로 여행 패키지 기획 가능**

### 🍁 **사계절 여행 정보 (Seasons 메뉴)**
- **한국관광공사 API**를 활용하여 **사계절별 대표 여행지 정보 실시간 제공**
- 네이버 블로그 검색을 통해 추가 여행 정보를 제공
- 희망하는 사계절 테마로 **맞춤형 여행 패키지 기획 지원**

### 🏨 **관광지 및 호텔 정보 (Tourist Spot 메뉴)**
- 선택한 **축제 정보, 사계절 테마**를 반영한 **맞춤형 호텔·관광지 추천**
- **호텔 & 관광지 지도 시각화** (카카오 맵 API 활용)
- 네이버 블로그 데이터 연동으로 관광지 & 호텔 정보 검색 가능

### 🤖 **AI 여행 플래너 (AI Planner 메뉴)**
- **google/gemma-2-9b-it LLM 기반 API** 활용
- 선택한 **국가, 날짜, 축제, 사계절 테마, 관광지, 호텔 정보**를 기반으로 AI가 맞춤형 여행 계획서 생성
- 각국 고객을 위한 **사전 준비 요소 분석 & 마케팅 전략 가이드 제공**

---

## 📊 **데이터 수집 & 모델 개발 과정**

### 📌 **데이터 선정 기준**
- **2022~2024년 데이터를 기반으로 분석 진행**
    - 2021년까지는 **코로나 영향으로 입국제한**이 있어 제외
    - 2022년 7월 이후부터 입국 제한이 완화되었으나 **일부 국가의 입국 제한이 지속** → **2023년~2024년 데이터로 예측**
- **코로나 이전 패턴을 반영하기 위해 2018~2019년 데이터 추가 활용**
- 최종적으로 **2018, 2019, 2023, 2024년 데이터 활용**
- 유의미한 관광 수요 분석을 위해 모든 나라 대상이 아닌 **입국자 상위 15개국**으로 타겟 설정

### 📌 **데이터 분석 예측 모델 선정 과정**

#### **🔹 Linear Regression (선형 회귀 분석)**
- 원핫인코딩으로 국가별 데이터를 변환 후 예측 시도
- **r2_score = 0.88**로 높은 성능을 보였지만, **계절성 반영 실패로 음수 값이 발생**하는 문제가 있어 사용 어려움

#### **🔹 XGBoost 모델**
- 초기 모델: **r2_score = 0.98**로 높은 성능이었으나, **예측값이 예년 평균 입국자 수보다 낮게 나오는 문제** 발생
- 해결: **'월_sin', '월_cos' 변환**을 통해 **1월과 12월간의 간극**을 줄여 계절성 반영 
    모델 파라미터(n_estimators,learning_rate,max_depth,reg_lambda) 조절로 성능 또한 **r2_score = 0.987**로 개선

#### **🔹 Prophet 모델**
- 계절성을 반영한 예측이 가능했으며, **MAPE(%) 기준 4-15%로 전반적으로 우수한 성능**을 보임
- 단, **중국의 경우 52%의 높은 오차 발생** → **중국은 XGBoost 모델로 보완**

#### **🔹 Hierarchical clustering 분류 모델**
- 국가별 계절 선호도를 확인하고자 입국인원 스케일링, '월_sin', '월_cos'변환으로 월 간격을 줄여 진행했으나, 크게 유의미한 분석결과가 나오지 않았음
- 계절 선호도는 전체 기간 입국자 수 대비 각 계절의 입국자 수 비율(%)로 산출

### 📌 **최종 모델 선정**
✅ **Prophet 모델**: 전체적으로 계절별 트렌드를 반영하여 예측 가능  
✅ **XGBoost 모델**: **중국처럼 코로나 회복 영향이 큰 국가**의 경우 별도로 적용  

---

## 📡 **사용한 API 및 외부 데이터**
- **법무부_외국인 국적 및 월별 입국자 현황** "[데이터 출처: 공공데이터포털](https://www.data.go.kr/data/3074937/fileData.do)"
- **한국관광공사 API** ([데이터 출처](https://www.data.go.kr/data/15101578/openapi.do#/API))
- **네이버 블로그 검색 API** ([블로그 검색](https://openapi.naver.com/v1/search/blog.json))
- **카카오 맵 API** ([지도 서비스](https://developers.kakao.com/console/app/1196178/config/platform))
- **gemma-2-9b-it LLM** ([허깅페이스](https://huggingface.co/google/gemma-2-9b-it)))
---
## **프롬프트 설정**
    prompt = """
    나는 한국 여행사의 직원입니다. 
    {year}년 {month}월 {selected_country} 손님을 위한 한국{selected_location} 여행 코스를 준비해야 합니다. 
    {language} 언어를 사용하는 {selected_country} 손님을 위해 사전에 준비하면 좋을 것이 무엇인지 알려주세요.
    이동은 우리 여행사 제공 버스로 이동합니다.
    이번 여행은 {selected_travel}를 중심으로 진행되며, 주요 방문지는 다음과 같습니다.

    ### 1. 숙박지 (호텔/펜션/리조트)
    다음 장소에서 숙박이 이루어집니다.
    - {", ".join([f"{hotel} ({category})" for hotel, category in selected_hotels.items()])}

    ### 2. 관광지
    다음 관광지를 방문할 예정입니다. 각 장소의 매력과 해당 국가 고객에게 어필할 만한 포인트를 설명해주세요.

    - {", ".join([f"{spot} ({category})" for spot, category in user_selection["selected_tourist_spots"].items()])}


    고객이 한국에 입국해서 {selected_location}의 관광지를 둘러보고, 귀국하는 전체 여행 일정을 작성해주세요.
    또한, {travel_preference} 성향의 {selected_country} 고객에게 이 여행에서 어떤 부분이 어필될지도 작성해주세요.

    한글로 작성해주세요.
    """
    messages = [{"role": "user", "content": prompt},{"role":"system","content":"당신은 여행 전문가입니다. 한글로, 꼼꼼하게 작성해주세요."}]
---
## 🚀 **Streamlit 배포**
1. **로컬 컴퓨터 작업:**  
- 코드 개발 및 테스트
- **session_state**를 활용하여 유저가 입력한 정보를 유지하고, **navigate_to** 함수를 활용하여 페이지 이동 구현
- 카카오맵 API에 접근 가능하도록 로컬 주소를 허용된 도메인으로 등록
2. **스트림릿 배포:**  
- **requirements.txt**으로 필요한 라이브러리 목록 관리
- GitHub에 최종 푸쉬 후 스트림릿에 연동
- 카카오맵 API에 접근 가능하도록 앱 주소를 허용된 도메인으로 변경
- <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"> 로 Mixed Content 문제 해결

---

## 📞 **문의**
- Email: marurun66@gmail.com
---

🎉 **AI 기반 국가별 입국자 예측 & 맞춤 여행 서비스로 더 나은 여행 기획을 경험하세요!** 🚀
