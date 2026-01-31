import joblib
import numpy as np

MODEL_PATH = "osint/data/risk_model.pkl"

def extract_features(correlated):
    return np.array([[
        len(correlated.get("platforms_found", {})),
        sum(1 for p in correlated["platforms_found"].values()
            if p.get("confidence") == "HIGH"),
        sum(1 for p in correlated["platforms_found"].values()
            if p.get("confidence") == "MEDIUM"),
        len(correlated.get("platforms_found", {})) > 1,
        any(p.get("visibility") == "PRIVATE"
            for p in correlated["platforms_found"].values()),
        bool(correlated.get("image_metadata")),
        bool(correlated.get("geo_risk")),
        len(correlated.get("web_exposure", {}).get("exposed_sensitive_files", [])),
        len(correlated.get("web_exposure", {}).get("security_headers", {}).get("missing", []))
    ]], dtype=float)

def predict_risk(correlated):
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    encoder = bundle["encoder"]

    X = extract_features(correlated)
    probs = model.predict_proba(X)[0]
    pred = model.predict(X)[0]

    return {
        "score": int(max(probs) * 100),
        "level": encoder.inverse_transform([pred])[0],
        "probabilities": probs.tolist()
    }