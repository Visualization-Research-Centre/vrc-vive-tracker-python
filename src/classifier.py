import joblib
import numpy as np
import logging


class Classifier:
    
    def __init__(self, config=None):
        self.model = None
        self.thread = None
        self.running = False
        self.scaler = None
        self.imputer = None
        self.input_size = None
        self.labels = None
        if config:
            self.model_path = config.get("classifier_path", None)
            self.input_size = config.get("input_size", 10)
            self.labels = config.get("labels", ["circle", "line", "random"])
            self.scaler_path = config.get("scaler_path", None)
            self.imputer_path = config.get("imputer_path", None)
        self.load_models()

    def load_models(self):
        """Load the model from the specified path."""
        self.model = joblib.load(self.model_path)
        logging.info(f"Model loaded from {self.model_path}")
        if self.scaler_path:
            self.scaler = joblib.load(self.scaler_path)
            logging.info(f"Scaler loaded from {self.scaler_path}")
        else:
            self.scaler = None
        if self.imputer_path:
            self.imputer = joblib.load(self.imputer_path)
            logging.info(f"Imputer loaded from {self.imputer_path}")
        else:
            self.imputer = None
        
    def preprocess_data(self, data):

        trackers = [np.nan] * self.input_size
        trackers[:len(data)] = data
        trackers = np.array(trackers).astype(np.float32).reshape(1, -1)
        trackers = trackers / 4
        
        if self.imputer:
            trackers = self.imputer.transform(trackers)
        if self.scaler:
            trackers = self.scaler.transform(trackers)
        return trackers
    
    def predict(self, trackers):
        """Predict the class of the input data."""
        data = self.preprocess_data(trackers)
        if self.model is None:
            raise ValueError("Model not loaded. Please load a model before predicting.")
        probs = self.model.predict_proba(data)
        probs = probs[0]
        label = self.labels[np.argmax(probs)]
        return probs, label
    
    
if __name__ == "__main__":
    
    trackers = [-2.4, -1.2, 1, -3, -2, 1]
    model_path = "f[0,1,2]_v520_r10000_cart_evenCirc_mlp_model.pkl"
    
    classifier = Classifier(model_path)
    prediction = classifier.predict(trackers)
    
    
    print(f"Prediction: {prediction}")