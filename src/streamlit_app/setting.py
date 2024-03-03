import streamlit as st
import requests
import logging
import json

def update_userdata(username, new_hashed_password):
    try:
        payload = {'username': username, 'password': new_hashed_password}
        headers = {'Content-Type': 'application/json'}
        response = requests.put('http://127.0.0.1:5000/update_user', data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except (requests.exceptions.RequestException, Exception) as e:
        logging.error(f"An error occurred: {str(e)}")
        return False

def settings_page():
    if st.session_state.logged_in:
            st.subheader("Update Your Password 🔧")
            new_password = st.text_input("New Password 🔑", type='password')
            if st.button("Update 🔄"):
                update_userdata(st.session_state.username, new_password)
                st.success("Settings Updated Successfully ✅")
            st.session_state.last_page = choice
    else:
        st.warning("Please login to access this feature 🔐")
