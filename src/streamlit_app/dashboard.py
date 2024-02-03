import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests

# Main function
def main():
    # Set page title and icon
    st.set_page_config(
        page_title="Anomaly Detection App",
        page_icon="📊"
    )

    # Title and description
    st.title("Anomaly Detection App")
    st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")

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

        # Select features for anomaly detection
        selected_features = st.sidebar.multiselect("Select Features for Anomaly Detection", df.columns.tolist())

        # Create threshold sliders for selected features
        thresholds = {}
        for feature in selected_features:
            thresholds[feature] = st.sidebar.slider(f"Threshold for {feature}", min_value=0.0, max_value=100.0, value=50.0)

        # Detect anomalies
        if selected_features:
            # Filter selected features (excluding 'date')
            numeric_columns = df[selected_features]

            # Send selected features and thresholds to the backend for anomaly detection
            response = requests.post('http://127.0.0.1:5000/detect_anomalies', json={'data': numeric_columns.to_dict(orient='list'), 'thresholds': thresholds})
            if response.status_code == 200:
                anomaly_indices = response.json()
                if anomaly_indices:
                    st.error("Anomalies detected! See details below.")
                    st.write("Anomaly Indices:", anomaly_indices)
                else:
                    st.success("No anomalies detected.")
            else:
                st.error("An error occurred during anomaly detection.")

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
