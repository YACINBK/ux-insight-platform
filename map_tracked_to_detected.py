import json
import sys
import os
from typing import List, Dict, Any

def bbox_to_xyxy(bbox):
    # Convert {x, y, width, height} to [x1, y1, x2, y2]
    if not bbox:
        return None
    return [bbox['x'], bbox['y'], bbox['x'] + bbox['width'], bbox['y'] + bbox['height']]

def iou(boxA, boxB):
    # Compute intersection over union for two [x1, y1, x2, y2] boxes
    if not boxA or not boxB:
        return 0.0
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    if boxAArea == 0 or boxBArea == 0:
        return 0.0
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def normalize_type(t):
    # Map synonyms to canonical types
    t = t.lower()
    if t in ['button', 'menuitem', 'btn']:
        return 'button'
    if t in ['a', 'link']:
        return 'link'
    if t in ['input', 'textbox', 'text']:
        return 'input'
    return t

def main():
    if len(sys.argv) != 4:
        print("Usage: python map_tracked_to_detected.py detected.json tracked.json output.json")
        sys.exit(1)
    detected_path, tracked_path, output_path = sys.argv[1:4]
    with open(detected_path, 'r') as f:
        detected_items = json.load(f)
    with open(tracked_path, 'r') as f:
        tracked_events = json.load(f)
    # Preprocess tracked events
    for event in tracked_events:
        event['bbox_xyxy'] = bbox_to_xyxy(event.get('bbox'))
        event['elementTypeNorm'] = normalize_type(event.get('elementType', ''))
    # Preprocess detected items
    for det in detected_items:
        det['bbox_xyxy'] = det['bbox']
        det['classNorm'] = normalize_type(det.get('class', ''))
    # Mapping
    IOU_THRESHOLD = 0.5
    mapped = []
    for det in detected_items:
        matches = []
        for event in tracked_events:
            if det['classNorm'] == event['elementTypeNorm']:
                overlap = iou(det['bbox_xyxy'], event['bbox_xyxy'])
                if overlap > IOU_THRESHOLD:
                    matches.append({
                        'eventType': event.get('eventType'),
                        'elementText': event.get('elementText'),
                        'elementClasses': event.get('elementClasses'),
                        'bbox': event.get('bbox'),
                        'timestamp': event.get('timestamp'),
                        'sessionId': event.get('sessionId'),
                        'url': event.get('url'),
                        'iou': overlap
                    })
        det_out = dict(det)
        det_out['matched_tracked_events'] = matches
        mapped.append(det_out)
    with open(output_path, 'w') as f:
        json.dump(mapped, f, indent=2)
    # Print summary
    print(f"Mapping complete. {len(detected_items)} detected items processed.")
    matched = sum(1 for d in mapped if d['matched_tracked_events'])
    print(f"{matched} detected items had at least one tracked event mapped (IoU > {IOU_THRESHOLD}).")
    print(f"Output written to {output_path}")

if __name__ == '__main__':
    main() 