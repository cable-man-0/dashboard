# notes !!
## 1. Finding the right Datatset
Select a dataset that contain multiple features
Preprocess the data if needed(important step !!)
Preparing and cleaning the data is the most important step in data analysis. It is the process of detecting and correcting (or removing) corrupt or inaccurate records from a record set, table, or database and refers to identifying incomplete, incorrect, inaccurate or irrelevant parts of the data and then replacing, modifying, or deleting the dirty or coarse data. (Wikipedia)

First, we will use the built-in function bfill(). The latter is used to backward fill the missing values in the dataset, since sometimes we find missing values of the different features. We believe that the variation of the features between consecutives days will not vary much.

Second, we will use the built-in function dropna(). This function is used to remove the totally missing rows. There is not interest in working with an acquisation that contains no values at all.]

## 2. Model training
Train the model on a specific dataset(use 40% of the dataset)
Test the model on the remaining ones(use 20%)
use real time data for testing_bengin (use 20%)
use real time data for tesing_anomalies(use 20%) {modify the remaining data add anomalies to it}

## 3. create a dashboard (Flask,...) 
Takes the real time data from the MQTT broker visulize the data and use the trained model to identify anomalies, if the model find an anomaly the dashboard generate alerts(msg,pop-ups,...) to the users.  
you can also upload a dataset dirctely to the dashboard to detect anomalies.


## 4. How to Run :
### install requirements in requirements.txt
### run the flask server                    
```python
python3 backend.py
```
### run the streamlit app                    
```python
streamlit run main.py
```
