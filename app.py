import streamlit as st
from streamlit_option_menu import option_menu

from ui.about import run_about
from ui.country import run_country
from ui.home import run_home
from ui.festival import run_festival
from ui.recomend import run_ask
from ui.seasons import run_seasons
from ui.tourist_spots import run_tourist_spots

st.set_page_config(
    layout="wide",
    page_title="25,26년 해외관광객 대상 축제와 함께하는 여행 패키지 가이드",
    page_icon="🌍"
)

# ✅ 초기 세션 상태 설정
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"
if "next_page" not in st.session_state:
    st.session_state["next_page"] = None  # ✅ 초기화
if "force_rerun" not in st.session_state:
    st.session_state["force_rerun"] = False  # ✅ 강제 새로고침 플래그 초기화

# ✅ next_page 감지 후 즉시 반영
if st.session_state.get("next_page") is not None:
    st.session_state["current_page"] = st.session_state["next_page"]
    st.session_state["next_page"] = None  # ✅ `next_page` 초기화
    st.session_state["force_rerun"] = True  # ✅ 강제 새로고침 플래그 설정
    st.rerun()

# ✅ force_rerun이 설정되었으면 강제 새로고침 실행
if st.session_state.get("force_rerun"):
    st.session_state["force_rerun"] = False
    print("📌 [DEBUG] 강제 새로고침 실행!")
    st.rerun()

# ✅ 디버깅 정보 출력
st.write("🔍 **[디버그 정보]**")
st.write(f"현재 페이지: {st.session_state.get('current_page')}")
print(f"📌 디버그: 현재 페이지: {st.session_state.get('current_page')}")

def main():
    menu = {
        "Home": "홈",
        "Country": "국가별 입국 예측",
        "Festival": "축제 정보",
        "Seasons": "계절별 여행지",
        "TouristSpot": "관광지 추천",
        "About": "정보",
        "Ask": "문의"
    }

    with st.sidebar:
        default_index = list(menu.keys()).index(st.session_state["current_page"]) if st.session_state["current_page"] in menu else 0
        choice = option_menu(
            "Menu", list(menu.keys()),
            icons=['house', 'globe', 'calendar-event', 'cloud-sun', 'binoculars', 'info-circle', 'question-circle'],
            menu_icon="app-indicator",
            default_index=default_index,
            styles={
                "container": {"padding": "4!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#fafafa"},
                "nav-link-selected": {"background-color": "#08c7b4"},
            }
        )

    # ✅ 선택한 메뉴와 session_state["current_page"]를 동기화
    if choice != st.session_state["current_page"]:
        st.session_state["next_page"] = choice
        print(f"🌍 메뉴에서 선택한 페이지: {choice}")  # ✅ 터미널 디버깅
        st.rerun()  # ✅ 즉시 새로고침하여 반영

    # ✅ 페이지 실행 함수 매핑
    page_mapping = {
        "Home": run_home,
        "Country": run_country,
        "Festival": run_festival,
        "Seasons": run_seasons,
        "TouristSpot": run_tourist_spots,
        "About": run_about,
        "Ask": run_ask
    }

    # ✅ 현재 페이지 실행
    page_mapping[st.session_state["current_page"]]() 

if __name__ == '__main__':
    main()
