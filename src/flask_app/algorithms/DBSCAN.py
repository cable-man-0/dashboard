from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt

# Load train and test datasets
train_df = pd.read_csv("/home/teemo/Desktop/pfe/env/src/dataset/training.csv", parse_dates=["date"], index_col="date")
test_df = pd.read_csv("/home/teemo/Desktop/pfe/env/src/dataset/testing.csv", parse_dates=["date"], index_col="date")

# Preprocessing
scaler = MinMaxScaler()
X_train = scaler.fit_transform(train_df.values)
X_test = scaler.transform(test_df.values)

# Fit DBSCAN model
outlier_detection = DBSCAN(eps=0.2, metric="euclidean", min_samples=5, n_jobs=-1)
clusters_train = outlier_detection.fit_predict(X_train)
clusters_test = outlier_detection.fit_predict(X_test)

# Plot anomalies
plt.figure(figsize=(10, 6))

# Plot normal data points
plt.scatter(test_df.index, test_df.values, c=clusters_test, cmap='Set1', label='Normal')

# Plot anomaly data points
anomaly_indices = test_df[clusters_test == -1]
plt.scatter(anomaly_indices.index, anomaly_indices.values, color='red', label='Anomaly')

plt.title('DBSCAN Anomaly Detection')
plt.xlabel('Date')
plt.ylabel('Feature')
plt.legend()
plt.show()
