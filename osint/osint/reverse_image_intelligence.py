import os
import hashlib
from PIL import Image

def analyze_image_exposure(image_path, image_url):
    data = {}

    if image_path and os.path.exists(image_path):
        # Hash
        with open(image_path, "rb") as f:
            data["image_hash"] = hashlib.md5(f.read()).hexdigest()

        data["source"] = "uploaded_image"
        data["file_size_kb"] = round(os.path.getsize(image_path) / 1024, 2)

        # Image properties
        img = Image.open(image_path)
        data["resolution"] = f"{img.width}x{img.height}"
        data["format"] = img.format

        # Simple reuse heuristic
        if data["file_size_kb"] < 100:
            data["reuse_probability"] = "High"
        elif data["file_size_kb"] < 500:
            data["reuse_probability"] = "Medium"
        else:
            data["reuse_probability"] = "Low"

    elif image_url:
        data["source"] = "public_image_url"
        data["reuse_probability"] = "High"
        data["resolution"] = "Unknown"
        data["format"] = "Unknown"

    

    return data
