import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

# Load the CSV file
csv_file_path = "RT_IOT2022_Dataset.csv"
data = pd.read_csv(csv_file_path)

# Preprocess the data
scaler = StandardScaler()
data[X_columns] = scaler.fit_transform(data[X_columns])  # Assuming X_columns is defined

# Use the trained model
predictions = predict_2_classes(data)  # Assuming 'model' is your trained Decision Tree model

# Postprocess the predictions
# For example, you can create a new DataFrame with the original data and the predicted labels
results = pd.DataFrame({'Data': data, 'Predicted_Label': predictions})

# Save the results to a new CSV file
results.to_csv("path/to/save/predictions.csv", index=False)
