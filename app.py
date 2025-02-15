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

# ✅ 세션 상태가 변경되었을 경우 먼저 처리 (가장 먼저 실행)
if st.session_state["next_page"] is not None:
    st.session_state["current_page"] = st.session_state["next_page"]
    st.session_state["next_page"] = None  # ✅ 한 번 반영 후 초기화
    st.rerun()  # ✅ 즉시 새로고침하여 반영

def main():
    menu = ["Home", "Country", "Festival", "Seasons", "TouristSpot", "About", "Ask"]

    with st.sidebar:
        # ✅ default_index를 session_state["current_page"] 값과 동기화
        default_index = menu.index(st.session_state["current_page"]) if st.session_state["current_page"] in menu else 0
        choice = option_menu("Menu", menu,
                            icons=['house', 'kanban', 'bi bi-robot', 'bi bi-airplane', 'bi bi-binoculars'],
                            menu_icon="app-indicator",
                            default_index=default_index,
                            styles={
                                "container": {"padding": "4!important", "background-color": "#fafafa"},
                                "icon": {"color": "black", "font-size": "25px"},
                                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#fafafa"},
                                "nav-link-selected": {"background-color": "#08c7b4"},
                            })

    # ✅ 선택한 메뉴와 session_state["current_page"]를 동기화
    if choice != st.session_state["current_page"]:
        print(f"🌍 현재 선택된 페이지 변경됨: {st.session_state['current_page']} → {choice}")  
        st.session_state["current_page"] = choice
        st.rerun()  # ✅ 즉시 새로고침

    # ✅ 현재 페이지 상태 디버깅 출력
    st.write(f"🌍 현재 페이지: {st.session_state['current_page']}")  

    # ✅ 세션 상태에 따라 페이지 실행
    if st.session_state["current_page"] == menu[0]:
        run_home()
    elif st.session_state["current_page"] == menu[1]:
        run_country()
    elif st.session_state["current_page"] == menu[2]:
        run_festival()
    elif st.session_state["current_page"] == menu[3]:
        run_seasons()   
    elif st.session_state["current_page"] == menu[4]:
        run_tourist_spots()
    elif st.session_state["current_page"] == menu[5]:
        run_about()
    elif st.session_state["current_page"] == menu[6]:
        run_ask()

if __name__ == '__main__':
    main()
