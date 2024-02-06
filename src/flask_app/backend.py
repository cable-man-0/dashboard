from flask import Flask, request, jsonify
from pycaret.anomaly import *
import pandas as pd
from algorithms.dbscan import detect_anomalies_dbscan

app = Flask(__name__)

# Endpoint for anomaly detection
@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    try:
        # Check if the content type is JSON
        if request.headers['Content-Type'] != 'application/json':
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 100

        # Get JSON data from request
        data = request.json
        if 'data' not in data or 'algorithm' not in data:
            return jsonify({'error': 'Invalid JSON format. Expected "data" and "algorithm" keys.'}), 300

        # Convert data to DataFrame
        df = pd.DataFrame(data['data'])

        # Select anomaly detection algorithm
        algorithm = data['algorithm']
        if algorithm == 'isolation_forest':
            anomaly_indices = isolation_forest(df, threshold)
        elif algorithm == 'SVM':
            anomaly_indices = svm(df)
        elif algorithm == 'DBSCAN':
            anomaly_indices = dbscan(df)
        else:
            return jsonify({'error': 'Invalid algorithm specified.'}), 600

        # Assign the anomalies to the original dataset
        df_anomalies = assign_model(model)

        # Extract anomaly indices
        anomaly_indices = df_anomalies[df_anomalies['Anomaly'] == 1].index.tolist()

        return jsonify(anomaly_indices), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
