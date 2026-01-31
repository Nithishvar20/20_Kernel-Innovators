import os
import cv2
import random
from flask import Blueprint, render_template, request

ai_face_morph_bp = Blueprint(
    "ai_face_morph_detector",
    __name__,
    template_folder="../templates"
)

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

@ai_face_morph_bp.route("/ai-face-morph", methods=["GET", "POST"])
def ai_face_morph():

    # ======================
    # GET → Upload Page
    # ======================
    if request.method == "GET":
        return render_template("ai_face_morph_upload.html")

    # ======================
    # POST → Process Image
    # ======================
    image = request.files.get("image")

    if not image or image.filename == "":
        return render_template(
            "ai_face_morph_upload.html",
            error="Please upload an image"
        )

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)

    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    output_path = os.path.join(STATIC_FOLDER, "ai_face_morph_result.jpg")

    image.save(input_path)

    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    results = []

    # Demo logic: exactly ONE real face
    real_index = -1
    if len(faces) > 0:
        real_index = random.randint(0, len(faces) - 1)

    for i, (x, y, w, h) in enumerate(faces):
        if i == real_index:
            label = "REAL"
            color = (0, 255, 0)
            confidence = random.randint(85, 95)
        else:
            label = "AI-MORPHED"
            color = (0, 0, 255)
            confidence = random.randint(85, 95)

        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            img,
            f"{label} ({confidence}%)",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        results.append({
            "face": i + 1,
            "result": label,
            "confidence": confidence
        })

    cv2.imwrite(output_path, img)

    return render_template(
        "ai_face_morph_result.html",
        image="ai_face_morph_result.jpg",
        results=results
    )