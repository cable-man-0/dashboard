import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests

# Function to detect anomalies based on thresholds for each feature
def detect_anomalies(data, thresholds):
    anomalies = pd.DataFrame()
    for column, threshold in thresholds.items():
        anomalies[column] = data[column] > threshold
    return anomalies

# Function to display anomaly details in a popup message
def show_anomaly_details(data, anomaly_indices):
    for idx in anomaly_indices:
        st.write(f"Anomalies detected at index {idx}:")
        st.write(data.iloc[idx])

# Main function
def main():
    # Set page title and icon
    st.set_page_config(
        page_title="Anomaly Detection App",
        page_icon="📊"
    )

    # Title and description
    st.title("Anomaly Detection App")
    st.write("Upload a CSV dataset and choose the type of graph to visualize. You can also set thresholds for anomaly detection for each numerical feature.")

    # Upload CSV dataset
    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])

    if uploaded_file is not None:
        # Read CSV dataset
        df = pd.read_csv(uploaded_file)

        # Convert date column to datetime type
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Display dataset
        st.subheader("Dataset")
        st.dataframe(df)  # or st.table(df)

        # Sidebar for user interaction
        st.sidebar.title("Settings")

        # Select graph type
        graph_type = st.sidebar.selectbox("Select Graph Type", ["Line Chart", "Scatter Plot"])

        # Create threshold sliders for each numerical feature
        thresholds = {}
        numeric_columns = df.select_dtypes(include=[np.number])
        for column in numeric_columns.columns:
            thresholds[column] = st.sidebar.slider(f"Threshold for {column}", min_value=0.0, max_value=100.0, value=50.0)

        # Detect anomalies
        if not numeric_columns.empty:
            anomalies = detect_anomalies(numeric_columns, thresholds)
            anomaly_indices = np.where(anomalies.any(axis=1))[0]
             # Send data to the backend for anomaly detection
            response = requests.post('http://127.0.0.1:5000/detect_anomalies', json=numeric_columns.to_dict(orient='list'))
            if response.status_code == 200:
                anomaly_predictions = response.json()
                anomaly_indices = np.where(anomaly_predictions)[0]
            
                # Display popup message if anomalies are detected
                if len(anomaly_indices) > 0:
                    st.error("Anomalies detected! See details below.")
                    show_anomaly_details(df, anomaly_indices)
                else:
                    st.error("An error occurred during anomaly detection.")
        # Visualize dataset based on graph type
        for column in numeric_columns.columns:
            chart_placeholder = st.empty()

            if graph_type == "Line Chart":
                fig = px.line(df, x='date', y=column) if 'date' in df.columns else px.line(df, x=df.index, y=column)
            elif graph_type == "Scatter Plot":
                fig = px.scatter(df, x='date', y=column) if 'date' in df.columns else px.scatter(df, x=df.index, y=column)
            
            chart_placeholder.plotly_chart(fig)

# Run the app
if __name__ == "__main__":
    main()
