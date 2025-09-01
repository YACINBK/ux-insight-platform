import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tritonclient.http as httpclient

# === USER: Set your image path here ===
IMAGE_PATH = r"D:\dataset\combined\16.jpg"
CLASS_NAMES = [
    'button', 'text', 'input', 'image', 'container', 'navigation', 'checkbox', 'radio', 'slider',
    'progress', 'toolbar', 'card', 'list_item', 'webview', 'ad'
]

TRITON_URL = "localhost:8000"
MODEL_NAME = "best"
IMG_SIZE = 640
CONF_THRESH = 0.10  # Restored to normal value
IOU_THRESH = 0.45


def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_np = np.array(img).astype(np.float32) / 255.0
    img_np = img_np.transpose(2, 0, 1)
    img_np = np.expand_dims(img_np, axis=0)
    return img_np, img

def infer(image_np):
    client = httpclient.InferenceServerClient(url=TRITON_URL)
    inputs = [httpclient.InferInput("images", image_np.shape, "FP32")]
    inputs[0].set_data_from_numpy(image_np)
    outputs = [httpclient.InferRequestedOutput("output0")]
    response = client.infer(MODEL_NAME, inputs=inputs, outputs=outputs)
    return response.as_numpy("output0")

def non_max_suppression(boxes, scores, iou_threshold):
    idxs = np.argsort(scores)[::-1]
    keep = []
    while len(idxs) > 0:
        i = idxs[0]
        keep.append(i)
        if len(idxs) == 1:
            break
        ious = compute_iou(boxes[i], boxes[idxs[1:]])
        idxs = idxs[1:][ious < iou_threshold]
    return keep

def compute_iou(box, boxes):
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])
    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - inter_area
    return inter_area / (union_area + 1e-6)

def postprocess(output, orig_img):
    output = np.squeeze(output).transpose(1, 0)  # (8400, 19)
    boxes = output[:, :4]
    objectness = output[:, 4]
    class_probs = output[:, 5:]
    print('Max objectness:', objectness.max())
    print('Max class prob:', class_probs.max())
    scores = objectness[:, None] * class_probs  # (8400, 15)
    boxes_all, scores_all, class_ids_all = [], [], []
    for class_idx in range(scores.shape[1]):
        class_scores = scores[:, class_idx]
        mask = class_scores > CONF_THRESH
        if not np.any(mask):
            continue
        filtered_boxes = boxes[mask]
        filtered_scores = class_scores[mask]
        filtered_boxes = xywh2xyxy(filtered_boxes) * IMG_SIZE
        keep = non_max_suppression(filtered_boxes, filtered_scores, IOU_THRESH)
        boxes_all.extend(filtered_boxes[keep])
        scores_all.extend(filtered_scores[keep])
        class_ids_all.extend([class_idx] * len(keep))
    return boxes_all, scores_all, class_ids_all

def xywh2xyxy(boxes):
    x_c, y_c, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    x1 = x_c - w / 2
    y1 = y_c - h / 2
    x2 = x_c + w / 2
    y2 = y_c + h / 2
    return np.stack([x1, y1, x2, y2], axis=1)

def draw_boxes(img, boxes, scores, class_ids):
    draw = ImageDraw.Draw(img)
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        pass
    for box, score, class_id in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = box
        label = f"{CLASS_NAMES[class_id]}: {score:.2f}"
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1, y1), label, fill="red", font=font)
    return img

if __name__ == "__main__":
    image_np, orig_img = preprocess_image(IMAGE_PATH)
    output = infer(image_np)
    print("First 5 output values:", output.flatten()[:5])
    boxes, scores, class_ids = postprocess(output, orig_img)
    print(f"Detections: {len(boxes)}")
    for i, (box, score, class_id) in enumerate(zip(boxes, scores, class_ids)):
        print(f"Box {i}: {box}, Score: {score:.2f}, Class: {CLASS_NAMES[class_id]}")
    img_with_boxes = draw_boxes(orig_img, boxes, scores, class_ids)
    img_with_boxes.save("output_with_boxes.png")
    print("Saved image with detections as output_with_boxes.png") 