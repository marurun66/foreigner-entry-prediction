from huggingface_hub import InferenceClient
import streamlit as st
import csv
from io import StringIO
from navigation import navigate_to

HUGGING_FACE_READ_KEY = st.secrets["HUGGING_FACE_READ_KEY"]


def get_user_selection():
    """세션 상태에서 유저가 선택한 정보 가져오기"""
    return {
        "year": st.session_state.get("year", 2025),
        "month": st.session_state.get("month", 4),
        "selected_country": st.session_state.get("selected_country", "대만"),
        "info": st.session_state.get("info", {}),
        "selected_travel": st.session_state.get(
            "selected_travel", "축제,테마 정보 없음"
        ),
        "selected_location": st.session_state.get(
            "selected_location", "위치 정보 없음"
        ),
        "selected_places": st.session_state.get("selected_places", []),
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
    info, selected_travel, selected_location, selected_places = (
        user_selection["info"],
        user_selection["selected_travel"],
        user_selection["selected_location"],
        user_selection["selected_places"],
    )
    language = info.get("언어", "알 수 없음")
    travel_preference = info.get("여행 성향", "알 수 없음")

    # ✅ AI에게 보낼 프롬프트 생성
    prompt = f"""
    나는 한국 여행사의 직원입니다. 
    {year}년 {month}월 {selected_country} 손님을 위한 한국 여행 코스를 준비해야 합니다. 
    {language} 언어를 사용하는 {selected_country} 손님을 위해 사전에 준비하면 좋을 게 무엇인지 알려주세요.
    {selected_travel}를 중심으로 {selected_location}을 방문하며, 
    다음 관광지를 여행 코스에 포함하려고 합니다 (다음 관광지 중 "호텔", "숙소", "펜션", "리조트"에서는 숙박합니다. 숙박지에 대해서도 작성해주세요.): {", ".join(selected_places)}.
    
    고객이 한국에 입국해서 관광지들을 둘러보고, 귀국할 수 있는 여행 일정을 작성해주세요.
    또한, {travel_preference} 성향의 {selected_country} 고객에게 이 여행에서 어떤 부분이 어필될지도 작성해주세요.
    
    한글로 작성해주세요.
    """

    # ✅ LLM에게 요청 보내기
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="google/gemma-2-9b-it",
        messages=messages,
        max_tokens=1024,
    )

    # ✅ 응답 결과 반환
    return completion.choices[0].message["content"]


def save_travel_plan_to_csv(travel_plan, filename):
    """여행 계획을 CSV 파일로 저장"""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["여행 일정"])
    writer.writerow([travel_plan])
    return output.getvalue()


def run_ai_planner():
    """AI 여행 플래너 실행"""
    user_selection = get_user_selection()

    # ✅ 선택된 관광지가 없을 경우 안내 메시지 출력 후 종료
    if not user_selection["selected_places"]:
        st.warning(
            """🚨 해당 메뉴에서는 외국인 관광객, 여행 날짜, 여행 지역 정보를 바탕으로 AI와 함께 여행 일정을 계획할 수 있습니다.  
                Country 메뉴부터 시작해주세요.😉"""
        )
        if st.button("➡ Country메뉴로 이동"):
            navigate_to("Country")
        return

    st.title("🤖 AI 여행 플래너")
    st.write(
        """
    ✨ AI가 선택한 정보를 기반으로 맞춤형 여행 일정을 생성합니다.  
    아래 버튼을 클릭하면 AI가 여행 코스를 추천해줍니다! 🚀
    """
    )

    # ✅ AI 여행 일정 생성 버튼
    if st.button("🚀 AI 여행 패키지 생성하기"):
        with st.spinner("AI가 여행 일정을 생성 중입니다... ⏳"):
            travel_plan = generate_ai_travel_plan(user_selection)

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

    # ✅ 세션 초기화 감지 후 실행
    if st.session_state.get("reset"):
        st.session_state.clear()  # 세션 초기화
        st.session_state["reset"] = False  # 다시 초기화 방지
        st.experimental_rerun()  # 앱 새로고침
