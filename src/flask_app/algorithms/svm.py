from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

def detect_anomalies_svm(df):
    try:
        # Preprocessing
        scaler = StandardScaler()
        X = scaler.fit_transform(df.values)
        
        # Fit One-Class SVM
        svm = OneClassSVM()
        svm.fit(X)
        
        # Predict anomalies
        y_pred = svm.predict(X)
        
        # Convert continuous predictions to binary (1 for anomaly, -1 for normal)
        thresholds = np.linspace(-1, 1, 100)
        best_threshold = None
        best_f1 = 0

        for threshold in thresholds:
            y_pred_binary = (y_pred == 1).astype(int)
            y_test = (df.values > threshold).astype(int)
            f1 = f1_score(y_test, y_pred_binary)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        print("Best Threshold:", best_threshold)
        print("Best F1 Score:", best_f1) 
        y_pred_binary = (y_pred == 1).astype(int)

        # Convert continuous targets to binary
        y_test = (df.values > threshold).astype(int)

        # Evaluate model
        precision = precision_score(y_test, y_pred_binary)
        recall = recall_score(y_test, y_pred_binary)
        f1 = f1_score(y_test, y_pred_binary)

        print("Precision:", precision)
        print("Recall:", recall)
        print("F1 Score:", f1)
        
        return y_pred, best_threshold, best_f1, precision, recall, f1
    except Exception as e:
        return None, None, None, None, None, None

# Example usage
# anomaly_pred, best_threshold, best_f1, precision, recall, f1 = detect_anomalies_svm(df)
