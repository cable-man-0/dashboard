import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests

# Define a function to load data from CSV file with caching
@st.cache_data()
def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    df = df.bfill().dropna()  # Preprocess the data once
    return df

# Define a function to detect anomalies with caching

def detect_anomalies(data, algorithm, thresholds=None):
    if thresholds is None:
        thresholds = {}
    response = requests.post('http://127.0.0.1:5000/detect_anomalies', json={'data': data.to_dict(orient='list'), 'thresholds': thresholds, 'algorithm': algorithm})
    return response

# Define a function to validate login credentials
def authenticate(username,password):
    response = requests.post('http://127.0.0.1:5000/authenticate', json={'username': username, 'password': password})
    if response.ok:
        return response.json()['authenticated']
    return False
# Define a function to register a new user
def register(username, password):
    response = requests.post('http://127.0.0.1:5000/register', json={'username': username, 'password': password})
    return response.ok

# Main function
def main():
    # Set page title and icon
    st.set_page_config(page_title="Anomaly Detection App", page_icon="🔍")
        
    # Title and description
    st.title("Anomaly Detection App")
        
    # Check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Login section
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.success("Logged in successfully!")
            st.session_state.authenticated = True
        else:
            st.error("Invalid username or password.")
            st.session_state.authenticated = False

    # Registration section
    st.subheader("Register")
    register_username = st.text_input("Create a Username")
    register_password = st.text_input("Create a Password", type="password")
    register_button = st.button("Register")

    if register_button:
        if register(register_username, register_password):
            st.success("Registered successfully!")
        else:
            st.error("Registration failed.")

    if st.session_state.authenticated:   
            # Load Style css
        with open('/home/teemo/Desktop/pfe/env/src/streamlit/src/style/style.css') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        # Upload CSV dataset
        st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")
        uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])

        # Check if a file has been uploaded
        if uploaded_file is not None:
            # Load CSV dataset
            df = load_data(uploaded_file)
            
            # Dsplay dataset
            st.subheader("Dataset")
            st.write(df)  # Display the dataset
            
            # Sidebar for user interaction
            st.sidebar.title("Settings")
            
            # Select graph type
            graph_type = st.sidebar.selectbox("Select Graph Type", ["Line Chart", "Scatter Plot"])
            algorithm = st.sidebar.selectbox("Select Anomaly Detection Algorithm", ["isolation_forest","SVM","DBSCAN"])
            selected_features = st.sidebar.multiselect("Select Features for Anomaly Detection", df.columns.tolist())
            
            if algorithm == "isolation_forest":
                thresholds = {}
                for feature in selected_features:
                    thresholds[feature] = st.sidebar.slider(f"Threshold for {feature}", min_value=0.0, max_value=100.0, value=50.0)    
            
            # Confirm button
            if st.sidebar.button("Confirm"):
                if selected_features:
                    data = df[selected_features]  # Use selected features directly
                    
                    if algorithm == "isolation_forest":
                        # Detect anomalies
                        response = detect_anomalies(data, algorithm, thresholds)
                    elif algorithm in ["DBSCAN", "SVM"]:
                        # Detect anomalies
                        response = detect_anomalies(data, algorithm)
                    
                    if response is not None and response.status_code == 200:
                        anomaly_indices = response.json()
                        if anomaly_indices:
                            st.info("Anomalies detected! See details below.")
                            #anomaly_data_points = df.loc[anomaly_indices]
                            st.subheader("Anomaly Data Points")
                            st.table(pd.DataFrame({'Index': [idx for idx in anomaly_indices if idx < 0]}))
                        else:
                            st.success("No anomalies detected.")
                    else:
                        st.error("An error occurred during anomaly detection.")
                    # Visualization based on selected graph type
                    for column in data.columns:
                        chart_placeholder = st.empty()
                        if graph_type == "Line Chart":
                            fig = px.line(data, x='date', y=column) if 'date' in data.columns else px.line(data, x=data.index, y=column)
                        elif graph_type == "Scatter Plot":
                            fig = px.scatter(data, x='date', y=column) if 'date' in data.columns else px.scatter(data, x=data.index, y=column)
                            
                        chart_placeholder.plotly_chart(fig)

# Run the ap
if __name__ == "__main__":
    main()