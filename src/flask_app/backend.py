from flask import Flask, request, jsonify
from algorithms.dbscan import detect_anomalies_dbscan
from algorithms.svm import detect_anomalies_svm
from algorithms.isolation_forest import detect_anomalies_iforest
import logging
import pandas as pd
from ml_models import predict_34_classes, predict_8_classes, predict_2_classes

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


# Endpoint for anomaly detection
@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    try:
        # Check if the content type is JSON
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        # Get JSON data from request
        data = request.json
        if 'data' not in data or 'algorithm' not in data:
            logging.error('Invalid JSON format. Expected "data" and "algorithm" keys.')
            return jsonify({'error': 'Invalid JSON format. Expected "data" and "algorithm" keys.'}), 400

        # Convert data to DataFrame
        df = pd.DataFrame(data['data'])

        # Select anomaly detection algorithm
        algorithm = data['algorithm']
        parameters = data.get('parameters', {})  # Extract additional parameters, default to empty dict

        if algorithm == 'isolation_forest':
            anomaly_indices = detect_anomalies_iforest(df, **parameters)  # Pass parameters
            if anomaly_indices is None:
                logging.error('An error occurred while detecting anomalies with isolation_forest.')
                return jsonify({'error': 'An error occurred while detecting anomalies with isolation_forest.'}), 500
        elif algorithm == 'SVM':
            anomaly_indices = detect_anomalies_svm(df, **parameters)  # Pass parameters
            if anomaly_indices is None:
                logging.error('An error occurred while detecting anomalies with SVM.')
                return jsonify({'error': 'An error occurred while detecting anomalies with SVM.'}), 500
        elif algorithm == 'DBSCAN':
            anomaly_indices = detect_anomalies_dbscan(df, **parameters)  # Pass parameters
            if anomaly_indices is None:
                logging.error('An error occurred while detecting anomalies with DBSCAN.')
                return jsonify({'error': 'An error occurred while detecting anomalies with DBSCAN.'}), 500
        else:
            logging.error('Invalid algorithm specified')
            return jsonify({'error': 'Invalid algorithm specified.'}), 400

        # Check if anomalies are detected
        if anomaly_indices is None:
            logging.error('An error occurred while detecting anomalies.')
            return jsonify({'error': 'An error occurred while detecting anomalies.'}), 500

        # Return anomaly indices
        logging.info('Success')
        return jsonify(anomaly_indices), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500
    
@app.route('/predict_34_classes', methods=['POST'])
def predict_34_classes_route():
    data = request.get_json()
    prediction = predict_34_classes(pd.DataFrame(data))
    return jsonify(prediction.tolist())

@app.route('/predict_8_classes', methods=['POST'])
def predict_8_classes_route():
    data = request.get_json()
    prediction = predict_8_classes(pd.DataFrame(data))
    return jsonify(prediction.tolist())

@app.route('/predict_2_classes', methods=['POST'])
def predict_2_classes():
    try:
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400
        
        data = request.json  # Parse the JSON data from the request
        # Ensure that 'data' is a list of dictionaries where each dictionary represents a row of the DataFrame
        if not isinstance(data, list):
            raise ValueError("Invalid data format. Expected a list of dictionaries.")
        
        # Create DataFrame from the JSON data
        df = pd.DataFrame(data)
        
        # Perform prediction using the DataFrame
        logging.info('test is true')
        prediction = predict_2_classes(df)
        logging.info('Success')
        
        # Return prediction as JSON response
        return jsonify(prediction.tolist()), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
