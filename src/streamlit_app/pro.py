import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from joblib import load

def load_data(uploaded_file):
    new_test_data = pd.read_csv(uploaded_file)
    X_columns = ['IAT', 'rst_count', 'urg_count', 'flow_duration', 'Variance', 'Duration', 'Header_Length', 'Number', 'Weight', 'Rate']
    return new_test_data, X_columns

def make_predictions(new_test_data, X_columns):
    model_8_classes = load("models/newRandomForest_model_8_classes.joblib")
    model_2_classes = load("models/newRandomForest_model_2_classes.joblib")
    scaler = StandardScaler()
    scaler.fit(new_test_data[X_columns])
    new_test_data[X_columns] = scaler.transform(new_test_data[X_columns])
    predictions_8_classes = model_8_classes.predict(new_test_data[X_columns])
    predictions_2_classes = model_2_classes.predict(new_test_data[X_columns])
    new_test_data['predictions_2'] = predictions_2_classes
    new_test_data['predictions_8'] = predictions_8_classes
    return new_test_data

def visualize_data(new_test_data):
    chart_data_2 = new_test_data['predictions_2'].value_counts().reset_index()
    chart_data_2.columns = ['Predicted Class', 'Count']
    fig_2 = px.bar(chart_data_2, x='Predicted Class', y='Count')
    st.subheader("Predictions for 2 Classes")
    st.plotly_chart(fig_2)

    chart_data_8 = new_test_data['predictions_8'].value_counts().reset_index()
    chart_data_8.columns = ['Predicted Class', 'Count']
    fig_8 = px.bar(chart_data_8, x='Predicted Class', y='Count')
    st.subheader("Predictions for 8 Classes")
    st.plotly_chart(fig_8)

def pro_page():
    if st.session_state.logged_in:
        st.subheader("Inspect Your Data Flow")
        st.write("Upload a CSV dataset")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file is not None:
            new_test_data, X_columns = load_data(uploaded_file)
            st.write(new_test_data.head(10))
            selected_features = st.multiselect("Select Features to Visualize", X_columns)

            if len(selected_features) > 0:
                scatter_data = new_test_data[selected_features]
                scatter_fig = px.scatter(scatter_data, title=f"Scatter Plot of Selected Features: {', '.join(selected_features)}")
                st.plotly_chart(scatter_fig)
            if st.button("Launch"):
                new_test_data = make_predictions(new_test_data, X_columns)
                st.write(new_test_data)
                visualize_data(new_test_data)
