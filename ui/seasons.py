import time
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import streamlit as st

from navigation import navigate_to

# ✅ 네이버 API 키 설정 (네이버 개발자 센터에서 발급)
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
NAVER_SEARCH_API_URL = "https://openapi.naver.com/v1/search/blog.json"  # 블로그 검색 API 사용

# ✅ 공공데이터 API 키 설정
data_go_API_KEY = st.secrets["data_go_API_KEY"]
KEYWORD_BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchKeyword1"

def clean_html_with_bs(text):
    """HTML 태그 제거"""
    return BeautifulSoup(text, "html.parser").get_text()

def get_season(month):
    """입력된 월(month)에 따라 계절을 반환"""
    if month in [12, 1, 2]:
        return "겨울"
    elif month in [3, 4, 5]:
        return "봄"
    elif month in [6, 7, 8]:
        return "여름"
    elif month in [9, 10, 11]:
        return "가을"
    return ""

def get_travel_description(travel_name):
    """네이버 검색 API - 여행지 설명, 블로그 주소 가져오기"""
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": travel_name,
        "display": 1,
        "sort": "sim"
    }
    response = requests.get(NAVER_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            raw_text = data["items"][0]["description"]
            clean_text = clean_html_with_bs(raw_text)
            blog_link = data["items"][0]["link"]
            return clean_text, blog_link 
    return "설명 없음", None

def run_seasons():
    """키워드 검색을 통한 여행 정보 조회"""
    st.title("🌸⛱️ 계절별 여행 정보 조회🍁⛷️")
    st.write("""
    🌸🌞🍂❄️ **사계절 여행 정보, 한눈에 확인하세요!**  
    한국관광공사가 제공하는 여행 정보를 통해 **계절별 추천 여행지**를 살펴보세요.  
    마음에 드는 여행지를 선택하면, **맞춤형 여행 코스**를 함께 준비할 수 있어요! ✨🚀  
    """)


    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정

    # ✅ 값이 있을 경우 정상 출력
    if year and month and selected_country:
        st.session_state["year"] = year
        st.session_state["month"] = month
        language = info.get("언어", "알 수 없음")
        travel_preference = info.get("여행 성향", "알 수 없음")

        st.write(f"""📅 선택한 날짜: {year}년 {month}월  
                🌍 선택한 국가: {selected_country}  
                🗣 언어: {language}  
                🏝 여행 성향: {travel_preference}  
                👥 입국 예상 인원: {expected_visitors:,} 명""")
    else:        
        # ✅ 연도 및 월 선택
        col1, col2 = st.columns([1, 1])

        with col1:
            # ✅ 이전 페이지에서 선택한 값이 있으면 유지, 없으면 `None`
            default_year = st.session_state.get("year")
            year_options = [2025, 2026]

            # ✅ 이전 값이 있으면 해당 값으로 선택, 없으면 `index=None` (초기 상태)
            year_index = year_options.index(default_year) if default_year in year_options else None
            year = st.selectbox("연도", year_options, key="year", index=year_index, placeholder="연도를 선택하세요")

        with col2:
            # ✅ 이전 페이지에서 선택한 값이 있으면 유지, 없으면 `None`
            default_month = st.session_state.get("month")
            month_list = list(range(1, 13))

            # ✅ 이전 값이 있으면 해당 값으로 선택, 없으면 `index=None` (초기 상태)
            month_index = month_list.index(default_month) if default_month in month_list else None
            month = st.selectbox("월", month_list, key="month", index=month_index, placeholder="월을 선택하세요")
            # ✅ year, month가 유지된 경우 자동 검색 실행

        # ✅ 입력값이 없는 경우 경고 메시지 출력
        if year is None or month is None:
            st.warning("""
            📅 **여행 날짜와 🌎 대상 국가를 아직 선택하지 않으셨네요!**  
            **[Country]** 메뉴에서 15개국의 예상 입국 인원을 비교하고, **어느 국가**의 여행객을 위한 패키지를 구상할지 선택 해보세요. 😉  
            만약 **계절별 여행 정보를 먼저 확인하고 싶다면, 여행 날짜를 선택**해 주세요! 🎉  
            """)
            
            return

##################

    
    season = get_season(month)  # ✅ 계절 결정
    st.write(f"""📅 선택한 날짜: {year}년 {month}월 (계절: {season})  
             정보는 **정확한 날짜를 한번 더 확인**하세요.""")

    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "xml",
        "keyword": season
    }
    response = requests.get(KEYWORD_BASE_URL, params=params)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        
        if not items:
            st.warning("❌ 검색 결과가 없습니다.")
            return
        
        travel_list = []
        for item in items:
            title = item.find("title").text if item.find("title") is not None else "정보 없음"
            addr = item.find("addr1").text if item.find("addr1") is not None else "정보 없음"
            image_url = item.find("firstimage").text if item.find("firstimage") is not None else None
            description, blog_link = get_travel_description(title)
            travel_list.append({
                "여행지명": title,
                "위치": addr,
                "설명": description,
                "블로그 링크": blog_link,
                "이미지": image_url
            })

        st.success(f"""총 {len(travel_list)}개의 여행 정보를 조회했습니다.""")
        
        for idx, travel in enumerate(travel_list):
            with st.expander(f"📌 {travel['여행지명']} (자세히 보기)"):
                st.write(f"📍 위치: {travel['위치']}")
                st.write(f"📝 설명: {travel['설명']}")
                if travel["블로그 링크"]:
                    st.markdown(f"[🔗 관련 블로그 보기]({travel['블로그 링크']})", unsafe_allow_html=True)
                if travel["이미지"]:
                    st.image(travel["이미지"], caption=travel["여행지명"], width=500)
                # ✅ 주소가 없을 경우만 입력창 표시
                    if not travel["위치"] or travel["위치"].strip() in ["정보 없음", ""]:  
                        user_input_address = st.text_input(
                            f"📍 한국관광공사에서 주소정보를 제공하지 않았습니다. 직접 지역 키워드를 입력해주세요. ex)강원도 삼척시",
                            key=f"address_input_{idx}"
                        )
                    else:
                        user_input_address = travel["위치"]  # 주소가 있으면 기존 값 사용
#####               
                    if selected_country is None:
                        st.warning("❌ 대상 국가를 선택하지 않았습니다. **Country** 메뉴에서 먼저 대상 국가를 선택해주세요.")

                    else :
                        if st.button(f"➡ {travel['여행지명']} 시즌테마로 여행 패키지 만들기"):
                            st.session_state.selected_travel = travel["여행지명"]
                            st.session_state.selected_location = user_input_address
                            st.write(f"선택국가: {selected_country}")
                            st.write(f"선택한 시즌테마: {travel['여행지명']}")
                            st.write(f"선택한 위치: {user_input_address}")
                            navigate_to("TouristSpot")

    print(f"시즌 저장값 :{year}, {month}, {selected_country}, {travel['여행지명']}, {user_input_address}")