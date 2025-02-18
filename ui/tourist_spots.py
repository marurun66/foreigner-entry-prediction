import re
from bs4 import BeautifulSoup
import requests
import streamlit as st
import streamlit.components.v1 as components

from navigation import navigate_to

# ✅ API 키 설정
KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]
KAKAO_JS_KEY = st.secrets["KAKAO_JS_KEY"]
data_go_API_KEY = st.secrets["data_go_API_KEY"]
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]

################################################

def extract_region(address):
    """
    입력된 주소에서 '도 + 시/군' 또는 '광역시' 정보만 추출
    - '전북특별자치도 고창군 공음면 청천길 41-27' → ('전라북도', '고창군')
    - '서울특별시 중구 을지로 281 (을지로7가)' → ('서울특별시', '중구')
    - '경기도 수원시 영통구 영통동' → ('경기도', '수원시')
    - '김천시 청암사' → ('', '김천시')  ✅ 청암사 제거
    """

    # ✅ "특별자치도" → 기존 명칭으로 변환
    special_district_map = {
        "전북특별자치도": "전라북도",
        "강원특별자치도": "강원도"
    }
    
    # ✅ 정규식 패턴 (특별자치도 포함)
    pattern = re.compile(
        r"^(?:(서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|제주특별자치도|"
        r"전북특별자치도|강원특별자치도|경기도|충청북도|충청남도|전라북도|전라남도|경상북도|경상남도)\s*)?"
        r"(\S+시|\S+군|\S+구)"
    )

    match = pattern.search(address)

    if match:
        province = match.group(1) if match.group(1) else ""  # 도·광역시·특별시
        city_or_district = match.group(2) if match.group(2) else ""  # 시·군·구

        # ✅ 특별자치도 변환 적용
        if province in special_district_map:
            province = special_district_map[province]

        # ✅ 서울특별시는 '구' 정보까지만 반환
        if province == "서울특별시":
            return province, city_or_district

        # ✅ "김천시 청암사" → "김천시" 처리
        return province, city_or_district

    return None, None

def clean_html_with_bs(text):
    """HTML 태그 및 마크다운 기호 제거"""
    # 1️⃣ HTML 태그 제거
    cleaned_text = BeautifulSoup(text, "html.parser").get_text()

    # 2️⃣ 마크다운 기호 제거 (취소선, 볼드, 이탤릭 등)
    markdown_patterns = [
        r"\*\*(.*?)\*\*",  # **볼드체**
        r"__(.*?)__",      # __이탤릭체__
        r"~~(.*?)~~",      # ~~취소선~~
        r"`(.*?)`",        # `코드 블록`
        r"\[(.*?)\]\(.*?\)" # [링크 텍스트](URL)
    ]
    for pattern in markdown_patterns:
        cleaned_text = re.sub(pattern, r"\1", cleaned_text)  # 태그 내용만 남기고 마크다운 기호 삭제

    return cleaned_text


def get_tourist_description(place_name):
    """
    네이버 블로그 검색 API를 사용하여 관광지 설명과 블로그 링크 가져오기
    """
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": place_name, "display": 1, "sort": "sim"}  # 관련성 높은 블로그 1개 검색

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            raw_text = data["items"][0]["description"]
            clean_text = clean_html_with_bs(raw_text)  # ✅ HTML 태그 제거
            blog_link = data["items"][0]["link"]  # ✅ 블로그 링크
            return clean_text, blog_link
    return "❌ 관련 블로그 설명을 찾을 수 없습니다.", None


def get_coordinates_from_address(address):
    """
    카카오 주소 검색 API를 사용하여 주소를 위도, 경도로 변환하는 함수
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}



    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()

        
        if data["documents"]:
            x = data["documents"][0]["x"]  # 경도 (longitude)
            y = data["documents"][0]["y"]  # 위도 (latitude)
            return float(y), float(x)  # 위도, 경도 반환


################################################
def search_tourist_spots(query, region, display=10):
    """
    카카오 키워드 검색 API를 사용하여 지역 내 관광지를 검색
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": f"{region} {query}", "size": min(display, 15)}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("documents", [])
    else:
        st.error(f"❌ API 요청 실패: {response.status_code}, {response.text}")
        return []
    
