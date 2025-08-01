import numpy as np
from sklearn.linear_model import LogisticRegression

class ChurnPredictor:
    def __init__(self):
        self.model = LogisticRegression()
        self.is_fitted = False

    def fit(self, X, y):
        self.model.fit(X, y)
        self.is_fitted = True

    def predict(self, features):
        if not self.is_fitted:
            # Dummy prediction if not fitted
            return 0.1
        features = np.array(features).reshape(1, -1)
        return float(self.model.predict_proba(features)[0, 1]) 