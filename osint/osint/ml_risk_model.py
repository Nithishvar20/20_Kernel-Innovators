# osint/ml_ai_detector.py

import os
import joblib
import numpy as np

MODEL_PATH = os.path.join("data", "risk_model.pkl")

_model = None

# Load model if it exists
if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
        print("[AI] Risk model loaded successfully")
    except Exception as e:
        print("[AI] Failed to load model:", e)


def predict_risk_ml(features: dict):
    """
    Predict risk using a trained ML model.
    Falls back gracefully if model is unavailable.
    """

    # ---------- SAFETY CHECK ----------
    if _model is None:
        return {
            "level": "UNKNOWN",
            "score": 0,
            "confidence": 0.0,
            "note": "ML model not trained yet"
        }

    # ---------- FEATURE VECTOR ----------
    X = np.array([[
        features.get("platform_count", 0),
        features.get("high_confidence_accounts", 0),
        int(features.get("private_profiles", False)),
        int(features.get("image_metadata", False)),
        features.get("media_risk", 0),
        features.get("text_risk", 0),
        features.get("identity_correlation", 0),
    ]])

    # ---------- PREDICTION ----------
    prediction = _model.predict(X)[0]
    probability = max(_model.predict_proba(X)[0])

    label_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

    return {
        "level": label_map.get(prediction, "UNKNOWN"),
        "score": int(probability * 100),
        "confidence": round(float(probability), 2),
    }