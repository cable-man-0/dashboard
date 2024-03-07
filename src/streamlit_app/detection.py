import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import logging
import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
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
    st.title("Anomaly Detection Dashboard")
    option = st.radio("Choose an option:", ["Upload Dataset", "Connect to MQTT Broker"])

    if option == "Upload Dataset":
        detection_page()
    elif option == "Connect to MQTT Broker":
        st.subheader("MQTT Broker Configuration")
        broker_address = st.text_input("Broker Address")
        port = st.number_input("Port", min_value=0, max_value=65535, value=1883)
        topic = st.text_input("Topic")
        if st.button("Connect"):
            visualize_mqtt_data(broker_address, port, topic)

def on_connect(client, userdata, flags, rc, topic):
    if rc == 0:
        st.write("Connected to MQTT Broker")
        client.subscribe(topic)
    else:
        st.write("Failed to connect to MQTT Broker")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        timestamp = pd.to_datetime(payload["timestamp"], unit="s")
        value = payload["value"]
        data.append((timestamp, value))
    except Exception as e:
        st.write("Error parsing MQTT message:", e)

def visualize_mqtt_data(broker_address, port, topic):
    global data
    data = []

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = lambda client, userdata, flags, rc: on_connect(client, userdata, flags, rc, topic)
    client.on_message = on_message

    st.write("Connecting to MQTT Broker...")
    client.connect(broker_address, port)
    client.loop_start()

    st.write("Waiting for MQTT messages...")

    while True:
        if len(data) > 0:
            df = pd.DataFrame(data, columns=["Timestamp", "Value"])
            df.set_index("Timestamp", inplace=True)

            st.write("Received MQTT Messages:")
            st.write(df)

            st.write("Visualizing MQTT Messages:")
            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df["Value"], marker='o', linestyle='-')
            plt.xlabel("Timestamp")
            plt.ylabel("Value")
            plt.title("MQTT Message Visualization")
            st.pyplot(plt)
            break