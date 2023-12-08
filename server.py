from flask import Flask, request, jsonify
import torch
import requests
from model_multi import AdvancedURLNetWithAttention, transform_and_predict
import joblib
import concurrent.futures
import threading
import base64

from hyperlinks import WebpageLinkCounter
from subdomain_count import SubdomainCounter
from google_index import Index_Checker

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import base64

# Load the private key from a file
private_key = ""

# Load the private key from a file
with open("url_safe.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=b'114514',  # Use a password if your key is encrypted
        backend=default_backend()
    )

def sign_message(private_key, message):
    # Ensure message is bytes
    if isinstance(message, str):
        message = message.encode('utf-8')

    # Sign the message
    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )

    (r, s) = decode_dss_signature(signature)
    signatureP1363 = r.to_bytes(32, byteorder='big') + s.to_bytes(32, byteorder='big')
    return signatureP1363


links_counter = WebpageLinkCounter()
subdomain_counter = SubdomainCounter()
index_checker = Index_Checker()


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

        future_subdomain = executor.submit(subdomain_counter.get_subdomain_count, url)
        future_google_index = executor.submit(index_checker.check_google_index_api, url)
        future_hyperlinks = executor.submit(links_counter.hyperlink_number, url)

        # Wait for the results
        nb_subdomain = future_subdomain.result()
        google_index = future_google_index.result()
        hyperlinks = future_hyperlinks.result()

    return [feature_url, feature_length, feature_dots, feature_protocol, nb_subdomain, google_index, hyperlinks]
    # return [feature_url, feature_length, feature_dots, feature_protocol, nb_subdomain]


####################################Test##############################
@app.route('/predict2', methods=['GET'])
def predict_url2():
    url = request.args.get("url")
    result =  url + "Benign"
    # Assuming sign_message function returns a bytes object
    signature_bytes = base64.b64encode(sign_message(private_key, result))

    # Convert the bytes object to a string
    signature_string = signature_bytes.decode('utf-8')
    return jsonify({
        "url": url, 
        "prediction": "Malicious", 
        "signature": signature_string
    })


@app.route('/predict1', methods=['GET'])
def predict_url1():
    url = request.args.get("url")
    result =  url + "Benign"
    # Assuming sign_message function returns a bytes object
    signature_bytes = base64.b64encode(sign_message(private_key, result))

    # Convert the bytes object to a string
    signature_string = signature_bytes.decode('utf-8')
    return jsonify({
        "url": url, 
        "prediction": "Benign", 
        "signature": signature_string
    })


####################################Main Service##############################
@app.route('/predict', methods=['GET'])
def predict_url():
    url = request.args.get("url")
    if not url:
        return "No URL provided", 400
    
    features = generate_features(url)

    prediction = transform_and_predict(features, vectorizer, scaler, model)

    print("url, length, dots, is_http, nb_subdomain, google_indexed, hyperlinks, malicious")
    print(features, prediction)

    result =  url+("Malicious" if prediction == 1 else "Benign")
    # Assuming sign_message function returns a bytes object
    signature_bytes = base64.b64encode(sign_message(private_key, result))

    # Convert the bytes object to a string
    signature_string = signature_bytes.decode('utf-8')

    return jsonify({
        "google_indexed": features[5], 
        "nb_hyperlinks": features[6],
        "nb_subdomain": features[4], 
        "url": url, 
        "prediction": "Malicious" if prediction == 1 else "Benign", 
        "signature": signature_string
    })
    


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"online": "true"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)

    