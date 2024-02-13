import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np                                              
import requests
import matplotlib.pyplot as plt
import logging
# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'last_page' not in st.session_state:
    st.session_state.last_page = 'Home 🏠'

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        df = df.bfill().dropna()
        return df
    except FileNotFoundError:
        st.error("Please upload a valid CSV file.")
        return None

# Define a function to detect anomalies with caching
def detect_anomalies(data, algorithm, **parameters):

    # Ensure data is converted to a dictionary suitable for JSON
    data_dict = data.to_dict(orient='list')

    try:
        # Remove unnecessary "thresholds" key from the payload since thresholds are no longer used
        payload = {'data': data_dict, 'algorithm': algorithm}
        payload.update(parameters)  # Add algorithm-specific parameters

        # Send the request to the backend server
        response = requests.post('http://127.0.0.1:5000/detect_anomalies', json=payload)

        # Return the response if successful
        response.raise_for_status()  # Raise an error for non-2xx status codes
        return response

    except (requests.exceptions.RequestException, Exception) as e:
        # Log the error for debugging
        logging.error(f"An error occurred: {str(e)}")
        return None


# Function to hash passwords
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Function to check hashes
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Database connection
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

# Create the table
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

# Add user data
def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()

# Login user
def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data

# Update user data
def update_userdata(username, new_password):
    c.execute('UPDATE userstable SET password = ? WHERE username = ?', (new_password, username))
    conn.commit()

