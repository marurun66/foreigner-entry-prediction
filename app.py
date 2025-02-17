import streamlit as st
from streamlit_option_menu import option_menu
from navigation import navigate_to  # ✅ `navigate_to()`를 별도 파일에서 가져옴

from ui.about import run_about
from ui.country import run_country
from ui.home import run_home
from ui.festival import run_festival
from ui.ai_planner import run_ai_planner
from ui.seasons import run_seasons
from ui.tourist_spots import run_tourist_spots

st.set_page_config(
    layout="wide",
    page_title="25,26년 해외관광객 대상 축제와 함께하는 여행 패키지 가이드",
    page_icon="🌍"
)

# ✅ 초기 페이지 설정
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# ✅ 페이지 실행 함수 매핑
page_mapping = {
    "Home": run_home,
    "Country": run_country,
    "Festival": run_festival,
    "Seasons": run_seasons,
    "TouristSpot": run_tourist_spots,
    "AI PLANNER": run_ai_planner,
    "About": run_about,
}

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

    # ✅ 사이드바에서 선택한 메뉴에 따라 이동
    if choice != st.session_state["current_page"]:
        navigate_to(choice)

    # ✅ 현재 페이지 실행
    page_mapping[st.session_state["current_page"]]() 

if __name__ == '__main__':
    main()
