from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
def detect_anomalies_dbscan(df, eps=0.2, min_samples=5, metric="euclidean", evaluate=False):

    try:
        # Ensure data is numerical
        if not pd.api.types.is_numeric_dtype(df.dtypes.all()):
            raise ValueError("Data must contain only numerical values.")

        # Preprocess data
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df.values)

        # Fit DBSCAN with user-provided parameters
        outlier_detection = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        clusters = outlier_detection.fit_predict(X)

        # Mark outliers (noise) as -1
        clusters[clusters == -1] = -1  # Ensure outlier label is consistently -1

        # Optionally evaluate the DBSCAN model
        if evaluate:
            if len(set(clusters)) > 1:
                evaluation_metrics = {
                    "Silhouette Score": silhouette_score(X, clusters),
                    "Calinski-Harabasz Score": calinski_harabasz_score(X, clusters),
                    "Davies-Bouldin Score": davies_bouldin_score(X, clusters)
                }
                print(evaluation_metrics)  # Print in a more organized format

        return clusters.tolist()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
