from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import streamlit as st

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

def get_festival_description(festival_name):
    """네이버 검색 API - 축제 설명, 블로그주소 가져오기"""
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

######################################3

def run_festival():
    st.title("🥳 축제 정보 조회")
    st.write("""
    ✨ **한국관광공사 제공! 전국 축제 정보를 한눈에 확인하세요!** ✨  
    원하는 축제를 선택하면, 해당 지역에 맞춘 **맞춤형 여행 패키지**를 함께 구상해볼 수 있어요.  
    멋진 여행 계획을 지금 바로 시작해보세요! 🚀🌍  
    """)
    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정

    # ✅ year, month, selected_country 값이 있을 경우 정상 출력
    if year and month and selected_country:
        language = info.get("언어", "알 수 없음")
        travel_preference = info.get("여행 성향", "알 수 없음")

        st.write(f"""📅 선택한 날짜: {year}년 {month}월  
                🌍 선택한 국가: {selected_country}  
                🗣 언어: {language}  
                🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
                👥 입국 예상 인원: {expected_visitors:,} 명""")
        
    else:        
        # ✅ 연도 및 월 선택
        col1, col2 = st.columns([1, 1])
        with col1:
            year = st.selectbox("연도", [2025, 2026], key="year", index=None, placeholder="연도를 선택하세요")
        with col2:
            month = st.selectbox("월", list(range(1, 13)), key="month", index=None, placeholder="월을 선택하세요")
        
        if year is None or month is None:
            st.warning("""
            📅 **여행 날짜와 🌎 대상 국가를 아직 선택하지 않으셨네요!**  
            **[Country]** 메뉴에서 15개국의 예상 입국 인원을 비교하고, **어느 국가**의 여행객을 위한 패키지를 구상할지 선택 해보세요. 😉  
            만약 **축제 정보를 먼저 확인하고 싶다면, 여행 날짜를 선택**해 주세요! 🎉  
            """)

            return

    # ✅ API 요청 파라미터 설정
    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 50,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "xml",
        "eventStartDate": f"{year}{month:02d}01",
    }

    # ✅ API 요청 및 응답 처리
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        st.error("❌ API 요청 실패! 다시 시도해 주세요.")
        return

    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    festival_list = []
    selected_month_str = f"{year}{month:02d}"

    # ✅ 축제 데이터 파싱
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

    # ✅ 축제 데이터가 없을 경우 처리
    if len(festival_list) == 0:
        st.warning(f"""🚨 한국관광공사에 {year}년 {month}월에 진행 예정인 축제 정보가 아직 업데이트되지 않았습니다.  
                Seasons 메뉴에서 해당 달에 어울리는 여행 코스를 고려해보세요.""")

    # ✅ 축제 데이터가 있을 경우 표시
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

                if selected_country==None:
                    st.warning("❌ 여행지를 선택하지 않았습니다. **Country** 메뉴에서 여행지를 선택해주세요.")

                # ✅ 축제 선택 버튼 추가
                else:
                    if st.button(f"➡ 🎉 {festival['축제명']}와 함께하는 여행 패키지 만들기 시작하기", key=f"btn_{idx}"):
                        st.session_state["current_page"] = "TouristSpot"  # ✅ 페이지 상태 변경
                        st.write(f"🔄 페이지 변경됨: {st.session_state['current_page']}")  # 디버깅용 출력
                        st.rerun() 



