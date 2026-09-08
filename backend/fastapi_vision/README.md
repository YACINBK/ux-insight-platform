# FastAPI Vision service

Screenshot analysis for the platform, combining two TorchScript models from
the [WebUI project (biglab, CMU)](https://huggingface.co/biglab) with
EasyOCR-based label enhancement.

## Endpoints

- `POST /analyze` — UI-element detections (`class`, `confidence`, `bbox`),
  labels refined with OCR text by `ocr_enhancer.py`
- `POST /classify_screen` — ENRICO screen classification
  (`{label, confidence}`)

## Model checkpoints (required setup — not in the repo)

The service expects, relative to this directory:

```
webui-main/downloads/checkpoints/screenrecognition-web7k.torchscript
webui-main/downloads/checkpoints/screenclassification-resnet-noisystudent+web350k.torchscript
```

Download them from the WebUI project's published checkpoints
([HuggingFace — biglab](https://huggingface.co/biglab)) and drop them in.
The class/label maps are already committed under
`webui-main/metadata/` (`screenrecognition/class_map.json`,
`screenclassification/class_map_enrico.json`). Without the checkpoints the
service fails its model load at startup.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --port 8001          # local
docker build -t ux-insight-vision .   # container (port 5001 in compose)
```

First run downloads EasyOCR recognition models. Heavy dependencies
(PyTorch, torchvision, OpenCV) — see "First build expectations" in the root
README.
