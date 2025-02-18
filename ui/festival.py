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

# ✅ data_go_API_KEY 설정
data_go_API_KEY = st.secrets["data_go_API_KEY"]
BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"


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


@st.cache_data(ttl=3600)  # 1시간 동안 캐싱
def get_festival_description(festival_name):
    """네이버 검색 API - 축제 설명, 블로그주소 가져오기 (캐싱 적용)"""
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": festival_name, "display": 1, "sort": "sim"}
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
def fetch_festival_data(year, month):
    """한국관광공사 API를 통해 축제 정보를 가져오기 (캐싱 적용)"""
    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 50,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "xml",
        "eventStartDate": f"{year}{month:02d}01",
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    festival_list = []
    selected_month_str = f"{year}{month:02d}"

    for item in items:
        title = (
            item.find("title").text if item.find("title") is not None else "정보 없음"
        )
        addr = (
            item.find("addr1").text if item.find("addr1") is not None else "정보 없음"
        )
        start_date = (
            item.find("eventstartdate").text
            if item.find("eventstartdate") is not None
            else "정보 없음"
        )
        end_date = (
            item.find("eventenddate").text
            if item.find("eventenddate") is not None
            else "정보 없음"
        )
        image_url = (
            item.find("firstimage").text
            if item.find("firstimage") is not None
            else None
        )

        if start_date[:6] <= selected_month_str <= end_date[:6]:
            description, blog_link = get_festival_description(
                title
            )  # ✅ 캐싱된 함수 사용
            festival_list.append(
                {
                    "축제명": title,
                    "위치": addr,
                    "일정": f"{start_date} ~ {end_date}",
                    "설명": description,
                    "블로그 링크": blog_link,
                    "이미지": image_url,
                }
            )

    return festival_list


def run_festival():
    st.title("🥳 축제 정보 조회")
    st.write(
        """
    ✨ **한국관광공사 제공! 전국 축제 정보를 한눈에 확인하세요!** ✨  
    원하는 축제를 선택하면, 해당 지역에 맞춘 **맞춤형 여행 패키지**를 함께 구상해볼 수 있어요.  
    멋진 여행 계획을 지금 바로 시작해보세요! 🚀🌍  
    """
    )

    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})
    expected_visitors = st.session_state.get("expected_visitors", "미정")

    if year and month and selected_country:
        st.session_state["year"] = year
        st.session_state["month"] = month

        language = info.get("언어", "알 수 없음")
        travel_preference = info.get("여행 성향", "알 수 없음")

        st.write(
            f"""📅 선택한 날짜: {year}년 {month}월  
                🌍 선택한 국가: {selected_country}  
                🗣 언어: {language}  
                🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
                👥 입국 예상 인원: {expected_visitors:,} 명"""
        )

    else:
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
            st.warning(
                """
            📅 **여행 날짜와 🌎 대상 국가를 아직 선택하지 않으셨네요!**  
            **[Country]** 메뉴에서 15개국의 예상 입국 인원을 비교하고, **어느 국가**의 여행객을 위한 패키지를 구상할지 선택 해보세요. 😉  
            만약 **축제 정보를 먼저 확인하고 싶다면, 여행 날짜를 선택**해 주세요! 🎉  
            """
            )
            return

    festival_list = fetch_festival_data(year, month)  # ✅ API 캐싱 적용

    st.success(f"총 {len(festival_list)}개의 축제를 조회했습니다.")

    for _, festival in enumerate(festival_list):
        with st.expander(f"📌 {festival['축제명']} (자세히 보기)"):
            st.write(f"📍 위치: {festival['위치']}")
            st.write(f"📅 일정: {festival['일정']}")
            st.write(f"📝 설명: {festival['설명']}")
            if festival["블로그 링크"]:
                st.markdown(
                    f"[🔗 관련 블로그 보기]({festival['블로그 링크']})",
                    unsafe_allow_html=True,
                )
            if festival["이미지"]:
                st.image(festival["이미지"], caption=festival["축제명"], width=500)

            if selected_country is None:
                st.warning(
                    "❌ 대상 국가를 선택하지 않았습니다. **Country** 메뉴에서 먼저 대상 국가를 선택해주세요."
                )
            else:
                if st.button(
                    f"➡ 🎉 {festival['축제명']}와 함께하는 여행 패키지 만들기"
                ):
                    st.session_state["selected_travel"] = festival["축제명"]
                    st.session_state["selected_location"] = festival["위치"]
                    navigate_to("TouristSpot")

    if len(festival_list) == 0:
        st.warning(
            f"""🚨 한국관광공사에 {year}년 {month}월 예정된 축제 정보가 아직 업데이트되지 않았습니다."""
        )
        if st.button(f"➡ Seasons 메뉴로 이동"):
            navigate_to("Seasons")