def search_hotels(region, display=10):
    """
    카카오 키워드 검색 API를 사용하여 지역 내 호텔을 검색
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": f"{region} 호텔", "size": min(display, 15)}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("documents", [])
    else:
        st.error(f"❌ 호텔 정보 API 요청 실패: {response.status_code}, {response.text}")
        return []
    
################################################

def filter_tourist_spots(places):
    """
    검색된 관광지 목록에서 유의미한 장소만 필터링
    """
    tourist_keywords = ["관광", "명소", "유적지", "문화재", "전망대", "박물관", "테마파크", "공원"]
    return [place for place in places if any(keyword in place.get("category_group_name", "") for keyword in tourist_keywords)]

def filter_hotel(places):
    """
    검색된 숙박 목록에서 유의미한 장소만 필터링 (호텔, 숙소, 펜션, 리조트 포함)
    """
    hotel_keywords = ["호텔", "숙소", "펜션", "리조트"]

    return [
        place for place in places
        if any(keyword in (place.get("category_group_name", "") + place.get("place_name", "")) for keyword in hotel_keywords)
    ]

def generate_kakao_map(places,hotels,selected_location=None):

    selected_location = st.session_state.get("selected_location", "위치 정보 없음")
    if not selected_location:
        return
    """
    카카오 지도 HTML 생성 및 축제 위치 및 관광지 표시
    """
    # ✅ 축제 위치를 위도·경도로 변환

    selected_lat, selected_lng = None, None
    if selected_location:
        selected_lat, selected_lng = get_coordinates_from_address(selected_location)

    # ✅ 지도 중심 좌표 설정
    if selected_lat and selected_lng:
        center_lat, center_lng = selected_lat, selected_lng
    elif places:
        center_lat, center_lng = places[0]['y'], places[0]['x']
    else:
        center_lat, center_lng = 37.5665, 126.9780  

    markers_js = ""

    # ✅ 🎉 축제 위치 마커 추가
    if selected_location and selected_lat and selected_lng:
        markers_js += f"""
            console.log("🎯 축제 마커 추가: {selected_lat}, {selected_lng}"); // JS 디버깅 로그
            var selectedMarkerImage = new kakao.maps.MarkerImage(
                "https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png",
                new kakao.maps.Size(36, 45),
                new kakao.maps.Point(18, 45)
            );

            var selectedMarker = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({selected_lat}, {selected_lng}),
                map: map,
                image: selectedMarkerImage
            }});

            var selectedOverlay = new kakao.maps.CustomOverlay({{
                position: new kakao.maps.LatLng({selected_lat}, {selected_lng}),
                content: '<div class="custom-label" style="background:#ffaaaa; border-radius:6px; ' +
                        'padding:6px 8px; font-size:12px; color:#000; font-weight:bold; ' +
                        'display: inline-block; white-space: nowrap; ' +
                        'box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"><b>🎉 {selected_location} (테마 위치)</b></div>',
                yAnchor: 1.8  
            }});
            selectedOverlay.setMap(map);
        """

    # ✅ 관광지 마커 추가
    for idx, place in enumerate(places):
        markers_js += f"""
            var marker{idx} = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({place['y']}, {place['x']}),
                map: map
            }});

            var overlay{idx} = new kakao.maps.CustomOverlay({{
                position: new kakao.maps.LatLng({place['y']}, {place['x']}),
                content: '<div class="custom-label" style="background:#aaffde; border-radius:6px; ' +
                        'padding:6px 8px; font-size:12px; color:#000; font-weight:bold; ' +
                        'display: inline-block; white-space: nowrap; ' +
                        'box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"><b>🏞️{place["place_name"]}</b></div>',
                yAnchor: 1.8  
            }});
            overlay{idx}.setMap(map);
        """

    # ✅ 호텔 마커 추가 (파란색)
    for idx, hotel in enumerate(hotels):
        markers_js += f"""
            var hotelMarker{idx} = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({hotel['y']}, {hotel['x']}),
                map: map
            }});

            var hotelOverlay{idx} = new kakao.maps.CustomOverlay({{
                position: new kakao.maps.LatLng({hotel['y']}, {hotel['x']}),
                content: '<div class="custom-label" style="background:#aaddff; border-radius:6px; ' +
                        'padding:6px 8px; font-size:12px; color:#000; font-weight:bold; ' +
                        'display: inline-block; white-space: nowrap; ' +
                        'box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"><b>🏨 {hotel["place_name"]}</b></div>',
                yAnchor: 1.8  
            }});
            hotelOverlay{idx}.setMap(map);
        """

    # ✅ 카카오 지도 HTML 코드 생성
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
                    level: 10
                }};
            var map = new kakao.maps.Map(mapContainer, mapOption);

            {markers_js}
        </script>
    </body>
    </html>
    """
    return map_html









