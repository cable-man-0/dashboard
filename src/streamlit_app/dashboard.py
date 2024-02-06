import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import matplotlib.pyplot as plt

# Define a function to load data from CSV file with caching
@st.cache_data()
def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# Define a function to detect anomalies with caching
def detect_anomalies(data, algorithm, thresholds=None):
    if thresholds is None:
        thresholds = {}
    response = requests.post('http://127.0.0.1:5000/detect_anomalies', json={'data': data.to_dict(orient='list'), 'thresholds': thresholds, 'algorithm': algorithm})
    return response


# Main function
def main():
    # Set page title and icon
    st.set_page_config(
        page_title="Anomaly Detection App",
        page_icon="📊")

    # Title and description
    st.title("Anomaly Detection App")
    st.write("Upload a CSV dataset and choose the features to run anomaly detection on. You can also set thresholds for anomaly detection for each numerical feature.")

    # Load Style css
    with open('/home/teemo/Desktop/pfe/env/src/streamlit/src/style/style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Upload CSV dataset
    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])

    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Load CSV dataset
        df = load_data(uploaded_file)

        df = df.bfill().dropna()

        # Display dataset
        st.subheader("Dataset")
        st.write(df)  # Display the dataset

        # Sidebar for user interaction
        st.sidebar.title("Settings")

        # Select graph type
        graph_type = st.sidebar.selectbox("Select Graph Type", ["Line Chart", "Scatter Plot"])

        algorithm = st.sidebar.selectbox("Select Anomaly Detection Algorithm", ["isolation_forest","SVM","DBSCAN"])
        
        selected_features = st.sidebar.multiselect("Select Features for Anomaly Detection", df.columns.tolist())

        if algorithm == "isolation_forest":
            # Select features for anomaly detection
            # Create threshold sliders for selected features
            thresholds = {}
            for feature in selected_features:
                thresholds[feature] = st.sidebar.slider(f"Threshold for {feature}", min_value=0.0, max_value=100.0, value=50.0)    

        # Confirm button
        if st.sidebar.button("Confirm"):
                if selected_features:
                    data=df[selected_features]
            
                    if algorithm == "isolation_forest":
                            # Filter selected features (excluding 'date')
                            data = df[selected_features]
                            # Detect anomalies
                            response = detect_anomalies(data, algorithm,thresholds)
                    elif (algorithm == "DBSCAN")or (algorithm == "SVM"):
                        if selected_features:
                            # Filter selected features (excluding 'date')
                            data = df[selected_features]
                            # Detect anomalies
                            response = detect_anomalies(data,algorithm)

                    if response is not None and response.status_code == 200:
                        anomaly_indices = response.json()
                        if anomaly_indices:
                            st.error("Anomalies detected! See details below.")
                            st.write("Anomaly Indices:")
                            st.table(pd.DataFrame({'Index': anomaly_indices}))
                            total_data_points = len(df)
                            num_anomalies = len(anomaly_indices)
                            num_normal_points = total_data_points - num_anomalies

                            labels = ['Normal Points', 'Anomalies']
                            sizes = [num_normal_points, num_anomalies]
                            colors = ['skyblue', 'salmon']
                            explode = (0, 0.1)

                            fig1, ax1 = plt.subplots()
                            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
                            ax1.axis('equal')

                            st.write("Distribution of Anomalies:")
                            st.pyplot(fig1)

                        else:
                            st.success("No anomalies detected.")
                    else:
                        st.error("An error occurred during anomaly detection.")

                    # Visualization based on selected graph type
                    for column in data.columns:
                        chart_placeholder = st.empty()

                        if graph_type == "Line Chart":
                            fig = px.line(df, x='date', y=column) if 'date' in df.columns else px.line(df, x=df.index, y=column)
                        elif graph_type == "Scatter Plot":
                            fig = px.scatter(df, x='date', y=column) if 'date' in df.columns else px.scatter(df, x=df.index, y=column)
                            
                        chart_placeholder.plotly_chart(fig)

# Run the app
if __name__ == "__main__":
    main()
