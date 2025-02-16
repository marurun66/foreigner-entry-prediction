import re
import requests
import streamlit as st
import streamlit.components.v1 as components

# ✅ API 키 설정
KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]
KAKAO_JS_KEY = st.secrets["KAKAO_JS_KEY"]
data_go_API_KEY = st.secrets["data_go_API_KEY"]


def extract_region(address):
    """
    주소에서 '도 + 시/군' 또는 '광역시' 정보를 추출하는 함수
    - '세종특별자치시 전동면 신송로 217' → ('세종특별자치시', '')
    - '경기도 가평군 청평면' → ('경기도', '가평군')
    - '서울특별시 강남구 역삼동' → ('서울특별시', '강남구') ✅ (서울특별시는 구 정보 포함)
    - '대구광역시 중구 동성로2길 80 (공평동)' → ('대구광역시', '')
    - '경기도 수원시 팔달구' → ('경기도', '수원시')
    """

    pattern = re.compile(
        r"(서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|제주특별자치도|경기도|강원특별자치도|충청북도|충청남도|전라북도|전라남도|경상북도|경상남도)"
        r"(?:\s+(\S+시|\S+군|\S+구))?"
    )

    match = pattern.search(address)
    print(f"📌 [DEBUG] 주소 입력: {address}, 매치 결과: {match}")

    if match:
        province = match.group(1)  # 도·광역시·특별시
        city_or_district = match.group(2) if match.group(2) else ""  # 시·군·구

        # ✅ 서울특별시는 '구' 정보만 반환 (예: '강남구')
        if province == "서울특별시":
            return province, city_or_district
        
        # ✅ 나머지 지역은 '시' 또는 '군'까지만 반환
        return province, city_or_district if "시" in city_or_district or "군" in city_or_district else ""

    return None, None



def search_tourist_spots(query, region, display=10):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "KA": "python/requests streamlit-app"
    }
    params = {
        "query": f"{region} {query}",  # 지역 + 검색 키워드 조합
        "size": min(display, 15)  # ✅ 최대 15개 제한 적용
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("documents", [])  # 장소 리스트 반환
    else:
        st.error(f"❌ API 요청 실패: {response.status_code}, {response.text}")
        return []

# ✅ 관광지 필터링 함수 (카카오 API 응답 데이터 구조에 맞게 수정)
def filter_tourist_spots(places):
    tourist_keywords = ["관광", "명소", "유적지", "문화재", "전망대", "박물관", "테마파크", "공원"]
    
    filtered_places = []
    for place in places:
        category = place.get("category_group_name", "")  # 카테고리 정보
        if any(keyword in category for keyword in tourist_keywords):
            filtered_places.append(place)
    
    return filtered_places

# ✅ 카카오 지도 HTML 생성 함수 (수정된 버전)
def generate_kakao_map(places):
    # ✅ 첫 번째 관광지를 중심 좌표로 설정 (기본값: 서울)
    if places:
        center_lat, center_lng = places[0]['y'], places[0]['x']
    else:
        center_lat, center_lng = 37.5665, 126.9780  # 기본 서울 좌표

    # ✅ 마커 정보를 JavaScript로 변환
    markers_js = ""
    for place in places:
        markers_js += f"""
            var marker = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({place['y']}, {place['x']}),
                map: map
            }});
        """

    # ✅ 카카오 지도 HTML 코드 생성 (SDK에 `libraries=services` 추가)
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script type="text/javascript" 
            src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&libraries=services"></script>
    </head>
    <body>
        <div id="map" style="width: 100%; height: 500px;"></div>
        <script>
            var mapContainer = document.getElementById('map'),
                mapOption = {{
                    center: new kakao.maps.LatLng({center_lat}, {center_lng}),
                    level: 7  // 지도 확대 레벨
                }};
            var map = new kakao.maps.Map(mapContainer, mapOption);
            
            // ✅ 마커 추가
            {markers_js}
        </script>
    </body>
    </html>
    """

    return map_html



# ✅ 관광지 정보 조회 실행 함수
def run_tourist_spots():
    st.title("🌍 관광지 정보 조회")

    ## 이전페이지 정보들
    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정
    selected_travel = st.session_state.get("selected_travel", "축제,테마 정보 없음")
    selected_location = st.session_state.get("selected_location", "위치 정보 없음")
    print(f"selected_location:{selected_location}")

    province, city = extract_region(selected_location)  # ✅ 도, 시 정보 추출
    print(f"도시정보:{province}, {city}")
  
    # ✅ year, month, selected_country 값이 있을 경우 정상 출력
    if year and month and selected_country :
        language = info.get("언어", "알 수 없음")
        travel_preference = info.get("여행 성향", "알 수 없음")

        st.write(f"""📅 선택한 날짜: {year}년 {month}월  
                🌍 선택한 국가: {selected_country}  
                🗣 언어: {language}  
                🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
                👥 입국 예상 인원: {expected_visitors:,} 명  
                🎉 선택 테마: {selected_travel}""")
        
            # ✅ 위치 정보가 없는 경우 경고 메시지 출력
    if not province or not city:
        st.warning("❌ 올바른 여행 지역 정보가 없습니다. Festival, Seasons 메뉴에서 테마를 선택하면 해당 지역 관광지를 알려드립니다.")
        return
        
    st.subheader(f"📍 {province} {city} 인근 관광지 검색 결과")
    places = search_tourist_spots("관광지", f"{province} {city}", display=10)
    tourist_spots = filter_tourist_spots(places)


    # ✅ 검색 결과가 있을 경우 `expander()`로 출력
    if tourist_spots:
        st.success(f"🔎 {province} {city}에서 {len(tourist_spots)}개의 관광지를 찾았습니다.")
        # ✅ 카카오 지도 표시
        st.subheader("🗺 카카오 지도에서 관광지 확인")
        map_html = generate_kakao_map(tourist_spots)
        components.html(map_html, height=500, scrolling=False)

        for idx, place in enumerate(tourist_spots):
            with st.expander(f"📍 {place['place_name']} (자세히 보기)"):
                st.write(f"📍 **주소:** {place['road_address_name'] or place['address_name']}")
                st.write(f"📞 **전화번호:** {place['phone'] if place['phone'] else '없음'}")
                st.write(f"🏷 **카테고리:** {place['category_name']}")
                
                # ✅ 네이버 지도 또는 카카오 지도에서 보기 버튼 추가
                map_url = f"https://map.kakao.com/link/map/{place['id']}"
                st.markdown(f"[📍 카카오 지도에서 보기]({map_url})", unsafe_allow_html=True)

    else:
        st.warning("🔍 해당 지역에서 관광지를 찾을 수 없습니다.")
                
    if selected_location == "위치 정보 없음":
        st.write(f"""여행패키지 구상을 위해서는 나라선택, 축제나 사계절 정보 후 원하는 테마 선택이 필요합니다.  
                 Country에서부터 차근차근 선택해주세요.""")
        return
    
    print(f"투어리스트:{year}, {month},{info} {selected_country}, {selected_travel}, {selected_location}")
