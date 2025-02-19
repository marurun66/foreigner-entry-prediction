import streamlit as st
from streamlit_option_menu import option_menu
from navigation import navigate_to
from ui.about import run_about
from ui.ai_planner import run_ai_planner
from ui.country import run_country
from ui.home import run_home
from ui.festival import run_festival
from ui.seasons import run_seasons
from ui.tourist_spots import run_tourist_spots
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    layout="wide",
    page_title="사계절 축제와 함께하는 여행 패키지 가이드",
    page_icon="🌍",
)

# JavaScript 코드 수정
st.markdown("""
<script>
const sidebarMenu = window.parent.document.querySelector('.stSidebar');
if (sidebarMenu) {
    sidebarMenu.addEventListener('click', () => {
        setTimeout(() => {
            window.parent.scrollTo(0, 0);
        }, 100);
    });
}

const tabs = window.parent.document.querySelectorAll('.stTabs [data-baseweb="tab-list"] [role="tab"]')
const tabPanels = window.parent.document.querySelectorAll('.stTabs [data-baseweb="tab-panel"]')
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    setTimeout(() => {
      window.parent.scrollTo(0, 0)
    }, 100)
  })
})
</script>
""", unsafe_allow_html=True)

# CSS 스타일 추가
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
  position: sticky;
  top: 0;
  background: white;
  z-index: 1000;
}
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# 초기 페이지 설정
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# 페이지 실행 함수 매핑
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
        "AI PLANNER": "AI 플래너",
        "About": "정보",
    }

    with st.sidebar:
        default_index = (
            list(menu.keys()).index(st.session_state["current_page"])
            if st.session_state["current_page"] in menu
            else 0
        )
        choice = option_menu(
            "Menu",
            list(menu.keys()),
            icons=[
                "house",
                "globe",
                "calendar-event",
                "cloud-sun",
                "binoculars",
                "bi bi-chat-dots",
                "info-circle",
            ],
            menu_icon="app-indicator",
            default_index=default_index,
            styles={
                "container": {"padding": "4!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#fafafa",
                },
                "nav-link-selected": {"background-color": "#08c7b4"},
            },
        )

    # 사이드바에서 선택한 메뉴에 따라 이동
    if choice != st.session_state["current_page"]:
        navigate_to(choice)
        st.experimental_set_query_params()  # URL 파라미터 초기화
        st.experimental_rerun()  # 페이지 재실행

    # 현재 페이지 실행
    page_mapping[st.session_state["current_page"]]()

if __name__ == "__main__":
    main()