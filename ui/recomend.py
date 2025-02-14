import streamlit as st
import requests
import openai

# ✅ ChatGPT API 호출 (사용자가 원하는 여행 스타일 분석)
def ask_chatgpt(user_prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-2",  # ChatGPT 2 사용 가능
        messages=[{"role": "system", "content": "당신은 여행 일정 추천 전문가입니다."},
                  {"role": "user", "content": user_prompt}],
        temperature=0.7
    )
    st.write(response)
    return response.choices[0].message.content


# ✅ Google Maps API로 거리 계산
def get_distance(origin, destination):
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}"
    response = requests.get(url).json()
    return response["rows"][0]["elements"][0]["distance"]["text"]


def run_ask():
# ✅ Streamlit UI 설정
    st.title("📍 AI 여행 일정 추천 시스템")

    # ✅ 사용자 입력
    user_input = st.text_input("여행 계획을 입력하세요", "서울 불꽃 축제에 가고 싶은데, 근처 관광지도 포함해서 일정을 추천해줘.")

    if st.button("여행 일정 추천받기"):
        # ✅ ChatGPT 2에게 요청
        itinerary = ask_chatgpt(user_input)
        st.subheader("📌 추천 일정")
        st.write(itinerary)

        # ✅ 이동 거리 계산 예제
        origin = "경복궁, 서울"
        destination = "남산타워, 서울"
        distance = get_distance(origin, destination)
        
        st.subheader("🚗 이동 거리 계산")
        st.write(f"{origin} → {destination}: {distance}")