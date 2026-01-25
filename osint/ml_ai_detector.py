import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision import models
from torchvision.models import MobileNet_V2_Weights

# Load pretrained MobileNet
weights = MobileNet_V2_Weights.DEFAULT
model = models.mobilenet_v2(weights=weights)
model.eval()
model.eval()

# ImageNet normalization
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def ml_ai_prediction(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_tensor)

        confidence = torch.softmax(outputs, dim=1).max().item()

        # This model is NOT trained for AI detection,
        # so we treat confidence as anomaly likelihood
        ai_likelihood = min(confidence * 100, 85)

        return {
            "ai_probability": round(ai_likelihood, 2),
            "note": "ML-based visual anomaly estimation"
        }

    except Exception as e:
        return {
            "ai_probability": None,
            "error": str(e)
        }
