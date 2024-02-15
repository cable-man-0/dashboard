from joblib import load
import pandas as pd

def load_model_34_classes():
    return load("decision_tree_model_34_classes.joblib")

def load_model_8_classes():
    return load("decision_tree_model_8_classes.joblib")

def load_model_2_classes():
    return load("decision_tree_model_2_classes.joblib")

def predict_34_classes(data):
    model = load_model_34_classes()
    return model.predict(data)

def predict_8_classes(data):
    model = load_model_8_classes()
    return model.predict(data)

def predict_2_classes(data):
    model = load_model_2_classes()
    return model.predict(data)
