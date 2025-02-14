from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import streamlit as st

# ✅ 네이버 API 키 설정 (네이버 개발자 센터에서 발급)
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
NAVER_SEARCH_API_URL = "https://openapi.naver.com/v1/search/blog.json"  # 블로그 검색 API 사용


def clean_html_with_bs(text):
    """BeautifulSoup을 이용한 HTML 태그 제거"""
    return BeautifulSoup(text, "html.parser").get_text()

def get_festival_description(festival_name):
    """네이버 검색 API를 이용해 축제 설명 가져오기"""
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": festival_name,  # 검색할 축제명
        "display": 1,  # 상위 1개의 결과만 가져오기
        "sort": "sim"  # 관련성 높은 결과 우선
    }
    
    response = requests.get(NAVER_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            raw_text = data["items"][0]["description"]  # 첫 번째 검색 결과의 설명 반환
            clean_text=clean_html_with_bs(raw_text) # HTML 태그 제거 후 반환
            blog_link = data["items"][0]["link"]  # 블로그 링크
            return clean_text, blog_link 
        
    return "설명 없음",None

def run_festival():
    if "year" not in st.session_state or "month" not in st.session_state:
        st.error("📅 날짜가 선택되지 않았습니다. EDA 페이지에서 설정해 주세요.")
        return

    year = st.session_state.year
    month = st.session_state.month
    st.write(f"📅 선택한 날짜: {year}년 {month}월")

    # ✅ 발급받은 API 키 입력
    data_go_API_KEY = st.secrets["data_go_API_KEY"]
    BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"

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
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        festival_list = []
        selected_month_str = f"{year}{month:02d}"
        for item in items:
            title = item.find("title").text if item.find("title") is not None else "정보 없음"
            addr = item.find("addr1").text if item.find("addr1") is not None else "정보 없음"
            start_date = item.find("eventstartdate").text if item.find("eventstartdate") is not None else "정보 없음"
            end_date = item.find("eventenddate").text if item.find("eventenddate") is not None else "정보 없음"
            image_url = item.find("firstimage").text if item.find("firstimage") is not None else None

            if start_date[:6] <= selected_month_str <= end_date[:6]:
                description, blog_link = get_festival_description(title)  # ✅ 설명 & 블로그 링크 가져오기
                festival_list.append({
                    "축제명": title,
                    "위치": addr,
                    "일정": f"{start_date} ~ {end_date}",
                    "설명": description,
                    "블로그 링크": blog_link,
                    "이미지": image_url
                })

        if len(festival_list) == 0:
            st.warning(f"""🚨 한국관광공사에 {year}년 {month}월에 진행 예정인 축제정보가 아직 업데이트 되지 않았습니다.  
                       계절별 여행추천 메뉴에서 고려해보세요.""")
        else:
            st.success(f"총 {len(festival_list)}개의 축제를 조회했습니다.")
            for idx, festival in enumerate(festival_list):
                with st.expander(f"📌 {festival['축제명']} (자세히 보기)"):
                    st.write(f"📍 위치: {festival['위치']}")
                    st.write(f"📅 일정: {festival['일정']}")
                    st.write(f"📝 설명: {festival['설명']}")  # ✅ 설명 추가
                    if festival["블로그 링크"]:
                        st.markdown(f"[🔗 관련 블로그 보기]({festival['블로그 링크']})", unsafe_allow_html=True)  # ✅ 블로그 링크 추가
                    if festival["이미지"]:
                        st.image(festival["이미지"], caption=festival["축제명"], width=500)
    else:
        st.error("❌ API 요청 실패! 다시 시도해 주세요.")


