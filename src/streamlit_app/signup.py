import streamlit as st
import json
import requests
import logging

def add_user(new_user, new_password):
    try:
        payload = {'username': new_user, 'password': new_password}
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://127.0.0.1:5000/register', data=json.dumps(payload), headers=headers)
        if response.status_code == 201:
            return True
        else:
            return False
    except (requests.exceptions.RequestException, Exception) as e:
        logging.error(f"An error occurred: {str(e)}")
        return False

def signup_page():
    st.subheader("Create New Account 🌱")
    new_user = st.text_input("Username 👤")
    new_password = st.text_input("Password 🔑", type='password')
    confirm_password = st.text_input("Confirm Password 🔑", type='password')
    if st.button("Signup 🌟"):
        if new_password == confirm_password:
            response = add_user(new_user, new_password)
            if response:
                st.success("You have successfully created an account ✅")
                st.info("Go to Login Menu to login 🔑")
            else:
                st.warning("Error while creating user account")
        else:
            st.warning("Password do not match !")