# ✅ 관광지 정보 조회 실행 함수
def run_tourist_spots():
    st.title("🌍 관광지 정보 조회")

    ## 🔹 이전 페이지에서 가져온 정보들
    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정
    selected_travel = st.session_state.get("selected_travel", "축제,테마 정보 없음")
    selected_location = st.session_state.get("selected_location", "위치 정보 없음")
    # ✅ year, month, selected_country 값이 있을 경우 정상 출력
    if year and month and selected_country:
        # 🛠️ ✅ session_state에 year, month 값 저장
        st.session_state["year"] = year
        st.session_state["month"] = month


    # 🔹 위치 정보가 없는 경우 → 경고 메시지 출력 후 종료
    if selected_location == "위치 정보 없음" or not selected_country:
        st.warning(""" 해당 메뉴에서는 선택한 외국인 관광객, 여행 날짜, 여행 지역 정보를 바탕으로 여행 일정을 계획할 수 있습니다.  
                   ❌ 현재 설정된 외국인 관광객 및 여행 정보가 없습니다.❌  
                   Country 메뉴에서부터 시작해주세요.😉""")
        if st.button("➡ Country 메뉴로 이동"):
            navigate_to("Country")
        return
    
    province, city = extract_region(selected_location)  # ✅ 도, 시 정보 추출
    
    # 🔹 선택된 정보 출력
    language = info.get("언어", "알 수 없음")
    travel_preference = info.get("여행 성향", "알 수 없음")

    st.write(f"""📅 선택한 날짜: {year}년 {month}월  
            🌍 선택한 국가: {selected_country}  
            🗣 언어: {language}  
            🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
            👥 입국 예상 인원: {expected_visitors:,} 명  
            🎉 선택 테마: {selected_travel}  
            📍 테마 지역: {selected_location}""")

    # 🔹 위치 정보가 없을 경우 → 경고 메시지 출력 후 종료
    if not province and not city:
        st.warning("""❌ 입력하신 위치정보로 검색에 실패했습니다.  
                   해당 앱은 '도 + 시/군' 또는 '광역시' 정보로만 검색 가능합니다.""")
        return
    if not year:
        st.warning("❌ 날짜 선택이 되지 않았어요. 이전 메뉴에서 날짜를 선택하면 해당 지역 관광지를 알려드립니다.")
        return

    # 🔹 관광지 검색
    places = search_tourist_spots("관광지", f"{province} {city}", display=10)
    tourist_spots = filter_tourist_spots(places)

    # 🔹 숙소 검색
    hotel_places = search_hotels(f"{province} {city}", display=10)
    hotels = filter_hotel(hotel_places)

    # ✅ 선택한 관광지 및 숙소를 저장할 세션 상태 초기화
    if "selected_places" not in st.session_state:
        st.session_state.selected_places = set()
