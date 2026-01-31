import torch
import torchvision.transforms as T
import torchvision.models as models
import torch.nn as nn
from PIL import Image
from pathlib import Path

# ================= CONFIG =================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "ai_image_model.pt"

# ================= TRANSFORMS =================
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ================= MODEL =================
model = models.efficientnet_b0(
    weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1
)

# 🔥 MUST MATCH TRAINING (1 output neuron)
model.classifier[1] = nn.Linear(
    model.classifier[1].in_features, 1
)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location=DEVICE)
)

model.to(DEVICE)
model.eval()

# ================= PREDICT =================
def predict(image_path: str):
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(img)
        prob = torch.sigmoid(logits).item()  # 0–1

    score = int(prob * 100)

    if score > 70:
        verdict = "Highly AI Generated"
    elif score >= 50:
        verdict = "Possibly AI Generated"
    else:
        verdict = "Likely Real Image"

    return {
        "score": score,
        "probability": round(prob, 3),
        "verdict": verdict
    }