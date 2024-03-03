import streamlit as st

def show_home_page():
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
