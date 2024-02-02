import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Read the dataset
df = pd.read_csv("/home/teemo/Desktop/pfe/env/src/dataset/testing.csv")

# Set page title and icon
st.set_page_config(
    page_title="Anomaly Detection Dashboard",
    page_icon="🛑"
)

# Dashboard title
st.title("Anomaly Detection Dashboard")

# Sidebar for user interaction
st.sidebar.title("Settings")

# Add interactive elements
date_range = st.sidebar.slider("Select Date Range", min_value=0, max_value=len(df), value=(0, len(df)))

# Placeholder for chart and anomalies
chart_placeholder = st.empty()

# Function to detect anomalies based on threshold
def detect_anomalies(data):
    # Classify temperatures above 30 degrees as anomalies
    anomalies = data > 30
    return anomalies

# Filter data based on selected date range
filtered_df = df.iloc[date_range[0]:date_range[1]]

# Remove non-numeric columns
numeric_df = filtered_df.select_dtypes(include=[np.number]).dropna()

# Detect anomalies
anomalies = detect_anomalies(numeric_df['Temperature'])

# Add anomaly column to the dataset
filtered_df['Anomaly'] = anomalies.astype(int)

# Display KPIs
avg_temp = np.mean(numeric_df['Temperature'])
max_temp = np.max(numeric_df['Temperature'])
min_temp = np.min(numeric_df['Temperature'])

st.subheader("Key Performance Indicators (KPIs)")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Average Temperature", value=round(avg_temp, 2))
kpi2.metric(label="Maximum Temperature", value=round(max_temp, 2))
kpi3.metric(label="Minimum Temperature", value=round(min_temp, 2))

# Display the chart
fig = px.scatter(filtered_df, x='date', y='Temperature', title='Temperature over Time', color='Anomaly')
chart_placeholder.plotly_chart(fig, use_container_width=True)

# Check if anomalies are detected
if np.sum(anomalies) > 0:
    st.error("Anomalies detected! Check the data for anomalies.")
    # Get the indices of all anomalies
    anomaly_indices = numeric_df.index[anomalies].tolist()
    # Get the data points causing the anomalies
    anomaly_data_points = filtered_df.loc[anomaly_indices]
    st.subheader("Anomaly Data Points:")
    st.write(anomaly_data_points)