# Streamlit UI
def main():
    st.markdown("<h1 style='text-align: center; color: blue;'>📄 Anomaly Detector 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Upload/Analyze/Detect</h3>", unsafe_allow_html=True)
    
    menu = ["Home 🏠", "Login 🔑", "SignUp 📝", "Detection 📊", "Settings ⚙️"]
    
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
        st.subheader("Welcome to Anomaly Detector! 🌟")
        st.info("with 1 click upload your data! 💼")
        st.info("""
        ## About Anomaly Detector 🚀
        
        **Anomaly Detector** 

        ### Features:
        - **feature 1**: 
        - **feature 2**: 
        - **feature 3**: 
        - **feature 4**:
        - **Email**: 
        - **LinkedIn**:
        - **GitHub**: 

        ### stay safe 🏆🚀
        """)
        st.session_state.last_page = choice

    elif choice == "Login 🔑":
        if st.session_state.logged_in:
            st.success(f"Already logged in as {st.session_state.username} 👋")
        else:
            st.subheader("Login Section 🔐")
            username = st.sidebar.text_input("User Name 👤")
            password = st.sidebar.text_input("Password 🔒", type='password')
            if st.sidebar.button("Login 🚪"):
                create_usertable()
                hashed_password = make_hashes(password)
                result = login_user(username, check_hashes(password, hashed_password))
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.last_page = "Detection 📊"
                    st.rerun()

    elif choice == "SignUp 📝":
        st.subheader("Create New Account 🌱")
        new_user = st.text_input("Username 👤")
        new_password = st.text_input("Password 🔑", type='password')
        if st.button("Signup 🌟"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created an account ✅")
            st.info("Go to Login Menu to login 🔑")

    elif choice == "Detection 📊":
        if st.session_state.logged_in:
    # Title and description
            st.title("Anomaly Detection")
            with open('/home/teemo/Desktop/pfe/env/src/streamlit/src/style/style.css') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

            st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

            # Check if a file has been uploaded
            if uploaded_file is not None:
                # Load CSV dataset
                df = load_data(uploaded_file)

                # Display dataset
                st.subheader("Dataset")
                st.write(df)  # Display the dataset

                # Sidebar for user interaction
                st.sidebar.title("Parameters")

                # Select graph type
                graph_type = st.sidebar.multiselect("Select Graph Type", ["Line Chart", "Scatter Plot"])
                algorithm = st.sidebar.selectbox("Select Anomaly Detection Algorithm", ["isolation_forest","SVM","DBSCAN"])
                selected_features = st.sidebar.multiselect("Select Features for Anomaly Detection", df.columns.tolist())

                parameters = {}
                if algorithm == "isolation_forest":
                    parameters["contamination"] = st.sidebar.slider(
                        "Contamination (outlier %)", min_value=0.0, max_value=0.5, value=0.1
                    )
                    parameters["n_estimators"] = st.sidebar.slider(
                        "Number of Trees", min_value=10, max_value=1000, value=100
                    )
                elif algorithm == "SVM":
                    parameters["kernel"] = st.sidebar.selectbox("Kernel", ["linear", "rbf"])
                    parameters["C"] = st.sidebar.slider("Regularization Parameter", min_value=0.1, max_value=100.0, value=1.0)
                elif algorithm == "DBSCAN":
                    parameters["eps"] = st.sidebar.slider(
                        "Epsilon (minimum distance)", min_value=0.0, max_value=1.0, value=0.5
                    )
                    parameters["min_samples"] = st.sidebar.slider(
                        "Minimum Samples", min_value=1, max_value=len(df), value=5
                    )

                # Confirm button
                if st.sidebar.button("Run Anomaly Detection"):
                    with st.spinner("Detecting anomalies..."):
                        data = df[selected_features]  # Use selected features directly
    
                        response = detect_anomalies(data, algorithm, **parameters)
    
                        if response is not None and response.status_code == 200:
                            anomaly_indices = response.json()
                            if anomaly_indices:
                                st.info("Anomalies detected! See details below.")
    
                                # Create a DataFrame with original indices and anomaly labels
                                anomaly_df = pd.DataFrame({'Index': range(len(df)), 'Anomaly': anomaly_indices})
    
                                # Filter for anomalies (indices less than 0) and display the table
                                st.subheader("Anomaly Data Points")
                                st.table(anomaly_df[anomaly_df['Anomaly'] < 0])
                            else:
                                st.success("No anomalies detected.")
                        else:
                            st.error("An error occurred during anomaly detection.")
                            st.toast("Please check the backend server and try again.")
    

                            # Determine the number of charts based on the length of graph_type
                        num_charts = len(graph_type)
                        # Create columns for multiple charts
                        chart_rows = st.columns(num_charts)
                        # Loop through graph_type and chart_rows simultaneously
                        for chart_type, chart_col in zip(graph_type, chart_rows):
                            # Loop through columns within each chart
                            for column in data.columns:
                                # Add space above the first chart in each subplot
                                if num_charts > 1 and chart_col is chart_rows[0]:
                                    chart_col.empty()
                                # Create chart based on type
                                if chart_type == "Line Chart":
                                    fig = px.line(data, x='date', y=column) if 'date' in data.columns else px.line(data, x=data.index, y=column)
                                elif chart_type == "Scatter Plot":
                                    fig = px.scatter(data, x='date', y=column) if 'date' in data.columns else px.scatter(data, x=data.index, y=column)
                                # Display chart and adjust layout (flexible layout recommended)
                                chart_col.plotly_chart(fig, use_container_width=True)  # Display directly within the loop


# Optional steps based on requirements:
        else:
            st.warning("Please login to access this feature 🔐")
    elif choice == "Settings ⚙️":
        if st.session_state.logged_in:
            st.subheader("Update Your Password 🔧")
            new_password = st.text_input("New Password 🔑", type='password')
            if st.button("Update 🔄"):
                update_userdata(st.session_state.username, make_hashes(new_password))
                st.success("Settings Updated Successfully ✅")
            st.session_state.last_page = choice
        else:
            st.warning("Please login to access this feature 🔐")
    # Contact Form
    with st.expander("Contact us"):
        with st.form(key='contact', clear_on_submit=True):
            email = st.text_input('Contact Email')
            st.text_area("Query",placeholder="Please fill in all the information or we may not be able to process your request")  
            submit_button = st.form_submit_button(label='Send Information')

if __name__ == '__main__':
    st.set_page_config(page_title="Anomaly Detector",
                       page_icon="✨", layout="centered", initial_sidebar_state="auto")
    main()