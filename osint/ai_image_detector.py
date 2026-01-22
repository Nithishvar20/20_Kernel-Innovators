import cv2
import numpy as np
from osint.ml_ai_detector import ml_ai_prediction

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image):
    exif = {}
    raw = image._getexif()
    if not raw:
        return exif

    for tag_id, value in raw.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value
    return exif


def get_gps_info(exif):
    gps_data = {}
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    for key in gps_info:
        name = GPSTAGS.get(key, key)
        gps_data[name] = gps_info[key]

    return gps_data
def analyze_noise_and_sharpness(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        return None

    # Noise estimation using Laplacian variance
    noise_score = cv2.Laplacian(img, cv2.CV_64F).var()

    # Sharpness consistency
    edges = cv2.Canny(img, 100, 200)
    edge_density = np.mean(edges > 0)

    return {
        "noise_score": noise_score,
        "edge_density": edge_density
    }



def analyze_ai_image(image_path):
    score = 0
    reasons = []

    # ---------- Load image ----------
    img = Image.open(image_path)
    width, height = img.size

    # ---------- EXIF extraction ----------
    exif = get_exif_data(img)
    camera_make = exif.get("Make")
    camera_model = exif.get("Model")
    date_taken = exif.get("DateTimeOriginal")
    gps = get_gps_info(exif)

    # ---------- Image origin detection ----------
    image_origin = "Unknown"
    mobile_brands = ["Apple", "Samsung", "Xiaomi", "OnePlus", "OPPO", "Vivo", "Google"]

    if camera_make:
        for brand in mobile_brands:
            if brand.lower() in camera_make.lower():
                image_origin = "Mobile Camera"
                break

    # ---------- Noise & Sharpness Analysis (UPDATED) ----------
    visual_metrics = analyze_noise_and_sharpness(image_path)

    if visual_metrics:
        noise = visual_metrics["noise_score"]
        edge_density = visual_metrics["edge_density"]

        # 🔥 AI: over-smooth synthetic image (MOST IMPORTANT)
        if noise < 40 and edge_density < 0.05:
            score += 50
            reasons.append(
                "Over-smooth image with extremely low sensor noise (synthetic AI pattern)"
            )

        # AI: uniform sharpness pattern
        elif noise < 80 and edge_density > 0.15:
            score += 30
            reasons.append(
                "Low sensor noise with uniform sharpness (AI-like pattern)"
            )

        # Real camera indicator
        elif noise > 120:
            reasons.append(
                "Natural sensor noise detected (real camera characteristic)"
            )

    # ---------- ML-based Analysis ----------
    ml_result = ml_ai_prediction(image_path)

    if ml_result.get("ai_probability") is not None:
        ml_score = ml_result["ai_probability"]

        if ml_score > 60:
            score += 30
            reasons.append(
                f"ML model detected synthetic visual patterns ({ml_score}%)"
            )

    # ---------- Resolution check (STRONG AI signal) ----------
    if width in (512, 1024) and height in (512, 1024):
        score += 50
        reasons.append("Fixed square resolution commonly used by AI generators")

    # ---------- Metadata handling (WEAK signal only) ----------
    if not exif:
        reasons.append("Metadata missing (may be stripped by platform)")

    # ---------- Mobile safety cap ----------
    if image_origin == "Mobile Camera":
        score = min(score, 25)

    # ---------- Verdict ----------
    if score >= 60:
        verdict = "Likely AI Generated"
    elif score >= 30:
        verdict = "Possibly AI Generated"
    else:
        verdict = "Likely Real Image"

    # ---------- Confidence ----------
    if image_origin == "Mobile Camera":
        confidence = "Low"
    elif score >= 60:
        confidence = "High"
    elif score >= 30:
        confidence = "Medium"
    else:
        confidence = "High"

    return {
        "score": score,
        "verdict": verdict,
        "confidence": confidence,
        "image_origin": image_origin,
        "reasons": reasons,
        "resolution": f"{width} x {height}",
        "camera_make": camera_make,
        "camera_model": camera_model,
        "date_taken": date_taken,
        "gps": gps,
        "visual_analysis": visual_metrics,
        "ml_analysis": ml_result

        
    }
