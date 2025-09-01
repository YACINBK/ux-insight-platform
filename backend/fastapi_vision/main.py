from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image, ImageDraw
import io
import json
import os
import base64
import numpy as np
from torch.nn import functional as F
from ocr_enhancer import get_ocr_enhancer

app = FastAPI(title="Vision Model API")

# Globals for model and label map
global_model = None
global_idx2Label = None

# Globals for classification model and label map
screen_classification_model = None
screen_classification_idx2Label = None

def get_model_and_labels():
    global global_model, global_idx2Label
    if global_model is None or global_idx2Label is None:
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "webui-main", "downloads", "checkpoints", "screenrecognition-web7k.torchscript")
        class_map_path = os.path.join(base_dir, "webui-main", "metadata", "screenrecognition", "class_map.json")
        global_model = torch.jit.load(model_path)
        with open(class_map_path, "r") as f:
            class_map = json.load(f)
        global_idx2Label = class_map['idx2Label']
    return global_model, global_idx2Label

def get_screen_classification_model_and_labels():
    global screen_classification_model, screen_classification_idx2Label
    if screen_classification_model is None or screen_classification_idx2Label is None:
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "webui-main", "downloads", "checkpoints", "screenclassification-resnet-noisystudent+web350k.torchscript")
        class_map_path = os.path.join(base_dir, "webui-main", "metadata", "screenclassification", "class_map_enrico.json")
        screen_classification_model = torch.jit.load(model_path)
        with open(class_map_path, "r") as f:
            class_map = json.load(f)
        screen_classification_idx2Label = class_map['idx2Label']
    return screen_classification_model, screen_classification_idx2Label

@app.on_event("startup")
def load_model():
    get_model_and_labels()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        model, idx2Label = get_model_and_labels()
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_input = transforms.ToTensor()(image)
        pred = model([img_input])[1]
        conf_thresh = 0.5
        detections = []

        # Draw on a copy of the image
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        for i in range(len(pred[0]["boxes"])):
            conf_score = pred[0]["scores"][i].item()
            if conf_score > conf_thresh:
                x1, y1, x2, y2 = pred[0]["boxes"][i].detach().cpu().numpy()
                label_idx = int(pred[0]["labels"][i].item())
                label = idx2Label.get(str(label_idx), f"unknown_{label_idx}")
                detections.append({
                    "class": label,  # Changed from "label" to "class" to match expected format
                    "confidence": conf_score,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                })
                # Draw rectangle and label
                draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
                draw.text((x1, y1), f"{label} {conf_score:.2f}", fill="red")

        # Enhance detections with OCR
        try:
            ocr_enhancer = get_ocr_enhancer()
            image_np = np.array(image)
            enhanced_detections = ocr_enhancer.enhance_detections(image_np, detections)
            
            # Update annotated image with enhanced labels
            draw = ImageDraw.Draw(annotated_image)
            for detection in enhanced_detections:
                bbox = detection.get('bbox', [])
                if len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                    enhanced_class = detection.get('class', 'Unknown')
                    extracted_text = detection.get('extracted_text', '')
                    draw.rectangle([x1, y1, x2, y2], outline='blue', width=2)
                    label_text = f"{enhanced_class}"
                    if extracted_text:
                        label_text += f" ({extracted_text})"
                    draw.text((x1, y1-20), label_text, fill="blue")
            
            detections = enhanced_detections
            print(f"✅ Enhanced {len(detections)} detections with OCR")
            
        except Exception as ocr_error:
            print(f"⚠️ OCR enhancement failed: {ocr_error}")
            # Continue with original detections if OCR fails

        # Encode annotated image as base64
        buffered = io.BytesIO()
        annotated_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return JSONResponse(content={
            "detections": detections
        })
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/classify_screen")
async def classify_screen(file: UploadFile = File(...)):
    try:
        model, idx2Label = get_screen_classification_model_and_labels()
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_transforms = transforms.Compose([
            transforms.Resize(128),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        img_input = img_transforms(image)
        pred = model(img_input.unsqueeze(0))
        conf = F.softmax(pred, dim=-1)
        _, ind = pred.max(dim=-1)
        label = idx2Label[str(int(ind))]
        confidence = float(conf[0][ind])
        return JSONResponse(content={
            "label": label,
            "confidence": confidence
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)}) 