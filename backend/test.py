import requests
import numpy as np
from PIL import Image

# 1. Load and preprocess the image
# Replace 'your_image.png' with your image file path
img = Image.open("workflow.png").convert("RGB")  # Ensure 3 channels (RGB), drop alpha if present
img = img.resize((224, 224))                      # Resize to 224x224 as expected by ResNet-50
img_np = np.array(img).astype(np.float32)         # Convert to numpy array, shape: (224, 224, 3)

# 2. Transpose to CHW format (channels, height, width)
img_np = img_np.transpose(2, 0, 1)                # Now shape: (3, 224, 224)

# 3. Add batch dimension
img_np = np.expand_dims(img_np, axis=0)           # Now shape: (1, 3, 224, 224)

# 4. (Optional) Normalize the image
# Many ResNet-50 models expect normalization, but the ONNX model you downloaded may work with raw 0-255 values.
# If you get strange results, try uncommenting the following lines:
# mean = np.array([0.485, 0.456, 0.406]).reshape(1, 3, 1, 1)
# std = np.array([0.229, 0.224, 0.225]).reshape(1, 3, 1, 1)
# img_np = img_np / 255.0
# img_np = (img_np - mean) / std

# 5. Prepare the Triton inference request
data = {
    "inputs": [
        {
            "name": "data",  # Must match the input name in config.pbtxt
            "shape": list(img_np.shape),  # [1, 3, 224, 224]
            "datatype": "FP32",
            "data": img_np.flatten().tolist()
        }
    ]
}

# 6. Send the request to Triton
response = requests.post(
    "http://localhost:8000/v2/models/resnet50/infer",
    json=data
)

# 7. Print the result
print("Triton response:")
print(response.json())