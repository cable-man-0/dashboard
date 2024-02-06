from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_anomalies_iforest(df, threshold):
    try:
        # Preprocessing
        scaler = StandardScaler()
        X = scaler.fit_transform(df.values)
        
        # Fit Isolation Forest
        clf = IsolationForest()
        clf.fit(X)
        
        # Predict anomaly scores
        anomaly_scores = clf.decision_function(X)
        
        # Convert scores to binary based on the threshold
        #y_pred_binary = (anomaly_scores < threshold).astype(int)
        
        return anomaly_scores.tolist()
    except Exception as e:
        return None