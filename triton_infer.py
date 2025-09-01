import numpy as np
from PIL import Image
import tritonclient.http as httpclient

# === USER: Set your image path here ===
IMAGE_PATH = r"D:\dataset\combined\16.jpg"  # <-- Updated to your image file

# Triton server details
TRITON_URL = "localhost:8000"
MODEL_NAME = "best"

# 1. Load and preprocess the image
def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((640, 640))  # Resize to model's expected input
    img_np = np.array(img).astype(np.float32) / 255.0  # Normalize to 0-1
    img_np = img_np.transpose(2, 0, 1)  # HWC to CHW
    img_np = np.expand_dims(img_np, axis=0)  # Add batch dimension: (1, 3, 640, 640)
    return img_np

# 2. Prepare Triton client and request
def infer(image_np):
    client = httpclient.InferenceServerClient(url=TRITON_URL)
    inputs = [httpclient.InferInput("images", image_np.shape, "FP32")]
    inputs[0].set_data_from_numpy(image_np)
    outputs = [httpclient.InferRequestedOutput("output0")]
    response = client.infer(MODEL_NAME, inputs=inputs, outputs=outputs)
    return response.as_numpy("output0")

if __name__ == "__main__":
    image_np = preprocess_image(IMAGE_PATH)
    output = infer(image_np)
    print("Model output shape:", output.shape)
    print("Model output (first 5 values):", output.flatten()[:5]) 