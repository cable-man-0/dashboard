from flask import Flask, request, jsonify
from pycaret.anomaly import *
import pandas as pd
from algorithms.dbscan import detect_anomalies_dbscan
from algorithms.svm import detect_anomalies_svm
from algorithms.isolation_forest import detect_anomalies_iforest
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
users={}
@app.route('/register', methods=['POST'])
def register():
    try:
        # Check if the content type is JSON
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        # Get JSON data from request
        data = request.json
        if 'username' not in data or 'password' not in data:
            logging.error('Invalid JSON format. Expected "username" and "password" keys.')
            return jsonify({'error': 'Invalid JSON format. Expected "username" and "password" keys.'}), 400

        # Extract username and password from data
        username = data['username']
        password = data['password']

        # Check if the username is already taken
        if username in users:
            logging.error('Username already exists.')
            return jsonify({'error': 'Username already exists.'}), 400

        # Register the user
        users[username] = password

        logging.error('User registration successful.')
        return jsonify({'message': 'User registration successful.'}), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Endpoint for user authentication
@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        # Check if the content type is JSON
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        # Get JSON data from request
        data = request.json
        if 'username' not in data or 'password' not in data:
            logging.error('Invalid JSON format. Expected "username" and "password" keys.')
            return jsonify({'error': 'Invalid JSON format. Expected "username" and "password" keys.'}), 400

        # Extract username and password from data
        username = data['username']
        password = data['password']

        # Check if the username exists
        if username not in users:
            logging.error('Invalid username or password.')
            return jsonify({'authenticated': False}), 401

        # Check if the password is correct
        if users[username] != password:
            logging.error('Invalid username or password.')
            return jsonify({'authenticated': False}), 401

        logging.error('User authentication successful.')
        return jsonify({'authenticated': True}), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500


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
        thresholds = data['thresholds']
        
        # Select anomaly detection algorithm
        algorithm = data['algorithm']
        if algorithm == 'isolation_forest':
            anomaly_indices = detect_anomalies_iforest(df, thresholds)
            if anomaly_indices is None:
                logging.error('An error occurred while detecting anomalies with isolation_forest.')
                return jsonify({'error': 'An error occurred while detecting anomalies with isolation_forest.'}), 500
        elif algorithm == 'SVM':
            anomaly_indices = detect_anomalies_svm(df)
            if anomaly_indices is None:
                logging.error('An error occurred while detecting anomalies with SVM.')
                return jsonify({'error': 'An error occurred while detecting anomalies with SVM.'}), 500
        elif algorithm == 'DBSCAN':
            anomaly_indices = detect_anomalies_dbscan(df)
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
        logging.error('Success')
        return jsonify(anomaly_indices), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)