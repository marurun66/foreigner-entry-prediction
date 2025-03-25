from huggingface_hub import InferenceClient
import streamlit as st
import csv
from io import StringIO
from navigation import navigate_to

HUGGING_FACE_READ_KEY = st.secrets["HUGGING_FACE_READ_KEY"]


def get_user_selection():
    """세션 상태에서 유저가 선택한 정보 가져오기"""
    
    # ✅ 리스트로 저장된 경우, 딕셔너리로 변환 (예외 처리)
    if isinstance(st.session_state.get("selected_tourist_spots", {}), list):
        st.session_state.selected_tourist_spots = {
            place: "일반 관광지" for place in st.session_state.selected_tourist_spots
        }
    
    if isinstance(st.session_state.get("selected_hotels", {}), list):
        st.session_state.selected_hotels = {
            hotel: "숙박 시설" for hotel in st.session_state.selected_hotels
        }

    return {
        "year": st.session_state.get("year", 2025),
        "month": st.session_state.get("month", 4),
        "selected_country": st.session_state.get("selected_country", "대만"),
        "info": st.session_state.get("info", {}),
        "selected_travel": st.session_state.get("selected_travel", "축제,테마 정보 없음"),
        "selected_location": st.session_state.get("selected_location", "위치 정보 없음"),
        "selected_tourist_spots": st.session_state.get("selected_tourist_spots", {}),
        "selected_hotels": st.session_state.get("selected_hotels", {}),
    }



def generate_ai_travel_plan(user_selection):
    """AI에게 여행 패키지 생성을 요청하고 결과를 반환"""
    client = InferenceClient(provider="hf-inference", api_key=HUGGING_FACE_READ_KEY)

    # ✅ 유저 선택 정보 할당
    year, month, selected_country = (
        user_selection["year"],
        user_selection["month"],
        user_selection["selected_country"],
    )
    info, selected_travel, selected_location = (
        user_selection["info"],
        user_selection["selected_travel"],
        user_selection["selected_location"],
    )
    selected_tourist_spots = user_selection["selected_tourist_spots"]
    selected_hotels = user_selection["selected_hotels"]

    language = info.get("언어", "알 수 없음")
    travel_preference = info.get("여행 성향", "알 수 없음")

    # ✅ AI에게 보낼 프롬프트 생성
    prompt = f"""
    나는 한국 여행사의 직원입니다. 
    {year}년 {month}월 {selected_country} 손님을 위한 한국{selected_location} 여행 코스를 준비해야 합니다. 
    {language} 언어를 사용하는 {selected_country} 손님을 위해 사전에 준비하면 좋을 것이 무엇인지 알려주세요.
    이동은 우리 여행사 제공 버스로 이동합니다.
    이번 여행은 {selected_travel}를 중심으로 진행되며, 주요 방문지는 다음과 같습니다.

    ### 1. 숙박지 (호텔/펜션/리조트)
    다음 장소에서 숙박이 이루어집니다.
    - {", ".join([f"{hotel} ({category})" for hotel, category in selected_hotels.items()])}

    ### 2. 관광지
    다음 관광지를 방문할 예정입니다. 각 장소의 매력과 해당 국가 고객에게 어필할 만한 포인트를 설명해주세요.

    - {", ".join([f"{spot} ({category})" for spot, category in user_selection["selected_tourist_spots"].items()])}


    고객이 한국에 입국해서 {selected_location}의 관광지를 둘러보고, 귀국하는 전체 여행 일정을 작성해주세요.
    또한, {travel_preference} 성향의 {selected_country} 고객에게 이 여행에서 어떤 부분이 어필될지도 작성해주세요.

    한글로 작성해주세요.
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "system", "content": "당신은 여행 전문가입니다. 한글로, 꼼꼼하게 작성해주세요."},
    ]

    try:
        completion = client.chat.completions.create(
            model="google/gemma-2-9b-it",
            messages=messages,
            max_tokens=1024,
        )
        return completion.choices[0].message["content"]
    
    except Exception as e:
        # 스트림릿에 경고 메시지 출력
        st.warning("⚠️ AI 여행 일정을 생성하는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
        print(f"[ERROR] AI 호출 실패: {e}")
        return None


def save_travel_plan_to_csv(travel_plan, filename):
    """여행 계획을 CSV 파일로 저장"""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["여행 일정"])
    writer.writerow([travel_plan])
    return output.getvalue()


def run_ai_planner():
    """AI 여행 플래너 실행"""
    st.title("🤖 AI 여행 플래너")
    user_selection = get_user_selection()

    # ✅ 선택된 관광지 및 숙박지가 없을 경우 안내 메시지 출력 후 종료
    if not user_selection["selected_tourist_spots"] and not user_selection["selected_hotels"]:
        st.warning(
            """🚨 해당 메뉴에서는 외국인 관광객, 여행 날짜, 여행 지역 정보를 바탕으로 AI와 함께 여행 일정을 계획할 수 있습니다.  
                Country 메뉴부터 시작해주세요.😉"""
        )
        if st.button("➡ Country메뉴로 이동"):
            navigate_to("Country")
        return

    st.write(
        """
    ✨ AI가 선택한 정보를 기반으로 맞춤형 여행 일정을 생성합니다.  
    아래 버튼을 클릭하면 AI가 여행 코스를 추천해줍니다! 🚀
    """
    )

    # ✅ AI 여행 일정 생성 버튼
    if st.button("🚀 AI 여행 패키지 생성하기"):
        with st.spinner("AI가 여행 일정을 생성 중입니다... ⏳"):
            travel_plan = generate_ai_travel_plan(user_selection)  # ✅ 수정된 함수 적용

        # ✅ AI가 생성한 여행 패키지 표시
        st.subheader("📌 AI 추천 여행 일정")
        st.write(travel_plan)

        # ✅ 다운로드 버튼이 클릭되었는지 확인하는 변수 추가
        if "download_clicked" not in st.session_state:
            st.session_state["download_clicked"] = False
        if "reset" not in st.session_state:
            st.session_state["reset"] = False  # 초기화 변수 추가

        filename = f"{user_selection['selected_country']}고객을_위한_{user_selection['year']}년{user_selection['month']}월_{user_selection['selected_travel']}_여행계획서.csv"
        csv_data = save_travel_plan_to_csv(travel_plan, filename)

        # ✅ CSV 파일 저장 기능 추가
        if st.download_button(
            label="📥 여행 일정 CSV 다운로드",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
        ):
            # ✅ 세션 초기화 플래그 설정
            st.session_state["reset"] = True

        else:
            st.info("AI 일정 생성이 실패했기 때문에 다운로드는 불가능합니다. 😢")

    # ✅ 세션 초기화 감지 후 실행
    if st.session_state.get("reset"):
        st.session_state.clear()  # 세션 초기화
        st.session_state["reset"] = False  # 다시 초기화 방지
        st.experimental_rerun()  # 앱 새로고침
