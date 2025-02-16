import re
import requests
import streamlit as st
import streamlit.components.v1 as components

# ✅ API 키 설정
KAKAO_API_KEY = st.secrets["KAKAO_API_KEY"]
KAKAO_JS_KEY = st.secrets["KAKAO_JS_KEY"]
data_go_API_KEY = st.secrets["data_go_API_KEY"]

import re


def extract_region(address):
    """
    주소에서 '도 + 시/군' 또는 '광역시' 정보만 추출
    - '전북특별자치도 고창군 공음면 청천길 41-27' → ('전라북도', '고창군')
    - '서울특별시 중구 을지로 281 (을지로7가)' → ('서울특별시', '중구')
    - '경기도 수원시 영통구 영통동' → ('경기도', '수원시')
    - '김천시 청암사' → ('', '김천시')  ✅ 청암사 제거
    - '부산' → ('부산광역시', '')  ✅ 광역시만 입력해도 정상 처리
    """

    # ✅ "특별자치도" → 기존 명칭으로 변환
    special_district_map = {
        "전북특별자치도": "전라북도",
        "강원특별자치도": "강원도"
    }
    
    # ✅ 정규식 패턴 (특별자치도 포함, 시·군·구가 없어도 매칭 가능하도록 개선)
    pattern = re.compile(
        r"^(서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|제주특별자치도|"
        r"전북특별자치도|강원특별자치도|경기도|충청북도|충청남도|전라북도|전라남도|경상북도|경상남도)"
        r"(?:\s+(\S+시|\S+군|\S+구))?"  # 시·군·구가 없어도 매칭되도록 변경
    )

    match = pattern.search(address)
    print(f"📌 [DEBUG] 주소 입력: {address}, 매치 결과: {match}")

    if match:
        province = match.group(1) if match.group(1) else ""  # 도·광역시·특별시
        city_or_district = match.group(2) if match.group(2) else ""  # 시·군·구

        # ✅ 특별자치도 변환 적용
        if province in special_district_map:
            province = special_district_map[province]

        # ✅ 서울특별시는 '구' 정보까지만 반환
        if province == "서울특별시":
            return province, city_or_district

        # ✅ 광역시·특별시·도만 입력한 경우 → 시·군·구 없이 반환
        if province and not city_or_district:
            return province, ""

        # ✅ 도가 없는 경우 → 유저가 "경주시"만 입력한 경우, 그대로 반환
        if not province and city_or_district:
            return "", city_or_district
        
        # ✅ 기본적으로 '도 + 시/군' 반환 (구 이하 정보는 제외)
        return province, city_or_district if city_or_district else ""

    return None, None



