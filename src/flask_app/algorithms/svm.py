import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

def detect_anomalies_svm(df, nu=0.1, kernel="rbf", gamma="auto"):

    try:
        # Ensure data is numerical
        if not pd.api.types.is_numeric_dtype(df.dtypes.all()):
            raise ValueError("Data must contain only numerical values.")

        # Preprocess data
        scaler = StandardScaler()
        X = scaler.fit_transform(df.values)

        # Fit One-Class SVM with user-provided parameters
        svm = OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)
        svm.fit(X)

        # Predict anomalies
        y_pred = svm.predict(X)

        # Optionally evaluate the model (using true labels if available)
        if "true_labels" in df.columns:
            y_true = df["true_labels"]
            evaluation_metrics = {
                "Precision": precision_score(y_true, y_pred, pos_label=-1),
                "Recall": recall_score(y_true, y_pred, pos_label=-1),
                "F1-Score": f1_score(y_true, y_pred, pos_label=-1)
            }
            print(evaluation_metrics)  # Print in an organized format

        return y_pred.tolist()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
