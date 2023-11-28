import torch
import joblib

from model_multi import AdvancedURLNetWithAttention, transform_and_predict

# Assuming the saved model file is named 'model_state_dict.pth'
# and the saved vectorizer and scaler are named 'tfidf_vectorizer.joblib' and 'standard_scaler.joblib', respectively.

# Load the trained model
num_features = 1004
model = AdvancedURLNetWithAttention(num_features)
model.load_state_dict(torch.load('model_state_dict.pth'))
model.eval()  # Set the model to evaluation mode

# Load the vectorizer and scaler
vectorizer = joblib.load('tfidf_vectorizer.joblib')
scaler = joblib.load('standard_scaler.joblib')


# Example use of the loaded model and preprocessing tools to make predictions
new_data_points = [ 
   ["http://example.com", 35, 3, 1, 2],  # Example data point with numerical features
    # Add more data points as needed
]

for features_list in new_data_points:
    prediction = transform_and_predict(features_list, vectorizer, scaler, model)
    print("Malicious" if prediction == 1 else "Benign")
