import streamlit as st

from ui.about import run_about
from ui.eda import run_eda
from ui.home import run_home
from ui.festival import run_festival
from ui.recomend import run_ask



def main():
    st.set_page_config(layout="wide")
    menu = ["Home", "EDA", "Festival","About","Ask"]
    choice = st.sidebar.radio("Menu", menu)
    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        run_eda()
    elif choice == menu[2]:
        run_festival()
    elif choice == menu[3]:
        run_about()
    elif choice == menu[4]:
        run_ask()

if __name__ == '__main__':
    main()
