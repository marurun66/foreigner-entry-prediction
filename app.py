import streamlit as st

from ui.about import run_about
from ui.eda import run_eda
from ui.home import run_home
from ui.prediction import run_prediction



def main():
    menu = ["Home", "EDA", "Prediction","About"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        run_eda()
    elif choice == menu[2]:
        run_prediction()
    elif choice == menu[3]:
        run_about()

if __name__ == '__main__':
    main()
