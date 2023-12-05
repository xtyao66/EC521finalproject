from flask import Flask, request, jsonify
import torch
import requests
from model_multi import AdvancedURLNetWithAttention, transform_and_predict
import joblib
import concurrent.futures
import threading

from subdomain_count import subdomain_number
from google_index import index_search
from hyperlinks import hyperlink_number

app = Flask(__name__)

# Assuming the saved model file is named 'model_state_dict.pth'
# and the saved vectorizer and scaler are named 'tfidf_vectorizer.joblib' and 'standard_scaler.joblib', respectively.

# Load the trained model
num_features = 1006
model = AdvancedURLNetWithAttention(num_features)
model.load_state_dict(torch.load('model_state_dict.pth'))
model.eval()  # Set the model to evaluation mode

# Load the vectorizer and scaler
vectorizer = joblib.load('tfidf_vectorizer.joblib')
scaler = joblib.load('standard_scaler.joblib')

def generate_features(url):
    feature_url = url

    feature_length = len(url)

    feature_dots = url.count('.')

    # HTTP  1，HTTPS  0
    if url.startswith("http://"):
        feature_protocol = 1
    elif url.startswith("https://"):
        feature_protocol = 0
    else:
        feature_protocol = -1  

    nb_subdomain = -1

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the operations and mark each future with its function
        future_subdomain = executor.submit(subdomain_number, url)
        future_google_index = executor.submit(index_search, url)
        future_hyperlinks = executor.submit(hyperlink_number, url)

        # Wait for the results
        nb_subdomain = future_subdomain.result()
        google_index = future_google_index.result()
        hyperlinks = future_hyperlinks.result()

    return [feature_url, feature_length, feature_dots, feature_protocol, nb_subdomain, google_index, hyperlinks]
    # return [feature_url, feature_length, feature_dots, feature_protocol, nb_subdomain]


@app.route('/predict', methods=['GET'])
def predict_url():
    url = request.args.get("url")
    if not url:
        return "No URL provided", 400
    
    features = generate_features(url)

    prediction = transform_and_predict(features, vectorizer, scaler, model)

    print("url, length, dots, is_http, nb_subdomain, !google_indexed, hyperlinks, malicious")
    print(features, prediction)

    return jsonify({"google_indexed": not features[5], "nb_hyperlinks": features[6],"nb_subdomain": features[4], "url": url, "prediction": "Malicious" if prediction == 1 else "Benign"})


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"online": "true"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)

    