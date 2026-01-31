from osint.ai_image_ml.predictor import predict
from osint.ai_image_ml.explainer import explain
from PIL import Image


def analyze_ai_image(image_path: str):
    # Run ML prediction
    result = predict(image_path)

    # Generate explanations
    explanations = explain(result)

    # Final response object (NO label usage)
    return {
        "score": result["score"],                 # 0–100
        "confidence": result["score"],             # Alias for score
        "probability": result["probability"],     # 0–1
        "verdict": result["verdict"],             # Human readable
        "resolution": result.get("resolution"),
        "reasons": explanations,
        "camera_make": result.get("camera_make"),
        "camera_model": result.get("camera_model"),
        "date_taken": result.get("date_taken"),
        "gps": result.get("gps"),
    }