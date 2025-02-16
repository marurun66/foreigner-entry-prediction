import streamlit as st

def navigate_to(page):
    """페이지 이동 함수"""
    st.session_state["current_page"] = page
    st.rerun()
