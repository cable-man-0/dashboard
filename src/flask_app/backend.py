from flask import Flask, request, jsonify
from pycaret.anomaly import *
import pandas as pd

app = Flask(__name__)

# Endpoint for anomaly detection
@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    data = request.json
    df = pd.DataFrame(data)
    
    # Initialize the PyCaret anomaly detection module
    exp_ano101 = setup(df, session_id=123)
    
    # Create an anomaly detection model
    iforest = create_model('iforest')
    
    # Assign the anomalies to the original dataset
    df_anomalies = assign_model(iforest)
    
    # Extract anomaly indices
    anomaly_indices = df_anomalies[df_anomalies['Anomaly'] == 1].index.tolist()
    
    return jsonify(anomaly_indices)

if __name__ == '__main__':
    app.run(debug=True)
