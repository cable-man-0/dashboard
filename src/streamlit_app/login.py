import streamlit as st
import json
import requests
import logging

def login_user(username, password):
    try:
        payload = {'username': username, 'password': password}
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://127.0.0.1:5000/login', data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except (requests.exceptions.RequestException, Exception) as e:
        logging.error(f"An error occurred: {str(e)}")
        return False
    
def login_page():
    if st.session_state.logged_in:
        st.success(f"Already logged in as {st.session_state.username} 👋")
    else:
        st.subheader("Login Section 🔐")
        username = st.sidebar.text_input("User Name 👤")
        password = st.sidebar.text_input("Password 🔒", type='password')
        if st.sidebar.button("Login 🚪"): 
            #hashed_password = make_hashes(password)
            result = login_user(username, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.last_page = "Detection 📊"
                st.rerun()
            else:
                st.warning("Invalid username or password.")
