from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt

def detect_anomalies_dbscan(df):
    try:
        # Preprocessing
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df.values)
        
        # Fit DBSCAN model
        outlier_detection = DBSCAN(eps=0.2, metric="euclidean", min_samples=5, n_jobs=-1)
        clusters = outlier_detection.fit_predict(X)

        return clusters
    except Exception as e:
        return None

# Example usage
# clusters = detect_anomalies_dbscan(df)
