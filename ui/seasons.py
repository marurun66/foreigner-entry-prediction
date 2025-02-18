import re
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import streamlit as st

from navigation import navigate_to

# ✅ 네이버 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
NAVER_SEARCH_API_URL = "https://openapi.naver.com/v1/search/blog.json"

# ✅ 공공데이터 API 키 설정
data_go_API_KEY = st.secrets["data_go_API_KEY"]
KEYWORD_BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchKeyword1"


def clean_html_with_bs(text):
    """HTML 태그 및 마크다운 기호 제거"""
    cleaned_text = BeautifulSoup(text, "html.parser").get_text()
    markdown_patterns = [
        r"\*\*(.*?)\*\*",
        r"__(.*?)__",
        r"~~(.*?)~~",
        r"`(.*?)`",
        r"\[(.*?)\]\(.*?\)",
    ]
    for pattern in markdown_patterns:
        cleaned_text = re.sub(pattern, r"\1", cleaned_text)
    return cleaned_text


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


@st.cache_data(ttl=3600)  # 1시간 동안 캐싱
def get_travel_description(travel_name):
    """네이버 검색 API - 여행지 설명, 블로그 주소 가져오기 (캐싱 적용)"""
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": travel_name, "display": 1, "sort": "sim"}

    response = requests.get(NAVER_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            raw_text = data["items"][0]["description"]
            clean_text = clean_html_with_bs(raw_text)
            blog_link = data["items"][0]["link"]
            return clean_text, blog_link
    return "설명 없음", None


@st.cache_data(ttl=86400)  # 24시간 동안 캐싱
def fetch_seasonal_travel_data(season):
    """공공데이터 API에서 계절별 여행 정보 조회 (캐싱 적용)"""
    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "xml",
        "keyword": season,
    }

    response = requests.get(KEYWORD_BASE_URL, params=params)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    travel_list = []
    for item in items:
        title = (
            item.find("title").text if item.find("title") is not None else "정보 없음"
        )
        addr = (
            item.find("addr1").text if item.find("addr1") is not None else "정보 없음"
        )
        image_url = (
            item.find("firstimage").text
            if item.find("firstimage") is not None
            else None
        )
        description, blog_link = get_travel_description(title)

        travel_list.append(
            {
                "여행지명": title,
                "위치": addr,
                "설명": description,
                "블로그 링크": blog_link,
                "이미지": image_url,
            }
        )

    return travel_list


def run_seasons():
    """계절별 여행 정보 조회"""
    st.title("🌸⛱️ 계절별 여행 정보 조회🍁⛷️")
    st.write(
        """
    🌸🌞🍂❄️ **사계절 여행 정보, 한눈에 확인하세요!**  
    한국관광공사가 제공하는 여행 정보를 통해 **계절별 추천 여행지**를 살펴보세요.  
    마음에 드는 여행지를 선택하면, **맞춤형 여행 코스**를 함께 준비할 수 있어요! ✨🚀  
    """
    )

    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")

    if not (year and month and selected_country):
        col1, col2 = st.columns([1, 1])
        with col1:
            year = st.selectbox(
                "연도",
                [2025, 2026],
                key="year",
                index=None,
                placeholder="연도를 선택하세요",
            )
        with col2:
            month = st.selectbox(
                "월",
                list(range(1, 13)),
                key="month",
                index=None,
                placeholder="월을 선택하세요",
            )

        if year is None or month is None:
            st.warning("📅 여행 날짜를 선택하세요!")
            return

    season = get_season(month)
    st.write(f"📅 선택한 날짜: {year}년 {month}월 (계절: {season})")

    travel_list = fetch_seasonal_travel_data(season)  # ✅ API 캐싱 적용

    if not travel_list:
        st.warning(f"🚨 {season} 시즌의 여행 정보가 없습니다.")
        return

    st.success(f"총 {len(travel_list)}개의 여행 정보를 조회했습니다.")

    for idx, travel in enumerate(travel_list):
        with st.expander(f"📌 {travel['여행지명']} (자세히 보기)"):
            st.write(f"📍 위치: {travel['위치']}")
            st.write(f"📝 설명: {travel['설명']}")
            if travel["블로그 링크"]:
                st.markdown(
                    f"[🔗 관련 블로그 보기]({travel['블로그 링크']})",
                    unsafe_allow_html=True,
                )
            if travel["이미지"]:
                st.image(travel["이미지"], caption=travel["여행지명"], width=500)

            user_input_address = (
                travel["위치"]
                if travel["위치"] and travel["위치"].strip() not in ["정보 없음", ""]
                else st.text_input(
                    f"📍 주소 정보 없음. 직접 지역 키워드를 입력해주세요. (예: 강원도 삼척시)",
                    key=f"address_input_{idx}",
                )
            )

            if selected_country is None:
                st.warning(
                    "❌ 대상 국가를 선택하지 않았습니다. **Country** 메뉴에서 선택해주세요."
                )
            else:
                if st.button(f"➡ {travel['여행지명']} 시즌테마로 여행 패키지 만들기"):
                    st.session_state.selected_travel = travel["여행지명"]
                    st.session_state.selected_location = user_input_address
                    st.write(f"선택국가: {selected_country}")
                    st.write(f"선택한 시즌테마: {travel['여행지명']}")
                    st.write(f"선택한 위치: {user_input_address}")
                    navigate_to("TouristSpot")
