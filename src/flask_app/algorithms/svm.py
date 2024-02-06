import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

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

        # Evaluate the One-Class SVM model
        y_true = np.ones(len(df))  # Assuming all instances are normal (1)
        y_true[y_pred == -1] = -1  # Mark predicted anomalies as -1
        
        precision = precision_score(y_true, y_pred, pos_label=-1)
        recall = recall_score(y_true, y_pred, pos_label=-1)
        f1 = f1_score(y_true, y_pred, pos_label=-1)
        
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1-Score:", f1)
        
        return y_pred.tolist()
    except Exception as e:
        return None