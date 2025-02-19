import streamlit as st

def navigate_to(page):
    # 스크롤 리셋을 위한 JavaScript 코드
    st.markdown("""
    <script>
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

    # 탭 메뉴 고정을 위한 CSS
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
    position: sticky;
    top: 0;
    background: white;
    z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

    """페이지 이동 함수"""
    st.session_state["current_page"] = page
    st.rerun()
