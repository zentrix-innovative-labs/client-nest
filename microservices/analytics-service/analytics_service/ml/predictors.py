import numpy as np
from sklearn.linear_model import LinearRegression
import threading

# Generate synthetic data for demonstration (replace with real data later)
np.random.seed(42)
X_fake = np.random.rand(100, 3)  # 100 samples, 3 features
coef = np.array([2.5, -1.2, 0.7])
y_fake = X_fake @ coef + np.random.normal(0, 0.2, 100)

# Train a simple regression model on the fake data
_model = LinearRegression()
_model.fit(X_fake, y_fake)

# Thread lock for model access (for thread safety in production)
_model_lock = threading.Lock()

def predict_engagement(features):
    """
    Predict engagement using a provisional model.
    Args:
        features (list or np.ndarray): Feature vector of length 3.
    Returns:
        float: Predicted engagement value.
    """
    arr = np.array(features).reshape(1, -1)
    with _model_lock:
        pred = _model.predict(arr)
    return float(pred[0]) 