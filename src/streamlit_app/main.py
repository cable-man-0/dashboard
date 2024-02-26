import streamlit as st
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import logging
import os
from sklearn.preprocessing import StandardScaler 
from joblib import load
import altair as alt
import json
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
@st.cache_resource
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


# Streamlit UI
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
        st.subheader("Welcome to Anomaly Detector! 🌟")
        st.info("""
        ## About Anomaly Detector 🚀

         

        Anomaly Detector is a web application that allows you to upload CSV datasets, analyze them, and detect anomalies.
        It provides various anomaly detection algorithms such as Isolation Forest, SVM, and DBSCAN.
            
            ### Features:
            - Upload and analyze CSV datasets
            - Choose features for anomaly detection
            - Set thresholds for anomaly detection
            - Select from multiple graph types for visualization
            - Supports Isolation Forest, SVM, and DBSCAN algorithms
            - User authentication and account management
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
                #hashed_password = make_hashes(password)
                result = login_user(username, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.last_page = "Detection 📊"
                    st.rerun()
                else:
                    st.warning("Invalid username or password.")

    elif choice == "SignUp 📝":
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
                    st.warning("error while creating user account")
            else:
                ("Password do not match !")

    elif choice == "Detection 📊":
        if st.session_state.logged_in:
            st.title("Anomaly Detection")
            st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

            if uploaded_file is not None:
                df = load_data(uploaded_file)

                st.subheader("Dataset")
                st.write(df)

                st.sidebar.title("Parameters")

                graph_type = st.sidebar.multiselect("Select Graph Type", ["Line Chart", "Scatter Plot"])
                algorithm = st.sidebar.selectbox("Select Anomaly Detection Algorithm", ["isolation_forest", "SVM", "DBSCAN"])
                selected_features = st.sidebar.multiselect("Select Features for Anomaly Detection", [col for col in df.columns.tolist() if col != "date"], default=None)
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

                                st.subheader("Anomaly Data Points")
                                st.table(anomaly_df[anomaly_df['Anomaly'] < 0])
                            else:
                                st.success("No anomalies detected.")
                        else:
                            st.error("An error occurred during anomaly detection.")
                            st.toast("Please check the backend server and try again.")

                        # Display charts
                        num_charts = len(graph_type)
                        chart_rows = st.columns(num_charts)

                        for chart_type, chart_col in zip(graph_type, chart_rows):
                            # Loop through columns within each chart
                            for column in selected_features:
                                # Determine the x-axis variable based on the presence of 'date' column
                                x = 'date' if 'date' in df.columns else None

                                # Create the appropriate chart using px.line or px.scatter
                                if chart_type == "Line Chart":
                                    if x:
                                        fig = px.line(df, x=x, y=column, title="Line Chart")
                                    else:
                                        fig = px.line(df, y=column, title="Line Chart")
                                elif chart_type == "Scatter Plot":
                                    if x:
                                        fig = px.scatter(df, x=x, y=column, title="Scatter Plot")
                                    else:
                                        fig = px.scatter(df, y=column, title="Scatter Plot")

                                # Display the chart
                                st.plotly_chart(fig)

                                # Add space above the first chart in each row only (avoid unnecessary repetition)
                                if chart_col.index == 0:
                                    chart_col.write("")   # Create an empty space
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

    elif choice == "pro 📊":
        if st.session_state.logged_in:
            st.subheader("Inspect Your Data Flow")
            st.write("Upload a CSV dataset")
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

            if uploaded_file is not None:
                # Load the CSV data into a DataFrame
                new_test_data = pd.read_csv(uploaded_file)

                # Define feature columns
                X_columns = [
                    'IAT', 'rst_count', 'urg_count', 'flow_duration', 'Variance', 'Duration', 'Header_Length', 'Number', 'Weight', 'Rate']

                if st.button("Launch"):
                    model_34_classes = load("newRandomForest_model_34_classes.joblib")
                    model_8_classes = load("newRandomForest_model_8_classes.joblib")
                    model_2_classes = load("newRandomForest_model_2_classes.joblib")
                    # Standardize the data
                    scaler = StandardScaler()
                    scaler.fit(new_test_data[X_columns])
                    new_test_data[X_columns] = scaler.transform(new_test_data[X_columns])

                    # Make predictions using the trained model
                    predictions_34_classes = model_34_classes.predict(new_test_data[X_columns])
                    predictions_8_classes = model_8_classes.predict(new_test_data[X_columns])
                    predictions_2_classes = model_2_classes.predict(new_test_data[X_columns])

                    # Add predictions to DataFrame
                    new_test_data['predictions_2'] = predictions_2_classes
                    new_test_data['predictions_34'] = predictions_34_classes
                    new_test_data['predictions_8'] = predictions_8_classes
                    

                    # Display predictions
                    st.write(new_test_data)

                    # Additional data visualization or insights
                    chart_data = new_test_data['predictions_2'].value_counts().reset_index()
                    chart_data.columns = ['Predicted Class', 'Count']
                    chart = alt.Chart(chart_data).mark_bar().encode(x='Predicted Class',y='Count')
                    st.altair_chart(chart, use_container_width=True)

                    chart_data = new_test_data['predictions_8'].value_counts().reset_index()
                    chart_data.columns = ['Predicted Class', 'Count']
                    chart = alt.Chart(chart_data).mark_bar().encode(x='Predicted Class',y='Count')
                    st.altair_chart(chart, use_container_width=True)

                    chart_data = new_test_data['predictions_34'].value_counts().reset_index()
                    chart_data.columns = ['Predicted Class', 'Count']
                    chart = alt.Chart(chart_data).mark_bar().encode(x='Predicted Class',y='Count')
                    st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Please login to access this feature 🔐")


if __name__ == '__main__':
    st.set_page_config(page_title="Anomaly Detector",
                       page_icon="✨", layout="centered", initial_sidebar_state="auto")
    main()