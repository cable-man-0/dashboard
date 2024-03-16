import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import logging
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json

broker = ""
port = ""
topic = ""
 
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.set_index('date').resample('D').ffill().reset_index()
        df = df.dropna()
        return df
    except FileNotFoundError:
        st.error("Please upload a valid CSV file.")
        return None

def visualize(broker, port, topic):
    try:
        payload = {'broker': broker, 'port': port, 'topic': topic}
        response = requests.post('http://127.0.0.1:5000/subscribe_mqtt_topic', json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            payload_data = response_data.get('payload')  # Retrieve the payload from the response
            return payload_data  # Return the payload data
        else:
            logging.error(f"Failed to subscribe to MQTT topic. Status code: {response.status_code}")
            return None
    except (requests.exceptions.RequestException, Exception) as e:
        logging.error(f"An error occurred: {str(e)}")
        return None   

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


def detection_page():
    st.title("Anomaly Detection")
    st.write("Upload a CSV dataset and choose the features to run anomaly detection on.")
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
            parameters["contamination"] = st.sidebar.slider("Contamination (outlier %)", min_value=0.0, max_value=0.5, value=0.1)
            parameters["n_estimators"] = st.sidebar.slider("Number of Trees", min_value=10, max_value=1000, value=100)
        elif algorithm == "SVM":
            parameters["kernel"] = st.sidebar.selectbox("Kernel", ["linear", "rbf"])
            parameters["C"] = st.sidebar.slider("Regularization Parameter", min_value=0.1, max_value=100.0, value=1.0)
        elif algorithm == "DBSCAN":
            parameters["eps"] = st.sidebar.slider("Epsilon (minimum distance)", min_value=0.0, max_value=1.0, value=0.5)
            parameters["min_samples"] = st.sidebar.slider("Minimum Samples", min_value=1, max_value=len(df), value=5)
        if st.sidebar.button("Run Anomaly Detection"):
            with st.spinner("Detecting anomalies..."):
                data = df[selected_features]
                response = detect_anomalies(data, algorithm, **parameters)
                if response is not None and response.status_code == 200:
                    anomaly_indices = response.json()
                    if anomaly_indices:
                        st.info("Anomalies detected! See details below.")
                        anomaly_df = pd.DataFrame({'Index': range(len(df)), 'Anomaly': anomaly_indices})
                        st.subheader("Anomaly Data Points")
                        st.table(anomaly_df[anomaly_df['Anomaly'] < 0])
                    else:
                        st.success("No anomalies detected.")
                else:
                    st.error("An error occurred during anomaly detection.")
                    st.toast("Please check the backend server and try again.")
                num_charts = len(graph_type)
                chart_rows = st.columns(num_charts)
                for chart_type, chart_col in zip(graph_type, chart_rows):
                    for column in selected_features:
                        x = 'date' if 'date' in df.columns else None
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
                        st.plotly_chart(fig)
                        if chart_col.index == 0:
                            chart_col.write("")
    else:
        st.error("select a file")




def detect():
    logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
    logger = logging.getLogger(__name__)

    st.title("Anomaly Detection Dashboard")
    option = st.radio("Choose an option:", ["Upload Dataset", "Connect to MQTT Broker"])

    if option == "Upload Dataset":
        detection_page()
    elif option == "Connect to MQTT Broker":
        with st.form("mqtt_form"):
            broker = st.text_input("Broker", "localhost")
            port = st.text_input("Port", "1883")
            topic = st.text_input("Topic", "topic_name")
            submit_button = st.form_submit_button("Submit")
        
            if submit_button:
                try:
                    response = visualize(broker, int(port), topic)
                    if response is not None:
                        st.subheader("Data stream")

                        if isinstance(response, list):  # Check if response is a list (assuming payload is a list of dictionaries)
                            # Extract timestamp and payload values
                            timestamps = []
                            payload_values = []
                            for entry in response:
                                timestamps.append(entry["timestamp"])
                                payload_values.append(entry["payload"])

                            logger.info("Creating scatter plot...")
                            # Create a scatter plot
                            fig = go.Figure(data=go.Scatter(x=timestamps, y=payload_values))
                            fig.update_layout(
                                title="Payload Visualization",
                                xaxis_title="Timestamp",
                                yaxis_title="Payload"
                            )
                            st.plotly_chart(fig)

                            logger.info("Displaying response in a table...")
                            # Display response in a table
                            st.write("Response:")
                            st.table(response)
                        else:
                            logger.warning("Unexpected response format. Unable to visualize data.")
                            st.warning("Unexpected response format. Unable to visualize data.")
                    else:
                        logger.error("An error occurred during connecting.")
                        st.error("An error occurred during connecting.")
                except Exception as e:
                    logger.error(f"An error occurred during connecting: {str(e)}")
                    st.error("An error occurred during connecting.")