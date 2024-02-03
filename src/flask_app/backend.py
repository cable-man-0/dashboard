from flask import Flask, request, jsonify
from pycaret.anomaly import *
import pandas as pd

app = Flask(__name__)

# Endpoint for anomaly detection
@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    try:
        # Check if the content type is JSON
        if request.headers['Content-Type'] != 'application/json':
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        # Get JSON data from request
        data = request.json
        if 'data' not in data or 'thresholds' not in data:
            return jsonify({'error': 'Invalid JSON format. Expected "data" and "thresholds" keys.'}), 400

        # Convert data to DataFrame
        df = pd.DataFrame(data['data'])

        # Initialize the PyCaret anomaly detection module
        exp_ano101 = setup(df, session_id=123)

        # Create an anomaly detection model
        iforest = create_model('iforest')

        # Assign the anomalies to the original dataset
        df_anomalies = assign_model(iforest)

        # Extract anomaly indices
        anomaly_indices = df_anomalies[df_anomalies['Anomaly'] == 1].index.tolist()

        return jsonify(anomaly_indices), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
