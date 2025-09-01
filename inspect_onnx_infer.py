import onnxruntime as ort
import numpy as np

# Path to your ONNX model
model_path = r"D:\triton_model_repository\best\1\model.onnx"

# Create an ONNX Runtime session
session = ort.InferenceSession(model_path)

# Get input details
input_name = session.get_inputs()[0].name
input_shape = session.get_inputs()[0].shape
input_type = session.get_inputs()[0].type
print(f"Input name: {input_name}, shape: {input_shape}, type: {input_type}")

# Prepare a dummy input (use 640x640 as a common YOLO size, adjust if needed)
dummy_input = np.random.rand(1, 3, 640, 640).astype(np.float32)

# Run inference
outputs = session.run(None, {input_name: dummy_input})

# Print output details
for i, output in enumerate(outputs):
    print(f"Output {i}: shape {output.shape}, dtype {output.dtype}") 