#############시작
#######3시작
    
    # ✅ 검색 결과 출력
    success_box_html = f"""
        <div style="
            padding: 15px; 
            background-color: #dff0d8; 
            border: 1px solid #c3e6cb; 
            border-radius: 8px; 
            color: #155724; 
            font-size: 16px; 
            font-weight: bold; 
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        ">
            🔎 검색 결과<br>
            📍 {province} {city}에서 <b>{len(tourist_spots)}</b>개의 관광지를 찾았습니다.<br>
            🏨 {province} {city}에서 <b>{len(hotels)}</b>개의 숙소를 찾았습니다.
        </div>
    """

    st.markdown(success_box_html, unsafe_allow_html=True)


    # 🔹 카카오 지도 표시
    st.subheader("🗺 카카오 지도에서 관광지 & 숙소 확인")
    map_html = generate_kakao_map(tourist_spots, hotels)
    components.html(map_html, height=500, scrolling=False)
    
    # 🔹 관광지와 숙소를 2개 컬럼으로 표시
    st.subheader("📌 여행일정에 추가하고싶은 관광지 및 숙소를 선택하세요.")

    # ✅ 폼 제출 상태를 저장하는 변수 초기화
    if "submit_clicked" not in st.session_state:
        st.session_state.submit_clicked = False

    with st.form("selection_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📍 {province} {city} 인근 관광지 검색 결과")
            if tourist_spots:
                for place in tourist_spots:
                    place_name = place["place_name"]
                    place_address = place["road_address_name"] or place["address_name"]
                    place_category = place["category_name"]
                    place_map_url = f"https://map.kakao.com/link/map/{place['id']}"
                    
                    with st.expander(f"📍 {place['place_name']} (자세히 보기)"):

                                # ✅ 관광지 설명과 블로그 링크 가져오기
                        description, blog_url = get_tourist_description(place_name)
                        st.write(f"📍 **주소:** {place_address}")
                        if place.get("phone"):
                            st.write(f"📞 **전화번호:** {place['phone']}")
                        st.write(f"🏷 **카테고리:** {place_category}")
                        st.write(f"📝 **설명:** {description}"
                        )
                        if blog_url:
                            st.markdown(f"[📖 네이버 블로그 리뷰 보기]({blog_url})", unsafe_allow_html=True)
                        st.markdown(f"[📍 카카오 지도에서 보기]({place_map_url})", unsafe_allow_html=True)
                        #체크박스
                        key = f"tourist_{place['id']}"
                        selected = st.checkbox(f"{place['place_name']} 여행일정에 추가하기!", value=(key in st.session_state.selected_places))

                        if selected and key not in st.session_state.selected_places:
                            st.session_state.selected_places.add(place_name)
                        elif not selected and key in st.session_state.selected_places:
                            st.session_state.selected_places.discard(place_name)
                        
            else:
                st.warning("🔍 해당 지역에서 관광지를 찾을 수 없습니다.")

        with col2:
            st.subheader(f"🏨 {province} {city} 인근 숙소 검색 결과")
            if hotels:
                for hotel in hotels:
                    with st.expander(f"🏨 {hotel['place_name']} (자세히 보기)"):
                        st.write(f"📍 **주소:** {hotel['road_address_name'] or hotel['address_name']}")
                        if hotel.get("phone"):
                            st.write(f"📞 **전화번호:** {hotel['phone']}")
                        map_url = f"https://map.kakao.com/link/map/{hotel['id']}"
                        st.markdown(f"[📍 카카오 지도에서 보기]({map_url})", unsafe_allow_html=True)
                                                #체크박스
                        key = f"hotel_{hotel['id']}"
                        selected = st.checkbox(f"{hotel['place_name']} 여행일정에 추가하기!", value=(key in st.session_state.selected_places))
                        if selected and key not in st.session_state.selected_places:
                            st.session_state.selected_places.add(place_name)
                        elif not selected and key in st.session_state.selected_places:
                            st.session_state.selected_places.discard(place_name)
            else:
                st.warning("🔍 해당 지역에서 숙소를 찾을 수 없습니다.")

        submit_button = st.form_submit_button("✅선택 완료!")

    # ✅ "선택 완료" 버튼이 눌렸을 때만 아래 내용이 보이게 설정
    if submit_button:
        st.session_state.submit_clicked = True  # ✅ 제출 상태 저장

    if st.session_state.submit_clicked:
        st.subheader("✅ 선택한 관광지 & 숙소 목록")

        if st.session_state.selected_places:
            selected_list = list(st.session_state.selected_places)  # ✅ set을 리스트로 변환
            for place_name in st.session_state.selected_places:
                st.write(f"✔️ {place_name}")

            # ✅ LLM 여행 패키지 생성 버튼 (submit 후에만 나타남)
            if st.button("➡ AI와 함께 여행 패키지 만들기"):
                navigate_to("AI PLANNER")
        
        else:
            st.write("❌ 아직 선택된 관광지 & 숙소가 없습니다.")


