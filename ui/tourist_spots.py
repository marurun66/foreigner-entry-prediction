import streamlit as st
from bs4 import BeautifulSoup
import requests

# ✅ 네이버 API 키 설정 (네이버 개발자 센터에서 발급)
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
NAVER_SEARCH_API_URL = "https://openapi.naver.com/v1/search/blog.json"  # 블로그 검색 API 사용
#data_go_API_KEY 설정
data_go_API_KEY = st.secrets["data_go_API_KEY"]
BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"

def clean_html_with_bs(text):
    """HTML 태그 제거"""
    return BeautifulSoup(text, "html.parser").get_text()

def get_spots(location):
    """한국관광공사 API를 이용해 관광지 정보를 가져옴"""
    BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchKeyword1"
    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 5,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "json",
        "keyword": location
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "관광지명": item["title"],
                "주소": item["addr1"],
                "이미지": item.get("firstimage", None)
            }
            for item in data["response"]["body"]["items"]["item"]
        ]
    return []

def get_hotels(location):
    """네이버 API를 이용해 호텔 정보를 검색"""
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": f"{location} 호텔",
        "display": 3,  # 상위 3개만 가져오기
        "sort": "sim"
    }
    
    response = requests.get(NAVER_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "호텔명": item["title"],
                "링크": item["link"],
                "설명": clean_html_with_bs(item["description"])
            }
            for item in data["items"]
        ]
    return []

def run_tourist_spots():
    st.title("🌍 관광지 정보 조회")
    
    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정
    selected_festival = st.session_state.get("selected_festival", "축제 정보 없음")
    selected_location = st.session_state.get("selected_location", "위치 정보 없음")


    # ✅ year, month, selected_country 값이 있을 경우 정상 출력
    if year and month and selected_country :
        language = info.get("언어", "알 수 없음")
        travel_preference = info.get("여행 성향", "알 수 없음")

        st.write(f"""📅 선택한 날짜: {year}년 {month}월  
                🌍 선택한 국가: {selected_country}  
                🗣 언어: {language}  
                🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
                👥 입국 예상 인원: {expected_visitors:,} 명  
                🎉 선택한 축제: {selected_festival}""")
    else:
        st.write(f"""여행패키지 구상을 위해서는 나라선택, 축제나 사계절 정보 후 원하는 테마 선택이 필요합니다.  
                 Country에서부터 차근차근 선택해주세요.""")
        
    print(f"투어리스트:{year}, {month},{info} {selected_country}, {selected_festival}, {selected_location}")

