import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import logging
import os
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

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
    
@st.cache_resource
def predict_2_classes(data):
    data_dict = data.to_dict(orient='list')
    try:
        # Remove unnecessary "thresholds" key from the payload since thresholds are no longer used
        payload = {'data': data_dict}

        # Send the request to the backend server
        predictions = requests.post('http://127.0.0.1:5000/predict_2_classes', json=payload)

        # Return the response if successful
        predictions.raise_for_status()  # Raise an error for non-2xx status codes
        return predictions

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
def init_database():
    if not os.path.exists('data.db'):
        conn = sqlite3.connect('data.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
        conn.commit()
        conn.close()

init_database()

# Create the table
def create_usertable():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

# Add user data
def add_userdata(username, password):
    conn = sqlite3.connect('data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

# Login user
def login_user(username, password):
    conn = sqlite3.connect('data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# Update user data
def update_userdata(username, new_password):
    conn = sqlite3.connect('data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE userstable SET password = ? WHERE username = ?', (new_password, username))
    conn.commit()
    conn.close()

# Streamlit UI
def main():
    st.markdown("<h1 style='text-align: center; color: blue;'>📄 Anomaly Detector 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Upload/Analyze/Detect</h3>", unsafe_allow_html=True)

    menu = ["Home 🏠", "Login 🔑", "SignUp 📝", "Detection 📊","pro 📊", "Settings ⚙️"]

    # Function to update the last page and rerun the app
    def update_page_and_rerun(new_page):
        st.session_state.last_page = new_page
        st.experimental_rerun()

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
        - **Email**: [example@email.com](mailto:example@email.com)
        - **LinkedIn**: [linkedin.com/in/yourprofile](http://linkedin.com/in/yourprofile)
        - **GitHub**: [github.com/yourusername](http://github.com/yourusername)

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
                result = login_user(username, hashed_password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.last_page = "Detection 📊"
                    st.experimental_rerun()
                else:
                    st.warning("Invalid username or password.")

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
            st.subheader("Keep your data safe")
            st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
            if uploaded_file is not None:
                # Load the CSV data into a DataFrame
                data = pd.read_csv("test.csv")
    
                # Convert DataFrame to list of dictionaries
                data_json = data.to_dict(orient="records")
    
                # Send a POST request to the Flask app
                url = "http://127.0.0.1:5000/predict_2_classes"  # Change the URL based on your endpoint
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json=data_json, headers=headers)
    
                # Log the response
                logging.info(response.json())
        else:
            st.warning("Please login to access this feature 🔐")

            '''
                predictions = predict_2_classes(df)  # Assuming 'model' is your trained Decision Tree model

                # For example, you can create a new DataFrame with the original data and the predicted labels
                results = pd.DataFrame({'Index': range(len(df)), 'Predicted_Label': predictions})

                # Display the table
                st.subheader("Prediction Results")
                st.table(results)

                # Save the results to a new CSV file
                results.to_csv("predictions.csv", index=False)
            '''
        

    # Contact Form
    with st.expander("Contact us"):
        with st.form(key='contact', clear_on_submit=True):
            email = st.text_input('Contact Email')
            query = st.text_area("Query", placeholder="Please fill in all the information or we may not be able to process your request")
            submit_button = st.form_submit_button(label='Send Information')
            if submit_button:
                st.success("Your query has been submitted. We will get back to you soon.")

if __name__ == '__main__':
    st.set_page_config(page_title="Anomaly Detector",
                       page_icon="✨", layout="centered", initial_sidebar_state="auto")
    main()