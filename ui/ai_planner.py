import streamlit as st
from huggingface_hub import InferenceClient

# ✅ API 키 설정
HUGGING_FACE_READ_KEY = st.secrets["KAKAO_API_KEY"]

def run_ai_planner():
    client = InferenceClient(
        provider="hf-inference",
<<<<<<< HEAD
        api_key="" #readAPIKEY
=======
        api_key=HUGGING_FACE_READ_KEY #readAPIKEY
>>>>>>> c90580d (와우 실수)
    )

    messages = [
        {
            "role": "user",
            "content": "나는 한국 여행사의 직원입니다. 25년 4월 대만 손님을 위한 한국 여행 코스를 준비해야합니다. 대만 손님을 위해 사전에 준비하면 좋을 게 무엇인지 알려주세요. 전라남도 강진군 강진청자축제를 둘러보며, 가우도, 주작산자연휴양림, 덕룡산을 여행코스에 넣고 싶습니다. 고객이 한국에 입국해서 관광지들을 둘러보고, 귀국할 수 있는 여행 일정을 작성해주세요. 한글로 작성해주세요."
        }
    ]

    completion = client.chat.completions.create(
        model="google/gemma-2-9b-it", 
        messages=messages, 
        max_tokens=1024,
    )

    print(completion.choices[0].message)



def run_ai_planner():
    ## 🔹 이전 페이지에서 가져온 정보들
    year = st.session_state.get("year")
    month = st.session_state.get("month")
    selected_country = st.session_state.get("selected_country")
    info = st.session_state.get("info", {})  # 기본값 빈 딕셔너리
    expected_visitors = st.session_state.get("expected_visitors", "미정")  # 기본값 설정
    selected_travel = st.session_state.get("selected_travel", "축제,테마 정보 없음")
    selected_location = st.session_state.get("selected_location", "위치 정보 없음")
    selected_places = st.session_state.get("selected_places", [])
    pass
