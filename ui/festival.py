from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

def run_festival():
    # ✅ 세션 상태 변수 확인
    if "year" not in st.session_state or "month" not in st.session_state:
        st.error("📅 날짜가 선택되지 않았습니다. EDA 페이지에서 설정해 주세요.")
        return  # 🚨 실행 중단

    year = st.session_state.year
    month = st.session_state.month
    st.write(f"📅 선택한 날짜: {year}년 {month}월")
# 관광공사 
    # 관광공사 발급받은 API 키 입력
    data_go_API_KEY = st.secrets["data_go_API_KEY"]
    BASE_URL = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"

    # ✅ API 요청 파라미터 설정
    params = {
        "serviceKey": data_go_API_KEY,
        "numOfRows": 50,  # ✅ 더 많은 축제 포함
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "TravelApp",
        "_type": "xml",
        "eventStartDate": f"{year}{month:02d}01",  # ✅ YYYYMMDD 형식 유지
    }

    # ✅ API 요청
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        root = ET.fromstring(response.content)  # XML 데이터 파싱
        items = root.findall(".//item")  # 축제 리스트 찾기

        festival_list = []
        for item in items:
            title = item.find("title").text if item.find("title") is not None else "정보 없음"
            addr = item.find("addr1").text if item.find("addr1") is not None else "정보 없음"
            start_date = item.find("eventstartdate").text if item.find("eventstartdate") is not None else "정보 없음"
            end_date = item.find("eventenddate").text if item.find("eventenddate") is not None else "정보 없음"
            image_url = item.find("firstimage").text if item.find("firstimage") is not None else None

            # ✅ 🎯 해당 월에 진행 중인 축제 포함 (start_date ≤ 선택 날짜 ≤ end_date)
            selected_month_str = f"{year}{month:02d}"  # 202503 형식
            if start_date[:6] <= selected_month_str <= end_date[:6]:
                festival_list.append({
                    "축제명": title,
                    "위치": addr,
                    "일정": f"{start_date} ~ {end_date}",
                    "이미지": image_url
                })
# 관광공사 
        # ✅ Streamlit에서 필터링된 데이터 출력
        if len(festival_list) == 0:
            st.warning(f"""🚨 한국관광공사에 {year}년 {month}월에 진행 예정인 축제정보가 아직 업데이트 되지 않았습니다.  
                       계절별 여행추천 메뉴에서 고려해보세요.""")
        else:
            st.success(f"총 {len(festival_list)}개의 축제를 조회했습니다.")
            for idx, festival in enumerate(festival_list):# 관광공사 
                with st.expander(f"📌 {festival['축제명']} (자세히 보기)"):# 관광공사 
                    st.write(f"📍 위치: {festival['위치']}")# 관광공사 
                    st.write(f"📅 일정: {festival['일정']}")# 관광공사 
                    if festival["이미지"]:# 관광공사 
                        st.image(festival["이미지"], caption=festival["축제명"], width=500)
    else:
        st.error("❌ API 요청 실패! 다시 시도해 주세요.")


