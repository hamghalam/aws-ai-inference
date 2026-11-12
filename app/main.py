from io import BytesIO

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from torchvision.models import (
    MobileNet_V2_Weights,
    mobilenet_v2,
)

app = FastAPI(
    title="AWS AI Inference Service",
    description="Image classification using PyTorch and MobileNetV2",
    version="1.0.0",
)

# Select CPU for local development
device = torch.device("cpu")

# Load pretrained model
weights = MobileNet_V2_Weights.DEFAULT
model = mobilenet_v2(weights=weights)
model.eval()
model.to(device)

# Image preprocessing
preprocess = weights.transforms()

# ImageNet class labels
categories = weights.meta["categories"]


@app.get("/")
def home():
    return {
        "message": "AI inference service is running",
        "model": "MobileNetV2",
        "device": str(device),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    try:
        contents = await file.read()

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Image must be smaller than 10 MB",
            )

        image = Image.open(BytesIO(contents)).convert("RGB")
        input_tensor = preprocess(image).unsqueeze(0).to(device)

        with torch.inference_mode():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

        confidence, predicted_idx = torch.max(probabilities, dim=0)

        return {
            "prediction": categories[predicted_idx.item()],
            "confidence": round(confidence.item(), 4),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image or inference error: {str(exc)}",
        )
