import torch
from torchvision import transforms
from PIL import Image
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models/ai_image_model.pt"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = torch.load(MODEL_PATH, map_location=device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def predict_ai_image(image_path):
    image = Image.open(image_path).convert("RGB")
    x = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(x)
        prob = torch.sigmoid(logits).item()

    score = int(prob * 100)

    # 🔥 CALIBRATED VERDICT
    if score >= 75:
        verdict = "HIGHLY AI GENERATED"
    elif score >= 55:
        verdict = "POSSIBLY AI GENERATED"
    else:
        verdict = "LIKELY REAL IMAGE"

    return {
        "score": score,
        "verdict": verdict,
        "confidence": min(max(score, 5), 95),
        "raw_probability": round(prob, 4)
    }