import joblib
import numpy as np

MODEL_PATH = "osint/data/risk_model.pkl"

# Load once
_model, _feature_columns, _label_encoder = joblib.load(MODEL_PATH)


def predict_risk_ml(features: dict):
    """
    Predict risk using trained ML model
    """

    # Build feature vector in correct order
    X = np.array([
        features.get(col, 0) for col in _feature_columns
    ]).reshape(1, -1)

    prediction_encoded = _model.predict(X)[0]
    prediction_label = _label_encoder.inverse_transform(
        [prediction_encoded]
    )[0]

    confidence = None
    if hasattr(_model, "predict_proba"):
        confidence = float(max(_model.predict_proba(X)[0]))

    score_map = {
        "LOW": 25,
        "MEDIUM": 55,
        "HIGH": 85
    }

    return {
        "score": score_map.get(prediction_label, 50),
        "level": prediction_label,
        "confidence": confidence
    }