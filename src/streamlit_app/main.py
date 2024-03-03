import streamlit as st
from login import login_page
from signup import signup_page
from detection import detect
from pro import pro_page
from setting import settings_page
from home import show_home_page
# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'last_page' not in st.session_state:
    st.session_state.last_page = 'Home 🏠'

def main():
    st.markdown("<h1 style='text-align: center; color: blue;'>📄 Anomaly Detector 🚀</h1>", unsafe_allow_html=True)
    menu = ["Home 🏠", "Login 🔑", "SignUp 📝", "Detection 📊","pro 📊", "Settings ⚙️"]

    # Function to update the last page and rerun the app
    def update_page_and_rerun(new_page):
        st.session_state.last_page = new_page
        st.rerun()

    if st.session_state.logged_in:
        if st.session_state.last_page not in menu:
            st.session_state.last_page = 'Home 🏠'
        choice = st.sidebar.selectbox("Menu 📜", menu, index=menu.index(st.session_state.last_page))
        # Update and rerun if the page choice has changed
        if choice != st.session_state.last_page:
            update_page_and_rerun(choice)
    else:
        choice = st.sidebar.selectbox("Menu 📜", ["Home 🏠", "Login 🔑", "SignUp 📝"])
        if choice != st.session_state.last_page:
            update_page_and_rerun(choice)

    if choice == "Home 🏠":
        show_home_page()

    elif choice == "Login 🔑":
        login_page()

    elif choice == "SignUp 📝":
        signup_page()

    elif choice == "Detection 📊":
        detect()

    elif choice == "pro 📊":
        pro_page()

    elif choice == "Settings ⚙️":
        settings_page()

if __name__ == '__main__':
    st.set_page_config(page_title="Anomaly Detector",
                       page_icon="✨", layout="centered", initial_sidebar_state="auto")
    main()