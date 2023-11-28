import numpy as np
import torch
import torch.nn as nn

class Attention(nn.Module):
    def __init__(self, feature_dim):
        super(Attention, self).__init__()
        self.feature_dim = feature_dim
        self.proj = nn.Linear(feature_dim, 64)
        self.out = nn.Linear(64, feature_dim)  # Ensure output dimension matches feature_dim

    def forward(self, x):
        eij = self.proj(x)
        eij = torch.tanh(eij)
        eij = self.out(eij)
        a = torch.softmax(eij, dim=1)
        weighted_input = x * a
        return weighted_input  # Return the weighted input for further processing

     
class AdvancedURLNetWithAttention(nn.Module):
    def __init__(self, num_features):
        super(AdvancedURLNetWithAttention, self).__init__()
        # Increased the complexity of the first layer and added a second attention layer
        self.fc1 = nn.Linear(num_features, 1024)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)  # Reduced dropout
        self.attention1 = Attention(1024)
        self.fc2 = nn.Linear(1024, 512)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.3)
        self.attention2 = Attention(512)  # New attention layer
        self.fc3 = nn.Linear(512, 128)
        self.relu3 = nn.ReLU()
        self.dropout3 = nn.Dropout(0.3)
        self.fc4 = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        x = self.attention1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        x = self.attention2(x)
        x = self.fc3(x)
        x = self.relu3(x)
        x = self.dropout3(x)
        x = self.fc4(x)
        x = self.sigmoid(x)
        return x
    
    
    
def transform_and_predict(features_list, vectorizer, scaler, model):
    # Separate the URL from the numerical features
    url, numerical_features = features_list[0], np.array(features_list[1:])

    # Transform the URL using the pre-fitted TF-IDF vectorizer
    tfidf_features = vectorizer.transform([url]).toarray()

    # Ensure numerical_features is a 2D array with a single sample
    numerical_features = numerical_features.reshape(1, -1)

    # Combine TF-IDF features with other numerical features
    combined_features = np.hstack((tfidf_features, numerical_features))

    # Standardize the features using the pre-fitted scaler
    scaled_features = scaler.transform(combined_features)  # No need for additional brackets now

    # Convert to PyTorch tensor
    features_tensor = torch.tensor(scaled_features, dtype=torch.float32)

    # Predict using the model
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():
        prediction = model(features_tensor)
        predicted_class = (prediction.squeeze() > 0.5).float()
        return predicted_class.item()  # Return the prediction as a Python scalar