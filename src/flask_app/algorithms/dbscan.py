import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler

def detect_anomalies_dbscan(df):
    try:
        # Preprocessing
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df.values)
        
        # Fit DBSCAN model
        outlier_detection = DBSCAN(eps=0.2, metric="euclidean", min_samples=5, n_jobs=-1)
        clusters = outlier_detection.fit_predict(X)

        # Evaluate the DBSCAN model
        if len(set(clusters)) > 1:  # At least 2 clusters are required for evaluation
            silhouette = silhouette_score(X, clusters)
            calinski_harabasz = calinski_harabasz_score(X, clusters)
            davies_bouldin = davies_bouldin_score(X, clusters)
            
            print("Silhouette Score:", silhouette)
            print("Calinski-Harabasz Score:", calinski_harabasz)
            print("Davies-Bouldin Score:", davies_bouldin)
        
        return clusters.tolist()  # Convert ndarray to list
    except Exception as e:
        return None