def get_coordinates_from_address(address):
    """
    카카오 주소 검색 API를 사용하여 주소를 위도, 경도로 변환하는 함수
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}

    print(f"🔍 [DEBUG] API 요청: {url}, 주소: {address}")

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ [DEBUG] API 응답 데이터: {data}")  # API 응답 데이터 출력
        
        if data["documents"]:
            x = data["documents"][0]["x"]  # 경도 (longitude)
            y = data["documents"][0]["y"]  # 위도 (latitude)
            print(f"🎯 [DEBUG] 변환된 좌표: ({y}, {x})")  # 변환된 좌표 확인
            return float(y), float(x)  # 위도, 경도 반환
        else:
            print(f"⚠️ [DEBUG] 변환된 좌표 없음: {address}")
    else:
        print(f"❌ [DEBUG] 주소 변환 실패: {response.status_code}, {response.text}")



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

def filter_tourist_spots(places):
    """
    검색된 관광지 목록에서 유의미한 장소만 필터링
    """
    tourist_keywords = ["관광", "명소", "유적지", "문화재", "전망대", "박물관", "테마파크", "공원"]
    return [place for place in places if any(keyword in place.get("category_group_name", "") for keyword in tourist_keywords)]

def generate_kakao_map(places, selected_location=None):
    print("✅ [DEBUG] generate_kakao_map() 실행됨")
    selected_location = st.session_state.get("selected_location", "위치 정보 없음")
    if not selected_location:
        print("❌ [DEBUG] selected_location 값이 None 또는 빈 값입니다.")  # ✅ selected_location이 없을 경우 경고 출력
        return
    """
    카카오 지도 HTML 생성 및 축제 위치 및 관광지 표시
    """
    # ✅ 축제 위치를 위도·경도로 변환
    print("🛠️ [DEBUG] get_coordinates_from_address() 호출됨")
    selected_lat, selected_lng = None, None
    if selected_location:
        selected_lat, selected_lng = get_coordinates_from_address(selected_location)
        print("🛠️ [DEBUG] get_coordinates_from_address() 함수 실행됨")
        print(f"🎯 [DEBUG] 축제 위치 변환 결과: {selected_location} → ({selected_lat}, {selected_lng})")  # 디버깅용 프린트

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
                content: '<div class="custom-label" style="background:#ffffff; border-radius:6px; ' +
                        'padding:6px 8px; font-size:12px; color:#000; font-weight:bold; ' +
                        'display: inline-block; white-space: nowrap; ' +
                        'box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"><b>{place["place_name"]}</b></div>',
                yAnchor: 1.8  
            }});
            overlay{idx}.setMap(map);
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

    # 🔹 위치 정보가 없는 경우 → 경고 메시지 출력 후 종료
    if selected_location == "위치 정보 없음" or not selected_country:
        st.warning("❌ 올바른 여행 지역 정보가 없습니다. Festival, Seasons 메뉴에서 테마를 선택하면 해당 지역 관광지를 알려드립니다.")
        return
    
    province, city = extract_region(selected_location)  # ✅ 도, 시 정보 추출
    
    # 🔹 먼저, 선택된 정보 출력
    language = info.get("언어", "알 수 없음")
    travel_preference = info.get("여행 성향", "알 수 없음")

    st.write(f"""📅 선택한 날짜: {year}년 {month}월  
            🌍 선택한 국가: {selected_country}  
            🗣 언어: {language}  
            🏝 여행 성향: {travel_preference} * **여행 성향 분석은 예시 입니다.**  
            👥 입국 예상 인원: {expected_visitors:,} 명  
            🎉 선택 테마: {selected_travel}  
            테마 지역: {selected_location}""")

    # 🔹 위치 정보가 없을 경우 → 경고 메시지 출력 후 종료
    if not province and not city:
        st.warning("❌ 올바른 여행 지역 정보가 없습니다. Festival, Seasons 메뉴에서 테마를 선택하면 해당 지역 관광지를 알려드립니다.")
        return
    if not year :
        st.warning("❌ 날짜 선택이 되지 않았어요. 이전 메뉴에서 날짜를 선택하면 해당 지역 관광지를 알려드립니다.")
        return

    # 🔹 관광지 검색 시작
    st.subheader(f"📍 {province} {city} 인근 관광지 검색 결과")
    places = search_tourist_spots("관광지", f"{province} {city}", display=10)
    tourist_spots = filter_tourist_spots(places)

    # 🔹 관광지 정보가 있을 경우 출력
    if tourist_spots:
        st.success(f"🔎 {province} {city}에서 {len(tourist_spots)}개의 관광지를 찾았습니다.")
        
        # 🔹 카카오 지도 표시
        st.subheader("🗺 카카오 지도에서 관광지 확인")
        map_html = generate_kakao_map(tourist_spots)
        
        components.html(map_html, height=500, scrolling=False)

        # 🔹 개별 관광지 정보 출력 (Expander)
        for idx, place in enumerate(tourist_spots):
            with st.expander(f"📍 {place['place_name']} (자세히 보기)"):
                st.write(f"📍 **주소:** {place['road_address_name'] or place['address_name']}")
                st.write(f"📞 **전화번호:** {place['phone'] if place['phone'] else '없음'}")
                st.write(f"🏷 **카테고리:** {place['category_name']}")
                
                # 🔹 카카오 지도에서 보기 버튼 추가
                map_url = f"https://map.kakao.com/link/map/{place['id']}"
                st.markdown(f"[📍 카카오 지도에서 보기]({map_url})", unsafe_allow_html=True)

    else:
        st.warning("🔍 해당 지역에서 관광지를 찾을 수 없습니다.")
