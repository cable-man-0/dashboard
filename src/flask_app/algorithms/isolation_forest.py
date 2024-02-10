import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_anomalies_iforest(df, contamination=0.1, n_estimators=100, max_samples='auto', random_state=42):

    try:
        # Ensure data is numerical
        if not pd.api.types.is_numeric_dtype(df.dtypes.all()):
            raise ValueError("Data must contain only numerical values.")

        # Preprocess data
        scaler = StandardScaler()
        X = scaler.fit_transform(df.values)

        # Fit Isolation Forest with user-provided parameters
        clf = IsolationForest(contamination=contamination,
                              n_estimators=n_estimators,
                              max_samples=max_samples,
                              random_state=random_state)
        clf.fit(X)

        # Predict anomaly scores
        anomaly_scores = clf.decision_function(X)

        return anomaly_scores.tolist()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
